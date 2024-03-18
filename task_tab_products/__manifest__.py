{
    'name': 'Task Tab Products',
    'depends': [
        'base_setup',
        'project',
        'product',
        'sale',
        'uom'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/project_task_views.xml',
        'views/product_configurator.xml'
    ],
    'installable': True,
    'application': True,
}