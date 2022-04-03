# -*- coding: utf-8 -*-
from markupsafe import string
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
import re


class ResPartner(models.Model):
    _inherit = 'res.partner'

    code = fields.Char(
        string="Code",
        copy=False)