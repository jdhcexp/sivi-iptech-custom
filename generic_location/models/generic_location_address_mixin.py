from odoo import models, fields


# TODO: Merge into 'generic.location.mixin'
class GenericLocationAddressMixin(models.AbstractModel):
    _name = 'generic.location.address.mixin'
    _inherit = 'generic.location.mixin'
    _description = 'Generic Location Address Mixin'

    country_id = fields.Many2one(related='location_id.country_id')
    state_id = fields.Many2one(related='location_id.state_id')
    city = fields.Char(related='location_id.city')
    zip = fields.Char(related='location_id.zip')
    street = fields.Char(related='location_id.street')
    street2 = fields.Char(related='location_id.street2')
