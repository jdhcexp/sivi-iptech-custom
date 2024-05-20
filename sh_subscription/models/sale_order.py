# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sh_subscription_count = fields.Integer(
        string="Subscription", compute='compute_view_subscription_sale_order', default=0, groups="sh_subscription.group_user_sh_subscription")

    prorated=fields.Integer(string="Dias Prorateo", default=0)

    def compute_view_subscription_sale_order(self):
        for rec in self:
            rec.sh_subscription_count = self.env['sh.subscription.subscription'].search_count(
                [('sh_order_ref_id.id', '=', self.id)])

    def sh_action_view_subscription_sale_order(self):
        self.ensure_one()
        subscription = self.env['sh.subscription.subscription'].search(
            [('sh_order_ref_id.id', '=', self.id)])
        action = self.env["ir.actions.actions"]._for_xml_id(
            "sh_subscription.sh_subscription_subscription_action")
        if len(subscription) > 1:
            action['domain'] = [('id', 'in', subscription.ids)]
        elif len(subscription) == 1:
            form_view = [
                (self.env.ref('sh_subscription.sh_subscription_subscription_form_view').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + \
                    [(state, view)
                        for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = subscription.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_confirm(self):
        print("!!!!!!!!!!!!!!!!!!!!!!!!!")
        super(SaleOrder, self).action_confirm()
        for order_ln in self.order_line:
            if order_ln.product_id.detailed_type == 'service' and order_ln.product_id.sh_product_subscribe == True:
                result = self.env["sh.subscription.subscription"].sudo().create(
                    {
                        'sh_partner_id': self.partner_id.id,
                        'product_id': order_ln.product_id.id,
                        'sh_taxes_ids': [(6, 0, order_ln.tax_id.ids)],
                        'sh_qty': order_ln.product_uom_qty,
                        'sh_order_ref_id': self.id,
                        'sh_source': 'sales_order',
                        'sh_subscription_plan_id': order_ln.product_id.sh_subscription_plan_id.id,
                        'sh_plan_price': order_ln.price_unit
                    })

                result._onchange_sh_product_id()
                result._onchange_sh_partner_id()
                result._onchange_sh_subscription_plan_id()
                result._onchange_sh_trial_subcription_start_date()
                result._onchange_sh_trial_subcription_end_date()
                result.sh_subscription_confirm()

    @api.onchange("prorated")
    def _onchange_prorated(self):               
        products=[]
        for order_ln in self.order_line:
            if "prorateo" not in order_ln.name:
                products.append({'order_name':order_ln.name,'order_price_unit':order_ln.price_unit})
        print('productos no prorateados:')
        print(products)
        exist_prorateo = False
        for prod in products:            
            for order_ln in self.order_line:
                print('todos los productos:')
                print(order_ln.name)
                # pro_name = prod+' prorateo'
                if prod['order_name']+' prorateo' in order_ln.name:
                    print('productio prorateado!!!!!!')                    
                    product_id = self.env['product.product'].search([('id', '=', order_ln.product_id.id)])
                    order_ln.price_unit = (prod['order_price_unit']/30)*self.prorated
                    order_ln.name = prod['order_name']+' prorateo '+str(self.prorated)+" dias"                    
                    print('nuevo nombre')
                    print(order_ln.name)
                    exist_prorateo = True
        
        if exist_prorateo == False:
            for order_ln in self.order_line:            
                if order_ln.product_id.sh_product_subscribe == True and "prorateo" not in order_ln.name :                
                    product_id = self.env['product.product'].search([('id', '=', order_ln.product_id.id)])
                    print(product_id.id)                
                    line_vals = {'product_id': product_id.id, 
                        'name': order_ln.name+' prorateo '+str(self.prorated)+" dias", 
                        'price_unit': (order_ln.price_unit/30)*self.prorated, 
                        'product_uom_qty': 1.0,
                        'currency_id': order_ln.currency_id,
                        'discount':order_ln.discount
                        }
                    lines = []
                    lines.append((0, 0, line_vals))                    
                    self.order_line = lines

