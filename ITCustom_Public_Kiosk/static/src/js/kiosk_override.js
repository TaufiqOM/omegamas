odoo.define('itcustom_kiosk.override', function (require) {
    "use strict";
    
    console.log("Loading Kiosk Text Override..."); // Debug
    
    // Method 1: DOM Mutation Observer
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            const scanTexts = document.querySelectorAll('.o_mobile_barcode span');
            scanTexts.forEach(function(span) {
                if (span.textContent.includes('Scan your badge')) {
                    console.log("Found text, replacing..."); // Debug
                    span.textContent = 'SCAN DISINI';
                    span.classList.add('scan-disini-text');
                }
            });
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: false,
        characterData: false
    });
    
    // Method 2: Fallback interval checker
    setTimeout(function checkText() {
        const scanTexts = document.querySelectorAll('.o_mobile_barcode span');
        let found = false;
        
        scanTexts.forEach(function(span) {
            if (span.textContent.includes('Scan your badge')) {
                span.textContent = 'SCAN DISINI';
                span.classList.add('scan-disini-text');
                found = true;
            }
        });
        
        if (!found) {
            setTimeout(checkText, 500);
        }
    }, 1000);
});