/** @odoo-module */

export class PaymentMercadoPagoExtended extends PaymentMercadoPago {
    async create_payment_intent() {
        // Override to add new parameters
        const order = this.pos.get_order();
        const line = order.get_selected_paymentline();

        // Build informations for creating a payment intend on Mercado Pago.
        // Data in "external_reference" are send back with the webhook notification
        const infos = {
            amount: parseInt(line.amount * 100, 10),
            additional_info: {
                external_reference: `${this.pos.config.current_session_id.id}_${line.payment_method_id.id}_${order.uuid}`,
                print_on_terminal: true,
                pos_reference: order.pos_reference,
                order_uuid: order.order.uuid
            },
        };
        // mp_payment_intent_create will call the Mercado Pago api
        return await this.env.services.orm.silent.call(
            "pos.payment.method",
            "mp_payment_intent_create",
            [[line.payment_method_id.id], infos]
        );
    }
    async cancel_payment_intent() {
        // Override to add new parameters
        const line = this.pos.get_order().get_selected_paymentline();
        const order = this.pos.get_order();

        const additional_info = {
            order_uuid: order.order.uuid,
            payment_intent_id: this.payment_intent.id
        }

        // mp_payment_intent_cancel will call the Mercado Pago api
        return await this.env.services.orm.silent.call(
            "pos.payment.method",
            "mp_payment_intent_cancel",
            [[line.payment_method_id.id], additional_info]
        );
    }
}
