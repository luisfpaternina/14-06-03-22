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
    motive = fields.Many2one(string='Incidence Cause')
    solution = fields.Boolean('Solution')
    date = fields.Date(string='Claim Date', index=True, default=fields.Datetime.now)
    pickup_id = fields.Many2one('pickup.order', string='Pickup Order')
    state_pickup = fields.Selection([
    ('draft', 'Draft'),
    ('done', 'Done'),
    ('received', 'Received'),
    ('cancel', 'Cancel')], string='State Pickup Order')
  
class ClaimLine(models.Model):
    _name = 'claim.line'

    label = fields.Char('Label', required=True)
    length = fields.Float(readonly="1")
    height = fields.Float(readonly="1")
    width = fields.Float(readonly="1")
    
class IncidenceCause(models.Model):
    _name = "incidence.cause"
    
    description = fields.Char(string='Description', store=True)