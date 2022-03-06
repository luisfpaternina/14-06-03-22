from odoo import api, fields, models, exceptions, tools, _

class PickupOrderLine(models.Model):
    _name = 'pickup_order.line'
    _description = 'PickupOrderLine'

    name = fields.Char(
        String="Name",
        tracking=True)
    active = fields.Boolean(
        string="Active",
        default=True,
        tracking=True)
