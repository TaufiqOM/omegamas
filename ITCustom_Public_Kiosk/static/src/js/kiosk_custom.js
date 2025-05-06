odoo.define('itcustom_public_kiosk.custom', function (require) {
    "use strict";
    
    console.log("ITCustom Public Kiosk loaded"); // Debugging
    
    require('web.dom_ready');
    var publicWidget = require('web.public.widget');

    publicWidget.registry.HrAttendanceKioskCustom = publicWidget.Widget.extend({
        selector: '.o_hr_attendance_kiosk_mode',
        events: {
            'click .o_mobile_barcode': '_onBarcodeClick',
        },

        start: function () {
            console.log("Kiosk Custom Widget started"); // Debugging
            this._replaceScanText();
            return this._super.apply(this, arguments);
        },

        _replaceScanText: function () {
            var $scanText = this.$el.find('.o_mobile_barcode span:contains("Scan your badge")');
            if ($scanText.length) {
                console.log("Found scan text, replacing..."); // Debugging
                $scanText.text('Scan Disini');
            } else {
                console.log("Scan text not found"); // Debugging
            }
        },

        _onBarcodeClick: function () {
            console.log("Barcode button clicked"); // Debugging
        }
    });
});