# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CrmLeadType(models.Model):
    _name = 'travel_sale'
    _description = 'Oportunity type'

    name = fields.Char(
        String="Name",
        tracking=True)
    active = fields.Boolean(
        string="Active",
        default=True,
        tracking=True)
    days_maximum_stage = fields.Integer(
        string="Days maximum stage",
        tracking=True)


    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False
    