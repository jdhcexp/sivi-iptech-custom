odoo.define('order_preview_extra.signature_form', function(require) {
    "use strict";
    var NameAndSignature = require('web.name_and_signature').NameAndSignature;
    var publicWidget = require('web.public.widget');
    NameAndSignature.include({
        template: 'order_preview_extra.sign_name_and_signature',
        xmlDependencies: (NameAndSignature.prototype.xmlDependencies || []).concat(
            ['/order_preview_extra/static/src/sign_and_accept.xml']
        ),
    });

});