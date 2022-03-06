# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # def _compute_line_pickup_order_ids(self):
    #     for picking in self:
    #         if picking.pickup_order_id:
    #             line_pickup_order_ids = picking.pickup_order_id.line_ids
    #             picking.picking_ids = line_pickup_order_ids
    #
    # line_pickup_order_ids = fields.Many2many('pickup.order.line',  compute='_compute_line_pickup_order_ids',
    #     string="Articles with problems")

   #and# pickup_order_id = fields.Many2one('pickup.order', string="Pickup Orders", readonly=True, copy=False)
   #and# line_pickup_order_ids = fields.Many2many('pickup.order.line', related='pickup_order_id.line_ids',
        string="Articles with problems"

    # @api.model
    # def _prepare_values_extra_move(self, op, product, remaining_qty):
    #     res = super(StockPicking, self)._prepare_values_extra_move(op, product, remaining_qty)
    #     for m in op.linked_move_operation_ids:
    #         if m.move_id.purchase_line_id and m.move_id.product_id == product:
    #             res['purchase_line_id'] = m.move_id.purchase_line_id.id
    #             break
    #     return res
"""
    @api.model
    def _create_backorder(self, backorder_moves=[]):
        res = super(StockPicking, self)._create_backorder(backorder_moves)
        for picking in self:
            if picking.picking_type_id.code == 'incoming' and picking.pickup_order_id:
                for backorder in self.search([('backorder_id', '=', picking.id)]):
                    backorder.message_post_with_view('mail.message_origin_link',
                        values={'self': backorder, 'origin': backorder.pickup_order_id},
                        subtype_id=self.env.ref('mail.mt_note').id)
        return res

    def action_done(self):
        for rec in self:
            if rec.pickup_order_id:
                move = rec.mapped('move_lines')
                move.write({
                    'group_id': rec.group_id.id,
                })
        res = super(StockPicking, self).action_done()
        for rec in self:
            if rec.pickup_order_id and not rec.pickup_order_id.mapped('picking_ids').filtered(lambda x: x.state not in ('done', 'cancel')):
                rec.pickup_order_id.action_received()
        return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    pickup_order_id = fields.Many2one('pickup.order', related='picking_id.pickup_order_id',
        string="Pickup Orders", readonly=True, copy=False)

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    lot_pickup_order_id = fields.Many2one('stock.location', 'Location Pickup Orders', domain=[('usage', '=', 'internal')],
                                   required=True)

    @api.model
    def create(self, vals):
        sub_locations = {
            'lot_pickup_order_id': {'name': _('Pickup Orders'), 'active': True, 'usage': 'internal'}
        }
        for field_name, values in sub_locations.items():
            values[''] = vals['view_location_id']
            if vals.get('company_id'):
                values['company_id'] = vals.get('company_id')
            vals[field_name] = self.env['stock.location'].with_context(active_test=False).create(values).id

        # actually create WH
        warehouse = super(StockWarehouse, self).create(vals)
        return warehouse

class StockMove(models.Model):
    _inherit = 'stock.move'

    def action_done(self):
        for rec in self:
            if rec.picking_id and rec.picking_id.pickup_order_id:
                move = rec.picking_id.mapped('move_lines').filtered(lambda x: not x.group_id)
                move.write({
                    'group_id': rec.group_id.id,
                })
        res = super(StockMove, self).action_done()
        for rec in self:
            if rec.picking_id and rec.picking_id.pickup_order_id and not rec.picking_id.pickup_order_id.mapped('picking_ids').filtered(
                    lambda x: x.state not in ('done', 'cancel')):
                rec.picking_id.pickup_order_id.action_received()
        return res

"""