{
    'name': 'Order Preview Documents',
    'depends': [
        'base_setup',
        'sale'
    ],
    'data': [
        'views/documents_upload.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'order_preview_documents/static/src/js/document_upload.js',
            'order_preview_documents/static/src/css/document_upload.css',
        ],
    },
    'installable': True,
    'application': True,
}