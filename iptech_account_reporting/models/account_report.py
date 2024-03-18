from odoo import models, fields, api

class AccountReport(models.Model):
    _name='account.sql.report.custom'
    _description = 'account sql report'
    _auto = False

    invoice_partner = fields.Char(string='Cliente')
    razon_social = fields.Char(string='Razon Social')
    nit = fields.Char(string='NIT')
    service = fields.Char(string="Servicio")
    address = fields.Char(string="Direccion")
    reference = fields.Char(string="Referencia")
    comercial = fields.Char(string="Comercial")
    service_line = fields.Char(string="Linea Servicio IPTECH")
    sub_business_line = fields.Char(string="Sub Linea de Negocio")
    client_type = fields.Char(string="Tipo de Cliente")
    id_city = fields.Char(string='ID_Municipio')
    city = fields.Char(string='Lugar de servicio')
    service_type = fields.Char(string='Tipo de servicio')
    total = fields.Float(string="Valor contratado")
    payment_date = fields.Datetime(string='Fecha de pago')



    def init(self):
        self._cr.execute("""
            DROP VIEW account_sql_report_custom;
            CREATE OR REPLACE VIEW account_sql_report_custom AS (
                SELECT row_number() OVER() as id,               
                rp.name as invoice_partner,   
                COALESCE(SPLIT_PART(am.invoice_partner_display_name, ',', 1), '') as razon_social,
                rp.vat as nit,                
                aml.name as service,
                rp.street as address,
                pp.default_code as reference,
                rp1.name as comercial,
				COALESCE(SPLIT_PART(pg.complete_name, '/', 1), '') AS service_line,
				COALESCE(SPLIT_PART(pg.complete_name, '/', 2), '') AS sub_business_line,
				COALESCE(SPLIT_PART(pg.complete_name, '/', array_length(string_to_array(pg.complete_name, '/'), 1)), '') AS client_type,                
				rp.zip as id_city,
				rp.city as city,				
				COALESCE(SPLIT_PART(pg.complete_name, '/', array_length(string_to_array(pg.complete_name, '/'), 1) - 1), '') AS service_type,				
                am.amount_total_signed as total,
				ap.create_Date as payment_date
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

