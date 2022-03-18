
from odoo import api, fields, models, exceptions, tools, _
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

class TravelSale(models.Model):
    _inherit = 'travel.sale'

    pickup_ids = fields.One2many('pickup.order', 'travel_id', string='Pickup Orders')
    line_pickup_order_ids = fields.Many2many('pickup.order.line', related='pickup_ids.line_ids',
                                             string="Articles with problems")



