# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import api, fields, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sh_product_subscribe = fields.Boolean(
        string="Is Subscription Type",
        help="click false to hide.",
        compute="_compute_sh_product_subscribe",
        inverse="_set_sh_product_subscribe",
        store=True,
        search="_search_sh_product_subscribe",
        groups="sh_subscription.group_user_sh_subscription",
    )
    sh_subscription_plan_id = fields.Many2one(
        comodel_name="sh.subscription.plan",
        string="Subscription Plan",
        compute="_compute_sh_subscription_plan_id",
        inverse="_set_sh_subscription_plan_id",
        store=True,
        search="_search_sh_subscription_plan_id",
        groups="sh_subscription.group_user_sh_subscription",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if (
                "sh_product_subscribe" in vals.keys()
                and "attribute_line_ids" in vals.keys()
                and vals["sh_product_subscribe"]
            ):
                temp = 0
                if (
                    vals["sh_product_subscribe"] == True
                    and len(vals["attribute_line_ids"]) > 1
                ):
                    temp = 1
                    raise UserError(
                        "you can't take more than one attribute in the subscription type product..."
                    )

                elif (
                    vals["sh_product_subscribe"] == True
                    and len(vals["attribute_line_ids"]) == 1
                ):
                    subscription_attribute = self.env.ref(
                        "sh_subscription.product_attribute_subscription"
                    )

                    for att in vals["attribute_line_ids"]:
                        if att[2]["attribute_id"] == subscription_attribute.id:
                            pass
                        else:
                            temp = 1
                            raise UserError(
                                "you must be select subscription attribute in the subscription type product..."
                            )
                    if temp == 0:
                        return super(ProductTemplate, self).create(vals)
            #     else:
            #         return super(ProductTemplate, self).create(vals)
            # else:
            #     return super(ProductTemplate, self).create(vals)
        return super(ProductTemplate, self).create(vals_list)

    def write(self, vals):
        if (
            "sh_product_subscribe" in vals.keys()
            and "attribute_line_ids" in vals.keys()
            and vals["sh_product_subscribe"]
        ):
            temp = 0
            if (
                vals["sh_product_subscribe"] == True
                and len(vals["attribute_line_ids"]) > 1
            ):
                temp = 1
                raise UserError(
                    "you can't take more than one attribute in the subscription type product..."
                )

            elif (
                vals["sh_product_subscribe"] == True
                and len(vals["attribute_line_ids"]) == 1
            ):
                subscription_attribute = self.env.ref(
                    "sh_subscription.product_attribute_subscription"
                )

                for att in vals["attribute_line_ids"]:
                    if att[2]["attribute_id"] == subscription_attribute.id:
                        pass
                    else:
                        temp = 1
                        raise UserError(
                            "you must be select subscription attribute in the subscription type product..."
                        )
                if temp == 0:
                    return super(ProductTemplate, self).write(vals)
            else:
                return super(ProductTemplate, self).write(vals)
        else:
            return super(ProductTemplate, self).write(vals)

    @api.depends("product_variant_ids.sh_product_subscribe")
    def _compute_sh_product_subscribe(self):
        self.sh_product_subscribe = False
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.sh_product_subscribe = (
                    template.product_variant_ids.sh_product_subscribe
                )

    def _search_sh_product_subscribe(self, operator, value):
        templates = self.with_context(active_test=False).search(
            [("product_variant_ids.sh_product_subscribe", operator, value)]
        )
        return [("id", "in", templates.ids)]

    def _set_sh_product_subscribe(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.sh_product_subscribe = self.sh_product_subscribe

    @api.depends("product_variant_ids.sh_subscription_plan_id")
    def _compute_sh_subscription_plan_id(self):
        self.sh_subscription_plan_id = False
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.sh_subscription_plan_id = (
                    template.product_variant_ids.sh_subscription_plan_id.id
                )

    def _search_sh_subscription_plan_id(self, operator, value):
        templates = self.with_context(active_test=False).search(
            [("product_variant_ids.sh_subscription_plan_id", operator, value)]
        )
        return [("id", "in", templates.ids)]

    def _set_sh_subscription_plan_id(self):

        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.sh_subscription_plan_id = (
                self.sh_subscription_plan_id.id
            )

    @api.onchange("sh_product_subscribe")
    def _onchange_sh_product_subscribe(self):
        if self.sh_product_subscribe == True:
            self.detailed_type = "service"

    @api.onchange("sh_subscription_plan_id")
    def _onchange_sh_subscription_plan_id_product(self):
        if self.sh_subscription_plan_id:

            if self.sh_subscription_plan_id.sh_override_product == True:
                self.list_price = self.sh_subscription_plan_id.sh_plan_price


class Product(models.Model):
    _inherit = "product.product"

    sh_product_subscribe = fields.Boolean(
        string="Is Subscription Type", help="click false to hide."
    )
    sh_subscription_plan_id = fields.Many2one(
        comodel_name="sh.subscription.plan", string="Subscription Plan"
    )

    @api.onchange("sh_product_subscribe")
    def _onchange_sh_product_subscribe(self):
        if self.sh_product_subscribe == True:
            self.detailed_type = "service"

    @api.onchange("sh_subscription_plan_id")
    def _onchange_sh_subscription_plan_id_product(self):
        if (
            self.sh_subscription_plan_id
            and self.sh_subscription_plan_id.sh_override_product
        ):
            subscription_attribute = self.env.ref(
                "sh_subscription.product_attribute_subscription"
            )
            if (
                subscription_attribute
                and self.product_template_variant_value_ids
                and self.product_template_variant_value_ids.filtered(
                    lambda x: x.attribute_id == subscription_attribute
                )
            ):
                subscription_product_template_variant_value_ids = (
                    self.product_template_variant_value_ids.filtered(
                        lambda x: x.attribute_id == subscription_attribute
                    )
                )

                subscription_product_template_variant_value_id = (
                    subscription_product_template_variant_value_ids[0]
                )
                subscription_product_template_variant_value_id._origin.price_extra = (
                    self.sh_subscription_plan_id.sh_plan_price
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            template_id = (
                self.env["product.template"].sudo().browse(vals.get("product_tmpl_id"))
            )
            if template_id:
                sh_product_subscribe = template_id.sh_product_subscribe
                sh_subscription_plan_id = template_id.sh_subscription_plan_id
                if (
                    vals.get("product_template_attribute_value_ids")
                    and len(vals.get("product_template_attribute_value_ids")[0][2]) == 0
                ):
                    vals.update(
                        {
                            "sh_product_subscribe": sh_product_subscribe,
                            "sh_subscription_plan_id": sh_subscription_plan_id.id,
                        }
                    )
        return super(Product, self).create(vals_list)
