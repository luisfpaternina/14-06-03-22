# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement_order'

    pickup_manufacturing_id = fields.Many2one('pickup.order.manufacturing', string='Pickup manufacturing')