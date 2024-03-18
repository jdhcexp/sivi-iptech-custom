import odoo.exceptions
from odoo import fields, models, api
from datetime import datetime, timedelta

class AccountMove(models.Model):
    _inherit = "account.move"

