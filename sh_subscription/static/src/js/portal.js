$(document).ready(function(e) {
    $(".sh_cancel_btn_list").click(function(event) {
        var $el = $(event.target).parents('tr').find("#subscription_id").attr("value")
        var subscription_id = parseInt($el)
        $('#cancel_subscription_id').val(subscription_id);
        $('#cancel_subscription_modal').modal('show');
    });
    $(".sh_cancel_btn").click(function(event) {
        $('#cancel_subscription_id').val($('#subscription_id_form').val());
        $('#cancel_subscription_modal').modal('show');
    });
    $("#sh_cancel_now").click(function(event) {
        $.ajax({
            url: "/cancel-subscription",
            data: { subscription_id: $('#cancel_subscription_id').val(), 'description': $('#sh_description').val(), 'sh_reason_id': $('#sh_reason_id').val() },
            type: "post",
            cache: false,
            success: function(result) {
                var datas = JSON.parse(result);
                if (datas.required == true) {
                    alert("Reason is required");
                }
                if (datas.reload == true) {

                    location.reload(true);
                }
            },
        });
    });

    $(".sh_close_btn_list").click(function(event) {
        var $el = $(event.target).parents('tr').find("#subscription_id").attr("value")
        var subscription_id = parseInt($el)
        $('#cancel_subscription_id').val(subscription_id);
        $('#cancel_subscription_modal').modal('show');
    });
    $(".sh_close_btn").click(function(event) {
        $('#cancel_subscription_id').val($('#subscription_id_form').val());
        $('#cancel_subscription_modal').modal('show');
    });

    $(".sh_renew_btn_list").click(function(event) {
        var $el = $(event.target).parents('tr').find("#subscription_id").attr("value")
        var subscription_id = parseInt($el)
        $.ajax({
            url: "/renew-subscription",
            data: { subscription_id: subscription_id },
            type: "post",
            cache: false,
            success: function(result) {
                var datas = JSON.parse(result);
                if (datas.reload == true) {
                    location.reload(true);
                }
            },
        });
    });
    $(".sh_renew_btn").click(function(event) {
        $.ajax({
            url: "/renew-subscription",
            data: { subscription_id: $('#subscription_id_form').val() },
            type: "post",
            cache: false,
            success: function(result) {
                var datas = JSON.parse(result);
                if (datas.reload == true) {
                    location.reload(true);
                }
            },
        });
    });
});