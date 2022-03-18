
from odoo import api, fields, models, exceptions, tools, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT

import logging

_logger = logging.getLogger(__name__)

class PickupOrder(models.Model):
    _name = 'pickup.order'
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
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, states={'done': [('readonly', True)],
                                                                                  'received': [('readonly', True)],
                                                                                  'cancel': [('readonly', True)]},
                                 default=lambda self: self.env.user.company_id.id)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse',required=True, readonly=True,
                                   states={'done': [('readonly', True)],
                                           'received': [('readonly', True)],'cancel': [('readonly', True)]},
                                   default=_default_warehouse_id)
    picking_count = fields.Integer(compute='_compute_picking', string='Receptions', default=0)
    picking_ids = fields.Many2many('stock.picking', compute='_compute_picking', string='Receptions', copy=False)
    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To', states={'done': [('readonly', True)],
                                                                                  'received': [('readonly', True)],
                                                                                  'cancel': [('readonly', True)]}, required=True,
                                      default=_default_picking_type,
                                      help="This will determine picking type of incoming shipment")
    group_id = fields.Many2one('procurement.group', string="Procurement Group", copy=False)

    #Viaje
    travel_id = fields.Many2one('travel.sale', string='Travel', copy=False)



    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.sale_order_id = False

    #Solo el onchange de sale_order porque no hay type
    @api.onchange('sale_order_id', 'type')
    def onchange_sale_order_type(self):
        if self.sale_order_id and self.type:
            self.line_ids = [(5, 0, 0)]
            line_ids = self.env['pickup.order.line']

            semifinished_label = self.env['semifinished.product.label'].search([('sale_id', '=', self.sale_order_id.id)])
            for label in semifinished_label:
                line_ids += self.env['pickup.order.line'].create({
                    # 'order_id': self.id,
                    'semifinished_id': label.id,
                    'label': label.code,
                    'product_id': label.product_id.id
                })
            package_label = self.env['package.product.label'].search([('sale_id', '=', self.sale_order_id.id)])
            for label in package_label:
                line_ids += self.env['pickup.order.line'].create({
                    # 'order_id': self.id,
                    'package_id': label.id,
                    'label': label.code,
                    'product_id': label.product_id.id
                })
            if self.type == 'total':
                self.line_ids = [(6, False, line_ids.ids)]
            self.domain_line_ids = [(4, line.id, False) for line in line_ids]

        else:
            self.line_ids = [(5, 0, 0)]

    def action_done(self):
        self.state = 'done'
        self.name = self.env['ir.sequence'].next_by_code('pickup.order.seq')
        vals = self._prepare_procurement_group()
        self.group_id = self.env["procurement.group"].create(vals)
        self._create_picking()
        return True

    def action_received(self):
        if not self.travel_id:
            raise UserError(
                _('You cannot receive a pickup order without being assigned to a trip.'))
        self.state = 'received'
        return True

    def action_cancel(self):
        self.state = 'cancel'
        return True

    def _get_destination_location(self):
        self.ensure_one()
        if self.warehouse_id:
            return self.warehouse_id.lot_pickup_order_id.id
        return self.picking_type_id.default_location_dest_id.id

    @api.model
    def _prepare_picking(self):
        if not self.group_id:
            self.group_id = self.group_id.create({
                'name': self.name,
                'partner_id': self.partner_id.id
            })
        if not self.partner_id.property_stock_supplier.id:
            raise UserError(_("You must set a Vendor Location for this partner %s") % self.partner_id.name)
        return {
            'picking_type_id': self.picking_type_id.id,
            'partner_id': self.partner_id.id,
            'date': self.expected_date,
            'min_date': self.expected_date,
            'origin': self.name,
            'location_dest_id': self._get_destination_location(),
            'location_id': self.partner_id.property_stock_supplier.id,
            'company_id': self.company_id.id,
            'pickup_order_id': self.id,
            'group_id': self.group_id.id,
        }

    def _create_picking(self):
        StockPicking = self.env['stock.picking']
        for order in self:
            res = order._prepare_picking()
            picking = StockPicking.create(res)
            picking.message_post_with_view('mail.message_origin_link',
                                           values={'self': picking, 'origin': order},
                                           subtype_id=self.env.ref('mail.mt_note').id)
        return True

    def action_view_picking(self):
        action = self.env.ref('stock.action_picking_tree')
        result = action.read()[0]

        result.pop('id', None)
        result['context'] = {}
        pick_ids = sum([order.picking_ids.ids for order in self], [])

        if len(pick_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, pick_ids)) + "])]"
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids and pick_ids[0] or False
        return result

    def action_assign_travel(self):
        routing = self.mapped('partner_id.route_id')
        if len(routing) > 1:
            raise UserError(
                _('You can not select pickup orders that are not associated with the same route.'))
        for rec in self:
            if not rec.partner_id.route_id:
                raise UserError(
                    _('There are orders that your customers are not associated with any route.'))
        if self.filtered(lambda x: x.state != 'done'):
            raise UserError(
                _('Already existing pickup orders must have been confirmed.'))
        if self.filtered(lambda x: x.travel_id):
            raise UserError(
                _('There are already orders associated with a trip.'))
        ctx = self._context.copy()
        ctx.update({'default_pickup_ids': self.ids})
        action_rec = self.env['ir.model.data'].xmlid_to_object(
            'sale_claim_customization.action_assign_pickup_travel_wizard_form')
        action = action_rec.read([])[0]
        action['context'] = ctx
        # action['domain'] = [('journal_id', '=', self.id),
        #                     ('payment_type', '=', payment_type)]
        return action

    def _prepare_procurement_group(self):
        return {'name': self.name}

    @api.model
    def create(self, vals):
        if vals.get('line_ids', False):
            lines_val = []
            for line in vals.get('line_ids', False):
                if line[0] == 1:
                    line[0] = 4
                    line[2] = False
                lines_val.append(line)
            vals['line_ids'] = lines_val
        return super(PickupOrder, self).create(vals)

    def write(self, vals):
        if vals.get('line_ids', False):
            lines_val = []
            for line in vals.get('line_ids', False):
                if line[0] == 1:
                    line[0] = 4
                    line[2] = False
                lines_val.append(line)
            vals['line_ids'] = lines_val
        return super(PickupOrder, self).write(vals)


class PickupOrderLine(models.Model):
    _name = 'pickup.order.line'

    # order_id = fields.Many2one('pickup.order', string='Pickup Order', ondelete='cascade')
    semifinished_id = fields.Many2one('semifinished.product.label', string='Semifinished', required=False)
    package_id = fields.Many2one('package.product.label', string='Package', required=False)
    label = fields.Char('Label', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=False)
    length = fields.Float(related='product_id.length', readonly="1")
    height = fields.Float(related='product_id.height', readonly="1")
    width = fields.Float(related='product_id.width', readonly="1")

class PickupOrderManufacturing(models.Model):
    _name = 'pickup.order.manufacturing'

    claim_id = fields.Many2one('crm.claim', string='Claim', ondelete='cascade')
    semifinished_id = fields.Many2one('semifinished.product.label', string='Semifinished', required=False)
    package_id = fields.Many2one('package.product.label', string='Package', required=False)
    label = fields.Char('Label', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=False)
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure',
                               default=1.0)
    product_uom_id = fields.Many2one(
        'product.uom', 'Product Unit of Measure')
    length = fields.Float(related='product_id.length', readonly="1")
    height = fields.Float(related='product_id.height', readonly="1")
    width = fields.Float(related='product_id.width', readonly="1")
    production_id = fields.Many2one('mrp.production', string='Production', compute='_compute_production_id')
    state_production = fields.Selection(related='production_id.state', readonly="1")

    def _compute_production_id(self):
        procurment_order = self.env['procurement.order'].search([('pickup_manufacturing_id', '=', self.id)], limit=1)
        if procurment_order:
            self.production_id = procurment_order.production_id

    def _prepare_order_line_procurement(self, group_id=False):
        self.ensure_one()
        rule_id = self.env['procurement.rule'].search([('action', '=', 'manufacture'), ('warehouse_id', '=', self.claim_id.warehouse_id.id)])
        location_id = self.env.ref('stock.location_production')
        return {
            'name': self.product_id.display_name,
            'origin': self.claim_id.name,
            'date_planned': datetime.now().strftime('%Y-%m-%d'),
            'product_id': self.product_id.id,
            'product_qty': self.product_qty,
            'product_uom': self.product_uom_id.id,
            'company_id': self.claim_id.company_id.id,
            'group_id': group_id,
            'rule_id': rule_id and rule_id[0].id or False,
            'location_id': rule_id and location_id[0].id or False,
            'pickup_manufacturing_id': self.id
        }

    def _action_procurement_create(self):
        """
        Create procurements based on quantity ordered. If the quantity is increased, new
        procurements are created. If the quantity is decreased, no automated action is taken.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        new_procs = self.env['procurement.order']  # Empty recordset
        for line in self:
            # if line.pickup_id.state != 'done':
            #     continue

            if not line.claim_id.group_id:
                vals = line.claim_id._prepare_procurement_group()
                line.claim_id.group_id = self.env["procurement.group"].create(vals)

            vals = line._prepare_order_line_procurement(group_id=line.claim_id.group_id.id)
            new_proc = self.env["procurement.order"].with_context(procurement_autorun_defer=True).create(vals)
            new_proc.message_post_with_view('mail.message_origin_link',
                                            values={'self': new_proc, 'origin': line.claim_id},
                                            subtype_id=self.env.ref('mail.mt_note').id)
            new_procs += new_proc
        new_procs.run()
        return new_procs




