import logging

from odoo import fields, models, _
from odoo.exceptions import AccessError, UserError

from .mercado_pago_pos_request import MercadoPagoPosRequest

_logger = logging.getLogger(__name__)


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    mp_smart_payment = fields.Boolean(string='Mercado Pago Smart payment')

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

        mode = {
            "operating_mode": "PDV",
            "id": self.mp_id_point_smart_complet
        }
        resp = mercado_pago.call_mercado_pago("patch", f"/terminals/v1/setup/", mode)
        if resp.get("operating_mode") != "PDV":
            raise UserError(_("Unexpected Mercado Pago response: %s", resp))
        _logger.debug("Successfully set the terminal mode to 'PDV'.")
        return None

    def mp_payment_intent_create(self, infos):
        """
        Called from frontend for creating an order in Mercado Pago
        """
        if not self.mp_smart_payment:
            del infos['additional_info']['external_reference']['pos_reference']
            del infos['additional_info']['external_reference']['order_uuid']
            return super(PosPaymentMethod, self).mp_payment_intent_create(infos)

        self._check_special_access()
        mercado_pago = MercadoPagoPosRequest(self.sudo().mp_bearer_token, infos['additional_info']['external_reference']['order_uuid'])
        # const infos = {
        #             amount: parseInt(line.amount * 100, 10),
        #             additional_info: {
        #                 external_reference: `${this.pos.config.current_session_id.id}_${line.payment_method_id.id}_${order.uuid}`,
        #                 print_on_terminal: true,
        #             },
        #         };
        # Call Mercado Pago for create order
        external_reference = infos['additional_info']['external_reference']
        info_pos_order = {
          "type": "point",
          "external_reference": external_reference,
          "transactions": {"payments": [{"amount": infos["amount"]}]},
          "config": {
            "point": {
              "terminal_id": self.mp_id_point_smart_complet,
              "print_on_terminal": infos['additional_info']['print_on_terminal'],
              "ticket_number": infos['additional_info']['external_reference']['pos_reference']
            },
            # "payment_method": {
              # "default_type": "credit_card",
              # "default_installments": 6,
              # "installments_cost": "seller"
            # }
          },
          # "description": "Point Mini",
          # "integration_data": {
          #   "platform_id": "1234567890",
          #   "integrator_id": "1234567890",
          #   "sponsor": {"id": "446566691"}
          # },
          # "taxes": [{"payer_condition": "payment_taxable_iva"}]
        }
        resp = mercado_pago.call_mercado_pago("post", f"/v1/orders", info_pos_order)
        _logger.debug("mp_payment_intent_create(), Order response from Mercado Pago: %s", resp)
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
        resp = mercado_pago.call_mercado_pago("get", f"/v1/orders/{payment_intent_id}", {})
        _logger.debug("mp_payment_intent_get(), Order response from Mercado Pago: %s", resp)
        return resp

    def mp_payment_intent_cancel(self, infos):
        """
        Called from frontend to cancel an Order in Mercado Pago
        """
        if not self.mp_smart_payment:
            return super(PosPaymentMethod, self).mp_payment_intent_get(infos['payment_intent_id'])

        self._check_special_access()

        mercado_pago = MercadoPagoPosRequest(self.sudo().mp_bearer_token, infos['order_uuid'])
        # Call Mercado Pago for order cancellation
        resp = mercado_pago.call_mercado_pago("post", f"/v1/orders/{infos['payment_intent_id']}/cancel", {})
        _logger.debug("mp_payment_intent_cancel(), Order response from Mercado Pago: %s", resp)
        return resp

    def _find_terminal(self, token, point_smart):
        if not self.mp_smart_payment:
            return super(PosPaymentMethod, self)._find_terminal(token, point_smart)

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
