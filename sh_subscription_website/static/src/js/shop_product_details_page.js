odoo.define('sh_subscription_website.website_sale', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    require('website_sale.website_sale');


    publicWidget.registry.WebsiteSale.include({
        /**
         * Adds the stock checking to the regular _onChangeCombination method
         * @override
        */
        _onChangeCombination: function (ev, $parent, combination) {
            this._super.apply(this, arguments);            
            
            // STEP 1: remove highlighted class in all subscription plans.

            $(document).find('.subscription_plan').removeClass('active_background_color')

            // STEP 2: add highlighted class in selected product variant.
            if (combination.product_id){
                var subscription_plan_div =  $(document).find('.js_cls_subscription_plans_wrapper div[data-subscription_id="' + combination.product_id +'"]');
                subscription_plan_div.addClass('active_background_color')
            }            
        }
    });

});