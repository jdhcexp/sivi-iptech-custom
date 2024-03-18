# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
{
    "name": "Subscription Management System - Website | Subscription Management Website",

    "author": "Softhealer Technologies",

    "website": "https://www.softhealer.com",

    "version": "16.0.1",

    "license": "OPL-1",

    "support": "support@softhealer.com",

    "category": "Extra Tools",

    "summary": "Customized Subscription Plans Subscription Based Products Subscription Odoo Subscription Manage Subscription Website Subscription Portal Product Subscription Plan Manage Sales Subscription Page Subscription Pricing Page on Website",

    "description": """Are you looking for a subscription management system? We provides the subscription system with subscription plans. You can create subscription plans like daily, weekly, monthly & yearly. You can send subscription reminders to customers using email templates. You can set recurring periods on subscriptions to renew it. Customer can manage their subscription plans for themselves directly from portal.""",
    
    'depends': ['sh_subscription','website_sale'],

    "data": [
            "data/product_ribbon_data.xml",
            "views/sh_product_details_page_template.xml",
    ],

    'assets': {
        'web.assets_frontend': [
            'sh_subscription_website/static/src/scss/sh_shop_page_details.scss',
            'sh_subscription_website/static/src/js/shop_product_details_page.js',
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": ["static/description/background.gif", ],
    "price": 30,
    "currency": "EUR"
}
