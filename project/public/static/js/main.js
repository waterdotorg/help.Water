/*
----------------------
Django CSRF Ajax Token
----------------------
*/
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

/*
------------------
Ajax Form Handling
------------------
*/
function apply_form_field_error (fieldname, error) {
    var input = $("#" + fieldname),
        container = $("#" + fieldname + "-form"),
        error_msg = $("<span />").addClass("alert-error ajax-error").text(error[0]);

    container.addClass("error");
    error_msg.insertAfter(container);
}

function clear_form_field_errors (form) {
    $(".ajax-error", $(form)).remove();
    $(".error", $(form)).removeClass("error");
}

$(document).ready(function () {
  $(".ttip").tooltip();

  $("#watch-ticket").click(function(e) {
      e.preventDefault();
      $("#watch-ticket-form").submit();
  })

  $("#watch-ticket-form").submit(function(e) {
      e.preventDefault();
      var self = $(this),
      url = self.attr("action"),
      ajax_req = $.ajax({
          url: url,
          type: "POST",
          data: {
              ticket_id: self.find("#id_ticket_id").val(),
              csrfmiddlewaretoken: self.find("input[name='csrfmiddlewaretoken']").val()
          },
          success: function(data, textStatus, jqXHR) {
              var c = $("#watch-ticket span").attr('class');
              if (c == 'glyphicon glyphicon-star') {
                  $("#watch-ticket span").attr('class', 'glyphicon glyphicon-star-empty');
                  $("#watch-ticket").attr('title', 'Watch')
                                    .attr('data-original-title', 'Watch')
                                    .tooltip('fixTitle');
              } else {
                  $("#watch-ticket span").attr('class', 'glyphicon glyphicon-star');
                  $("#watch-ticket").attr('title', 'Unwatch')
                                    .attr('data-original-title', 'Unwatch')
                                    .tooltip('fixTitle');
              }
          },
          error: function(data, textStatus, jqXHR) {
              var errors = data.responseText;
              alert(errors);
              /*
              $.each(errors, function(index, value) {
                  if (index === "__all__") {
                      alert(value[0], "error");
                  } else {
                      apply_form_field_error(index, value);
                  }
              });
              */
          }
      });
  });

});
