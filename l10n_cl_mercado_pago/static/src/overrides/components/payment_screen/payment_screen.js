import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";

patch(PaymentScreen.prototype, {
    async validateOrder(isForceValidate) {
        // Extended to avoid manually ask for chilean invoice number - l10n_cl_edi_pos
        let isChilean = false;
        if (this.pos.isChileanCompany()){
            this.company.country_id.code = "CL-2"
            isChilean = true
        }
        await super.validateOrder(...arguments);
        if (isChilean){
            this.company.country_id.code = "CL"
        }
    },
});
