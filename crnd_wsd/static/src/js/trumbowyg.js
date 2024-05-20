odoo.define('crnd_wsd.trumbowyg', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var core = require('web.core');

    require('crnd_wsd.trumbowyg.upload-file');

    // Fix trumbowyg svg icons path
    $.trumbowyg.svgPath = "/crnd_wsd/static/lib/trumbowyg/dist/ui/icons.svg";


    // Simple plugin to enable image loading
    $.extend(true, $.trumbowyg, {
        plugins: {
            uploadImage: {
                init: function (trumbowyg) {
                    trumbowyg.pasteHandlers.push(function (pasteEvent) {
                        var clipboardData = (
                            pasteEvent.originalEvent || pasteEvent
                        ).clipboardData;

                        var request_id = trumbowyg.$box.closest(
                            '.wsd_request').data('request-id');

                        var preventDefaultDone = false;

                        $.each(clipboardData.files, function (index, file) {
                            if (!preventDefaultDone) {
                                // Prevent default handling if required
                                pasteEvent.preventDefault();
                                preventDefaultDone = true;
                            }
                            if (file.type.match(/^image\//)) {
                                var ajax_data = {
                                    'upload': file,
                                    'is_image': true,
                                };
                                if (request_id) {
                                    ajax_data.request_id = request_id;
                                }

                                ajax.post(
                                    '/crnd_wsd/file_upload',
                                    ajax_data
                                ).then(function (result) {
                                    var data = JSON.parse(result);
                                    if (data.status === 'OK') {
                                        trumbowyg.execCmd(
                                            'insertImage',
                                            data.attachment_url, null, true);
                                        var $img = $(
                                            'img[src="' + data.attachment_url +
                                            '"]:not([width])', trumbowyg.$box);
                                        $img.css('max-width', '100%');
                                        trumbowyg.syncCode();
                                    }
                                    // TODO: handle status not ok
                                });
                            }
                        });

                    });
                },
            },
        },
    });


    var trumbowyg_options = {
        autogrow: true,
        resetCss: true,
        btns: [
            ['viewHTML'],
            ['undo', 'redo'],
            ['formatting'],
            ['strong', 'em', 'del'],
            ['foreColor', 'backColor'],
            ['link'],
            ['uploadFile'],
            ['justifyLeft', 'justifyCenter', 'justifyRight', 'justifyFull'],
            ['unorderedList', 'orderedList'],
            ['table'],
            ['horizontalRule'],
            ['removeformat'],
            ['fullscreen'],
        ],
        plugins: {
            uploadFile: {
                serverPath: '/crnd_wsd/file_upload/',
                fileFieldName: 'upload',
                isImageFieldName: 'is_image',
                urlPropertyName: 'attachment_url',
                data: [
                    {
                        name: 'csrf_token',
                        value: core.csrf_token,
                    },
                ],
            },
            table: {
                styler: "table table-bordered table-stripped",
            },
        },
    };

    function parseCookieString(str) {
    const cookie = {};
    const parts = str.split("; ");
    for (const part of parts) {
        const [key, value] = part.split("=");
        cookie[key] = value || "";
        }
    return cookie;
    }

    function getLang() {
    var html = document.documentElement;
    return (html.getAttribute('lang') || 'en_US').toLowerCase();
    }

    var browser_cookies = parseCookieString(document.cookie);
    var lang_parts = browser_cookies['frontend_lang'].toLowerCase() || getLang();
    if (lang_parts.indexOf('_') >= 0) {
        lang_parts = lang_parts.split('_');
    } else if (lang_parts.indexOf('-') >= 0) {
        lang_parts = lang_parts.split('-');
    } else {
        lang_parts = [lang_parts];
    }

    if ($.trumbowyg.langs[lang_parts[0]]) {
        trumbowyg_options.lang = lang_parts[0];
    } else if ($.trumbowyg.langs[lang_parts[1]]) {
        trumbowyg_options.lang = lang_parts[1];
    }


    return {
        trumbowygOptions: trumbowyg_options,
    };

});
