# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, tools


class SubscriptionReport(models.Model):
    _name = "sh.subscription.report"
    _auto = False
    _rec_name = 'id'
    _order = 'id desc'

    sh_month_price = fields.Float(string="Monthly Recurring Revenue")
    sh_partner_id = fields.Many2one(
        comodel_name="res.partner", string="Customer Name")
    sh_subscription_plan_id = fields.Many2one(
        comodel_name="sh.subscription.plan", string="Subscription Plan")
    sh_sale_person = fields.Many2one(
        comodel_name="res.users", string="Sales Person")

    def _select(self):
        return '''
        s."id" as id,
        s."sh_partner_id" as sh_partner_id,
        sum(
            coalesce(s."sh_plan_price" / nullif(s."sh_plan_price", 0), 0)
            *  s."sh_recurring_monthly"
        ) as sh_month_price,
        s."sh_subscription_plan_id" as sh_subscription_plan_id,
        s."create_uid" as sh_sale_person
        '''

    def _from(self):
        return '''sh_subscription_subscription AS s '''

    def _where(self):
        return 's.id > 0'

    def _group_by(self):
        return '''s.id,s."sh_partner_id", s."sh_subscription_plan_id",s."create_uid"'''

    def _query(self):
        res = '(SELECT %s FROM %s WHERE  %s GROUP BY %s)' % (
            self._select(),
            self._from(),
            self._where(),
            self._group_by()
        )
        return res

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""CREATE OR REPLACE VIEW %s AS %s""" %
                         (self._table, self._query()))
