
from odoo import api, fields, models

class TabLine(models.Model):
    _name = "tab.line"
    _inherit = ["tab.line", "mail.thread"]

    @api.onchange('product_id')
    def _update_product(self):
        ids = []
        if self.order_id.ids:
            ids = self.order_id.ids
        elif self.order_provider_id.ids:
            ids = self.order_provider_id.ids

        if len(self.ids) > 0 and len(ids):
            project_task = self.env['project.task'].search([('id', 'in', ids)])
            if self.product_id.name:
                message = "El producto: " + self.product_id.name + " ha sido configurado a: "+self.name
                project_task.message_post(body=message)

