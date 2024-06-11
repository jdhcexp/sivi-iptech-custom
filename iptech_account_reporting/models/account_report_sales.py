from odoo import models, fields, api

class AccountReport(models.Model):
    _name='account.sql.report.sales'
    _description = 'account sql report sales'
    _auto = False
    #a00 = fields.Many2one('account.move',string="Id Factura")
    #a0 = fields.Char(string="Factura")
    a1 = fields.Char(string='Centro de operación del documento')
    a2 = fields.Char(string='Tipo de documento')
    a0 = fields.Char(string='Numero de documento')
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
	    DROP VIEW IF EXISTS account_sql_report_movements;
	    DROP VIEW IF EXISTS account_sql_report_sales;
            CREATE OR REPLACE VIEW account_sql_report_sales as (
        select row_number() OVER() as id,
	    row_number() OVER() as a0, foo.* from
            (SELECT distinct
				'001' as a1,	
				'FEE' as a2,
				--row_number() OVER() as a3,
				--TO_CHAR(am.invoice_date, 'YYYYMMDD') as a4,
				TO_CHAR(date_trunc('month', am.invoice_date), 'YYYYMMDD') AS a4,
				rp.vat as a5,    
				'' as a6,
				'001' as a7,
				CASE COALESCE(SPLIT_PART(pg.complete_name, '/', array_length(string_to_array(pg.complete_name, '/'), 1)), '')
					WHEN ' CORPORATIVO' THEN '0001'
					WHEN ' RESIDENCIAL' THEN '0002'
					WHEN ' EMPLEADOS' THEN '0003'
					WHEN ' RESIDENCIALES MINTIC' THEN '0004'
					WHEN ' CLIENTES EN EL EXTERIOR' THEN '0005'
					ELSE 'UNKNOWN'
				END AS a8,
				CASE rp.state_id
					WHEN 666 THEN '002'
					ELSE '001'
				END AS a9,
				rp.vat as a10,  
				'001' as a11,
				rp1.vat as a12,
				CASE am.invoice_payment_term_id
					WHEN 1 THEN 'Inmediato'
					WHEN 2 THEN '15D'
					WHEN 3 THEN '21D'
					WHEN 4 THEN '30D'
					WHEN 5 THEN '45D'
					WHEN 6 THEN '60D'
					WHEN 7 THEN ''
					WHEN 8 THEN ''
					WHEN 9 THEN ''
					WHEN 10 THEN ''
					ELSE '--'
				END AS a13,
				CASE COALESCE(SPLIT_PART(pg.complete_name, '/', array_length(string_to_array(pg.complete_name, '/'), 1)), '')
					WHEN ' CORPORATIVO' THEN 'El Medio de pago, registrando si se trata de efectivo o transferencia electrónica u otro medio que aplique a la cuenta corriente # 131151581 del BANCO DE BOGOTA a nombre de IP TECHNOLOGIES SAS o generar el pago virtual PSE en la página www.ip.net.co. Enviar soporte de pago al correo cartera@ip.net.co. Dando cumplimiento al Art. 86 de la Ley 1676 de 2013, si pasados tres (3) días hábiles siguientes a la recepción de la factura, y ésta no ha sido rechazada, se dará por aceptada.'
					WHEN ' RESIDENCIAL' THEN 'Los únicos medios de pago para su factura son SUPER GIROS, corresponsales bancarios de Banco de Bogotá convenio 3782 (EFECTY, MOVIIRED, SURED) o generar el pago virtual PSE en la página www.ip.net.co. Cualquier inquietud no dude en comunicarse con nosotros Mesa de Servicio: 3015059691 Cartera: 601-7460160-104, 200, 202. No se aceptan consignaciones en bancos. Dando cumplimiento al Art. 86 de la Ley 1676 de 2013, si pasados tres (3) días hábiles siguientes a la recepción de la factura, y ésta no ha sido rechazada, se dará por aceptada.'
					ELSE '--'
				END AS a14
                FROM public.account_move am
                left join res_partner rp ON am.partner_id = rp.id
                left join account_move_line aml on am.id = aml.move_id
                left join product_product pp on aml.product_id = pp.id					
				left join product_template pt on pp.product_tmpl_id = pt.id
				left join product_category pg ON pt.categ_id = pg.id
                left join res_users ru ON am.invoice_user_id = ru.id
				left join res_partner rp1 ON ru.partner_id = rp1.id
				left join account_payment ap ON am.id = ap.move_id
				where pp.sh_product_subscribe = 'true') as foo
            );
        """)

