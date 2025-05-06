odoo.define('ITCustom_Public_Kiosk.override_kiosk', function (require) {
    "use strict";

    const KioskBadge = require('hr_attendance.kiosk_mode');

    KioskBadge.include({
        start: function () {
            this._super.apply(this, arguments);
            // Ganti teks setelah DOM siap
            setTimeout(() => {
                const badgeText = document.querySelector('.o_hr_attendance_kiosk_mode h1');
                if (badgeText && badgeText.innerText.includes("Scan your badge")) {
                    badgeText.innerText = "Scan Disini";
                }
            }, 100); // Delay kecil untuk pastikan DOM sudah ter-render
        },
    });
});
