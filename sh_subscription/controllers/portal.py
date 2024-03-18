# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
import json
from werkzeug.utils import redirect
from odoo.tools import ustr
from dateutil.relativedelta import relativedelta


class SHSubscriptionPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        subscription_obj = request.env['sh.subscription.subscription']
        subscription_count = subscription_obj.sudo().search_count(
            [('sh_partner_id', '=', request.env.user.partner_id.id)])
        subscriptions = subscription_obj.sudo().search(
            [('sh_partner_id', '=', request.env.user.partner_id.id)])
 
        values.update({
            'subscription_count':subscription_count,
        })

        return values

    @http.route(['/my/sh_subscription', '/my/sh_subscription/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_home_subscription(self, page=1):
        values = self._prepare_portal_layout_values()
        subscription_obj = request.env['sh.subscription.subscription']
        domain = [
            ('sh_partner_id', '=', request.env.user.partner_id.id)
        ]
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('sh_partner_id', '=', request.env.user.partner_id.id), ('state', 'in', ['draft', 'in_progress', 'cancel', 'close', 'expire', 'renewed'])]},
            'draft': {'label': _('Draft'), 'domain': [('sh_partner_id', '=', request.env.user.partner_id.id), ('state', 'in', ['draft'])]},
            'in_progress': {'label': _('In Progress'), 'domain': [('sh_partner_id', '=', request.env.user.partner_id.id), ('state', 'in', ['in_progress'])]},
            'cancel': {'label': _('Cancelled'), 'domain': [('sh_partner_id', '=', request.env.user.partner_id.id), ('state', 'in', ['cancel'])]},
            'close': {'label': _('Closed'), 'domain': [('sh_partner_id', '=', request.env.user.partner_id.id), ('state', 'in', ['close'])]},
            'expire': {'label': _('Expired'), 'domain': [('sh_partner_id', '=', request.env.user.partner_id.id), ('state', 'in', ['expire'])]},
            'renewed': {'label': _('Renewed'), 'domain': [('sh_partner_id', '=', request.env.user.partner_id.id), ('state', 'in', ['renewed'])]},
        }
        # default filter by value
        subscription_count = subscription_obj.sudo().search_count(domain)

        pager = portal_pager(
            url="/my/sh_subscription",
            total=subscription_count,
            page=page,
            step=self._items_per_page
        )

        subscriptions = subscription_obj.sudo().search(
            domain, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'subscriptions': subscriptions,
            'page_name': 'sh_subscription',
            'pager': pager,
            'default_url': '/my/sh_subscription',
            'subscription_count': subscription_count,
        })
        return request.render("sh_subscription.sh_portal_my_subscriptions", values)

    @http.route(['/my/sh_subscription/<int:subscription_id>'], type='http', auth="user", website=True)
    def portal_my_sh_subscription_form(self, subscription_id, message=False, **kw):
        sh_subscription = request.env['sh.subscription.subscription'].sudo().browse(
            subscription_id)
        if sh_subscription:
            if sh_subscription.sh_partner_id.id != request.env.user.partner_id.id:
                return request.redirect('/my')
            else:
                values = {
                    'sh_subscription': sh_subscription,
                    'message': message,
                    'bootstrap_formatting': True,
                    'sh_partner_id': sh_subscription.sh_partner_id.id,
                }
                return request.render('sh_subscription.sh_subscription_portal_content', values)

    @http.route('/cancel-subscription', type="http", auth="user", csrf=False)
    def portal_cancel_subscription(self, **kw):
        dic = {}
        if kw.get('subscription_id'):
            subscription_id = request.env['sh.subscription.subscription'].sudo().browse(
                int(kw.get('subscription_id')))
            if subscription_id:
                if kw.get('sh_reason_id') and kw.get('sh_reason_id') != 'reason':
                    reason_id = request.env['sh.subscription.reason'].sudo().browse(
                        int(kw.get('sh_reason_id')))
                    if reason_id:
                        if kw.get('description') and kw.get('description') != '':
                            subscription_id.sh_reason = reason_id.name + \
                                ' '+kw.get('description')
                            if subscription_id.state == 'draft':
                                subscription_id.state = 'cancel'
                            else:
                                subscription_id.state = 'close'
                            subscription_id._sh_send_subscription_email(False)
                        else:
                            subscription_id.sh_reason = reason_id.name
                            if subscription_id.state == 'draft':
                                subscription_id.state = 'cancel'
                            else:
                                subscription_id.state = 'close'
                            subscription_id._sh_send_subscription_email(False)
                        dic.update({
                            'reload': True
                        })
                else:
                    dic.update({
                        'required': True
                    })
        return json.dumps(dic)

    @http.route('/renew-subscription', type="http", auth="user", csrf=False)
    def portal_renew_subscription(self, **kw):
        dic = {}
        if kw.get('subscription_id'):
            subscription = request.env['sh.subscription.subscription'].sudo().browse(
                int(kw.get('subscription_id')))
            if subscription:
                if subscription.state == 'in_progress':
                    date_value = subscription.sh_end_date+relativedelta(days=1)
                    subscription.sh_renew_stage = 'not_time_to_renew'
                else:
                    date_value = fields.Date.today()
                    subscription.state = 'renewed'
                    subscription.sh_renew_stage = 'not_time_to_renew'
                subscription.sh_renewed = True
                if subscription.sh_subscription_plan_id.sh_override_product == True:
                    sub_vals = {
                        'sh_partner_id': subscription.sh_partner_id.id,
                        'product_id': subscription.product_id.id,
                        'sh_partner_invoice_id': subscription.sh_partner_invoice_id.id,
                        'sh_taxes_ids': subscription.sh_taxes_ids.ids,
                        'sh_qty': subscription.sh_qty,
                        'sh_subscription_plan_id': subscription.sh_subscription_plan_id.id,
                        'sh_plan_price': subscription.product_id.lst_price,
                        'sh_recurrency': subscription.sh_recurrency,
                        'sh_unit': subscription.sh_unit,
                        'sh_start_date': date_value,
                        'sh_no_of_billing_cycle': subscription.sh_no_of_billing_cycle,
                        'sh_source': subscription.sh_source,
                        'sh_order_ref_id': False,
                        'sh_subscription_ref': subscription.sh_subscription_ref,
                        'sh_subscription_id': subscription.id,
                        'sh_date_of_next_payment': date_value,
                    }
                elif 'website_id' in self.env['sale.order']._fields and subscription.sh_order_ref_id.website_id:
                    sub_vals = {
                        'sh_partner_id': subscription.sh_partner_id.id,
                        'product_id': subscription.product_id.id,
                        'sh_partner_invoice_id': subscription.sh_partner_invoice_id.id,
                        'sh_taxes_ids': subscription.sh_taxes_ids.ids,
                        'sh_qty': subscription.sh_qty,
                        'sh_subscription_plan_id': subscription.sh_subscription_plan_id.id,
                        'sh_plan_price': subscription.product_id.lst_price,
                        'sh_recurrency': subscription.sh_recurrency,
                        'sh_unit': subscription.sh_unit,
                        'sh_start_date': date_value,
                        'sh_no_of_billing_cycle': subscription.sh_no_of_billing_cycle,
                        'sh_source': subscription.sh_source,
                        'sh_order_ref_id': False,
                        'sh_subscription_ref': subscription.sh_subscription_ref,
                        'sh_subscription_id': subscription.id,
                        'sh_date_of_next_payment': date_value,
                    }
                else:
                    sub_vals = {
                        'sh_partner_id': subscription.sh_partner_id.id,
                        'product_id': subscription.product_id.id,
                        'sh_partner_invoice_id': subscription.sh_partner_invoice_id.id,
                        'sh_taxes_ids': subscription.sh_taxes_ids.ids,
                        'sh_qty': subscription.sh_qty,
                        'sh_subscription_plan_id': subscription.sh_subscription_plan_id.id,
                        'sh_plan_price': subscription.sh_plan_price,
                        'sh_recurrency': subscription.sh_recurrency,
                        'sh_unit': subscription.sh_unit,
                        'sh_start_date': date_value,
                        'sh_no_of_billing_cycle': subscription.sh_no_of_billing_cycle,
                        'sh_source': subscription.sh_source,
                        'sh_order_ref_id': False,
                        'sh_subscription_ref': subscription.sh_subscription_ref,
                        'sh_subscription_id': subscription.id,
                        'sh_date_of_next_payment': date_value,
                    }
                result = request.env["sh.subscription.subscription"].sudo().create(
                    sub_vals)
                result._onchange_sh_trial_subcription_start_date()
                result._onchange_sh_trial_subcription_end_date()
                subscription._sh_send_subscription_email(False)
                dic.update({
                    'reload': True
                })
        return json.dumps(dic)
