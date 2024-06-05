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
	   
           CREATE OR REPLACE VIEW account_sql_report_movements AS (
            SELECT row_number() OVER() as id,
								am.id as a0,
                                '001' as a1,
                                'FEE' as a2,
                                --am.id as a3,
								(select id 
								from account_sql_report_sales xx
								where xx.a5 = rp.vat
								and xx.a4 = TO_CHAR(date_trunc('month', am.invoice_date), 'YYYYMMDD')
								Limit 1) as a3,
                                ROW_NUMBER() OVER (PARTITION BY am.id ORDER BY aml.id) AS a5,
                                CASE rp.state_id
                                        WHEN 666 THEN '002'
                                        ELSE '001'
                                END AS a6,
                                rp.zip as a7,
                                CASE COALESCE(SPLIT_PART(pg.complete_name, '/', array_length(string_to_array(pg.complete_name, '/'), 1)), '')
                                        WHEN ' CORPORATIVO' THEN '0001'
                                        WHEN ' RESIDENCIAL' THEN '0002'
                                        WHEN ' EMPLEADOS' THEN '0003'
                                        WHEN ' RESIDENCIALES MINTIC' THEN '0004'
                                        WHEN ' CLIENTES EN EL EXTERIOR' THEN '0005'
                                        ELSE 'UNKNOWN'
                                END AS a8,
                                1 as a9,
                                aml.price_subtotal as a10,
                                'SERVICIO ENTREGADO ' || COALESCE(pt.name->>'en_US', 'Unknown') || ' ' || COALESCE(rp.street,'Unknown') || ' PERIODO FACTURADO ' || date_part('day', (date_trunc('month', (aml.date + interval '1 month')) - interval '1 day')::date) - date_part('day', aml.date)||' LUGAR DEL SERVICIO ' || COALESCE(rp.city,'Unknown') || ' DISPONIBILIDAD --' as a11,
                                pp.default_code as a12,
                                CASE COALESCE(SPLIT_PART(pg.complete_name, '/', 1), '')
                                        WHEN 'CONECTIVIDAD GESTIONADA' THEN '001'
                                        WHEN 'CONECTIVIDAD GESTIONADA ' THEN '001'
                                        WHEN 'IP MOBILE ' THEN '005'
  										 WHEN 'IP MOBILE' THEN '005'
                                        ELSE '--'
                                END AS a13
                FROM public.account_move am
                left join res_partner rp ON am.partner_id = rp.id
                left join account_move_line aml on am.id = aml.move_id
                left join product_product pp on aml.product_id = pp.id
                                left join product_template pt on pp.product_tmpl_id = pt.id
                                left join product_category pg ON pt.categ_id = pg.id
								where aml.price_subtotal > 0
                                order by am.id asc
            )
        """)

