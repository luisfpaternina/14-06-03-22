
from odoo import api, fields, models, exceptions, tools, _
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)

class TravelSale(models.Model):
    _inherit = 'travel_sale'
