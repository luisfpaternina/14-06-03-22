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


    @api.depends('nextcall','lastcall','write_date')
    def _compute_nextcall(self):
        now = datetime.datetime.now()
        logging.info("===================================")
        logging.info(now)
        if self.write_date == now:
            self.is_date=True
            logging.info("***************************************************************")
        else:
            self.is_date=False
            logging.info("#################################################################")
