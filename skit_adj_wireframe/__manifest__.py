# -*- coding: utf-8 -*-

{
    'name': 'Skit ADJ Wireframe',
    'category': 'Sales',
    'summary': 'ADJ WireFrame',
    'author': 'Srikesh Infotech',
    'license': "AGPL-3",
    'website': 'http://www.srikeshinfotech.com',
    'description': """

==========================

""",
    'depends': ['sale', 'account', 'sale_stock', 'purchase', 'stock',
                'skit_purchase_request', 'delivery','base'],
    'data': [
        'wizard/skit_sales_delivery.xml',
        'wizard/skit_warning.xml',
        'report/sale_delivery_report.xml',
        'report/sales_delivery_template.xml',
        'views/res_partner.xml',
        'views/sale_order.xml',
        'views/product_template.xml',
        'views/purchase_order.xml',
        'views/account_invoice.xml',
        'views/stock_picking_views.xml'
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
