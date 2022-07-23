    $(document).ready(function () {

        "use strict";
        if(localStorage.getItem("notify_show")==false)
        {return;}
        var i = -1;
        var toastCount = 0;
        var $toastlast;

        $('#showtoast').click(function () {
            var shortCutFunction = localStorage.getItem("notify_type");
            var msg = localStorage.getItem("notify_context");
            var title = localStorage.getItem("notify_tittle");
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


            toastr[shortCutFunction](msg, title); // Wire up an event handler to a button in the toast, if it exists

            localStorage.setItem("notify_show",false);
            localStorage.removeItem("notify_context");
            localStorage.removeItem("notify_tittle");
            localStorage.removeItem("notify_type");
            return;
        });
    });