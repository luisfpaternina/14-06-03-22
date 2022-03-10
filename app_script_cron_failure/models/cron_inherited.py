import datetime
import logging
from odoo import models, fields, api, _
from odoo.tools.translate import _
from odoo.exceptions import UserError

class CronInherited (models.Model):
    _inherit='ir.cron'

    is_date=fields.Boolean(
        string="Is Date",
        compute="_compute_nextcall")
    now = fields.Datetime(
        'Fecha y hora',
        tracking=True,
        default= fields.Datetime().now())

    time = fields.Integer(string="Tiempo", compute=('_calculate_time'))

    @api.depends('write_date','lastcall')
    def _calculate_time(self):
        if self.write_date and self.lastcall:
            self.time=(self.write_date-self.lastcall).minutes
        else:
            self.time=0


    @api.depends('nextcall','lastcall','write_date')
    def _compute_nextcall(self):
        if self.write_date == self.lastcall:
            self.is_date=True
            logging.info("***************************************************************")
        else:
            self.is_date=False
            logging.info("#################################################################")
