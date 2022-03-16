
{
    'name': 'Personalización de venta para gestionar las Reclamaciones y Ordenes de recogida',
    'description': """
        Personalización reclamaciones
        Gestion de ordenes de recogidas asociadas a una reclamacion. 
    """,
    'author':   'WVBS',
    'website':  'https://wvbs.eu/',
    'license': 'AGPL-3',
    'version': "14.0.1.0.0",
    'depends': ['mrp_sale_labels', 'crm_claim_type', 'stock'],
    'data': [
        #'security/ir.model.access.csv',
        #'data/pickup_order_data.xml',
        'views/pickup_order_view.xml',
        'views/crm_claim_view.xml'
        #'views/stock_view.xml',
        #'views/travel_sale_view.xml',
        #'wizard/assign_pickup_travel_wizard_view.xml',
        #'wizard/manufacturing_pickup_order_wizard_view.xml',
        #'report/report_deliveryslip.xml',
    ],
    'active': False,
    'application': False
}
