# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class AssignPickupTravelWizard(models.TransientModel):
    _name = 'assign.pickup.travel.wizard'

    @api.depends('pickup_ids')
    def _compute_travel_domain_ids(self):
        if self.pickup_ids:
            expected_date = self.pickup_ids.sorted(key=lambda p:p.expected_date, reverse=True)[0].expected_date
            if expected_date:
                self.date_up = expected_date
            travel_domain = self.env['travel.sale'].search([('date_up', '<=', self.date_up),
                                                            ('state', '=', 'open')])
            self.route_ids = [(4, router.id, False) for router in self.pickup_ids.mapped('partner_id.route_id')]
            if self.route_ids and travel_domain:
                travels = travel_domain.filtered(lambda x: set(self.route_ids.ids).issubset(set(x.route_ids.ids)))
                if travels:
                    self.travel_domain_ids = [(4, travel.id, False) for travel in travels]

    travel_id = fields.Many2one('travel.sale', string='Travel')
    pickup_ids = fields.Many2many('pickup.order', string='Pickup Orders')
    route_ids = fields.Many2many('route', string='Routers', compute='_compute_travel_domain_ids')
    travel_domain_ids = fields.Many2many('travel.sale', string='Travels domain', compute='_compute_travel_domain_ids')
    date_up = fields.Date(string='Date up', compute='_compute_travel_domain_ids')
    # assignable_volume = fields.Float(copy=False, string='Assignable volume (m^3)', digits=(12, 3))

    def confirm(self):
        self.pickup_ids.write({
            'travel_id': self.travel_id.id
        })
        return

