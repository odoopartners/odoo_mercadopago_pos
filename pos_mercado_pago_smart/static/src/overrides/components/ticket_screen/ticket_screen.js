/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";

patch(TicketScreen.prototype, {
    async addAdditionalRefundInfo(order, destinationOrder) {
        super.addAdditionalRefundInfo(...arguments);
        destinationOrder.refund_mp_order_id = order.mp_order_id;
        destinationOrder.refund_mp_order_amount_total = order.amount_total;
    },
});
