import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { _t } from "@web/core/l10n/translation";

patch(PaymentScreen.prototype, {
    async getPaymentStatus(line) {
        const payment_terminal = line.payment_method_id.payment_terminal;
        await payment_terminal.handleMercadoPagoWebhook();
        if (line.get_payment_status() !== "done" && line.get_payment_status() !== "cancel") {
            payment_terminal._showMsg(_t("Payment status could not be confirmed, try to validate again"), 'info');
        }
    }
});
