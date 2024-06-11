from odoo import models, fields, api

class AccountReport(models.Model):
    _name='account.sql.report.sales'
    _description = 'account sql report sales'
    _auto = False
    #a00 = fields.Many2one('account.move',string="Id Factura")
    #a0 = fields.Char(string="Factura")
    a1 = fields.Char(string='Centro de operación del documento')
    a2 = fields.Char(string='Tipo de documento')
    id = fields.Char(string='Numero de documento', readonly=False)
    a4 = fields.Char(string="Fecha del documento")
    a5 = fields.Char(string="Tercero cliente")
    a6 = fields.Char(string="Estado del documento")
    a7 = fields.Char(string="Sucursal del cliente")
    a8 = fields.Char(string="Tipo de cliente")
    a9 = fields.Char(string="Centro de operación de la factura")
    a10 = fields.Char(string="Tercero cliente a remisionar")
    a11 = fields.Char(string='Sucursal del cliente a remisionar"')
    a12 = fields.Char(string='Tercero vendedor')
    a13 = fields.Char(string='Condicion de pago')
    a14 = fields.Char(string='Observaciones del documento')
    


    def init(self):
        self._cr.execute("""
	    SELECT * FROM public.account_sql_report_sales
        """)

