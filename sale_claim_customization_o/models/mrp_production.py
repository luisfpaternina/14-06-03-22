
from odoo import api, fields, models, exceptions, _
import math
import logging
_logger = logging.getLogger(__name__)

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def generate_label(self):
        label_id = False
        if self._context.get('copy_label', False):
            if self._context.get('type_label', False) == 'semifinished':
                if self._context.get('label', False):
                    label = self.env['semifinished.product.label'].browse(self._context.get('label', False))
                    if label:
                        label_id = label.copy({
                            'child_semifinished_ids': False,
                            'child_package_ids': False,
                        })
                        if label_id:
                            self.write({
                                'label_id': ('%s,%i' % (label_id._name, label_id.id))
                            })
            elif self._context.get('type_label', False) == 'package':
                label = self.env['package.product.label'].browse(self._context.get('label', False))
                if label:
                    label_id = label.copy({
                            'child_semifinished_ids': False,
                            'child_package_ids': False,
                        })
                    if label_id:
                        self.write({
                            'label_id': ('%s,%i' % (label_id._name, label_id.id))
                        })
        elif self.origin:
            origin = self.origin.split(':')[1] if len(self.origin.split(':')) > 1 else self.origin
            pickup_id = self.env['pickup.order'].search([('name', '=', origin)])
            if pickup_id:
                production_parent = self.search([('name', '=', origin)])
                if production_parent.label_id and production_parent.label_id._name == 'semifinished.product.label':
                    label_parent_ids = pickup_id.mapped('domain_line_ids').filtered(lambda x: x.semifinished_id and
                                                                      x.semifinished_id.product_id == production_parent.product_id)
                    if label_parent_ids:
                        if not self.product_id.es_bulto:
                            label_ids = label_parent_ids.mapped('child_semifinished_ids').filtered(lambda x: x.semifinished_id.product_id == self.product_id)
                            if label_ids:
                                label_id = label_ids[0].copy({
                                        'child_semifinished_ids': False,
                                        'child_package_ids': False,
                                    })
                                if label_id:
                                    self.write({
                                        'label_id': ('%s,%i' % (label_id._name, label_id.id))
                                    })
                            #Pensar como no repetir etiquetas
                        else:
                            label_ids = label_parent_ids.mapped('child_package_ids').filtered(
                                lambda x: x.semifinished_id.product_id == self.product_id)
                            if label_ids:
                                label_id = label_ids[0].copy({
                                        'child_semifinished_ids': False,
                                        'child_package_ids': False,
                                    })
                                if label_id:
                                    self.write({
                                        'label_id': ('%s,%i' % (label_id._name, label_id.id))
                                    })
                elif production_parent.label_id and production_parent.label_id._name == 'package.product.label':
                    label_parent_ids = pickup_id.mapped('domain_line_ids').filtered(lambda x: x.package_id and
                                                                                              x.package_id.product_id == production_parent.product_id)
                    if label_parent_ids:
                        if not self.product_id.es_bulto:
                            label_ids = label_parent_ids.mapped('child_semifinished_ids').filtered(
                                lambda x: x.semifinished_id.product_id == self.product_id)
                            if label_ids:
                                label_id = label_ids[0].copy({
                                        'child_semifinished_ids': False,
                                        'child_package_ids': False,
                                    })
                                if label_id:
                                    self.write({
                                        'label_id': ('%s,%i' % (label_id._name, label_id.id))
                                    })
                            # Pensar como no repetir etiquetas
                        else:
                            label_ids = label_parent_ids.mapped('child_package_ids').filtered(
                                lambda x: x.semifinished_id.product_id == self.product_id)
                            if label_ids:
                                label_id = label_ids[0].copy({
                                        'child_semifinished_ids': False,
                                        'child_package_ids': False,
                                    })
                                if label_id:
                                    self.write({
                                        'label_id': ('%s,%i' % (label_id._name, label_id.id))
                                    })

        if label_id:
            return label_id
        else:
            return super(MrpProduction, self).generate_label()

