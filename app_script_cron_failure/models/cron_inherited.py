import datetime
import logging
from odoo import models, fields, api, _
from odoo.tools.translate import _
from odoo.exceptions import UserError

class CronInherited (models.Model):
    _inherit=['ir.cron']

    is_date=fields.Boolean(
        string="Is Date",
        compute="_compute_nextcall")
    now = fields.Datetime(
        'Fecha y hora',
        tracking=True,
        default= fields.Datetime().now())
    time = fields.Integer(string="Tiempo", compute=('_calculate_time'))
    is_send_email=fields.Boolean(string="Is Send Email", default=False)

    @api.depends('write_date','lastcall')
    def _calculate_time(self):
        time=0
        if self.write_date and self.lastcall:
            time=(self.write_date-self.lastcall)
            self.time=time.total_seconds() / 60
        else:
            self.time=0


    @api.depends('nextcall','lastcall','write_date')
    def _compute_nextcall(self):
        if self.time==0:
            self.is_date=True
        else:
            self.is_date=False
