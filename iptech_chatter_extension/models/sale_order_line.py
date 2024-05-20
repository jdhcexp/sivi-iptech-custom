
from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = ["sale.order.line", "mail.thread"]


    @api.onchange("discount")
    def _update_discount(self):
        sale_order = self.env['sale.order'].search([('id', 'in', self.order_id.ids)])
        if self.product_id.name:
            message ="Se ha aplicado un descuento del "+str(self.discount) +"% al producto: "+self.product_id.name
            sale_order.message_post(body=message)

