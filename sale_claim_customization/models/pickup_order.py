
from odoo import api, fields, models, exceptions, tools, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import logging
_logger = logging.getLogger(__name__)


class PickupOrder(models.Model):
    _name = 'pickup_order'
    _description = 'Pickup Orders'


class PickupOrderLine(models.Model):
    _name = 'pickup_order.line'

   

class PickupOrderManufacturing(models.Model):
    _name = 'pickup_order.manufacturing'

