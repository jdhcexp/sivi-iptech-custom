
from odoo import api, fields, models

class Project(models.Model):

    _inherit = ["project.project"]

    delivery_date=fields.Date(string="Fecha de Entrega")
