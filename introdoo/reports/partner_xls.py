from odoo import models, fields, api, _

class PartnerXls(models.AbstractModel):
    _name = 'report.introdoo.partner.xls'
    _inherit = 'report.report_xlsx.abstract'
