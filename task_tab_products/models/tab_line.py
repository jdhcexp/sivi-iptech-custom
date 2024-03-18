from odoo import fields, models, api
from odoo.tools import float_is_zero, float_compare, float_round


class TabLine(models.Model):
    _name = "tab.line"
    _description = "Tab product"

    type = fields.Char(default="equipos")

    order_line_id = fields.Many2one(
        comodel_name='project.task',
        string="Order Reference",
        ondelete='cascade', index=True, copy=False)
    order_id = fields.Many2one(
        comodel_name='project.task',
        string="Order Reference",
        ondelete='cascade', index=True, copy=False)
    order_provider_id = fields.Many2one(
        comodel_name='project.task',
        string="Order Reference",
        ondelete='cascade', index=True, copy=False)
    order_personal_id = fields.Many2one(
        comodel_name='project.task',
        string="Order Reference",
        ondelete='cascade', index=True, copy=False)
    order_software_id = fields.Many2one(
        comodel_name='project.task',
        string="Order Reference",
        ondelete='cascade', index=True, copy=False)
    order_docs_id = fields.Many2one(
        comodel_name='project.task',
        string="Order Reference",
        ondelete='cascade', index=True, copy=False)
    order_site_id = fields.Many2one(
        comodel_name='project.task',
        string="Order Reference",
        ondelete='cascade', index=True, copy=False)

    # tab_id = fields.Many2one(
    #     comodel_name='project.task',
    #     string="Tab Reference",
    #     required=True, ondelete='cascade', index=True, copy=False)

    product_id = fields.Many2one(
        comodel_name='product.product',
        string="Product",
        change_default=True)
    product_template_id = fields.Many2one(
        string="Product Template",
        comodel_name='product.template',
        compute='_compute_product_template_id',
        readonly=False,
        search='_search_product_template_id',
        # previously related='product_id.product_tmpl_id'
        # not anymore since the field must be considered editable for product configurator logic
        # without modifying the related product_id when updated.
        domain=[('sale_ok', '=', True)])

    is_configurable_product = fields.Boolean(
        string="Is the product configurable?",
        related='product_template_id.has_configurable_attributes',
        depends=['product_id'])
    product_template_attribute_value_ids = fields.Many2many(
        related='product_id.product_template_attribute_value_ids',
        depends=['product_id'])

    #task_id = fields.Many2one(comodel_name='project.task')

    name = fields.Text(
        string="Description",
        compute='_compute_name',
        store=True, readonly=False, precompute=True)

    product_custom_attribute_value_ids = fields.One2many(
        comodel_name='project.task.product.attribute.custom.value', inverse_name='task_product_id',
        string="Custom Values",
        compute='_compute_custom_attribute_values',
        store=True, readonly=False, precompute=True, copy=True)

    product_no_variant_attribute_value_ids = fields.Many2many(
        comodel_name='product.template.attribute.value',
        string="Extra Values",
        compute='_compute_no_variant_attribute_values',
        store=True, readonly=False, precompute=True, ondelete='restrict')

    product_uom_qty = fields.Float(
        string="Quantity",
        compute='_compute_product_uom_qty',
        digits='Product Unit of Measure', default=1.0,
        store=True, readonly=False, required=True, precompute=True)

    display_type = fields.Selection(
        selection=[
            ('line_section', "Section"),
            ('line_note', "Note"),
        ],
        default=False)

    product_packaging_id = fields.Many2one(
        comodel_name='product.packaging',
        string="Packaging",
        compute='_compute_product_packaging_id',
        store=True, readonly=False, precompute=True,
        domain="[('sales', '=', True), ('product_id','=',product_id)]",
        check_company=True)

    product_packaging_qty = fields.Float(
        string="Packaging Quantity",
        compute='_compute_product_packaging_qty',
        store=True, readonly=False, precompute=True)

    product_uom = fields.Many2one(
        comodel_name='uom.uom',
        string="Unit of Measure",
        compute='_compute_product_uom',
        store=True, readonly=False, precompute=True, ondelete='restrict',
        domain="[('category_id', '=', product_uom_category_id)]")

    @api.depends('product_id')
    def _compute_name(self):
        for line in self:
            if not line.product_id:
                continue
            # if not line.order_partner_id.is_public:
            #     line = line.with_context(lang=line.order_partner_id.lang)
            name = line._get_sale_order_line_multiline_description_sale()
            # if line.is_downpayment and not line.display_type:
            #     context = {'lang': line.order_partner_id.lang}
            #     dp_state = line._get_downpayment_state()
            #     if dp_state == 'draft':
            #         name = _("%(line_description)s (Draft)", line_description=name)
            #     elif dp_state == 'cancel':
            #         name = _("%(line_description)s (Canceled)", line_description=name)
            #     del context
            line.name = name

    @api.depends('display_type', 'product_id', 'product_packaging_qty')
    def _compute_product_uom_qty(self):
        for line in self:
            if line.display_type:
                line.product_uom_qty = 0.0
                continue

            if not line.product_packaging_id:
                continue
            packaging_uom = line.product_packaging_id.product_uom_id
            qty_per_packaging = line.product_packaging_id.qty
            product_uom_qty = packaging_uom._compute_quantity(
                line.product_packaging_qty * qty_per_packaging, line.product_uom)
            if float_compare(product_uom_qty, line.product_uom_qty, precision_rounding=line.product_uom.rounding) != 0:
                line.product_uom_qty = product_uom_qty

    @api.depends('product_packaging_id', 'product_uom', 'product_uom_qty')
    def _compute_product_packaging_qty(self):
        for line in self:
            if not line.product_packaging_id:
                line.product_packaging_qty = False
            else:
                packaging_uom = line.product_packaging_id.product_uom_id
                packaging_uom_qty = line.product_uom._compute_quantity(line.product_uom_qty, packaging_uom)
                line.product_packaging_qty = float_round(
                    packaging_uom_qty / line.product_packaging_id.qty,
                    precision_rounding=packaging_uom.rounding)

    @api.depends('product_id')
    def _compute_product_uom(self):
        for line in self:
            if not line.product_uom or (line.product_id.uom_id.id != line.product_uom.id):
                line.product_uom = line.product_id.uom_id

    @api.depends('product_id', 'product_uom_qty', 'product_uom')
    def _compute_product_packaging_id(self):
        print("todo")
        # for line in self:
        #     # remove packaging if not match the product
        #     if line.product_packaging_id.product_id != line.product_id:
        #         line.product_packaging_id = False
        #     # Find biggest suitable packaging
        #     if line.product_id and line.product_uom_qty and line.product_uom:
        #         line.product_packaging_id = line.product_id.packaging_ids.filtered(
        #             'sales')._find_suitable_product_packaging(line.product_uom_qty, line.product_uom) or line.product_packaging_id

    def _get_sale_order_line_multiline_description_sale(self):
        """ Compute a default multiline description for this sales order line.

        In most cases the product description is enough but sometimes we need to append information that only
        exists on the sale order line itself.
        e.g:
        - custom attributes and attributes that don't create variants, both introduced by the "product configurator"
        - in event_sale we need to know specifically the sales order line as well as the product to generate the name:
          the product is not sufficient because we also need to know the event_id and the event_ticket_id (both which belong to the sale order line).
        """
        self.ensure_one()
        return self.product_id.product_template_attribute_value_ids._get_combination_name() + self._get_sale_order_line_multiline_description_variants()

    def _get_sale_order_line_multiline_description_variants(self):
        """When using no_variant attributes or is_custom values, the product
        itself is not sufficient to create the description: we need to add
        information about those special attributes and values.

        :return: the description related to special variant attributes/values
        :rtype: string
        """
        if not self.product_custom_attribute_value_ids and not self.product_no_variant_attribute_value_ids:
            return ""

        name = "\n"

        custom_ptavs = self.product_custom_attribute_value_ids.custom_product_template_attribute_value_id
        no_variant_ptavs = self.product_no_variant_attribute_value_ids._origin

        # display the no_variant attributes, except those that are also
        # displayed by a custom (avoid duplicate description)
        for ptav in (no_variant_ptavs - custom_ptavs):
            name += "\n" + ptav.display_name

        # Sort the values according to _order settings, because it doesn't work for virtual records in onchange
        sorted_custom_ptav = self.product_custom_attribute_value_ids.custom_product_template_attribute_value_id.sorted()
        for patv in sorted_custom_ptav:
            pacv = self.product_custom_attribute_value_ids.filtered(
                lambda pcav: pcav.custom_product_template_attribute_value_id == patv)
            name += "\n" + pacv.custom_product_template_attribute_value_id[0].attribute_id[0].display_name +': '+ pacv.custom_value

        return name

    @api.depends('product_id')
    def _compute_custom_attribute_values(self):
        for line in self:
            if not line.product_id:
                line.product_custom_attribute_value_ids = False
                continue
            if not line.product_custom_attribute_value_ids:
                continue
            valid_values = line.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
            # remove the is_custom values that don't belong to this template
            for pacv in line.product_custom_attribute_value_ids:
                if pacv.custom_product_template_attribute_value_id not in valid_values:
                    line.product_custom_attribute_value_ids -= pacv

    @api.depends('product_id')
    def _compute_no_variant_attribute_values(self):
        for line in self:
            if not line.product_id:
                line.product_no_variant_attribute_value_ids = False
                continue
            if not line.product_no_variant_attribute_value_ids:
                continue
            valid_values = line.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
            # remove the no_variant attributes that don't belong to this template

            for ptav in line.product_no_variant_attribute_value_ids:
                if ptav._origin not in valid_values:
                    line.product_no_variant_attribute_value_ids -= ptav

    @api.depends('product_id')
    def _compute_product_template_id(self):
        for line in self:
            line.product_template_id = line.product_id.product_tmpl_id

    def _search_product_template_id(self, operator, value):
        print("00000000000000000000")
        print(value)
        print("op")
        print(operator)
        return [('product_id.product_tmpl_id', operator, value)]
