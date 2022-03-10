import datetime
import logging
from odoo import models, fields, api, _
from odoo.tools.translate import _
from odoo.exceptions import UserError

class CronInherited (models.Model):
    _inherit='ir.cron'

    is_date=fields.Boolean(string="Is Date", default=False, compute='compute_lastcall')

    @api.depends('lastcall')
    def compute_lastcall(self):
        if self.lastcall:
            self.is_date=True
        else:
            self.is_date=False

    
    #def _is_date(self):
    #    if(self.nextcall==datetime.date.today()):
    #        is_date=True




