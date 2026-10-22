/**
 * MickaelCode Platform Main JavaScript
 * Handles navigation, constellation background, mobile menu, notifications and interactions.
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

    // Particle constellation background canvas (if present)
    const canvas = document.getElementById('demo-canvas');
    if (canvas) {
        let width = window.innerWidth;
        let height = window.innerHeight;
        let target = { x: width / 2, y: height / 2 };
        const ctx = canvas.getContext('2d');
        canvas.width = width;
        canvas.height = height;

        // Create points
        const points = [];
        const step = Math.max(50, Math.floor(width / 18));
        for (let x = 0; x < width; x += step) {
            for (let y = 0; y < height; y += step) {
                const px = x + Math.random() * (step * 0.8);
                const py = y + Math.random() * (step * 0.8);
                points.push({
                    x: px,
                    originX: px,
                    y: py,
                    originY: py,
                    active: 0,
                    circleRadius: 1.5 + Math.random() * 2
                });
            }
        }

        // Find closest points for lines
        points.forEach((p1, i) => {
            const closest = [];
            points.forEach((p2, j) => {
                if (i !== j) {
                    const dist = Math.hypot(p1.x - p2.x, p1.y - p2.y);
                    closest.push({ point: p2, dist });
                }
            });
            closest.sort((a, b) => a.dist - b.dist);
            p1.closest = closest.slice(0, 5).map(c => c.point);
        });

        window.addEventListener('mousemove', (e) => {
            target.x = e.clientX || e.pageX;
            target.y = e.clientY || e.pageY;
        });

        window.addEventListener('resize', () => {
            width = window.innerWidth;
            height = window.innerHeight;
            canvas.width = width;
            canvas.height = height;
        });

        function animate() {
            ctx.clearRect(0, 0, width, height);

            points.forEach(p => {
                const distToTarget = Math.hypot(target.x - p.x, target.y - p.y);
                if (distToTarget < 250) {
                    p.active = 0.35 * (1 - distToTarget / 250);
                    p.lineAlpha = 0.25 * (1 - distToTarget / 250);
                } else {
                    p.active = 0.04;
                    p.lineAlpha = 0.03;
                }

                // Draw connecting lines
                p.closest.forEach(neighbor => {
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(neighbor.x, neighbor.y);
                    ctx.strokeStyle = `rgba(0, 255, 255, ${p.lineAlpha})`;
                    ctx.stroke();
                });

                // Draw circle node
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.circleRadius, 0, 2 * Math.PI, false);
                ctx.fillStyle = `rgba(0, 255, 255, ${p.active + 0.15})`;
                ctx.fill();
            });

            requestAnimationFrame(animate);
        }

        animate();
    }
});
