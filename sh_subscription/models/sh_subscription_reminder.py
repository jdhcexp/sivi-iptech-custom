# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models, api

class SubscriptionReminder(models.Model):
    _name = "sh.reminder.template"
    _description = "Subscription Reminder"

    name = fields.Char(string="Name", readonly=True)
    sh_reminder = fields.Integer(
        string="Reminder")
    sh_reminder_unit = fields.Selection([('days(s)', 'Day(s)'), (
        'week(s)', 'Week(s)'), ('month(s)', 'Month(s)')], string="Reminder Unit", default='days(s)',required=True)
    company_id = fields.Many2one(
        'res.company', 'Company', default=lambda self: self.env.company)
    sh_mail_template_id = fields.Many2one(
        'mail.template', string='Mail Template')

    def name_get(self):
        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        self.browse(self.ids).read(['sh_reminder', 'sh_reminder_unit'])
        return [(alarm.id, '%s%s' % (str(alarm.sh_reminder)+' ',str(alarm.sh_reminder_unit)))
                for alarm in self]

    @api.onchange('sh_reminder','sh_reminder_unit')
    def _onchange_name(self):
        for rec in self:
            rec.name = rec.name_get()[0][1]
