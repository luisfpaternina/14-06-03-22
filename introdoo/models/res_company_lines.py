
from odoo import models, fields, api

class ResCompanyLine(models.Model):
    _name = 'res.company.line'
    _description = 'company lines'

    partner_id = fields.Many2one('res.partner', string="Contacto")
    company_id = fields.Many2one('res.company',string="Compañia")
