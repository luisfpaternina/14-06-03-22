# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ManufacturingPickupOrderWizard(models.TransientModel):
    _name = 'manufacturing.pickup.order.wizard'

    @api.model
    def _get_default_order_id(self):
        if self._context.get('order_id', False):
            order_id = self._context['order_id']
        else:
            order_id = self.env['sale.order']
        return order_id

    @api.model
    def _get_default_claim_id(self):
        if self._context.get('claim_id', False):
            claim_id = self._context['claim_id']
        else:
            claim_id = self.env['crm.claim']
        return claim_id

    claim_id = fields.Many2one('crm.claim', string='Claim', default=_get_default_claim_id)
    order_id = fields.Many2one('sale.order', string='Sale order', default=_get_default_order_id)
    line_ids = fields.Many2many('manufacturing.pickup.order.aux', 'manufacturing_order_wizard_aux_rel', 'wizard_id',
                                'line_id', string='Articles to manufacturing')

    @api.onchange('order_id')
    def onchange_sale_order_type(self):
        self.env['manufacturing.pickup.order.aux'].search([]).unlink()
        self.line_ids = [(5, 0, 0)]
        if self.order_id:
            self.generate_aux_wizard(self.order_id)
        elif self._context.get('order_id', False):
            self.order_id = self._context.get('order_id', False)
            self.claim_id = self._context.get('claim_id', False)
            if self.order_id:
                self.generate_aux_wizard(self.order_id)

    def generate_aux_wizard(self, order_id):
        semifinished_label = self.env['semifinished.product.label'].search([('sale_id', '=', order_id.id)])
        for label in semifinished_label:
            self.env['manufacturing.pickup.order.aux'].create({
                # 'order_id': self.id,
                'semifinished_id': label.id,
                'label': label.code,
                'product_id': label.product_id.id,
                'product_qty': label.production_id.product_qty,
                'product_uom_id': label.production_id.product_uom_id.id
            })
        package_label = self.env['package.product.label'].search([('sale_id', '=', order_id.id)])
        for label in package_label:
            self.env['manufacturing.pickup.order.aux'].create({
                # 'order_id': self.id,
                'package_id': label.id,
                'label': label.code,
                'product_id': label.product_id.id,
                'product_qty': label.production_id.product_qty,
                'product_uom_id': label.production_id.product_uom_id.id
            })

    def confirm(self):
        manufacturing_obj = self.env['pickup.order.manufacturing']
        if not self.line_ids:
            raise UserError(
                _('You must select the products to be manufactured.'))
        else:
            for line in self.line_ids:
                manufacturing_obj.create({
                    'claim_id': self.claim_id.id,
                    'product_id': line.product_id.id,
                    'product_qty': line.product_qty,
                    'product_uom_id': line.product_uom_id.id,
                    'label': line.label,
                    'package_id': line.package_id and line.package_id.id or False,
                    'semifinished_id': line.semifinished_id and line.semifinished_id.id or False,
                })
        self.claim_id.action_manufacturing()
        return {'type': 'ir.actions.act_window_close'}

class PickupOrderLine(models.TransientModel):
    _name = 'manufacturing.pickup.order.aux'

    # wizard_id = fields.Many2one('semifinished.product.label', string='Semifinished', required=False)
    semifinished_id = fields.Many2one('semifinished.product.label', string='Semifinished', required=False)
    package_id = fields.Many2one('package.product.label', string='Package', required=False)
    label = fields.Char('Label', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=False)
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure',
                                   default=1.0)
    product_uom_id = fields.Many2one('product.uom', string='Product Unit of Measure')
    length = fields.Float(related='product_id.length', readonly="1")
    height = fields.Float(related='product_id.height', readonly="1")
    width = fields.Float(related='product_id.width', readonly="1")


