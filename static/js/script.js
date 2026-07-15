document.addEventListener("DOMContentLoaded", function () {
    console.log("⚡ Numero Annand AI Premium Interface Layer Ready.");
    
    // Auto Dismiss Flash System Framework Wrappers
    setTimeout(function() {
        let alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            let bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 4000);
});
