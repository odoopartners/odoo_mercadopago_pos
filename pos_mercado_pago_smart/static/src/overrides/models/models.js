import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {
    setup() {
        super.setup(...arguments);
        this.mp_order_id = this.mp_order_id || false;
        this.refund_mp_order_id = this.refund_mp_order_id || false;
    },
});
