/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";

patch(TicketScreen.prototype, {
    async addAdditionalRefundInfo(order, destinationOrder) {
        super.addAdditionalRefundInfo(...arguments);
        // If the payment method is a Mercado Pago payment terminal get data from order to refund the payment
        if (order.mp_order_id) {
            destinationOrder.refund_mp_order_id = order.mp_order_id;
            destinationOrder.refund_mp_transaction_id = order.mp_transaction_id;
            destinationOrder.refund_mp_order_amount_total = order.mp_order_amount_total;
        }
    },
});
