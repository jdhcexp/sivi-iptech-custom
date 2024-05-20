{
    'name': "Generic Request Location",

    'summary': """
        Generic Request Location
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Request',
    'version': '16.0.0.10.0',

    'depends': [
        'generic_request',
        'generic_location',
    ],

    'data': [
        'views/generic_location_views.xml',
        'views/request_request.xml',
    ],
    'images': [
        'static/description/banner.png'
    ],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
    'price': 5.0,
    'currency': 'EUR',
}
