import datetime
import logging
from odoo import models, fields, api, _
from odoo.tools.translate import _
from odoo.exceptions import UserError

class CronInherited (models.Model):
    _inherit='ir.cron'

    is_date=fields.Boolean(string="Is Date", default=False)
    lastcall=fields.Datetime(string="Last Call")

    @api.depends('nextcall')
    def _compute_nextcall(self):
        now=datetime.datetime.now()
        if self.nextcall == now:
            self.is_date=True
        else:
            self.is_date=False




