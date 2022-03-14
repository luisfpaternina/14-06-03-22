from odoo import api, fields, models, exceptions, tools, _
import logging
_logger = logging.getLogger(__name__)


class CrmClaim(models.Model):
    _inherit = "crm.claim"
    
    @api.model
    def _default_warehouse_id(self):
        company = self.env.user.company_id.id
        warehouse_ids = self.env['stock.warehouse'].search([('company_id', '=', company)], limit=1)
        return warehouse_ids

    order_id = fields.Many2one(comodel_name='sale.order', string='Sales Order')
    reference = fields.Char(string="Ntra Reference", store=True)
    reference_client = fields.Char(string="Client Reference", store=True)
    motive = fields.Many2one(comodel_name='incidence.cause',string='Incidence Cause')
    solution = fields.Boolean('Solution')
    line_ids = fields.Many2many('claim.line', 'claim_line_rel', 'claim_id', 'line_id', string='Articles with problems')
    domain_line_ids = fields.Many2many('claim.line', 'claim_line_domain_rel', 'claim_id', 'line_id', string='Domain Articles')
    date = fields.Date(string='Claim Date', index=True, default=fields.Datetime.now)
    pickup_id = fields.Many2one('pickup.order', string='Pickup Order',compute='_compute_pickup_id')
    state_pickup = fields.Selection([
    ('draft', 'Draft'),
    ('done', 'Done'),
    ('received', 'Received'),
    ('cancel', 'Cancel')], string='State Pickup Order',compute='_compute_pickup_id')
  
    # Fabricacion
    is_manufacturing = fields.Boolean('Manufacturing', default=False)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', required=True,
                                   default=_default_warehouse_id)
    group_id = fields.Many2one('procurement.group', string="Procurement Group", copy=False)

    def _compute_pickup_id(self):
        pickup_id = self.env['pickup.order'].search([('claim_id', '=', self.id)], limit=1)
        if pickup_id:
            self.pickup_id = pickup_id.id
            self.state_pickup = pickup_id.state

    @api.onchange('order_id')
    def onchange_sale_order(self):
        if self.order_id:
            self.line_ids = [(5, 0, 0)]
            line_ids = self.env['claim.line']

            semifinished_label = self.env['semifinished.product.label'].search(
                [('sale_id', '=', self.order_id.id)])
            for label in semifinished_label:
                line_ids += self.env['claim.line'].create({
                    'semifinished_id': label.id,
                    'label': label.code,
                    'product_id': label.product_id.id
                })
            package_label = self.env['package.product.label'].search([('sale_id', '=', self.order_id.id)])
            for label in package_label:
                line_ids += self.env['claim.line'].create({
                    'package_id': label.id,
                    'label': label.code,
                    'product_id': label.product_id.id
                })
            self.domain_line_ids = line_ids
        else:
            self.line_ids = [(5, 0, 0)]

class ClaimLine(models.Model):
    _name = 'claim.line'

    label = fields.Char('Label', required=True)
    length = fields.Float(readonly="1")
    height = fields.Float(readonly="1")
    width = fields.Float(readonly="1")
    
class IncidenceCause(models.Model):
    _name = "incidence.cause"
    
    description = fields.Char(string='Description', store=True)