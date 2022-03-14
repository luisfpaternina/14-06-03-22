# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock_picking'


    #pickup_order_id = fields.Many2one('pickup.order', string="Pickup Orders", readonly=True, copy=False)