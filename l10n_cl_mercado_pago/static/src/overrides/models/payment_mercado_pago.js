import { PaymentMercadoPago } from "@pos_mercado_pago/app/payment_mercado_pago";
import { patch } from "@web/core/utils/patch";

patch(PaymentMercadoPago.prototype, {
    async get_last_status_payment_intent() {
        // Extend to set voucher number when the payment is approved
        const mp_last_status_response = await super.get_last_status_payment_intent(...arguments);
        let order = this.pos.get_order();
        if (mp_last_status_response?.transactions?.payments[0]?.reference_id) {
            order.voucher_number = mp_last_status_response?.transactions.payments[0].reference_id;
        }
        return mp_last_status_response
    }
});
