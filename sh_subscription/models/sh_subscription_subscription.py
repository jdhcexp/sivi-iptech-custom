# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models, api, _
from datetime import date
from dateutil.relativedelta import relativedelta
from calendar import monthrange
from odoo.exceptions import UserError
import base64

INTERVAL_FACTOR = {
    'day': 30.0,
    'week': 30.0 / 7.0,
    'month': 1.0,
    'year': 1.0 / 12.0,
}


PERIODS = {'day': 'Day(s)', 'week': 'week(s)',
           'month': 'month(s)', 'year': 'year(s)'}


class SubscriptionSubscription(models.Model):

    _name = 'sh.subscription.subscription'
    _description = 'Subscription subscription'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    def _get_default_currency_id(self):
        return self.env.company.currency_id.id

    # Customer Details
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('cancel', 'Cancelled'),
        ('close', 'Finished'),
        ('expire', 'Expired'),
        ('renewed', 'Renewed')
    ], string='State', readonly=True,  copy=False, tracking=True, required=True, default='draft')
    name = fields.Char(string='Name',
                       readonly=True, default=lambda self: _('New'))
    active = fields.Boolean(string="Active", default=True)
    sh_partner_id = fields.Many2one(
        comodel_name="res.partner", string="Customer Name")
    product_id = fields.Many2one(
        comodel_name="product.product", string="Product", domain="[('sh_product_subscribe','=', True)]",)
    sh_partner_invoice_id = fields.Many2one(
        comodel_name="res.partner", string="Customer Invoice Address")
    sh_taxes_ids = fields.Many2many(
        comodel_name="account.tax", string="Taxes")
    sh_qty = fields.Float(string='Quantity', default=1)

    # Plan Details
    sh_subscription_plan_id = fields.Many2one(
        comodel_name="sh.subscription.plan", string="Subscription Plan")
    sh_plan_price = fields.Float(string='Price')
    currency_id = fields.Many2one(
        comodel_name="res.currency", string="Currency", default=_get_default_currency_id)
    sh_company_id = fields.Many2one(
        comodel_name="res.company", string="Company", readonly=True, default=lambda self: self.env.company)
    sh_recurrency = fields.Integer(string='Recurrency')
    sh_unit = fields.Selection([("day", "Day(s)"), ("week", "Week(s)"), (
        "month", "Month(s)"), ("year", "Year(s)")], string="Units")
    sh_start_date = fields.Date(
        string="Start Date", copy=False)
    sh_end_date = fields.Date(string="End Date", copy=False)
    sh_trial_end_date = fields.Date(string="Trial End Date", copy=False)
    sh_trial = fields.Boolean(string="Plan has trial period", copy=False)
    sh_trial_duration = fields.Integer(string='Trial duration', copy=False)
    sh_trial_unit = fields.Selection([("day", "Day(s)"), ("week", "Week(s)"), (
        "month", "Month(s)"), ("year", "Year(s)")], string="Unit", copy=False)
    sh_no_of_billing_cycle = fields.Integer(
        string='No of billing cycle')

    # Payment Details
    sh_source = fields.Selection(
        [("manual", "Manual"), ("sales_order", "Sales Order")], string="Source", default='manual')
    sh_subscription_ref = fields.Char(
        string="Subscription Reference", copy=False)
    sh_date_of_next_payment = fields.Date(string="Date Of Next Payment")
    sh_subscription_id = fields.Many2one(
        comodel_name="sh.subscription.subscription", string="Subscription Id", copy=False)
    sh_invoice_count = fields.Integer(
        string="Subscription", compute='compute_view_invoice', default=0, copy=False)
    sh_order_ref_id = fields.Many2one(
        comodel_name="sale.order", string="Order Ref", readonly=True, copy=False)
    sh_renew_stage = fields.Selection([
        ('not_time_to_renew', 'Not Time TO Renew'),
        ('time_to_renew', 'Time TO Renew')], string='Renew State', default='not_time_to_renew', copy=False)
    sh_last_payment_status = fields.Selection([
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid')], string='Invoice Status', compute='compute_sh_last_payment_status', readonly=True,  copy=False, default='unpaid', search='search_sh_last_payment_status')
    sh_amount_due = fields.Float(
        string='Amount Due', compute='compute_sh_amount_due', search='search_sh_amount_due', copy=False)
    sh_reason = fields.Char(string='Cancel/Close Reason', copy=False)
    sh_renewed = fields.Boolean(string="Renewed")
    sh_recurring_monthly = fields.Float(
        compute='_compute_sh_recurring_monthly', string="Monthly Recurring Revenue", store=True)
    # prorated = fields.Boolean(string="prorated", default=False)

    @api.depends('sh_plan_price', 'sh_recurrency', 'sh_unit')
    def _compute_sh_recurring_monthly(self):
        for sub in self:
            if sub.sh_plan_price and sub.sh_unit and sub.sh_recurrency:
                sub.sh_recurring_monthly = (
                    sub.sh_plan_price * INTERVAL_FACTOR[sub.sh_unit] / sub.sh_recurrency)
            else:
                sub.sh_recurring_monthly = 0.0

    def _sh_send_subscription_email(self, attachment_id):
        self.ensure_one()
        template_id = self.env.ref(
            'sh_subscription.sh_subscription_customer_email')
        if template_id and self.sh_invoice_count == 1:
            if attachment_id:
                email_values = {'attachment_ids': [(6, 0, attachment_id.ids)]}
                template_id.sudo().send_mail(self.id, force_send=True, email_values=email_values)
            else:
                template_id.sudo().send_mail(self.id, force_send=True)
        else:
            if template_id and self.sh_company_id.sh_invoice_email:
                if attachment_id:
                    email_values = {'attachment_ids': [
                        (6, 0, attachment_id.ids)]}
                    template_id.sudo().send_mail(self.id, force_send=True, email_values=email_values)
                else:
                    template_id.sudo().send_mail(self.id, force_send=True)

    def compute_sh_last_payment_status(self):
        for rec in self:
            last_payment_status = self.env['account.move'].search(
                [('sh_subscription_id', '=', rec.id)], limit=1)
            if last_payment_status.amount_residual == 0:
                rec.sh_last_payment_status = 'paid'
            else:
                rec.sh_last_payment_status = 'unpaid'

    def compute_sh_amount_due(self):
        for rec in self:
            move_ids = self.env['account.move'].search(
                [('sh_subscription_id', '=', rec.id)])
            amount = 0
            for move in move_ids:
                amount += move.amount_residual
            rec.sh_amount_due = amount

    def search_sh_last_payment_status(self, operator, value):
        paid_ids = []
        unpaid_ids = []
        for rec in self.search([]):
            last_payment_status = self.env['account.move'].search(
                [('sh_subscription_id', '=', rec.id)], limit=1)
            if last_payment_status.amount_residual == 0:
                paid_ids.append(rec.id)
                rec.sh_last_payment_status = 'paid'
            else:
                rec.sh_last_payment_status = 'unpaid'
                unpaid_ids.append(rec.id)
        if value == 'paid':
            return [('id', 'in', paid_ids)]
        elif value == 'unpaid':
            return [('id', 'in', unpaid_ids)]
        else:
            return []

    def search_sh_amount_due(self, operator, value):
        paid_ids = []
        unpaid_ids = []
        for rec in self.search([]):
            move_ids = self.env['account.move'].search(
                [('sh_subscription_id', '=', rec.id)])
            amount = 0
            for move in move_ids:
                amount += move.amount_residual
            if amount == 0:
                paid_ids.append(rec.id)
            else:
                unpaid_ids.append(rec.id)
        if operator == '=':
            return [('id', 'in', paid_ids)]
        elif operator == '!=':
            return [('id', 'in', unpaid_ids)]
        else:
            return []

    def _subscription_renew_button_visible(self):
        active_subscription_ids = self.env['sh.subscription.subscription'].sudo().search([
            ('state', 'in', ['in_progress'])
        ])
        if active_subscription_ids:
            for subscription in active_subscription_ids:
                if subscription.sh_end_date:
                    temp_date = subscription.sh_end_date - \
                        relativedelta(
                            days=subscription.sh_company_id.sh_renewal_days)
                    current_date = fields.Date.today()
                    if temp_date == current_date:
                        subscription.sh_renew_stage = 'time_to_renew'

    def _subscription_email_subject(self):
        self.ensure_one()
        status = ''
        if self.state == 'draft':
            status = 'Waiting'
        elif self.state == 'in_progress':
            if self.sh_renewed == True:
                status = 'Renewed'
            else:
                status = 'Active'
        elif self.state == 'cancel':
            status = 'Cancelled'
        elif self.state == 'close':
            status = 'Finished'
        elif self.state == 'expire':
            status = 'Expired'
        elif self.state == 'renewed':
            status = 'Renewed'
        return status

    @api.onchange('sh_trial', 'sh_trial_duration', 'sh_trial_unit', 'sh_subscription_plan_id', 'sh_partner_id', 'product_id')
    def _onchange_sh_trial_subcription_start_date(self):
        if self.sh_company_id.sh_trial_period_setting == True:
            sub = self.env['sh.subscription.subscription'].sudo().search(
                [('sh_partner_id', '=', self.sh_partner_id.id), ('sh_subscription_plan_id', '=', self.sh_subscription_plan_id.id), ('product_id', '=', self.product_id.id)])
            if sub and sub[-1].id != self.id:
                self.sh_trial = False
                self.sh_trial_end_date = False
                if self.sh_subscription_id and self.sh_subscription_id.state == 'in_progress':
                    self.sh_start_date = self.sh_subscription_id.sh_end_date + \
                        relativedelta(days=1)
                else:
                    self.sh_start_date = date.today()
                self.sh_date_of_next_payment = self.sh_start_date
            else:
                if self.sh_subscription_plan_id.sh_free_trial_for_current_month == True:
                    date_value = fields.Date.today()
                    trial_end_date = date_value.replace(day=monthrange(
                        date_value.year, date_value.month)[1])
                    self.sh_trial_end_date = trial_end_date
                    if self.sh_subscription_id and self.sh_subscription_id.state == 'in_progress':
                        self.sh_start_date = self.sh_subscription_id.sh_end_date + \
                            relativedelta(days=1)+trial_end_date + \
                            relativedelta(days=1)
                    else:
                        self.sh_start_date = trial_end_date + \
                            relativedelta(days=1)
                    self.sh_date_of_next_payment = self.sh_start_date + \
                        relativedelta(
                            days=self.sh_subscription_plan_id.sh_billing_day_of_the_month - 1)
                else:
                    self.sh_trial_end_date = False
                    if self.sh_trial == False:
                        if self.sh_subscription_id and self.sh_subscription_id.state == 'in_progress':
                            self.sh_start_date = self.sh_subscription_id.sh_end_date + \
                                relativedelta(days=1)
                        else:
                            self.sh_start_date = date.today()
                        self.sh_date_of_next_payment = self.sh_start_date
                    else:
                        if self.sh_subscription_id and self.sh_subscription_id.state == 'in_progress':
                            temp_date = self.sh_subscription_id.sh_end_date + \
                                relativedelta(days=1)
                        else:
                            temp_date = date.today()
                        if self.sh_trial_unit == 'day':
                            self.sh_start_date = temp_date + \
                                relativedelta(days=self.sh_trial_duration)
                            self.sh_date_of_next_payment = self.sh_start_date
                        if self.sh_trial_unit == 'week':
                            self.sh_start_date = temp_date + \
                                relativedelta(days=(self.sh_trial_duration*7))
                            self.sh_date_of_next_payment = self.sh_start_date
                        if self.sh_trial_unit == 'month':
                            self.sh_start_date = temp_date + \
                                relativedelta(months=self.sh_trial_duration)
                            self.sh_date_of_next_payment = self.sh_start_date
                        if self.sh_trial_unit == 'year':
                            self.sh_start_date = temp_date + \
                                relativedelta(years=self.sh_trial_duration)
                            self.sh_date_of_next_payment = self.sh_start_date
        else:
            if self.sh_subscription_plan_id.sh_free_trial_for_current_month == True:
                date_value = fields.Date.today()
                trial_end_date = date_value.replace(day=monthrange(
                    date_value.year, date_value.month)[1])
                self.sh_trial_end_date = trial_end_date
                if self.sh_subscription_id and self.sh_subscription_id.state == 'in_progress':
                    self.sh_start_date = self.sh_subscription_id.sh_end_date + \
                        relativedelta(days=1)+trial_end_date + \
                        relativedelta(days=1)
                else:
                    self.sh_start_date = trial_end_date + relativedelta(days=1)
                self.sh_date_of_next_payment = self.sh_start_date + \
                    relativedelta(
                        days=self.sh_subscription_plan_id.sh_billing_day_of_the_month - 1)
            else:
                self.sh_trial_end_date = False
                if self.sh_trial == False:
                    if self.sh_subscription_id and self.sh_subscription_id.state == 'in_progress':
                        self.sh_start_date = self.sh_subscription_id.sh_end_date + \
                            relativedelta(days=1)
                    else:
                        self.sh_start_date = date.today()
                    self.sh_date_of_next_payment = self.sh_start_date
                else:
                    if self.sh_subscription_id and self.sh_subscription_id.state == 'in_progress':
                        temp_date = self.sh_subscription_id.sh_end_date + \
                            relativedelta(days=1)
                    else:
                        temp_date = date.today()
                    if self.sh_trial_unit == 'day':
                        self.sh_start_date = temp_date + \
                            relativedelta(days=self.sh_trial_duration)
                        self.sh_date_of_next_payment = self.sh_start_date
                    if self.sh_trial_unit == 'week':
                        self.sh_start_date = temp_date + \
                            relativedelta(days=(self.sh_trial_duration*7))
                        self.sh_date_of_next_payment = self.sh_start_date
                    if self.sh_trial_unit == 'month':
                        self.sh_start_date = temp_date + \
                            relativedelta(months=self.sh_trial_duration)
                        self.sh_date_of_next_payment = self.sh_start_date
                    if self.sh_trial_unit == 'year':
                        self.sh_start_date = temp_date + \
                            relativedelta(years=self.sh_trial_duration)
                        self.sh_date_of_next_payment = self.sh_start_date

    @api.onchange('sh_start_date', 'sh_recurrency', 'sh_unit', 'sh_no_of_billing_cycle', 'sh_subscription_plan_id')
    def _onchange_sh_trial_subcription_end_date(self):
        if self.sh_subscription_plan_id.sh_never_expire == True:
            pass
        else:
            if self.sh_unit == 'day':
                self.sh_end_date = self.sh_start_date + \
                    relativedelta(days=self.sh_recurrency *
                                  self.sh_no_of_billing_cycle)-relativedelta(days=1)
            elif self.sh_unit == 'week':
                self.sh_end_date = self.sh_start_date + \
                    relativedelta(days=self.sh_recurrency *
                                  self.sh_no_of_billing_cycle*7)-relativedelta(days=1)
            elif self.sh_unit == 'month':
                self.sh_end_date = self.sh_start_date + \
                    relativedelta(months=self.sh_recurrency *
                                  self.sh_no_of_billing_cycle)-relativedelta(days=1)
            elif self.sh_unit == 'year':
                self.sh_end_date = self.sh_start_date + \
                    relativedelta(years=self.sh_recurrency *
                                  self.sh_no_of_billing_cycle)-relativedelta(days=1)

    @api.onchange('sh_partner_id')
    def _onchange_sh_partner_id(self):
        if self.sh_partner_id:
            invoice_contact_id = self.sh_partner_id.child_ids.sudo().filtered(
                lambda x: x.type in ['invoice'])
            if invoice_contact_id:
                self.sh_partner_invoice_id = invoice_contact_id[0].id
            else:
                self.sh_partner_invoice_id = self.sh_partner_id.id

    @api.onchange('sh_subscription_plan_id', 'sh_partner_id')
    def _onchange_sh_subscription_plan_id(self):
        if self.sh_subscription_plan_id:
            sub = self.env['sh.subscription.subscription'].sudo().search(
                [('sh_partner_id', '=', self.sh_partner_id.id), ('sh_subscription_plan_id', '=', self.sh_subscription_plan_id.id), ('product_id', '=', self.product_id.id)])
            self.sh_recurrency = self.sh_subscription_plan_id.sh_duration
            self.sh_unit = self.sh_subscription_plan_id.sh_unit
            if sub and sub[-1].id != self.id:
                self.sh_trial = False
            else:
                self.sh_trial = self.sh_subscription_plan_id.sh_trial
                self.sh_trial_duration = self.sh_subscription_plan_id.sh_trial_duration
                self.sh_trial_unit = self.sh_subscription_plan_id.sh_trial_unit
        if self.sh_subscription_plan_id.sh_never_expire == True:
            self.sh_no_of_billing_cycle = -1
            self.sh_end_date = False
        else:
            self.sh_no_of_billing_cycle = self.sh_subscription_plan_id.sh_no_of_billing_cycle

    @api.onchange('product_id', 'sh_subscription_plan_id')
    def _onchange_sh_product_id(self):
        if self.product_id:
            sub = self.env['sh.subscription.subscription'].search(
                [('sh_partner_id', '=', self.sh_partner_id.id), ('product_id', '=', self.product_id.id), ('sh_subscription_plan_id', '=', self.sh_subscription_plan_id.id)])
            self.sh_subscription_plan_id = self.product_id.sh_subscription_plan_id
            self.sh_taxes_ids = self.product_id.taxes_id.ids
            self.sh_recurrency = self.product_id.sh_subscription_plan_id.sh_duration
            self.sh_unit = self.product_id.sh_subscription_plan_id.sh_unit
            if sub and sub[-1].id != self.id:
                self.sh_trial = False
            else:
                self.sh_trial = self.sh_subscription_plan_id.sh_trial
                self.sh_trial_duration = self.sh_subscription_plan_id.sh_trial_duration
                self.sh_trial_unit = self.sh_subscription_plan_id.sh_trial_unit
            self.sh_plan_price = self.sh_order_ref_id.amount_untaxed

    def sh_subscription_confirm(self):
        self.ensure_one()
        if not self.active:
            raise UserError('you can not conform the inactive subscription')
        else:
            self.state = 'in_progress'
            invoice_vals = {}
            invoice_id = False
            if fields.Date.today() < self.sh_start_date:
                if self.sh_order_ref_id and 'website_id' in self.env['sale.order']._fields and self.sh_order_ref_id.website_id:
                    payment = self.env['payment.transaction'].sudo().search(
                        [('sale_order_ids', 'in', [self.sh_order_ref_id.id]), ('state', '=', 'done')], limit=1)
                    if payment:
                        if self.sh_invoice_count == 0 and self.sh_order_ref_id:
                            order_line = self.env['sale.order.line'].sudo().search(
                                [('order_id', '=', self.sh_order_ref_id.id), ('product_id', '=', self.product_id.id)])
                            if 'applied_coupon_ids' in self.env['sale.order']._fields and self.sh_order_ref_id.applied_coupon_ids:
                                product_ids = self.sh_order_ref_id.order_line.mapped('product_id')
                                discount_per=sum(self.env['loyalty.reward'].search([('discount_line_product_id', 'in', product_ids.ids),('program_id','=',self.sh_order_ref_id.applied_coupon_ids.program_id.id)]).mapped('discount'))
                                discount=(order_line.price_subtotal*discount_per)/100
                                price = order_line.price_subtotal-discount
                                invoice_vals.update({
                                    'sh_subscription_id': self.id,
                                    'partner_id': self.sh_partner_id.id,
                                    'invoice_date': fields.Date.today(),
                                    'currency_id': self.currency_id.id,
                                    'move_type': 'out_invoice',
                                    'journal_id': self.sh_company_id.sh_journal_id.id,
                                    'invoice_line_ids': [(0, 0, {
                                        'product_id': self.product_id.id,
                                        'name': self.product_id.name_get()[0][1],
                                        'currency_id':self.currency_id.id,
                                        'quantity': self.sh_qty,
                                        'price_unit':price,
                                        'tax_ids': [(6, 0, self.sh_taxes_ids.ids)],
                                    })]
                                })
                            elif order_line and order_line.discount:
                                invoice_vals.update({
                                    'sh_subscription_id': self.id,
                                    'partner_id': self.sh_partner_id.id,
                                    'invoice_date': fields.Date.today(),
                                    'currency_id': self.currency_id.id,
                                    'move_type': 'out_invoice',
                                    'journal_id': self.sh_company_id.sh_journal_id.id,
                                    'invoice_line_ids': [(0, 0, {
                                        'product_id': self.product_id.id,
                                        'name': self.product_id.name_get()[0][1],
                                        'currency_id':self.currency_id.id,
                                        'quantity': self.sh_qty,
                                        'price_unit':order_line.price_subtotal,
                                        'tax_ids': [(6, 0, self.sh_taxes_ids.ids)],
                                    })]
                                })
                            else:
                                invoice_vals.update({
                                    'sh_subscription_id': self.id,
                                    'partner_id': self.sh_partner_id.id,
                                    'invoice_date': fields.Date.today(),
                                    'currency_id': self.currency_id.id,
                                    'move_type': 'out_invoice',
                                    'journal_id': self.sh_company_id.sh_journal_id.id,
                                    'invoice_line_ids': [(0, 0, {
                                        'product_id': self.product_id.id,
                                        'name': self.product_id.name_get()[0][1],
                                        'currency_id':self.currency_id.id,
                                        'quantity': self.sh_qty,
                                        'price_unit':self.sh_plan_price,
                                        'tax_ids': [(6, 0, self.sh_taxes_ids.ids)],
                                    })]
                                })
                        else:
                            invoice_vals.update({
                                'sh_subscription_id': self.id,
                                'partner_id': self.sh_partner_id.id,
                                'invoice_date': fields.Date.today(),
                                'currency_id': self.currency_id.id,
                                'move_type': 'out_invoice',
                                'journal_id': self.sh_company_id.sh_journal_id.id,
                                'invoice_line_ids': [(0, 0, {
                                    'product_id': self.product_id.id,
                                    'name': self.product_id.name_get()[0][1],
                                    'currency_id':self.currency_id.id,
                                    'quantity': self.sh_qty,
                                    'price_unit':self.sh_plan_price,
                                    'tax_ids': [(6, 0, self.sh_taxes_ids.ids)],
                                })]
                            })
                    else:
                        if self.sh_order_ref_id.amount_total == 0:
                            if self.sh_unit == 'day':
                                next_payment_date = self.sh_date_of_next_payment + \
                                    relativedelta(days=self.sh_recurrency)
                            if self.sh_unit == 'week':
                                next_payment_date = self.sh_date_of_next_payment + \
                                    relativedelta(days=(self.sh_recurrency*7))
                            if self.sh_unit == 'month':
                                next_payment_date = self.sh_date_of_next_payment + \
                                    relativedelta(months=self.sh_recurrency)
                            if self.sh_unit == 'year':
                                next_payment_date = self.sh_date_of_next_payment + \
                                    relativedelta(years=self.sh_recurrency)
                            if next_payment_date:
                                self.sh_date_of_next_payment = next_payment_date

            elif self.sh_order_ref_id and 'website_id' in self.env['sale.order']._fields and self.sh_order_ref_id.website_id:
                payment = self.env['payment.transaction'].sudo().search(
                    [('sale_order_ids', 'in', [self.sh_order_ref_id.id]), ('state', '=', 'done')], limit=1)
                if payment:
                    if self.sh_invoice_count == 0 and self.sh_order_ref_id:
                        order_line = self.env['sale.order.line'].sudo().search(
                            [('order_id', '=', self.sh_order_ref_id.id), ('product_id', '=', self.product_id.id)])
                        if 'applied_coupon_ids' in self.env['sale.order']._fields and self.sh_order_ref_id.applied_coupon_ids:
                            product_ids = self.sh_order_ref_id.order_line.mapped('product_id')
                            discount_per=sum(self.env['loyalty.reward'].search([('discount_line_product_id', 'in', product_ids.ids),('program_id','=',self.sh_order_ref_id.applied_coupon_ids.program_id.id)]).mapped('discount'))
                            discount=(order_line.price_subtotal*discount_per)/100
                            price = order_line.price_subtotal-discount
                            invoice_vals.update({
                                'sh_subscription_id': self.id,
                                'partner_id': self.sh_partner_id.id,
                                'invoice_date': fields.Date.today(),
                                'currency_id': self.currency_id.id,
                                'move_type': 'out_invoice',
                                'journal_id': self.sh_company_id.sh_journal_id.id,
                                'invoice_line_ids': [(0, 0, {
                                    'product_id': self.product_id.id,
                                    'name': self.product_id.name_get()[0][1],
                                    'currency_id':self.currency_id.id,
                                    'quantity': self.sh_qty,
                                    'price_unit':price,
                                    'tax_ids': [(6, 0, self.sh_taxes_ids.ids)],
                                })]
                            })
                        elif order_line and order_line.discount:
                            invoice_vals.update({
                                'sh_subscription_id': self.id,
                                'partner_id': self.sh_partner_id.id,
                                'invoice_date': fields.Date.today(),
                                'currency_id': self.currency_id.id,
                                'move_type': 'out_invoice',
                                'journal_id': self.sh_company_id.sh_journal_id.id,
                                'invoice_line_ids': [(0, 0, {
                                    'product_id': self.product_id.id,
                                    'name': self.product_id.name_get()[0][1],
                                    'currency_id':self.currency_id.id,
                                    'quantity': self.sh_qty,
                                    'price_unit':order_line.price_subtotal,
                                    'tax_ids': [(6, 0, self.sh_taxes_ids.ids)],
                                })]
                            })
                        else:
                            invoice_vals.update({
                                'sh_subscription_id': self.id,
                                'partner_id': self.sh_partner_id.id,
                                'invoice_date': fields.Date.today(),
                                'currency_id': self.currency_id.id,
                                'move_type': 'out_invoice',
                                'journal_id': self.sh_company_id.sh_journal_id.id,
                                'invoice_line_ids': [(0, 0, {
                                    'product_id': self.product_id.id,
                                    'name': self.product_id.name_get()[0][1],
                                    'currency_id':self.currency_id.id,
                                    'quantity': self.sh_qty,
                                    'price_unit':self.sh_plan_price,
                                    'tax_ids': [(6, 0, self.sh_taxes_ids.ids)],
                                })]
                            })
                    else:
                        invoice_vals.update({
                            'sh_subscription_id': self.id,
                            'partner_id': self.sh_partner_id.id,
                            'invoice_date': fields.Date.today(),
                            'currency_id': self.currency_id.id,
                            'move_type': 'out_invoice',
                            'journal_id': self.sh_company_id.sh_journal_id.id,
                            'invoice_line_ids': [(0, 0, {
                                'product_id': self.product_id.id,
                                'name': self.product_id.name_get()[0][1],
                                'currency_id':self.currency_id.id,
                                'quantity': self.sh_qty,
                                'price_unit':self.sh_plan_price,
                                'tax_ids': [(6, 0, self.sh_taxes_ids.ids)],
                            })]
                        })
                else:
                    if self.sh_order_ref_id.amount_total == 0:
                        if self.sh_unit == 'day':
                            next_payment_date = self.sh_date_of_next_payment + \
                                relativedelta(days=self.sh_recurrency)
                        if self.sh_unit == 'week':
                            next_payment_date = self.sh_date_of_next_payment + \
                                relativedelta(days=(self.sh_recurrency*7))
                        if self.sh_unit == 'month':
                            next_payment_date = self.sh_date_of_next_payment + \
                                relativedelta(months=self.sh_recurrency)
                        if self.sh_unit == 'year':
                            next_payment_date = self.sh_date_of_next_payment + \
                                relativedelta(years=self.sh_recurrency)
                        if next_payment_date:
                            self.sh_date_of_next_payment = next_payment_date
            else:
                if not self.sh_end_date and self.sh_no_of_billing_cycle == -1:
                    if self.sh_invoice_count == 0 and self.sh_order_ref_id:
                        order_line = self.env['sale.order.line'].sudo().search(
                            [('order_id', '=', self.sh_order_ref_id.id), ('product_id', '=', self.product_id.id)])
                        if 'website_id' in self.env['sale.order']._fields and self.sh_order_ref_id.website_id and 'applied_coupon_ids' in self.env['sale.order']._fields and self.sh_order_ref_id.applied_coupon_ids:
                            product_ids = self.sh_order_ref_id.order_line.mapped('product_id')
                            discount_per=sum(self.env['loyalty.reward'].search([('discount_line_product_id', 'in', product_ids.ids),('program_id','=',self.sh_order_ref_id.applied_coupon_ids.program_id.id)]).mapped('discount'))
                            discount=(order_line.price_subtotal*discount_per)/100
                            price = order_line.price_subtotal-discount
                            invoice_vals.update({
                                'sh_subscription_id': self.id,
                                'partner_id': self.sh_partner_id.id,
                                'invoice_date': fields.Date.today(),
                                'currency_id': self.currency_id.id,
                                'move_type': 'out_invoice',
                                'journal_id': self.sh_company_id.sh_journal_id.id,
                                'invoice_line_ids': [(0, 0, {
                                    'product_id': self.product_id.id,
                                    'name': self.product_id.name_get()[0][1],
                                    'currency_id':self.currency_id.id,
                                    'quantity': self.sh_qty,
                                    'price_unit':price,
                                    'tax_ids': [(6, 0, self.sh_taxes_ids.ids)],
                                })]
                            })
                        elif order_line and order_line.discount:
                            invoice_vals.update({
                                'sh_subscription_id': self.id,
                                'partner_id': self.sh_partner_id.id,
                                'invoice_date': fields.Date.today(),
                                'currency_id': self.currency_id.id,
                                'move_type': 'out_invoice',
                                'journal_id': self.sh_company_id.sh_journal_id.id,
                                'invoice_line_ids': [(0, 0, {
                                    'product_id': self.product_id.id,
                                    'name': self.product_id.name_get()[0][1],
                                    'currency_id':self.currency_id.id,
                                    'quantity': self.sh_qty,
                                    'price_unit':order_line.price_subtotal,
                                    'tax_ids': [(6, 0, self.sh_taxes_ids.ids)],
                                })]
                            })
                        else:
                            invoice_vals.update({
                                'sh_subscription_id': self.id,
                                'partner_id': self.sh_partner_id.id,
                                'invoice_date': fields.Date.today(),
                                'journal_id': self.sh_company_id.sh_journal_id.id,
                                'move_type': 'out_invoice',
                                'currency_id': self.currency_id.id,
                                'invoice_line_ids': [(0, 0, {
                                    'product_id': self.product_id.id,
                                    'name': self.product_id.name_get()[0][1],
                                    'currency_id':self.currency_id.id,
                                    'quantity': self.sh_qty,
                                    'price_unit':self.sh_plan_price,
                                    'tax_ids': [(6, 0, self.sh_taxes_ids.ids)],
                                })]
                            })
                    else:
                        invoice_vals.update({
                            'sh_subscription_id': self.id,
                            'partner_id': self.sh_partner_id.id,
                            'invoice_date': fields.Date.today(),
                            'journal_id': self.sh_company_id.sh_journal_id.id,
                            'move_type': 'out_invoice',
                            'currency_id': self.currency_id.id,
                            'invoice_line_ids': [(0, 0, {
                                'product_id': self.product_id.id,
                                'name': self.product_id.name_get()[0][1],
                                'currency_id':self.currency_id.id,
                                'quantity': self.sh_qty,
                                'price_unit':self.sh_plan_price,
                                'tax_ids': [(6, 0, self.sh_taxes_ids.ids)],
                            })]
                        })
                elif self.sh_no_of_billing_cycle == 0:
                    self.state = 'expire'
                else:
                    if self.sh_invoice_count < self.sh_no_of_billing_cycle:
                        if self.sh_invoice_count == 0 and self.sh_order_ref_id:
                            order_line = self.env['sale.order.line'].sudo().search(
                                [('order_id', '=', self.sh_order_ref_id.id), ('product_id', '=', self.product_id.id)])
                            if 'website_id' in self.env['sale.order']._fields and self.sh_order_ref_id.website_id and 'applied_coupon_ids' in self.env['sale.order']._fields and self.sh_order_ref_id.applied_coupon_ids:
                                product_ids = self.sh_order_ref_id.order_line.mapped('product_id')
                                discount_per=sum(self.env['loyalty.reward'].search([('discount_line_product_id', 'in', product_ids.ids),('program_id','=',self.sh_order_ref_id.applied_coupon_ids.program_id.id)]).mapped('discount'))
                                discount=(order_line.price_subtotal*discount_per)/100
                                price = order_line.price_subtotal-discount
                                invoice_vals.update({
                                    'sh_subscription_id': self.id,
                                    'partner_id': self.sh_partner_id.id,
                                    'invoice_date': fields.Date.today(),
                                    'currency_id': self.currency_id.id,
                                    'move_type': 'out_invoice',
                                    'journal_id': self.sh_company_id.sh_journal_id.id,
                                    'invoice_line_ids': [(0, 0, {
                                        'product_id': self.product_id.id,
                                        'name': self.product_id.name_get()[0][1],
                                        'currency_id':self.currency_id.id,
                                        'quantity': self.sh_qty,
                                        'price_unit':price,
                                        'tax_ids': [(6, 0, self.sh_taxes_ids.ids)],
                                    })]
                                })
                            elif order_line and order_line.discount:
                                invoice_vals.update({
                                    'sh_subscription_id': self.id,
                                    'partner_id': self.sh_partner_id.id,
                                    'invoice_date': fields.Date.today(),
                                    'currency_id': self.currency_id.id,
                                    'move_type': 'out_invoice',
                                    'journal_id': self.sh_company_id.sh_journal_id.id,
                                    'invoice_line_ids': [(0, 0, {
                                        'product_id': self.product_id.id,
                                        'name': self.product_id.name_get()[0][1],
                                        'currency_id':self.currency_id.id,
                                        'quantity': self.sh_qty,
                                        'price_unit':order_line.price_subtotal,
                                        'tax_ids': [(6, 0, self.sh_taxes_ids.ids)],
                                    })]
                                })
                            else:
                                invoice_vals.update({
                                    'sh_subscription_id': self.id,
                                    'partner_id': self.sh_partner_id.id,
                                    'invoice_date': fields.Date.today(),
                                    'currency_id': self.currency_id.id,
                                    'move_type': 'out_invoice',
                                    'journal_id': self.sh_company_id.sh_journal_id.id,
                                    'invoice_line_ids': [(0, 0, {
                                        'product_id': self.product_id.id,
                                        'name': self.product_id.name_get()[0][1],
                                        'currency_id':self.currency_id.id,
                                        'quantity': self.sh_qty,
                                        'price_unit':self.sh_plan_price,
                                        'tax_ids': [(6, 0, self.sh_taxes_ids.ids)],
                                    })]
                                })
                        else:
                            invoice_vals.update({
                                'sh_subscription_id': self.id,
                                'partner_id': self.sh_partner_id.id,
                                'invoice_date': fields.Date.today(),
                                'currency_id': self.currency_id.id,
                                'move_type': 'out_invoice',
                                'journal_id': self.sh_company_id.sh_journal_id.id,
                                'invoice_line_ids': [(0, 0, {
                                    'product_id': self.product_id.id,
                                    'name': self.product_id.name_get()[0][1],
                                    'currency_id':self.currency_id.id,
                                    'quantity': self.sh_qty,
                                    'price_unit':self.sh_plan_price,
                                    'tax_ids': [(6, 0, self.sh_taxes_ids.ids)],
                                })]
                            })
            if invoice_vals:
                invoice_id = self.env['account.move'].sudo().create(
                    invoice_vals)
                self.compute_view_invoice()
                next_payment_date = False
                if self.sh_subscription_plan_id.sh_free_trial_for_current_month:
                    if self.sh_unit == 'month':
                        next_payment_date = self.sh_date_of_next_payment + \
                            relativedelta(months=self.sh_recurrency)
                else:
                    if self.sh_unit == 'day':
                        next_payment_date = self.sh_date_of_next_payment + \
                            relativedelta(days=self.sh_recurrency)
                    if self.sh_unit == 'week':
                        next_payment_date = self.sh_date_of_next_payment + \
                            relativedelta(days=(self.sh_recurrency*7))
                    if self.sh_unit == 'month':
                        next_payment_date = self.sh_date_of_next_payment + \
                            relativedelta(months=self.sh_recurrency)
                    if self.sh_unit == 'year':
                        next_payment_date = self.sh_date_of_next_payment + \
                            relativedelta(years=self.sh_recurrency)
                if next_payment_date:
                    self.sh_date_of_next_payment = next_payment_date
                if self.sh_company_id.sh_invoice_generated == 'post':
                    invoice_id.sudo().action_post()
                elif self.sh_company_id.sh_invoice_generated == 'paid':
                    if not self.sh_company_id.sh_paid_subscription_journal:
                        raise UserError(_("Default Journal not found."))
                    invoice_id.sudo().action_post()
                    payment = self.env['account.payment'].sudo().create(
                        {
                            'journal_id': self.sh_company_id.sh_paid_subscription_journal.id,
                            'amount': invoice_id.amount_total,
                            'payment_type': 'inbound',
                            'payment_method_id': self.env['account.payment.method'].search([('payment_type', '=', 'inbound')], limit=1).id,
                            'partner_type': 'customer',
                            'partner_id': invoice_id.partner_id.id,
                        }
                    )
                    payment.sudo().action_post()
                    invoice_id.payment_state = 'paid'
                    invoice_id.amount_residual = invoice_id.amount_total-invoice_id.amount_residual
                    invoice_id.amount_residual_signed = invoice_id.amount_total - \
                        invoice_id.amount_residual_signed
                    invoice_id.sudo()._compute_payments_widget_reconciled_info()
                self._sh_send_subscription_email(False)
                action = self.env["ir.actions.actions"]._for_xml_id(
                    "account.action_move_out_invoice_type")
                if len(invoice_id) > 1:
                    action['domain'] = [('id', 'in', invoice_id.ids)]
                elif len(invoice_id) == 1:
                    form_view = [
                        (self.env.ref('account.view_move_form').id, 'form')]
                    if 'views' in action:
                        action['views'] = form_view + \
                            [(state, view)
                                for state, view in action['views'] if view != 'form']
                    else:
                        action['views'] = form_view
                    action['res_id'] = invoice_id.id
                else:
                    action = {'type': 'ir.actions.act_window_close'}
                return action

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'sh.subscription.subscription.name') or _('New')
        return super(SubscriptionSubscription, self).create(vals_list)

    def compute_view_invoice(self):
        for rec in self:
            rec.sh_invoice_count = self.env['account.move'].search_count(
                [('sh_subscription_id', '=', rec.id)])

    def sh_action_view_invoice(self):
        self.ensure_one()
        invoices = self.env['account.move'].sudo().search(
            [('sh_subscription_id', '=', self.id)])
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_move_out_invoice_type")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [
                (self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + \
                    [(state, view)
                        for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def sh_generate_invoice(self):
        self.ensure_one()
        if fields.Date.today() < self.sh_start_date:
            raise UserError(
                "you can not create the invoice due to trial period")
        else:
            invoice_vals = {}
            invoice_id = False

            if self.sh_no_of_billing_cycle == -1:
                if self.sh_invoice_count == 0 and 'applied_coupon_ids' in self.env['sale.order']._fields and self.sh_order_ref_id.applied_coupon_ids:
                    order_line = self.env['sale.order.line'].sudo().search(
                        [('order_id', '=', self.sh_order_ref_id.id), ('product_id', '=', self.product_id.id)])
                    product_ids = self.sh_order_ref_id.order_line.mapped('product_id')
                    discount_per=sum(self.env['loyalty.reward'].search([('discount_line_product_id', 'in', product_ids.ids),('program_id','=',self.sh_order_ref_id.applied_coupon_ids.program_id.id)]).mapped('discount'))
                    discount=(order_line.price_subtotal*discount_per)/100
                    price = order_line.price_subtotal-discount
                    invoice_vals.update({
                        'sh_subscription_id': self.id,
                        'partner_id': self.sh_partner_id.id,
                        'invoice_date': fields.Date.today(),
                        'currency_id': self.currency_id.id,
                        'move_type': 'out_invoice',
                        'journal_id': self.sh_company_id.sh_journal_id.id,
                        'invoice_line_ids': [(0, 0, {
                            'product_id': self.product_id.id,
                            'name': self.product_id.name_get()[0][1],
                            'currency_id':self.currency_id.id,
                            'quantity': self.sh_qty,
                            'price_unit':price,
                            'tax_ids': [(6, 0, self.sh_taxes_ids.ids)],
                        })]
                    })
                else:
                    invoice_vals.update({
                        'sh_subscription_id': self.id,
                        'partner_id': self.sh_partner_id.id,
                        'invoice_date': fields.Date.today(),
                        'currency_id': self.currency_id.id,
                        'journal_id': self.sh_company_id.sh_journal_id.id,
                        'move_type': 'out_invoice',
                        'invoice_line_ids': [(0, 0, {
                            'product_id': self.product_id.id,
                            'name': self.product_id.name_get()[0][1],
                            'currency_id':self.currency_id.id,
                            'quantity': self.sh_qty,
                            'price_unit':self.sh_plan_price,
                            'tax_ids': [(6, 0, self.sh_taxes_ids.ids)],
                        })]
                    })
            else:
                if self.sh_order_ref_id and 'website_id' in self.env['sale.order']._fields and self.sh_order_ref_id.website_id and self.sh_order_ref_id.amount_total == 0:
                    if self.sh_invoice_count+1 < self.sh_no_of_billing_cycle:
                        if self.sh_invoice_count == 0 and 'applied_coupon_ids' in self.env['sale.order']._fields and self.sh_order_ref_id.applied_coupon_ids:
                            order_line = self.env['sale.order.line'].sudo().search(
                                [('order_id', '=', self.sh_order_ref_id.id), ('product_id', '=', self.product_id.id)])
                            product_ids = self.sh_order_ref_id.order_line.mapped('product_id')
                            discount_per=sum(self.env['loyalty.reward'].search([('discount_line_product_id', 'in', product_ids.ids),('program_id','=',self.sh_order_ref_id.applied_coupon_ids.program_id.id)]).mapped('discount'))
                            discount=(order_line.price_subtotal*discount_per)/100
                            price = order_line.price_subtotal-discount
                            invoice_vals.update({
                                'sh_subscription_id': self.id,
                                'partner_id': self.sh_partner_id.id,
                                'invoice_date': fields.Date.today(),
                                'currency_id': self.currency_id.id,
                                'move_type': 'out_invoice',
                                'journal_id': self.sh_company_id.sh_journal_id.id,
                                'invoice_line_ids': [(0, 0, {
                                    'product_id': self.product_id.id,
                                    'name': self.product_id.name_get()[0][1],
                                    'currency_id':self.currency_id.id,
                                    'quantity': self.sh_qty,
                                    'price_unit':price,
                                    'tax_ids': [(6, 0, self.sh_taxes_ids.ids)],
                                })]
                            })
                        else:
                            invoice_vals.update({
                                'sh_subscription_id': self.id,
                                'partner_id': self.sh_partner_id.id,
                                'currency_id': self.currency_id.id,
                                'invoice_date': self.sh_date_of_next_payment,
                                'journal_id': self.sh_company_id.sh_journal_id.id,
                                'move_type': 'out_invoice',
                                'invoice_line_ids': [(0, 0, {
                                    'product_id': self.product_id.id,
                                    'name': self.product_id.name_get()[0][1],
                                    'currency_id':self.currency_id.id,
                                    'quantity': self.sh_qty,
                                    'price_unit':self.sh_plan_price,
                                    'tax_ids': [(6, 0, self.sh_taxes_ids.ids)],
                                })]
                            })
                else:
                    if self.sh_invoice_count < self.sh_no_of_billing_cycle:
                        if self.sh_invoice_count == 0 and 'applied_coupon_ids' in self.env['sale.order']._fields and self.sh_order_ref_id.applied_coupon_ids:
                            order_line = self.env['sale.order.line'].sudo().search(
                                [('order_id', '=', self.sh_order_ref_id.id), ('product_id', '=', self.product_id.id)])
                            product_ids = self.sh_order_ref_id.order_line.mapped('product_id')
                            discount_per=sum(self.env['loyalty.reward'].search([('discount_line_product_id', 'in', product_ids.ids),('program_id','=',self.sh_order_ref_id.applied_coupon_ids.program_id.id)]).mapped('discount'))
                            discount=(order_line.price_subtotal*discount_per)/100
                            price = order_line.price_subtotal-discount
                            invoice_vals.update({
                                'sh_subscription_id': self.id,
                                'partner_id': self.sh_partner_id.id,
                                'invoice_date': fields.Date.today(),
                                'currency_id': self.currency_id.id,
                                'move_type': 'out_invoice',
                                'journal_id': self.sh_company_id.sh_journal_id.id,
                                'invoice_line_ids': [(0, 0, {
                                    'product_id': self.product_id.id,
                                    'name': self.product_id.name_get()[0][1],
                                    'currency_id':self.currency_id.id,
                                    'quantity': self.sh_qty,
                                    'price_unit':price,
                                    'tax_ids': [(6, 0, self.sh_taxes_ids.ids)],
                                })]
                            })
                        else:
                            invoice_vals.update({
                                'sh_subscription_id': self.id,
                                'partner_id': self.sh_partner_id.id,
                                'currency_id': self.currency_id.id,
                                'invoice_date': self.sh_date_of_next_payment,
                                'journal_id': self.sh_company_id.sh_journal_id.id,
                                'move_type': 'out_invoice',
                                'invoice_line_ids': [(0, 0, {
                                    'product_id': self.product_id.id,
                                    'name': self.product_id.name_get()[0][1],
                                    'currency_id':self.currency_id.id,
                                    'quantity': self.sh_qty,
                                    'price_unit':self.sh_plan_price,
                                    'tax_ids': [(6, 0, self.sh_taxes_ids.ids)],
                                })]
                            })
        if invoice_vals:
            invoice_id = self.env['account.move'].sudo().create(
                invoice_vals)
            self.compute_view_invoice()
            next_payment_date = False
            if self.sh_subscription_plan_id.sh_free_trial_for_current_month:
                if self.sh_unit == 'month':
                    next_payment_date = self.sh_date_of_next_payment + \
                        relativedelta(months=self.sh_recurrency)
            else:
                if self.sh_unit == 'day':
                    next_payment_date = self.sh_date_of_next_payment + \
                        relativedelta(
                            days=self.sh_recurrency)
                if self.sh_unit == 'week':
                    next_payment_date = self.sh_date_of_next_payment + \
                        relativedelta(
                            days=(self.sh_recurrency*7))
                if self.sh_unit == 'month':
                    next_payment_date = self.sh_date_of_next_payment + \
                        relativedelta(
                            months=self.sh_recurrency)
                if self.sh_unit == 'year':
                    next_payment_date = self.sh_date_of_next_payment + \
                        relativedelta(
                            years=self.sh_recurrency)
            if next_payment_date:
                self.sh_date_of_next_payment = next_payment_date
            if self.sh_company_id.sh_invoice_generated == 'post':
                invoice_id.sudo().action_post()
            elif self.sh_company_id.sh_invoice_generated == 'paid':
                if not self.sh_company_id.sh_paid_subscription_journal:
                    raise UserError(_("Default Journal not found."))
                invoice_id.action_post()
                payment = self.env['account.payment'].sudo().create(
                    {
                        'journal_id': self.sh_company_id.sh_paid_subscription_journal.id,
                        'amount': invoice_id.amount_total,
                        'payment_type': 'inbound',
                        'payment_method_id': self.env['account.payment.method'].search([('payment_type', '=', 'inbound')], limit=1).id,
                        'partner_type': 'customer',
                        'partner_id': invoice_id.partner_id.id,
                    }
                )
                payment.action_post()
                invoice_id.payment_state = 'paid'
                invoice_id.amount_residual = invoice_id.amount_total-invoice_id.amount_residual
                invoice_id.amount_residual_signed = invoice_id.amount_total - \
                    invoice_id.amount_residual_signed
                invoice_id._compute_payments_widget_reconciled_info()
            html =self.env['ir.actions.report'].sudo()._render_qweb_pdf('account.account_invoices',invoice_id.id)
            invoice_data = base64.b64encode(html[0])
            attachment_values = {
                'name': "Subscription Invoice",
                'type': 'binary',
                'datas': invoice_data,
                'store_fname': invoice_data,
                'mimetype': 'application/pdf',
                'res_id': str(invoice_id.id),
                'res_model': 'account.move'

            }
            attachment_id = self.env['ir.attachment'].sudo().create(
                attachment_values)
            self._sh_send_subscription_email(attachment_id)
            action = self.env["ir.actions.actions"]._for_xml_id(
                "account.action_move_out_invoice_type")
            if len(invoice_id) > 1:
                action['domain'] = [('id', 'in', invoice_id.ids)]
            elif len(invoice_id) == 1:
                form_view = [
                    (self.env.ref('account.view_move_form').id, 'form')]
                if 'views' in action:
                    action['views'] = form_view + \
                        [(state, view)
                            for state, view in action['views'] if view != 'form']
                else:
                    action['views'] = form_view
                action['res_id'] = invoice_id.id
            else:
                action = {'type': 'ir.actions.act_window_close'}
            return action

    @api.model
    def _sh_create_auto_invoice(self):
        subscription_ids = self.env['sh.subscription.subscription'].sudo().search([
            ('state', 'in', ['in_progress'])
        ])
        if subscription_ids:
            for subscription in subscription_ids:
                if subscription.sh_date_of_next_payment == fields.Date.today():
                    invoice_vals = {}
                    invoice_id = False
                    if subscription.sh_no_of_billing_cycle == -1:
                        invoice_vals.update({
                            'sh_subscription_id': subscription.id,
                            'partner_id': subscription.sh_partner_id.id,
                            'invoice_date': subscription.sh_date_of_next_payment,
                            'journal_id': subscription.sh_company_id.sh_journal_id.id,
                            'currency_id': subscription.currency_id.id,
                            'move_type': 'out_invoice',
                            'invoice_line_ids': [(0, 0, {
                                'product_id': subscription.product_id.id,
                                'name': subscription.product_id.name_get()[0][1],
                                'currency_id':subscription.currency_id.id,
                                'quantity': subscription.sh_qty,
                                'price_unit':subscription.sh_plan_price,
                                'tax_ids': [(6, 0, subscription.sh_taxes_ids.ids)],
                            })]
                        })
                    else:
                        if subscription.sh_order_ref_id and 'website_id' in self.env['sale.order']._fields and subscription.sh_order_ref_id.website_id and subscription.sh_order_ref_id.amount_total == 0:
                            if subscription.sh_invoice_count+1 < subscription.sh_no_of_billing_cycle:
                                invoice_vals.update({
                                    'sh_subscription_id': subscription.id,
                                    'partner_id': subscription.sh_partner_id.id,
                                    'currency_id': subscription.currency_id.id,
                                    'invoice_date': subscription.sh_date_of_next_payment,
                                    'journal_id': subscription.sh_company_id.sh_journal_id.id,
                                    'move_type': 'out_invoice',
                                    'invoice_line_ids': [(0, 0, {
                                        'product_id': subscription.product_id.id,
                                        'name': subscription.product_id.name_get()[0][1],
                                        'currency_id':subscription.currency_id.id,
                                        'quantity': subscription.sh_qty,
                                        'price_unit':subscription.sh_plan_price,
                                        'tax_ids': [(6, 0, subscription.sh_taxes_ids.ids)],
                                    })]
                                })
                        else:
                            if subscription.sh_invoice_count < subscription.sh_no_of_billing_cycle:
                                invoice_vals.update({
                                    'sh_subscription_id': subscription.id,
                                    'partner_id': subscription.sh_partner_id.id,
                                    'currency_id': subscription.currency_id.id,
                                    'invoice_date': subscription.sh_date_of_next_payment,
                                    'journal_id': subscription.sh_company_id.sh_journal_id.id,
                                    'move_type': 'out_invoice',
                                    'invoice_line_ids': [(0, 0, {
                                        'product_id': subscription.product_id.id,
                                        'name': subscription.product_id.name_get()[0][1],
                                        'currency_id':subscription.currency_id.id,
                                        'quantity': subscription.sh_qty,
                                        'price_unit':subscription.sh_plan_price,
                                        'tax_ids': [(6, 0, subscription.sh_taxes_ids.ids)],
                                    })]
                                })
                    if invoice_vals:
                        invoice_id = self.env['account.move'].sudo().create(
                            invoice_vals)
                        subscription.compute_view_invoice()
                        next_payment_date = False
                        if subscription.sh_subscription_plan_id.sh_free_trial_for_current_month:
                            if subscription.sh_unit == 'month':
                                next_payment_date = subscription.sh_date_of_next_payment + \
                                    relativedelta(
                                        months=subscription.sh_recurrency)

                        elif subscription.sh_order_ref_id and 'website_id' in self.env['sale.order']._fields and subscription.sh_order_ref_id.website_id and subscription.sh_order_ref_id.amount_total == 0:
                            if subscription.sh_unit == 'day':
                                next_payment_date = subscription.sh_date_of_next_payment + \
                                    relativedelta(
                                        days=subscription.sh_recurrency)
                            if subscription.sh_unit == 'week':
                                next_payment_date = subscription.sh_date_of_next_payment + \
                                    relativedelta(
                                        days=(subscription.sh_recurrency*7))
                            if subscription.sh_unit == 'month':
                                next_payment_date = subscription.sh_date_of_next_payment + \
                                    relativedelta(
                                        months=subscription.sh_recurrency)
                            if subscription.sh_unit == 'year':
                                next_payment_date = subscription.sh_date_of_next_payment + \
                                    relativedelta(
                                        years=subscription.sh_recurrency)

                        else:
                            if subscription.sh_unit == 'day':
                                next_payment_date = subscription.sh_date_of_next_payment + \
                                    relativedelta(
                                        days=subscription.sh_recurrency)
                            if subscription.sh_unit == 'week':
                                next_payment_date = subscription.sh_date_of_next_payment + \
                                    relativedelta(
                                        days=(subscription.sh_recurrency*7))
                            if subscription.sh_unit == 'month':
                                next_payment_date = subscription.sh_date_of_next_payment + \
                                    relativedelta(
                                        months=subscription.sh_recurrency)
                            if subscription.sh_unit == 'year':
                                next_payment_date = subscription.sh_date_of_next_payment + \
                                    relativedelta(
                                        years=subscription.sh_recurrency)

                        if next_payment_date:
                            subscription.sh_date_of_next_payment = next_payment_date
                        if subscription.sh_company_id.sh_invoice_generated == 'post':
                            invoice_id.sudo().action_post()
                        elif subscription.sh_company_id.sh_invoice_generated == 'paid':
                            if not subscription.sh_company_id.sh_paid_subscription_journal:
                                raise UserError(
                                    _("Default Journal not found."))
                            invoice_id.action_post()
                            payment = self.env['account.payment'].sudo().create(
                                {
                                    'journal_id': subscription.sh_company_id.sh_paid_subscription_journal.id,
                                    'amount': invoice_id.amount_total,
                                    'payment_type': 'inbound',
                                    'payment_method_id': self.env['account.payment.method'].search([('payment_type', '=', 'inbound')], limit=1).id,
                                    'partner_type': 'customer',
                                    'partner_id': invoice_id.partner_id.id,
                                }
                            )
                            payment.action_post()
                            invoice_id.payment_state = 'paid'
                            invoice_id.amount_residual = invoice_id.amount_total-invoice_id.amount_residual
                            invoice_id.amount_residual_signed = invoice_id.amount_total - \
                                invoice_id.amount_residual_signed
                            # invoice_id._compute_payments_widget_reconciled_info()
                        print("\n\n\\n invoice_id",invoice_id)
                        html =self.env['ir.actions.report'].sudo()._render_qweb_pdf('account.account_invoices',invoice_id.id)
                        # self.env.ref(
                        #     'account.account_invoices').sudo()._render_qweb_pdf(invoice_id.id)
                        print("\n\n\ html",html)
                        invoice_data = base64.b64encode(html[0])
                        print("\n\n\ invoice_data",invoice_data)
                        attachment_values = {
                            'name': "Subscription Invoice",
                            'type': 'binary',
                            'datas': invoice_data,
                            'store_fname': invoice_data,
                            'mimetype': 'application/pdf',
                            'res_id': str(invoice_id.id),
                            'res_model': 'account.move'

                        }
                        print("\n\n\ attachment_values",attachment_values)
                        attachment_id = self.env['ir.attachment'].sudo().create(
                            attachment_values)
                        print("\n\n\\n attachment_id",attachment_id)
                        subscription._sh_send_subscription_email(attachment_id)

    @api.model
    def _sh_auto_expired_subscription(self):
        active_subscription_ids = self.env['sh.subscription.subscription'].sudo().search([
            ('state', 'in', ['in_progress'])
        ])
        if active_subscription_ids:
            for subscription in active_subscription_ids:
                if subscription.sh_end_date:
                    if subscription.sh_end_date == fields.Date.today():
                        renew_subscription = self.env['sh.subscription.subscription'].sudo().search([
                            ('sh_subscription_id', '=', subscription.id)
                        ])
                        if renew_subscription:
                            subscription.state = 'renewed'
                        else:
                            subscription.state = 'expire'
                        subscription._sh_send_subscription_email(False)

    @api.model
    def _sh_auto_reminder_subscription(self):
        active_subscription_ids = self.env['sh.subscription.subscription'].sudo().search([
            ('state', 'in', ['in_progress', 'expire'])
        ])
        if active_subscription_ids:
            for subscription in active_subscription_ids:
                if subscription.sh_subscription_plan_id.sh_reminder:
                    for reminder in subscription.sh_subscription_plan_id.sh_reminder:
                        if reminder.sh_reminder_unit == 'days(s)':
                            date_reminder = subscription.sh_end_date + \
                                relativedelta(days=(reminder.sh_reminder))
                        elif reminder.sh_reminder_unit == 'week(s)':
                            date_reminder = subscription.sh_end_date + \
                                relativedelta(days=(reminder.sh_reminder*7))
                        elif reminder.sh_reminder_unit == 'month(s)':
                            date_reminder = subscription.sh_end_date + \
                                relativedelta(months=(reminder.sh_reminder))
                        if date_reminder == fields.Date.today():
                            if reminder.sh_mail_template_id:
                                if reminder.sh_reminder > 0 and subscription.state in ['expire']:
                                    reminder.sh_mail_template_id.sudo().send_mail(subscription.id, force_send=True)
                                elif reminder.sh_reminder < 0 and subscription.state == 'in_progress':
                                    reminder.sh_mail_template_id.sudo().send_mail(subscription.id, force_send=True)
                                elif reminder.sh_reminder == 0 and subscription.state in ['in_progress', 'expire', 'renewed']:
                                    reminder.sh_mail_template_id.sudo().send_mail(subscription.id, force_send=True)
                            else:
                                raise UserError(
                                    'Please Enter Email Template in Reminder.')
