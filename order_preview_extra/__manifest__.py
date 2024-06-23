{
    'name': 'Order Preview Extra',
    'depends': [
        'base',
        'base_setup',
        'sale',
        'web'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/documents_upload.xml',
        'views/sale_order_views.xml'
    ],
    'assets': {
        'order_preview_extra.assets_order': [
            'order_preview_extra/static/src/jquery-3.7.1.min.js',
            # bootstrap
            ('include', 'web._assets_helpers'),
            'web/static/src/scss/pre_variables.scss',
            'web/static/lib/bootstrap/scss/_variables.scss',
            ('include', 'web._assets_bootstrap'),

            'web/static/src/libs/fontawesome/css/font-awesome.css', # required for fa icons
            'web/static/src/legacy/js/promise_extension.js', # required by boot.js
            'web/static/src/boot.js', # odoo module system
            'web/static/src/env.js', # required for services
            'web/static/src/session.js', # expose __session_info__ containing server information
            'web/static/lib/owl/owl.js', # owl library
            'web/static/lib/owl/odoo_module.js', # to be able to import "@odoo/owl"
            'web/static/src/core/utils/hooks.js',
            'web/static/src/core/orm_service.js',
            'web/static/src/core/utils/functions.js',
            'web/static/src/core/browser/browser.js',
            'web/static/src/core/registry.js',
            'web/static/src/core/assets.js',
            'order_preview_extra/static/src/*',
            'order_preview_extra/static/src/**/*',
        ],
    },
    'installable': True,
    'application': True,
}