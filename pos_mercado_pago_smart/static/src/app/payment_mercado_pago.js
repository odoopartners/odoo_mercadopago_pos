import { PaymentMercadoPago } from "@pos_mercado_pago/app/payment_mercado_pago";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(PaymentMercadoPago.prototype, {
    setup() {
        super.setup(...arguments);
        this.mp_identity_key = null;
    },
    async create_payment_intent() {
        // Override to add new parameters
        const order = this.pos.get_order();
        const line = order.get_selected_paymentline();

        // Build information for creating a payment intend on Mercado Pago.
        // Data in "external_reference" are send back with the webhook notification
        this.mp_identity_key = `${this.pos.config.current_session_id.id}_${line.payment_method_id.id}_${order.uuid}_${Date.now()}`
        const infos = {
            amount: parseInt(line.amount * 100, 10),
            additional_info: {
                external_reference: `${this.pos.config.current_session_id.id}_${line.payment_method_id.id}_${order.uuid}`,
                print_on_terminal: true,
                pos_reference: order.pos_reference,
                idempotency_key: this.mp_identity_key,
            },
        };
        // mp_payment_intent_create will call the Mercado Pago api
        return await this.env.services.orm.silent.call(
            "pos.payment.method",
            "mp_payment_intent_create",
            [[line.payment_method_id.id], infos]
        );
    },
    async cancel_payment_intent() {
        // Override to add new parameters
        const line = this.pos.get_order().get_selected_paymentline();
        const order = this.pos.get_order();

        const additional_info = {
            idempotency_key: this.mp_identity_key,
            payment_intent_id: this.payment_intent.id
        }

        // mp_payment_intent_cancel will call the Mercado Pago api
        return await this.env.services.orm.silent.call(
            "pos.payment.method",
            "mp_payment_intent_cancel",
            [[line.payment_method_id.id], additional_info]
        );
    },
    async handleMercadoPagoWebhook() {
        // Extend the original method to handle manual payment status - action_required
        const line = this.pos.get_order().get_selected_paymentline();
        const showMessageAndManualButtonActive = (messageKey, status, resolverValue) => {
            if (!resolverValue) {
                this._showMsg(messageKey, status);
            }
            line.set_payment_status();
            this.webhook_resolver?.(resolverValue);
            return resolverValue;
        };

        const handleManualPayment = async (paymentIntent) => {
            if (paymentIntent.state === "ACTION_REQUIRED") {
                return showMessageAndManualButtonActive(_t("There was a problem with the payment, please validate manually if it was processed"), "info", true);
            }
        };

        if ("id" in this.payment_intent) {
            let last_status_payment_intent = await this.get_last_status_payment_intent();
            if (this.payment_intent.id == last_status_payment_intent.id) {
                if (["ACTION_REQUIRED"].includes(last_status_payment_intent.state)) {
                    return await handleManualPayment(last_status_payment_intent);
                }
            }
        }
        await super.handleMercadoPagoWebhook(...arguments);
    }
});
