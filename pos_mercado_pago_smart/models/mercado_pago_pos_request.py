from odoo.addons.pos_mercado_pago.models.mercado_pago_pos_request import MercadoPagoPosRequest, MERCADO_PAGO_API_ENDPOINT, REQUEST_TIMEOUT
import logging
import requests

_logger = logging.getLogger(__name__)


class MercadoPagoPosRequestExtended(MercadoPagoPosRequest):
    def __init__(self, mp_bearer_token, idempotency_key=False):
        super().__init__(mp_bearer_token)
        self.idempotency_key = idempotency_key

    def call_mercado_pago(self, method, endpoint, payload):
        """ Make a request to Mercado Pago POS API.

        :param method: "GET", "POST", ...
        :param endpoint: The endpoint to be reached by the request.
        :param payload: The payload of the request.
        :return The JSON-formatted content of the response.

        Note: The platform id below is not secret, and is just used to
        quantify the amount of Odoo users on Mercado's backend.
        """
        endpoint = MERCADO_PAGO_API_ENDPOINT + endpoint
        header = {}
        if self.mercado_pago_bearer_token:
            header['Authorization'] = f"Bearer {self.mercado_pago_bearer_token}"
        if self.idempotency_key:
            header['X-Idempotency-Key'] = self.idempotency_key
        else:
            header['X-platform-id'] = "dev_cdf1cfac242111ef9fdebe8d845d0987"

        try:
            _logger.debug("Enviando petición a Mercado Pago: método=%s, endpoint=%s, headers=%s, payload=%s", method, endpoint, header, payload)
            if not payload:
                response = requests.request(method, endpoint, headers=header, timeout=REQUEST_TIMEOUT)
            else:
                response = requests.request(method, endpoint, headers=header, json=payload, timeout=REQUEST_TIMEOUT)
            json_response = response.json()
            return json_response
        except requests.exceptions.RequestException as error:
            _logger.warning("Cannot connect with Mercado Pago POS. Error: %s", error)
            return {'errorMessage': str(error)}
        except ValueError as error:
            _logger.warning("Cannot decode response json. Error: %s", error)
            return {'errorMessage': f"Cannot decode Mercado Pago POS response. Error: {error}"}
