import hashlib
import hmac
import logging
import re

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class PosMercadoPagoWebhook(http.Controller):

    @http.route('/pos_mercado_pago/point-smart/notification', methods=['POST'], type="http", auth="none", csrf=False)
    def smart_point_notification(self, **kwargs):
        """
            Process the notification sent by Mercado Pago
            Notification format is always JSON
        """
        _logger.info('Mercado Pago webhook notification: Headers received: %s', request.httprequest.headers)
        _logger.info('Mercado Pago webhook notification: Data received: %s', kwargs)

        # Check for mandatory keys in the header
        x_request_id = request.httprequest.headers.get('X-Request-Id')
        if not x_request_id:
            _logger.warning('POST message received with no X-Request-Id in header')
            return http.Response(status=400)

        x_signature = request.httprequest.headers.get('X-Signature')
        if not x_signature:
            _logger.warning('POST message received with no X-Signature in header')
            return http.Response(status=400)

        ts_m = re.search(r"ts=(\d+)", x_signature)
        v1_m = re.search(r"v1=([a-f0-9]+)", x_signature)
        ts = ts_m.group(1) if ts_m else None
        v1 = v1_m.group(1) if v1_m else None
        if not ts or not v1:
            _logger.warning('Webhook bad X-Signature, ts: %s, v1: %s', ts, v1)
            return http.Response(status=400)

        # Check for payload
        data = kwargs
        _logger.info('POST message received: %s', data)
        if not data:
            _logger.warning('POST message received with no data')
            return http.Response(status=400)

        # If and only if this webhook is related with a payment intend (see payment_mercado_pago.js)
        # then the field data['additional_info']['external_reference'] contains a string
        # formated like `XXX_YYY_ZZZ` where:
        # - `XXX` is the session_id
        # - `YYY` is the payment_method_id
        # - `ZZZ` is the pos order uuid for customer identification (Format xxxx-xxxx-xxx) where x is a hexadecimal digit
        external_reference = data.get('data.external_reference')
        mercado_pago_pattern = r'(\d+)_(\d+)_([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'

        if not external_reference or not (match := re.fullmatch(mercado_pago_pattern, external_reference)):
            _logger.warning('POST message received with no or malformed "external_reference" key: %s', external_reference)
            return http.Response(status=400)

        session_id, payment_method_id, _ = match.groups()

        pos_session_sudo = request.env['pos.session'].sudo().browse(int(session_id))
        if not pos_session_sudo or pos_session_sudo.state != 'opened':
            _logger.error("Invalid session id: %s", session_id)
            # This error is not related with Mercado Pago, simply acknowledge Mercado Pago message
            return http.Response('OK', status=200)

        payment_method_sudo = pos_session_sudo.config_id.payment_method_ids.filtered(lambda p: p.id == int(payment_method_id))
        if not payment_method_sudo or payment_method_sudo.use_payment_terminal != 'mercado_pago':
            _logger.error("Invalid payment method id: %s", payment_method_id)
            # This error is not related with Mercado Pago, simply acknowledge Mercado Pago message
            return http.Response('OK', status=200)

        # We have to check if this comes from Mercado Pago with the secret key
        # secret_key = payment_method_sudo.mp_webhook_secret_key
        secret_key = payment_method_sudo.mp_webhook_secret_key
        signed_template = f"id:{data['data.id'].lower()};request-id:{x_request_id};ts:{ts};"
        cyphed_signature = hmac.new(secret_key.encode(), signed_template.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(cyphed_signature, v1):
            _logger.error('Webhook authenticating failure, ts: %s, v1: %s', cyphed_signature, v1)
            return http.Response(status=401)

        _logger.debug('Webhook authenticated, POST message: %s', data)

        # Notify the frontend that we received a message from Mercado Pago
        pos_session_sudo.config_id._notify('MERCADO_PAGO_LATEST_MESSAGE', {
            'config_id': pos_session_sudo.config_id.id
        })

        # Acknowledge Mercado Pago message
        return http.Response('OK', status=200)

    @http.route('/pos_mercado_pago/point-smart/oauth', methods=['GET'], type="http", auth="none", csrf=False)
    def smart_point_oauth_notification(self, **kwargs):
        _logger.info('Mercado Pago Oauth notification: Headers received: %s', request.httprequest.headers)
        _logger.info('Mercado Pago Oauth notification: Data received: %s', kwargs)
        if not kwargs:
            _logger.warning('POST message received with no data')
            return http.Response(status=400)
        msg = f"- Response: {kwargs}"
        return http.Response(msg, status=200)
