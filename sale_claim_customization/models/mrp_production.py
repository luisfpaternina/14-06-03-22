
from odoo import api, fields, models, exceptions, _
import math
import logging
_logger = logging.getLogger(__name__)

class MrpProduction(models.Model):
    _inherit = 'mrp_production'
