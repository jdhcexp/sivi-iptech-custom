from odoo import models, fields, api

class AccountReportCuotas(models.Model):
    _name='account.sql.report.cuotas'
    _description = 'account sql report cuotas'
    _auto = False

    a1 = fields.Char(string='Centro de operación del documento')
    a2 = fields.Char(string='Tipo de documento')
    a3 = fields.Char(string='Numero de documento')
    a4 = fields.Char(string="Fecha de vencimiento AAAAMMDD.")
    a5 = fields.Char(string="Fecha de pronto pago de la cuota")
  
    


    def init(self):
        self._cr.execute("""      
		DROP VIEW IF EXISTS account_sql_report_cuotas;        
            CREATE OR REPLACE VIEW account_sql_report_cuotas AS (
            SELECT row_number() OVER() as id,   
				'001' as a1,	
				'FEE' as a2,
				am.id as a3,				
				CASE am.invoice_payment_term_id
					WHEN 1 THEN TO_CHAR(am.invoice_date, 'YYYYMMDD')
					WHEN 2 THEN TO_CHAR((am.invoice_date + INTERVAL '15 days'), 'YYYYMMDD')
					WHEN 3 THEN TO_CHAR((am.invoice_date + INTERVAL '21 days'), 'YYYYMMDD')
					WHEN 4 THEN TO_CHAR((am.invoice_date + INTERVAL '30 days'), 'YYYYMMDD')
					WHEN 5 THEN TO_CHAR((am.invoice_date + INTERVAL '45 days'), 'YYYYMMDD')
					WHEN 6 THEN TO_CHAR((am.invoice_date + INTERVAL '60 days'), 'YYYYMMDD')
					WHEN 7 THEN ''
					WHEN 8 THEN ''
					WHEN 9 THEN ''
					WHEN 10 THEN ''
					ELSE '--'
				END AS a4,
				CASE am.invoice_payment_term_id
					WHEN 1 THEN TO_CHAR(am.invoice_date, 'YYYYMMDD')
					WHEN 2 THEN TO_CHAR((am.invoice_date + INTERVAL '15 days'), 'YYYYMMDD')
					WHEN 3 THEN TO_CHAR((am.invoice_date + INTERVAL '21 days'), 'YYYYMMDD')
					WHEN 4 THEN TO_CHAR((am.invoice_date + INTERVAL '30 days'), 'YYYYMMDD')
					WHEN 5 THEN TO_CHAR((am.invoice_date + INTERVAL '45 days'), 'YYYYMMDD')
					WHEN 6 THEN TO_CHAR((am.invoice_date + INTERVAL '60 days'), 'YYYYMMDD')
					WHEN 7 THEN ''
					WHEN 8 THEN ''
					WHEN 9 THEN ''
					WHEN 10 THEN ''
					ELSE '--'
				END AS a5
                FROM public.account_move am
                left join res_partner rp ON am.partner_id = rp.id
                left join account_move_line aml on am.id = aml.move_id
                left join product_product pp on aml.product_id = pp.id					
				left join product_template pt on pp.product_tmpl_id = pt.id
				left join product_category pg ON pt.categ_id = pg.id
                left join res_users ru ON am.invoice_user_id = ru.id
				left join res_partner rp1 ON ru.partner_id = rp1.id
				left join account_payment ap ON am.id = ap.move_id
				where pp.sh_product_subscribe = 'true'
            )
        """)

