from odoo import api, fields, models, exceptions, tools, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import logging

class mrproute(models.Model):
    _name = 'mrp_route'
    _description = 'Route'

    name = fields.Char(
        String="Name",
        tracking=True)
