from odoo import models, fields, api

class AccountReportMovements(models.Model):
    _name='account.sql.report.movements'
    _description = 'account sql report movements'
    _auto = False

    a0 = fields.Many2one('account.move',string="Id Factura")
    a1 = fields.Char(string='Centro de operación del documento')
    a2 = fields.Char(string='Tipo de documento')
    a3 = fields.Integer(string='Consecutivo numero')    
    a5 = fields.Integer(string="Numero de registro")
    a6 = fields.Char(string="Centro de operación movimiento")
    a7 = fields.Char(string="Centro de costo movimiento")
    a8 = fields.Char(string="Lista de precio")
    a9 = fields.Integer(string="Cantidad base")
    a10 = fields.Float(string="Valor bruto")
    a11 = fields.Char(string='Descripcion')
    a12 = fields.Char(string='Referencia item')
    a13 = fields.Char(string='Unidad de negocio movimiento')   


    def init(self):
        self._cr.execute("""      
        SELECT * FROM account_sql_report_movements;
        """)

