from odoo import api, fields, models, exceptions, tools, _
import logging
_logger = logging.getLogger(__name__)


class CrmClaim(models.Model):
    _inherit = "crm.claim"

    reference = fields.Char(string="Ntra Reference", store=True)
    reference_client = fields.Char(string="Client Reference", store=True)
    solution = fields.Boolean('Solution')
    date = fields.Date(string='Claim Date', index=True, default=fields.Datetime.now)
    state_pickup = fields.Selection([
    ('draft', 'Draft'),
    ('done', 'Done'),
    ('received', 'Received'),
    ('cancel', 'Cancel')], string='State Pickup Order')
  
class ClaimLine(models.Model):
    _name = 'claim.line'

    
class IncidenceCause(models.Model):
    _name = "incidence.cause"
