$(document).ready(function(e) {


    console.log("document_upload charged")

    $('#empresa').addClass('hidden');

    $('input[type=radio]').on('change', function () {
        var selectedValue = $('input[type=radio]:checked').val();
        console.log(selectedValue)
        if (selectedValue === "emp") {
                    $('#persona_natural').addClass('hidden');
                    $('#empresa').removeClass('hidden');
                } else {
                    $('#persona_natural').removeClass('hidden');
                    $('#empresa').addClass('hidden');
                }
    });

    cedulafileInput = $('.upload_cedula_fld');
    $(".upload_cedula_btn").click(function(event) {
        cedulafileInput.click();
    })

    $('.cedula-files').addClass('hidden');



    cedulafileInput.on('change', function(e) {
        debugger;
        files = cedulafileInput.prop('files')
        if(files.length > 0 ){
        $('.cedula-files').removeClass('hidden');
        $('.cedula_attachment_name').text(files[0].name);
        $('.cedula_attachment_embedded').data('data-mimetype',files[0].type)
        }
    })


    serviciosfileInput = $('.upload_servicios_fld');
    $(".upload_servicios_btn").click(function(event) {
        serviciosfileInput.click();
    })

    $('.servicios-files').addClass('hidden');



    serviciosfileInput.on('change', function(e) {
        debugger;
        files = serviciosfileInput.prop('files')
        if(files.length > 0 ){
        $('.servicios-files').removeClass('hidden');
        $('.servicios_attachment_name').text(files[0].name);
        $('.servicios_attachment_embedded').data('data-mimetype',files[0].type)
        }
    })

  rutfileInput = $('.upload_rut_fld');
    $(".upload_rut_btn").click(function(event) {
        rutfileInput.click();
    })

    $('.rut-files').addClass('hidden');



    rutfileInput.on('change', function(e) {
        debugger;
        files = rutfileInput.prop('files')
        if(files.length > 0 ){
        $('.rut-files').removeClass('hidden');
        $('.rut_attachment_name').text(files[0].name);
        $('.rut_attachment_embedded').data('data-mimetype',files[0].type)
        }
    })

     ccfileInput = $('.upload_cc_fld');
    $(".upload_cc_btn").click(function(event) {
        ccfileInput.click();
    })

    $('.cc-files').addClass('hidden');



    ccfileInput.on('change', function(e) {
        debugger;
        files = ccfileInput.prop('files')
        if(files.length > 0 ){
        $('.cc-files').removeClass('hidden');
        $('.cc_attachment_name').text(files[0].name);
        $('.cc_attachment_embedded').data('data-mimetype',files[0].type)
        }
    })


  cedrepfileInput = $('.upload_cedrep_fld');
    $(".upload_cedrep_btn").click(function(event) {
        cedrepfileInput.click();
    })

    $('.cedrep-files').addClass('hidden');



    cedrepfileInput.on('change', function(e) {
        debugger;
        files = cedrepfileInput.prop('files')
        if(files.length > 0 ){
        $('.cedrep-files').removeClass('hidden');
        $('.cedrep_attachment_name').text(files[0].name);
        $('.cedrep_attachment_embedded').data('data-mimetype',files[0].type)
        }
    })
   /* function _prepareAttachmentData(file) {
        return {
            'name': file.name,
            'file': file,
            'res_id': this.options.res_id,
            'res_model': this.options.res_model,
            'access_token': this.options.token,
        };
    }
    oe_attachment_embedded
    cedulafileInput.on


    var self = this;
        return Promise.all(_.map(cedulafileInput, function (file) {
            return new Promise(function (resolve, reject) {
                var data = _prepareAttachmentData(file);
                ajax.post('/portal/attachment/add', data).then(function (attachment) {
                    attachment.state = 'pending';
                    self.attachments.push(attachment);
                    self._updateAttachments();
                    resolve();
                }).guardedCatch(function (error) {
                    self.displayNotification({
                        message: _.str.sprintf(_t("Could not save file <strong>%s</strong>"),
                            _.escape(file.name)),
                        type: 'warning',
                        sticky: true,
                    });
                    resolve();
                });
            });
        })).then(function () {
            // ensures any selection triggers a change, even if the same files are selected again
            self.$fileInput[0].value = null;
            self.$sendButton.prop('disabled', false);
        });
    });*/



})

