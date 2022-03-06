from odoo import api, fields, models, exceptions, tools, _
import logging
_logger = logging.getLogger(__name__)


class CrmClaim(models.Model):
    _inherit = "crm.claim"
  
class ClaimLine(models.Model):
    _name = 'claim.line'

    
class IncidenceCause(models.Model):
    _name = "incidence.cause"
