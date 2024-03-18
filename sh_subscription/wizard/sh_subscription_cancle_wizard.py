# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models


class SubscriptionWizard(models.TransientModel):
    _name = 'sh.subscription.cancle.wizard'
    _description = 'Subscription Cancle/close Wizard'

    sh_subscription_reason_id = fields.Many2one(
        comodel_name="sh.subscription.reason", string="Reason", required=True)
    sh_description = fields.Text(string="Description")

    def sh_subscription_cancle_now(self):
        res_ids = self._context.get('active_ids')
        subscription = self.env['sh.subscription.subscription'].browse(res_ids)
        subscription.sh_renew_stage = 'time_to_renew'
        if subscription.state == 'draft':
            subscription.state = 'cancel'
        if subscription.state == 'in_progress':
            subscription.state = 'close'
        if self.sh_description:
            subscription.sh_reason = self.sh_subscription_reason_id.name+' '+self.sh_description
            subscription._sh_send_subscription_email(False)
        else:
            subscription.sh_reason = self.sh_subscription_reason_id.name
            subscription._sh_send_subscription_email(False)
