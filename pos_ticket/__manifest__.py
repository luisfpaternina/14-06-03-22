# -*- coding: utf-8 -*-
{
    'name': "pos order ticket",

    'summary': """
        Agregar campo en ticket del POS""",

    'author': "Andres Gutierrez",

    'website': "",

    'category': 'Point of sale',

    'version': '13.0.0.0.0',

    'depends': [
        'stock',
    ],

    'data': [

        "views/pos_order_ticket.xml",
    ],
    
    'installable': True,
}
