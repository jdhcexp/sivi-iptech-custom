import odoo.exceptions
from odoo import fields, models, api
from datetime import datetime, timedelta

class AccountMove(models.Model):
    _inherit = "account.move"

    isProrated = fields.Boolean(string="prorateo", default=False)
    prorate = fields.Integer(string="Dias Prorateo", default=0,  track_visibility='onchange', readonly=True)


    # @api.depends("isProrated")
    # def _computed_prorate(self):
    #     fecha_actual = datetime.now()
    #     primer_dia_siguiente_mes = datetime(fecha_actual.year, fecha_actual.month + 1, 1)
    #     diferencia_dias = (primer_dia_siguiente_mes - fecha_actual).days
    #     if self.isProrated == True:
    #         self.prorate = diferencia_dias
    #     else:
    #         self.prorate=0
    #     print(self.prorate)


    @api.onchange("isProrated")
    def _get_prorate_date(self):
        if self.isProrated:
            quotation = self.invoice_origin
            project = self.env['project.project'].search([('name','=',quotation+' - Implementación')])
            if project.delivery_date:
                fecha_actual = datetime.now()
                year = fecha_actual.year if fecha_actual.month < 12 else fecha_actual.year + 1
                month = fecha_actual.month + 1 if fecha_actual.month < 12 else 1
                primer_dia_siguiente_mes = datetime(year, month, 1)
                fecha_inicio = datetime.combine(project.delivery_date, datetime.min.time())
                if fecha_inicio >= primer_dia_siguiente_mes:
                    self.isProrated = False
                    return {

                        'warning': {

                            'title': '',

                            'message': 'La fecha de entrega es posterior al primer dia del siguiente mes'}

                    }
                diferencia_dias = (primer_dia_siguiente_mes - fecha_inicio).days
                self.prorate = diferencia_dias
            else:
                self.isProrated = False
                return {

                    'warning': {

                        'title': '',

                        'message': 'El proyecto asociado no tiene fecha de entrega'}

                }
        else:
            self.prorate = 0

    @api.onchange("prorate")
    def _update_prices(self):
        # for line in self.invoice_line_ids:
        #     if line.product_id.sh_product_subscribe:
        #         if self.isProrated == True:
        #             line.prorate_ammount = (line.price_subtotal / 30) * self.prorate
        #         else:
        #             line.prorate_ammount = 0
        for lineid in self.invoice_line_ids:
            if lineid.product_id.sh_product_subscribe:
                if self.prorate > 0:
                    if lineid.initial_amount == 0:
                        lineid.initial_amount = lineid.price_unit
                    else:
                        lineid.price_unit = lineid.initial_amount
                    lineid.price_unit = (lineid.price_unit / 30) * self.prorate
                    self.isProrated=True
                else:
                    lineid.price_unit = lineid.initial_amount
                    self.isProrated=False



        # for line in self.invoice_line_ids:
        #     if line.product_id.sh_product_subscribe:
        #         line.price_unit = (line.price_unit / 30) * diferencia_dias

        # for line in self.invoice_line_ids:
        #     if line.product_id.sh_product_subscribe:
        #         if self.prorate > 0:
        #             line.price_unit = (line.price_unit / self.prorate) * 30
        #         else:
        #             line.price_unit = (line.price_unit / diferencia_dias) * 30



        #     for line in self.invoice_line_ids:
        #         if line.product_id.sh_product_subscribe:
        #             if self.isProrated:
        #                 line.price_unit = (line.price_unit / 30) * self.prorate
        # else:
        #     if self.prorate > 0:
        #         for line in self.invoice_line_ids:
        #             if line.product_id.sh_product_subscribe:
        #                 line.price_unit = (line.price_unit / self.prorate) * 30
        #         self.prorate=0






