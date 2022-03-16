
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
    # estos son lo que debes hacer igual un campo para relacionar y uno para el domain
    line_ids = fields.Many2many('pickup.order.line', 'pickup_line_rel', 'pickup_id', 'line_id', string='Articles with problems')
    domain_line_ids = fields.Many2many('pickup.order.line', 'pickup_line_domain_rel', 'pickup_id', 'line_id', string='Domain Articles')
    route_id = fields.Many2one(related='partner_id.route_id', string='Router')
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
    claim_id = fields.Many2one('crm.claim', string='Claim')

    # Inventario
    company_id = fields.Many2one('res.company', 'Company',
        required=True,
        index=True,
        states={'done': [('readonly', True)],'received': [('readonly', True)],'cancel': [('readonly', True)]},
        default=lambda 
        self: self.env.user.company_id.id)
    warehouse_id = fields.Many2one('stock.warehouse', 
        string='Warehouse',
        required=True, 
        readonly=True,
        states={'done': [('readonly', True)],'received': [('readonly', True)],'cancel': [('readonly', True)]},
        default=_default_warehouse_id)
    picking_count = fields.Integer(compute='_compute_picking',
        string='Receptions',
        default=0)
    picking_ids = fields.Many2many('stock.picking',
        compute='_compute_picking',
        string='Receptions',
        copy=False)
    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To',
        states={'done': [('readonly', True)],'received': [('readonly', True)],'cancel': [('readonly', True)]}, 
        required=True,
        default=_default_picking_type,
        help="This will determine picking type of incoming shipment")
    group_id = fields.Many2one('procurement.group', 
        string="Procurement Group", 
        copy=False)

    #Viaje
    travel_id = fields.Many2one('travel.sale', 
        string='Travel', 
        copy=False)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.sale_order_id = False


class PickupOrderLine(models.Model):
    _name = 'pickup_order.line'

    order_id = fields.Many2one('pickup.order', string='Pickup Order', ondelete='cascade')
    semifinished_id = fields.Many2one('semifinished.product.label', string='Semifinished', required=False)
    package_id = fields.Many2one('package.product.label', string='Package', required=False)
    label = fields.Char('Label', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=False)
    length = fields.Float(readonly="1")
    height = fields.Float(readonly="1")
    width = fields.Float(readonly="1")




class PickupOrderManufacturing(models.Model):
    _name = 'pickup_order.manufacturing'

    claim_id = fields.Many2one('crm.claim', string='Claim', ondelete='cascade')
    semifinished_id = fields.Many2one('semifinished.product.label', string='Semifinished', required=False)
    package_id = fields.Many2one('package.product.label', string='Package', required=False)
    label = fields.Char('Label', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=False) 
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure',default=1.0)
    product_uom_id = fields.Many2one('product.uom', 'Product Unit of Measure')
    length = fields.Float(readonly="1")
    height = fields.Float(readonly="1")
    width = fields.Float(readonly="1")
    production_id = fields.Many2one('mrp.production', string='Production', compute='_compute_production_id')

