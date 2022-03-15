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
    line_ids = fields.Many2many('claim.line', 'claim_line_rel', string='Articles with problems')
    domain_line_ids = fields.Many2many('claim.line', 'claim_line_domain_rel', string='Domain Articles')
    date = fields.Date(string='Claim Date', index=True, default=fields.Datetime.now)
    pickup_id = fields.Many2one('pickup.order', string='Pickup Order')
    state_pickup = fields.Selection([
    ('draft', 'Draft'),
    ('done', 'Done'),
    ('received', 'Received'),
    ('cancel', 'Cancel')], string='State Pickup Order')
  
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


class ClaimLine(models.Model):
    _name = 'claim.line'

    semifinished_id = fields.Many2one('semifinished.product.label', string='Product', required=False)
    package_id = fields.Many2one('package.product.label', string='Product', required=False)
    product_id = fields.Many2one('product.product', string='Product', required=False)
    label = fields.Char('Label', required=True)
    length = fields.Float(readonly="1")
    height = fields.Float(readonly="1")
    width = fields.Float(readonly="1")
    
class IncidenceCause(models.Model):
    _name = "incidence.cause"
    
    description = fields.Char(string='Description', store=True)