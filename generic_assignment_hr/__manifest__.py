{
    'name': "Generic Assignment HR",

    'summary': """
        Provides integration between the
        Generic Assignment Policy and HR modules.
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Assignment',
    'version': '16.0.1.5.0',

    # any module necessary for this one to work correctly
    'depends': [
        'hr',
        'generic_assignment'
    ],

    # always loaded
    'data': [
        'views/generic_assign_policy_rule_view.xml',
    ],
    'images': ['static/description/banner.png'],
    'demo': [],

    'installable': True,
    'application': False,
    'license': 'OPL-1',
    'price': 50.0,
    'currency': 'EUR',
}
