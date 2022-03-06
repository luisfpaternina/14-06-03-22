from odoo import api, fields, models, exceptions, tools, _

class PickupOrderLine(models.Model):
    _name = 'Pickup_Order_Line'
    _description = 'PickupOrderLine'

    name = fields.Char(
        String="Name",
        tracking=True)
    active = fields.Boolean(
        string="Active",
        default=True,
        tracking=True)
