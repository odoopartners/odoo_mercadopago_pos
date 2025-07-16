import logging
from datetime import datetime, timedelta

from odoo import fields, models, _
from odoo.exceptions import AccessError, UserError

from .mercado_pago_pos_request import MercadoPagoPosRequestExtended as MercadoPagoPosRequest
from .test_data import create_order_data_resp, get_order_data_resp, refund_data_resp
_logger = logging.getLogger(__name__)


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    mp_smart_payment = fields.Boolean(string='Mercado Pago Smart payment', groups="point_of_sale.group_pos_manager")
    mp_client_id = fields.Char(string='Mercado Pago Client ID', groups="point_of_sale.group_pos_manager")
    mp_client_secret = fields.Char(string='Mercado Pago Client Secret', groups="point_of_sale.group_pos_manager")
    mp_refresh_token = fields.Char(string='Mercado Pago refresh token')
    mp_pkce = fields.Char(string='Mercado Pago PKCE')
    mp_pkce_code_verifier = fields.Char(string='Mercado Pago PKCE code verifier')
    mp_token_lifetime = fields.Date(string='Mercado Pago token lifetime')

    def force_pdv(self):
        """
        Triggered in debug mode when the user wants to force the "PDV" mode.
        It calls the Mercado Pago API to set the terminal mode to "PDV".
        """
        if not self.mp_smart_payment:
            return super(PosPaymentMethod, self).force_pdv()

        self._check_special_access()
        mercado_pago = MercadoPagoPosRequest(self.sudo().mp_bearer_token)
        _logger.info('Calling Mercado Pago to force the terminal mode to "PDV"')

        mode = {'terminals': [{
            "id": self.mp_id_point_smart_complet,
            "operating_mode": "PDV"
        }]}
        resp = mercado_pago.call_mercado_pago("patch", "/terminals/v1/setup", mode)
        if resp['terminals'][0].get("operating_mode") != "PDV":
            raise UserError(_("Unexpected Mercado Pago response: %s", resp))
        _logger.debug("Successfully set the terminal mode to 'PDV'.")
        return None

    def mp_get_url_redirect_uri(self):
        mp_redirect_uri = self.env['ir.config_parameter'].get_param('web.base.url')
        if not mp_redirect_uri:
            raise UserError(_("No se ha configurado la URL de redirección en la configuración de Odoo: web.base.url"))
        return f'{mp_redirect_uri}/pos_mercado_pago/point-smart/oauth'

    @staticmethod
    def mp_get_token_lifetime():
        return (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')

    def mp_create_bearer_token(self, mp_pkce, mp_pkce_code_verifier):
        self._check_special_access()
        token_data = {
            "client_secret": self.mp_client_secret,
            "client_id": self.mp_client_id,
            "code": mp_pkce,
            "code_verifier": mp_pkce_code_verifier,
            "grant_type": "authorization_code",
            "redirect_uri": self.mp_get_url_redirect_uri(),
            "test_token": "false"
        }
        resp = self._mp_request_token(token_data)
        self.mp_update_payment_method_data(
            resp['access_token'],
            resp['refresh_token'],
            mp_pkce,
            mp_pkce_code_verifier
        )

    def mp_refresh_bearer_token(self):
        self._check_special_access()
        if not self.mp_pkce or not self.mp_pkce_code_verifier:
            raise UserError(_("Fields mp_pkce or mp_pkce_code_verifier are empty, contact your administrator!"))
        token_data = {
            "client_secret": self.mp_client_secret,
            "client_id": self.mp_client_id,
            "grant_type": "refresh_token",
            "refresh_token": self.mp_refresh_token,
            "test_token": "false"
        }
        resp = self._mp_request_token(token_data)
        self.mp_update_payment_method_data(
            resp['access_token'],
            resp['refresh_token'],
            self.mp_pkce,
            self.mp_pkce_code_verifier
        )

    @staticmethod
    def _mp_request_token(token_data):
        mercado_pago = MercadoPagoPosRequest(False)
        _logger.info("_mp_request_token(), Oauth data from Mercado Pago: %s", token_data)
        resp = mercado_pago.call_mercado_pago("post", "/oauth/token", token_data)
        _logger.info("_mp_request_token(), Oauth response from Mercado Pago: %s", resp)
        if resp.get('error'):
            raise UserError(_("Please verify your client id and client secret as it was rejected: %s", resp.get('message', '-')))
        return resp

    def mp_update_payment_method_data(self, access_token, refresh_token, pkce, pkce_code_verifier):
        mp_token_lifetime = self.mp_get_token_lifetime()
        self._cr.execute("""
                         UPDATE pos_payment_method
                         SET mp_bearer_token=%s,
                             mp_refresh_token=%s,
                             mp_pkce=%s,
                             mp_pkce_code_verifier=%s,
                             mp_token_lifetime=%s
                         WHERE id = %s
                         """, (access_token, refresh_token, pkce, pkce_code_verifier, mp_token_lifetime, self.id))

    def mp_payment_intent_create(self, infos):
        """
        Called from frontend for creating an order in Mercado Pago
        """
        if not self.mp_smart_payment:
            del infos['additional_info']['pos_reference']
            del infos['additional_info']['idempotency_key']
            return super(PosPaymentMethod, self).mp_payment_intent_create(infos)

        self._check_special_access()
        mercado_pago = MercadoPagoPosRequest(self.sudo().mp_bearer_token, infos['additional_info']['idempotency_key'])
        external_reference = infos['additional_info']['external_reference']
        info_pos_order = {
            "type": "point",
            "external_reference": external_reference,
            "transactions": {"payments": [{"amount": str(int(infos["amount"]/ 100))}]},
            "config": {
                "point": {
                    "terminal_id": self.mp_id_point_smart_complet,
                    "print_on_terminal": 'seller_ticket'
                },
            },
            # Odoo ID in Mercado Pago
            "integration_data": {"platform_id": "dev_cdf1cfac242111ef9fdebe8d845d0987"},
        }
        _logger.info("mp_payment_intent_create(), Order response from data: %s", info_pos_order)
        # resp = mercado_pago.call_mercado_pago("post", f"/v1/orders", info_pos_order)
        resp = create_order_data_resp
        _logger.info("mp_payment_intent_create(), Order response from Mercado Pago: %s", resp)

        if resp.get('errors'):
            error_resp = {'error': True, 'message': self.mp_catch_smart_pago_errors(resp)}
            return error_resp
        return resp

    def mp_payment_intent_get(self, payment_intent_id):
        """
        Called from frontend to get the last Order from Mercado Pago
        """
        if not self.mp_smart_payment:
            return super(PosPaymentMethod, self).mp_payment_intent_get(payment_intent_id)

        self._check_special_access()

        mercado_pago = MercadoPagoPosRequest(self.sudo().mp_bearer_token)
        # Call Mercado Pago for order status
        _logger.info("mp_payment_intent_get(), Order data: %s", payment_intent_id)
        # resp = mercado_pago.call_mercado_pago("get", f"/v1/orders/{payment_intent_id}", {})
        resp = get_order_data_resp
        _logger.info("mp_payment_intent_get(), Order response from Mercado Pago: %s", resp)
        if resp.get('status', False):
            resp['state'] = resp['status'].upper()
            if resp['state'] in ['CREATED', 'AT_TERMINAL']:
                resp['state'] = 'OPEN'
        if resp.get('transactions', False) and resp['transactions'].get('payments', False):
            resp['payment'] = {'id': resp['transactions']['payments'][0]['id']}
        _logger.info("mp_payment_intent_get(), Update Order response from Mercado Pago: %s", resp)
        return resp

    def mp_payment_intent_cancel(self, infos):
        """
        Called from frontend to cancel an Order in Mercado Pago
        """
        if not self.mp_smart_payment:
            return super(PosPaymentMethod, self).mp_payment_intent_get(infos['payment_intent_id'])

        self._check_special_access()

        mercado_pago = MercadoPagoPosRequest(self.sudo().mp_bearer_token, infos['idempotency_key'])
        # Call Mercado Pago for order cancellation
        resp = mercado_pago.call_mercado_pago("post", f"/v1/orders/{infos['payment_intent_id']}/cancel", {})
        _logger.info("mp_payment_intent_cancel(), Order cancel: %s", infos['payment_intent_id'])
        _logger.info("mp_payment_intent_cancel(), Order response from Mercado Pago: %s", resp)
        if resp.get('errors'):
            resp.update({
                'error': resp['errors'],
                'status': 409
            })
        return resp

    def mp_payment_intent_reversal(self, infos):
        """
        Called from frontend to reversal an Order in Mercado Pago
        """
        if not self.mp_smart_payment:
            return False

        self._check_special_access()

        mercado_pago = MercadoPagoPosRequest(self.sudo().mp_bearer_token, infos['idempotency_key'])
        # Call Mercado Pago for order cancellation
        # resp = mercado_pago.call_mercado_pago("post", f"/v1/orders/{infos['payment_intent_id']}/refund", {})
        resp = refund_data_resp
        _logger.info("mp_payment_intent_reversal(), Order refund: %s", infos['payment_intent_id'])
        _logger.info("mp_payment_intent_reversal(), Order response from Mercado Pago: %s", resp)
        return resp

    def _find_terminal(self, token, point_smart):
        if not self.mp_smart_payment:
            return super(PosPaymentMethod, self)._find_terminal(token, point_smart)

        if not token:
            return self.mp_id_point_smart
        mercado_pago = MercadoPagoPosRequest(token)
        data = mercado_pago.call_mercado_pago("get", "/terminals/v1/list", {})
        if data.get('data') and data['data'].get('terminals'):
            # Search for a device id that contains the serial number entered by the user
            found_device = next((device for device in data['data']['terminals'] if point_smart in device['id']), None)

            if not found_device:
                raise UserError(_("The terminal serial number is not registered on Mercado Pago"))
            return found_device.get('id', '')
        else:
            raise UserError(_("Please verify your production user token as it was rejected"))

    @staticmethod
    def mp_catch_smart_pago_errors(json_data):
        error_messages = []
        for error in json_data['errors']:
            code = error.get('code', 'Sin código')
            message = error.get('message', 'Sin mensaje')
            details = "\n".join(error.get('details', []))
            error_messages.append(f"Código: {code}\nMensaje: {message}\nDetalles:\n{details}")

        error_message_string = "\n\n".join(error_messages)
        return error_message_string

    def mp_get_payment_status(self, payment_id):
        """
            Extended from pos_payment_method.py to avoid getting payment status because in Mercado pago order's not necessary this validation
        """
        if not self.mp_smart_payment:
            return super(PosPaymentMethod, self).mp_payment_intent_get(payment_id)

        self._check_special_access()
        resp = {
            "id": payment_id,
            "status": "approved"
        }
        _logger.info("mp_get_payment_status(), response from Mercado Pago: %s", resp)
        return resp

    def write(self, vals):
        records = super().write(vals)
        if self.mp_id_point_smart and self.mp_smart_payment:
            self.mp_id_point_smart_complet = self.mp_id_point_smart
        return records

    def create(self, vals):
        records = super().create(vals)
        for record in records:
            if record.mp_id_point_smart and record.mp_smart_payment:
                record.mp_id_point_smart_complet = record.mp_id_point_smart
        return records