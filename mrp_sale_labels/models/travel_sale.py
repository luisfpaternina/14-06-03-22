# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CrmLeadType(models.Model):
    _name = 'travel_sale'
    _description = 'Oportunity type'

    name = fields.Char(string="Name")
    active = fields.Boolean(string="Active")
    days_maximum_stage = fields.Integer(string="Days maximum stage")


    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False
    