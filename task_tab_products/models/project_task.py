from odoo import fields, models, api, _


class Task(models.Model):
    _inherit = 'project.task'

    order_line = fields.One2many(
        comodel_name='tab.line',
        inverse_name='order_line_id',
        string="Order Lines",
        copy=True, auto_join=True)

    # gear = fields.One2many(
    #     comodel_name='tab.line',
    #     inverse_name='order_id',
    #     string="Order Lines",
    #     computed = '_computed_gear'
    # )
    gear = fields.One2many(comodel_name='tab.line',
                           inverse_name='order_id',
                           copy=True, auto_join=True
                           )

    provider = fields.One2many(comodel_name='tab.line',
                               inverse_name='order_provider_id',
                               copy=True, auto_join=True
                               )
    #
    personal = fields.One2many(comodel_name='tab.line',
                               inverse_name='order_personal_id',
                               copy=True, auto_join=True
                               )

    software = fields.One2many(comodel_name='tab.line',
                               inverse_name='order_software_id',
                               copy=True, auto_join=True
                               )

    documentation = fields.One2many(comodel_name='tab.line',
                                    inverse_name='order_docs_id',
                                    copy=True, auto_join=True
                                    )
    #
    site = fields.One2many(comodel_name='tab.line',
                           inverse_name='order_site_id',
                           copy=True, auto_join=True
                           )

    simcard = fields.One2many(comodel_name='tab.line',
                           inverse_name='order_simcard_id',
                           copy=True, auto_join=True
                           )
    scheduled_date = fields.Date(string="Fecha Programada")

    @api.model
    def default_get(self, fields):
        res = super(Task, self).default_get(fields)
        lgear = len(self.gear)
        lprovider = len(self.provider)
        lpersonal = len(self.personal)
        lsoftware = len(self.software)
        ldocs = len(self.documentation)
        lsite = len(self.site)
        lsimcard = len(self.simcard)
        product_dict = [
            {'type': 'equipos', 'id': 2727},
            {'type': 'equipos', 'id': 2737},
            {'type': 'provider', 'id': 3715},
            {'type': 'provider', 'id': 3728},
            {'type': 'provider', 'id': 3723},
            {'type': 'personal', 'id': 3760},
            {'type': 'personal', 'id': 3765},
            {'type': 'software', 'id': 3770},
            {'type': 'software', 'id': 3775},
            {'type': 'documentation', 'id': 3733},
            {'type': 'documentation', 'id': 3747},
            {'type': 'documentation', 'id': 3775},
            {'type': 'documentation', 'id': 3779},
            {'type': 'documentation', 'id': 3937},
            {'type': 'documentation', 'id': 3781},
            {'type': 'documentation', 'id': 3781},
            {'type': 'site', 'id': 3950},
            {'type': 'site', 'id': 3962},
            {'type': 'site', 'id': 2727},
            {'type': 'site', 'id': 3983},
            {'type': 'site', 'id': 3998},
        ]
        for prod in product_dict:
            if self.name == 'Asignacion de Equipos':
                if prod['type'] == 'equipos' and lgear == 0:
                    product = self.env['product.product'].search([('id', '=', prod['id'])])
                    if product:
                        self.gear = [(0, 0, {'product_id': product.id, 'type': prod['type']})]
            if self.name == 'Configuración y Pruebas de Servicio':
                if prod['type'] == 'provider' and lprovider == 0:
                    product = self.env['product.product'].search([('id', '=', prod['id'])])
                    if product:
                        self.provider = [(0, 0, {'product_id': product.id, 'type': prod['type']})]
                if prod['type'] == 'personal' and lpersonal == 0:
                    product = self.env['product.product'].search([('id', '=', prod['id'])])
                    if product:
                        self.personal = [(0, 0, {'product_id': product.id, 'type': prod['type']})]
                if prod['type'] == 'software' and lsoftware == 0:
                    product = self.env['product.product'].search([('id', '=', prod['id'])])
                    if product:
                        self.software = [(0, 0, {'product_id': product.id, 'type': prod['type']})]
                if prod['type'] == 'documentation' and ldocs == 0:
                    product = self.env['product.product'].search([('id', '=', prod['id'])])
                    if product:
                        self.documentation = [(0, 0, {'product_id': product.id, 'type': prod['type']})]
            if self.name == 'Visita en Sitio':
                if prod['type'] == 'site' and lsite == 0:
                    product = self.env['product.product'].search([('id', '=', prod['id'])])
                    if product:
                        self.site = [(0, 0, {'product_id': product.id, 'type': prod['type']})]
            #if self.name == 'Entrega de SIMCARD':
            #    if prod['type'] == 'equipos' and lsimcard == 0:
            #        product = self.env['product.product'].search([('id', '=', prod['id'])])
            #        if product:
            #            self.simcard = [(0, 0, {'product_id': product.id, 'type': prod['type']})]
        return res
    #
    #
    # @api.depends("order_line")
    # def _computed_gear(self):
    #     for item in self:
    #         item.gear = item.order_line.search([('type', '=', 'equipos')])

    # def _computed_provider(self):
    #     self.provider = self.order_line.search([('type', '=', 'provider')])
    #
    # def _computed_personal(self):
    #     self.personal = self.order_line.search([('type', '=', 'personal')])
    #
    # def _computed_software(self):
    #     self.software = self.order_line.search([('type', '=', 'software')])
    #
    # def _computed_documentation(self):
    #     self.documentation = self.order_line.search([('type', '=', 'documentation')])
    #
    # def _computed_site(self):
    #     self.site = self.order_line.search([('type', '=', 'site')])

    def _inverse_computed_gear(self):
        pass


    # @api.depends("order_line")
    # def _computed_gear(self):
    #     for record in self:
    #         for line in record.order_line:
    #             if line.type == 'producto':
    #                 record.gear.append(self, line)
    #

    # gear = fields.One2many(
    #     comodel_name='task.tab',
    #     inverse_name='task_id',
    #     string='Gear tab',
    #     copy=True, auto_join=True
    # )

    # gear = fields.One2many(
    #     comodel_name='tab.line',
    #     inverse_name='tab_id',
    #     string='tab lines',
    #     copy=True, auto_join=True
    # )

    # providers = fields.One2many(
    #     comodel_name='task.tab',
    #     inverse_name='task_id',
    #     string='Gear tab',
    #     copy=True, auto_join=True
    # )
