import datetime
import logging
from odoo import models, fields, api, _
from odoo.tools.translate import _
from odoo.exceptions import UserError

class CronInherited (models.Model):
    _inherit='ir.cron'

    is_date=fields.Boolean(
        string="Is Date",
        default=False)
    now = fields.Datetime(
        'Fecha y hora',
        tracking=True,
        default= fields.Datetime().now())


    @api.depends('nextcall','lastcall','write_date')
    def _compute_nextcall(self):
        if self.write_date >= self.now:
            self.is_date=True
            logging.info("***************************************************************")
        else:
            self.is_date=False
            logging.info("#################################################################")
