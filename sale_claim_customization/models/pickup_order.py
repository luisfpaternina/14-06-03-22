
from odoo import api, fields, models, exceptions, tools, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import logging
_logger = logging.getLogger(__name__)


class PickupOrder(models.Model):
    _name = 'pickup_order'
    _description = 'Pickup Orders'

    def _compute_picking(self):
        for order in self:
            pickings = self.env['stock.picking'].search([('pickup_order_id', '=', order.id)])
            order.picking_ids = pickings
            order.picking_count = len(pickings)

    @api.model
    def _default_picking_type(self):
        type_obj = self.env['stock.picking.type']
        company_id = self.env.context.get('company_id') or self.env.user.company_id.id
        types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)])
        if not types:
            types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id', '=', False)])
        return types[:1]
    
    @api.model
    def _default_warehouse_id(self):
        company = self.env.user.company_id.id
        warehouse_ids = self.env['stock.warehouse'].search([('company_id', '=', company)], limit=1)
        return warehouse_ids
    
    name = fields.Char('Name', required=True, default=_('Draft Pickup Order'))
    emission_date = fields.Date(string='Emission Date', required=True, default=fields.Date.context_today)
    expected_date = fields.Date(string='Expected date', default=fields.Date.context_today)
    sale_order_id = fields.Many2one('sale.order', string='Sale order')
    partner_id = fields.Many2one("res.partner", "Customer", required=True, domain=[("customer", "=", True)])
    type = fields.Selection([
        ('partial', 'Partial'),
        ('total', 'Total')], string='Type',
        copy=False, default='total')
    make_payment = fields.Boolean('Make Payment', default=False)
    amount = fields.Float("Amount", default=0.0)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('received', 'Received'),
        ('cancel', 'Cancel')], string='State',
        copy=False, default='draft')

    # Inventario

    picking_count = fields.Integer(string='Receptions', default=0)


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
    
