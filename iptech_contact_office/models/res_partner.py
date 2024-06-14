import odoo.exceptions
from odoo import fields, models, api
from datetime import datetime, timedelta

class ResPartner(models.Model):
    _inherit = "res.partner"

    type = fields.Selection(
        [('contact', 'Contact'),
         ('invoice', 'Invoice Address'),
         ('delivery', 'Delivery Address'),
         ('private', 'Private Address'),
         ('other', 'Other Address'),
         ('office', 'Sucursal')
         ], string='Address Type',
        default='contact',
        help="- Contact: Use this to organize the contact details of employees of a given company (e.g. CEO, CFO, ...).\n"
             "- Invoice Address : Preferred address for all invoices. Selected by default when you invoice an order that belongs to this company.\n"
             "- Delivery Address : Preferred address for all deliveries. Selected by default when you deliver an order that belongs to this company.\n"
             "- Private: Private addresses are only visible by authorized users and contain sensitive data (employee home addresses, ...).\n"
             "- Other: Other address for the company (e.g. subsidiary, ...)")

    @api.onchange("type")
    def _get_contact_names(self):
        companyId = self.parent_id.id.origin
        print(companyId)
        officeNumber = 0;
        contact = self.env['res.partner'].search([('id', '=', companyId)])
        print(contact)
        for child in contact.child_ids:
            if child.type == "office":
                childnumber = int(child.name.replace("SUC",""))
                print(childnumber)
                if childnumber > officeNumber:
                    officeNumber = childnumber
        officeNumber = officeNumber+1
        if self.type == "office":
            self.name = f"SUC{officeNumber:03}"

