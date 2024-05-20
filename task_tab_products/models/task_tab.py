from odoo import fields, models, api

class TaskTab(models.Model):
    _name = "task.tab"
    _description = "task tab"

    name = fields.Char(string="tabname")

    task_id = fields.Many2one(
        comodel_name='project.task',
        string="Task Reference",
        required=True, ondelete='cascade', index=True, copy=False)

    tab_line = fields.One2many(
        comodel_name='tab.line',
        inverse_name='tab_id',
        string= 'tab lines',
        copy=True, auto_join=True
    )
