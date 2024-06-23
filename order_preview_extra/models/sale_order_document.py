from odoo import models, fields, api


class SaleOrderDocument(models.Model):
    _name = "sale.order.document"
    _description = "document for saleorder"

    sale_order_id = fields.Many2one('sale.order', required=True)
    type = fields.Char(string="Type")
    url = fields.Char(string="url")