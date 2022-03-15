# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ManufacturingPickupOrderWizard(models.TransientModel):
    _name = 'manufacturing.pickup.order.wizard'

    claim_id = fields.Many2one('crm.claim', string='Claim', default=_get_default_claim_id)
    order_id = fields.Many2one('sale.order', string='Sale order', default=_get_default_order_id)
    line_ids = fields.Many2many('manufacturing.pickup.order.aux', 'manufacturing_order_wizard_aux_rel', 'wizard_id',
                                'line_id', string='Articles to manufacturing')

 
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


