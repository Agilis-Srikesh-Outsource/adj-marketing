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
                'skit_purchase_request', 'delivery','base','product'],
    'data': [
        'security/product_security.xml',
        "security/ir.model.access.csv",
        'wizard/skit_sales_delivery.xml',
        'wizard/skit_warning.xml',
        'report/sale_delivery_report.xml',
        'report/sales_delivery_template.xml',
        'views/res_partner.xml',
        'views/sale_order.xml',
        'views/product_template.xml',
        'views/purchase_order.xml',
        'views/account_invoice.xml',
        'views/stock_picking_views.xml',
        'views/res_config_settings.xml',
        'views/date_config.xml',
        'views/date_config_demo.xml',
        'views/ship_via.xml',
        'views/report_purchase_order.xml',
        'views/report_sale_order.xml'
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
