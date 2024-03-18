{
    'name': "Generic team HR",

    'summary': """This module provide integration Generic Team module
     with HR module.""",

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Team',
    'version': '16.0.0.3.0',

    "depends": [
        'base',
        'hr',
        'generic_team',
    ],

    "data": [
        'views/generic_team_member_view.xml',
        'views/generic_team_view.xml',
    ],

    "demo": [],
    'images': ['static/description/banner.png'],
    "installable": True,
    "application": False,
    'license': 'OPL-1',
    'price': 5.0,
    'currency': 'EUR',
}
