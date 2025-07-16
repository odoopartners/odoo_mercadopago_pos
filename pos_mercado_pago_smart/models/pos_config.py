from datetime import datetime
from odoo import fields, models, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    def _action_to_open_ui(self):
        mp_payment_method_ids = self.sudo().payment_method_ids.filtered(lambda pm: pm.mp_smart_payment and pm.mp_token_lifetime)
        for mp_payment_method in mp_payment_method_ids:
            if mp_payment_method.mp_token_lifetime <= datetime.now().date():
                mp_payment_method.mp_refresh_bearer_token()
        return super(PosConfig, self)._action_to_open_ui()
