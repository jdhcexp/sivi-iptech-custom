# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.


from odoo import fields, models, api
from odoo.exceptions import UserError


class SubscriptionPlan(models.Model):

    _name = 'sh.subscription.plan'
    _description = 'Subscription Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_default_currency_id(self):
        return self.env.company.currency_id.id
    active = fields.Boolean(string="Active", default=True)
    name = fields.Char(string='Plan Name', required=True)
    company_id = fields.Many2one(
        'res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    # Plan Details
    sh_duration = fields.Integer(string='Duration', required=True)
    sh_unit = fields.Selection([("day", "Day(s)"), ("week", "Week(s)"), (
        "month", "Month(s)"), ("year", "Year(s)")], required=True,default='day')
    sh_plan_price = fields.Float(string='Price', required=True)
    currency_id = fields.Many2one(
        comodel_name="res.currency", string="Currency", default=_get_default_currency_id)
    sh_company_id = fields.Many2one(
        comodel_name="res.company", string="Company", readonly=True, default=lambda self: self.env.company,)
    sh_never_expire = fields.Boolean(string="Never Expire")
    sh_no_of_billing_cycle = fields.Integer(
        string='No of billing cycle', required=True)
    sh_start_immediately = fields.Boolean(string="Start Immediately")
    sh_billing_day_of_the_month = fields.Integer(
        string='Billing day of the month', default=1)
    sh_trial = fields.Boolean(string="Plan has trial period")
    sh_trial_duration = fields.Integer(string='Trial duration')
    sh_trial_unit = fields.Selection([("day", "Day(s)"), ("week", "Week(s)"), (
        "month", "Month(s)"), ("year", "Year(s)")], string="Unit")
    sh_free_trial_for_current_month = fields.Boolean(
        string="Free trial for current month")
    sh_is_close_by_customer = fields.Boolean(string="Is Closable By Customer")
    # Product details
    sh_override_product = fields.Boolean(string="Override Product Price")
    sh_description = fields.Text(string="Description")

    sh_subscription_count = fields.Integer(
        string="Subscription", compute='compute_view_subscription', default=0)
    sh_product_count = fields.Integer(
        string="Product", compute='compute_view_product', default=0)
    sh_reminder = fields.Many2many(
        comodel_name="sh.reminder.template", string="Reminder")
    color = fields.Integer('Color Index', default=0)

    @api.onchange('sh_unit')
    def _onchange_sh_unit(self):
        if self.sh_unit != 'month':
            self.sh_free_trial_for_current_month = False

    @api.constrains('sh_billing_day_of_the_month')
    def _check_sh_free_trial_for_current_month(self):
        self.ensure_one()
        if self.sh_free_trial_for_current_month:
            if self.sh_billing_day_of_the_month < 1:
                raise UserError("You can not select less than 1")

    @api.onchange('sh_plan_price')
    def _onchange_sh_plan_price(self):
        if self.sh_plan_price:
            products = self.env['product.product'].search(
                [('sh_subscription_plan_id', '=', (self._origin).id)])
            for product in products:
                product.lst_price = self.sh_plan_price

    @api.onchange('sh_start_immediately')
    def _onchange_sh_start_immediately(self):
        if self.sh_start_immediately == True:
            self.sh_trial = False
            self.sh_free_trial_for_current_month = False

    @api.onchange('sh_free_trial_for_current_month')
    def _onchange_sh_free_trial_for_current_month(self):
        if self.sh_free_trial_for_current_month == True:
            self.sh_trial = False
            self.sh_start_immediately = False

    @api.onchange('sh_trial')
    def _onchange_sh_trial(self):
        if self.sh_trial == True:
            self.sh_start_immediately = False
            self.sh_free_trial_for_current_month = False

    def compute_view_subscription(self):
        for rec in self:
            rec.sh_subscription_count = self.env['sh.subscription.subscription'].search_count(
                [('sh_subscription_plan_id', '=', rec.id)])

    def action_view_subscription(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "sh_subscription.sh_subscription_subscription_action")
        subscription = self.env['sh.subscription.subscription'].search(
            [('sh_subscription_plan_id', '=', self.id)])
        if len(subscription) > 1:
            action['domain'] = [('id', '=', subscription.ids)]
        elif subscription:
            form_view = [
                (self.env.ref('sh_subscription.sh_subscription_subscription_form_view').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + \
                    [(state, view)
                     for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = subscription.id
        action['context'] = {
            'active_test': False,
            'create': False,
        }
        return action

    def compute_view_product(self):
        for rec in self:
            rec.sh_product_count = self.env['product.product'].search_count(
                [('sh_subscription_plan_id', '=', rec.id)])

    def action_view_product(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "product.product_variant_action")
        product = self.env['product.product'].search(
            [('sh_subscription_plan_id', '=', self.id)])
        if len(product) > 1:
            action['domain'] = [('id', '=', product.ids)]
        elif product:
            form_view = [
                (self.env.ref('product.product_normal_form_view').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + \
                    [(state, view)
                     for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = product.id
        action['context'] = {
            'active_test': False,
            'create': False,
        }
        return action
