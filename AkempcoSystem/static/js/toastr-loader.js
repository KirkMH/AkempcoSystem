
  toastr.options = {
    "closeButton": true,
    "debug": false,
    "newestOnTop": true,
    "progressBar": false,
    "positionClass": "toast-top-center",
    "preventDuplicates": false,
    "onclick": null,
    "showDuration": "300",
    "hideDuration": "1000",
    "timeOut": "5000",
    "extendedTimeOut": "1000",
    "showEasing": "swing",
    "hideEasing": "linear",
    "showMethod": "fadeIn",
    "hideMethod": "fadeOut"
  }
  function showMessageNotifications() {
    $(".message_notif").each(function () {
      let msg = $(this).val().split(":");
      if (msg[0] == 'info') {
        toastr.info(msg[1])
      }
      else if (msg[0] == 'success') {
        toastr.success(msg[1])
      }
      else if (msg[0] == 'warning') {
        toastr.warning(msg[1])
      }
      else if (msg[0] == 'error') {
        toastr.error(msg[1])
      }
    });
  }
  showMessageNotifications();