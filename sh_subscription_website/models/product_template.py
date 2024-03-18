# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.onchange("sh_product_subscribe")
    def _onchange_sh_product_subscribe(self):

        res = super(ProductProduct, self)._onchange_sh_product_subscribe()

        if self.sh_product_subscribe:
            self.website_ribbon_id = self.env.ref(
                "sh_subscription_website.sh_subscription_product_ribbon"
            ).id
        else:
            self.website_ribbon_id = False
        return res


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.onchange("sh_product_subscribe")
    def _onchange_sh_product_subscribe(self):

        res = super(ProductTemplate, self)._onchange_sh_product_subscribe()

        if self.sh_product_subscribe:
            self.website_ribbon_id = self.env.ref(
                "sh_subscription_website.sh_subscription_product_ribbon"
            ).id
        else:
            self.website_ribbon_id = False
        return res
