from odoo import models, fields, api
from odoo.tools.translate import _
import os
import hashlib
import base64
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class MPAccessToken(models.TransientModel):
    _name = 'mp.access.token'
    _description = 'Generate Mercado Pago access token'

    payment_method_id = fields.Many2one(
        string='Método de pago',
        comodel_name='pos.payment.method',
        domain=[('use_payment_terminal', '=', 'mercado_pago')]
    )
    mp_pkce = fields.Char(
        string='PKCE',
        help='Pegar código recibido en la respuesta de Mercado Pago.'
    )
    mp_pkce_code_verifier = fields.Char(string='PKCE code verifier')
    pkce_generated = fields.Boolean(string='PKCE generado')

    @api.model
    def default_get(self, fields):
        res = super(MPAccessToken, self).default_get(fields)
        payment_method_id = self.env['pos.payment.method'].browse(self.env.context['active_ids']) if self.env.context.get(
            'active_model') == 'pos.payment.method' else self.env['pos.payment.method']
        if 'payment_method_id' in fields:
            res['payment_method_id'] = payment_method_id.id
        return res

    @staticmethod
    def mp_generate_code_verifier():
        """
            Generates a code verifier for the PKCE flow. The code verifier is a random string used to
            verify the authenticity of the authorization request.

            Returns:
                str: A random string of characters used as the code verifier.
        """
        length = 128
        characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~"
        return ''.join(characters[os.urandom(1)[0] % len(characters)] for _ in range(length))

    @staticmethod
    def mp_generate_code_challenge(code_verifier):
        """
            Generates a code challenge and its corresponding method based on a provided code verifier. The function attempts
            to use the S256 method for code challenge generation. If the S256 method fails, the function falls back to the Plain
            method.

            Args:
                code_verifier (str): The code verifier to be used for generating the code challenge.

            Returns:
                Tuple[str, str]: A tuple where the first element is the generated code challenge and the second is the method
                    used ("S256" or "Plain").
        """
        try:
            sha256_hash = hashlib.sha256(code_verifier.encode()).digest()
            code_challenge = base64.urlsafe_b64encode(sha256_hash).rstrip(b'=').decode('utf-8')
            code_challenge_method = "S256"
        except (AttributeError, TypeError):
            code_challenge = code_verifier
            code_challenge_method = "Plain"
        return code_challenge, code_challenge_method

    def mp_get_pkce(self):
        """
            Update the Mercado Pago bearer token for the payment method.
        """
        mp_client_id = self.payment_method_id.mp_client_id
        mp_redirect_uri = self.payment_method_id.mp_get_url_redirect_uri()

        code_verifier = self.mp_generate_code_verifier()
        _logger.info("mp_get_pkce - Code Verifier: %s", code_verifier)

        code_challenge, code_challenge_method = self.mp_generate_code_challenge(code_verifier)
        _logger.info("mp_get_pkce - Code Challenge: %s", code_challenge)
        _logger.info("mp_get_pkce - Code Challenge Method: %s", code_challenge_method)

        oauth_mp_url = f"https://auth.mercadopago.com/authorization?response_type=code&client_id={mp_client_id}&redirect_uri={mp_redirect_uri}&code_challenge={code_challenge}&code_challenge_method={code_challenge_method}"

        self.write({
            'pkce_generated': True,
            'mp_pkce_code_verifier': code_verifier
        })
        return {
            'type': 'ir.actions.act_url',
            'url': oauth_mp_url,
            'target': 'new',
        }

    def mp_create_bearer_token(self):
        """
            Check the status of the Mercado Pago bearer token for the payment method.
        """
        if not self.mp_pkce:
            raise UserError(_("Please insert PKCE code first"))
        self.payment_method_id.mp_create_bearer_token(self.mp_pkce, self.mp_pkce_code_verifier)
        return True
