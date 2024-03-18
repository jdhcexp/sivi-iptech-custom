{
    'name': "Generic Request Action Assignment",

    'summary': """
         Automatic assignments in request via actions
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",
    'category': 'Generic Request',
    'version': '16.0.1.4.0',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_request_action',
        'generic_request_assignment',
    ],

    # always loaded
    'data': [
        'views/request_event_action.xml',
    ],
    'demo': [
        'demo/request_event_action.xml',
    ],

    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'license': 'OPL-1',
    'price': 50.0,
    'currency': 'EUR',
}
