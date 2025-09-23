from datetime import datetime
from odoo import fields, models, _


class PosOrder(models.Model):
    _inherit = 'pos.order'

    mp_order_id = fields.Char('Mercado Pago Order ID', readonly=True, copy=False)
    mp_transaction_id = fields.Char('Mercado Pago transaction ID', readonly=True, copy=False)
    mp_order_amount_total = fields.Monetary('Total Amount Paid with Mercado Pago', readonly=True, copy=False)
    refund_mp_order_id = fields.Char('Refund Mercado Pago Order ID', readonly=True, copy=False)
    refund_mp_transaction_id = fields.Char('Refund Mercado Pago transaction ID', readonly=True, copy=False)
    refund_mp_order_amount_total = fields.Monetary('Total Amount Refunded with Mercado Pago', readonly=True, copy=False)
