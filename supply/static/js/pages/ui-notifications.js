    $(document).ready(function () {

        "use strict";

        var i = -1;
        var toastCount = 0;
        var $toastlast;

        $('#showtoast').click(function () {
            var shortCutFunction = "info";
            var msg = "信息";
            var title = "标题";
            var toastIndex = toastCount++;
            var addClear = true;

            toastr.options = {
                closeButton: true,
                debug: false,
                newestOnTop: false,
                progressBar: false,
                positionClass: "toast-bottom-full-width",
                preventDuplicates: true,
                onclick: null,
                showDuration: 300,
                hideDuration: 1000,
                timeOut: 4000,
                extendedTimeOut: 3000,
                showEasing: "swing",
                hideEasing: "linear",
                showMethod: "fadeIn",
                hideMethod: "slideUp",
            };


            var $toast = toastr[shortCutFunction](msg, title); // Wire up an event handler to a button in the toast, if it exists
            $toastlast = $toast;

            if (typeof $toast === 'undefined') {
                return;
            }

        });
    });