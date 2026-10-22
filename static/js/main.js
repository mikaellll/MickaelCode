/**
 * MickaelCode Platform Main JavaScript
 * Handles responsive navigation and notifications.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Mobile navigation toggle
    const burger = document.querySelector('.burger');
    const nav = document.querySelector('.navbar');
    const navlinks = document.querySelectorAll('.links li');

    if (burger && nav) {
        burger.addEventListener('click', () => {
            nav.classList.toggle('navbaract');
            burger.classList.toggle('toggle');

            navlinks.forEach((link, index) => {
                if (link.style.animation) {
                    link.style.animation = '';
                } else {
                    link.style.animation = `navlinkfade 0.5s ease forwards ${index / 7 + 0.1}s`;
                }
            });
        });
    }

    // Auto-dismiss alert messages after 5 seconds
    const alerts = document.querySelectorAll('.alert-banner');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 600);
        }, 5000);
    });
});
