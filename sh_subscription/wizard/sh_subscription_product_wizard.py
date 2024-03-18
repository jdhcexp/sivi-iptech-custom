# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models


class SubscriptionProduct(models.TransientModel):
    _name = 'sh.subscription.product.wizard'
    _description = 'Subscription Product Wizard'

    sh_product_id = fields.Many2one(
        comodel_name="product.product", string="Product", required=True, domain="[('sale_ok','=', True),('sh_product_subscribe','=', True)]")

    def sh_add_product(self):
        so_id = self.env['sale.order'].sudo().browse(
            self.env.context.get('active_id'))
        if so_id:
            line_vals = {
                'product_id': self.sh_product_id.id,
                'name': self.sh_product_id.name_get()[0][1],
                'price_unit': self.sh_product_id.lst_price,
                'product_uom_qty': 1.0,
            }
            print(line_vals)
            lines = []
            lines.append((0, 0, line_vals))
            so_id.order_line = lines
