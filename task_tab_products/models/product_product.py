from odoo import fields, models, api


class ProductProduct(models.Model):
    # _name="task.product"
    _inherit = "product.product"

    # product_group_id=fields.Many2one("task.product.group","products_id")
    def _get_combination_info_variant(self, add_qty=1, pricelist=False, parent_combination=False):
        """Return the variant info based on its combination.
        See `_get_combination_info` for more information.
        """
        self.ensure_one()
        return self.product_tmpl_id._get_combination_info(self.product_template_attribute_value_ids, self.id, add_qty,
                                                          pricelist, parent_combination)


class ProductAttributeCustomValue(models.Model):
    _name = "project.task.product.attribute.custom.value"
    _description = 'project task Product Attribute Custom Value'
    _order = 'custom_product_template_attribute_value_id, id'

    name = fields.Char("Name", compute='_compute_name')
    custom_product_template_attribute_value_id = fields.Many2one('product.template.attribute.value',
                                                                 string="Attribute Value", required=True,
                                                                 ondelete='restrict')
    custom_value = fields.Char("Custom Value")
    task_product_id = fields.Many2one('tab.line', string="sdkj skfjhjkdbf jksd jbnfjks dbjkf s",
                                      ondelete='cascade')

    @api.depends('custom_product_template_attribute_value_id.name', 'custom_value')
    def _compute_name(self):
        for record in self:
            name = (record.custom_value or '').strip()
            if record.custom_product_template_attribute_value_id.display_name:
                name = "%s: %s" % (record.custom_product_template_attribute_value_id.display_name, name)
            record.name = name
