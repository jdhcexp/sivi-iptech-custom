from odoo import api, fields, models

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    initial_amount = fields.Float(string="Valor inicial")


    # @api.depends('quantity', 'discount', 'price_unit', 'tax_ids', 'currency_id',"prorate_ammount")
    # def _compute_totals(self):
    #     for line in self:
    #         if line.display_type != 'product':
    #             line.price_total = line.price_subtotal = False
    #         # Compute 'price_subtotal'.
    #         if line.prorate_ammount > 0:
    #             line_discount_price_unit = line.prorate_ammount * (1 - (line.discount / 100.0))
    #         else:
    #             line_discount_price_unit = line.price_unit * (1 - (line.discount / 100.0))
    #
    #         subtotal = line.quantity * line_discount_price_unit
    #
    #         # Compute 'price_total'.
    #         if line.tax_ids:
    #             taxes_res = line.tax_ids.compute_all(
    #                 line_discount_price_unit,
    #                 quantity=line.quantity,
    #                 currency=line.currency_id,
    #                 product=line.product_id,
    #                 partner=line.partner_id,
    #                 is_refund=line.is_refund,
    #             )
    #             line.price_subtotal = taxes_res['total_excluded']
    #             line.price_total = taxes_res['total_included']
    #         else:
    #             line.price_total = line.price_subtotal = subtotal