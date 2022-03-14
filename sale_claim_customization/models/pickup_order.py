
from odoo import api, fields, models, exceptions, tools, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import logging
_logger = logging.getLogger(__name__)


class PickupOrder(models.Model):
    _name = 'pickup_order'
    _description = 'Pickup Orders'

    name = fields.Char('Name', required=True, default=_('Draft Pickup Order'))
    emission_date = fields.Date(string='Emission Date', required=True, default=fields.Date.context_today)
    expected_date = fields.Date(string='Expected date', default=fields.Date.context_today)




class PickupOrderLine(models.Model):
    _name = 'pickup_order.line'

    label = fields.Char('Label', required=True)
    length = fields.Float(readonly="1")
    height = fields.Float(readonly="1")
    width = fields.Float(readonly="1")




class PickupOrderManufacturing(models.Model):
    _name = 'pickup_order.manufacturing'

    product_id = fields.Many2one('product.product', string='Product', required=False) 
    label = fields.Char('Label', required=True)
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure',
                               default=1.0)
    length = fields.Float(readonly="1")
    height = fields.Float(readonly="1")
    width = fields.Float(readonly="1")
    
