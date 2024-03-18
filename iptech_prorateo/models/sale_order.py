
from odoo import api, fields, models

class SaleOrder(models.Model):

    _inherit = ["sale.order"]

    has_free_tax = fields.Boolean(string="estrato 1, 2 o 3", default=False)

    @api.onchange("has_free_tax")
    def _change_taxes(self):
        if self.has_free_tax:
            taxes_by_product_company = self.env['account.tax']
            for order_ln in self.order_line:
                order_ln.tax_id= [(5, 0,0)]
        else:
            for order_ln in self.order_line:
                order_ln.tax_id=order_ln.product_id.taxes_id

