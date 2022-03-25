###############################################################################################
#
# Luis Felipe Paternina  
# Ing.Sistemas                                
# Odoo Dev
# 
# Cel: 3215062353
#
#
# Bogotá,Colombia
#
#
###############################################################################################

{
    'name': 'Introdoo',

    'version': '13.1',

    'author': "Luis Felipe Paternina",

    'contributors': ['Luis Felipe Paternina'],

    'website': "",

    'category': 'Trainning',

    'depends': [

        'sale_management',
        'contacts',
        'stock',
        'base',
    ],

    'data': [
    
        'security/ir.model.access.csv',
        'views/res_company.xml',
        'views/res_config_settings.xml',
        'views/stock_picking.xml',
        'wizard/wizard.xml',
        'data/base_automatization.xml',           
    ],
    'installable': True
}

