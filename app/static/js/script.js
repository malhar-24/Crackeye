document.addEventListener("DOMContentLoaded", () => {
    // 1. Kick-off Initial Page Load Animations
    document.body.classList.add('loaded');

    const btn = document.getElementById('get-started-btn');
    
    // Ensure button exists
    if (btn) {

        // Once button fade-in animation finishes, remove keyframe locks
        setTimeout(() => {
            btn.classList.add('animation-complete');
         btn.style.animation = 'none';
         btn.style.pointerEvents = 'auto'; // 🔥 force enable click
        }, 2850);

        // 2. Button Ripple Effect Interactivity
        btn.addEventListener('mousedown', function (e) {
            const rect = e.target.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            
            const radius = Math.max(rect.width, rect.height);
            ripple.style.width = ripple.style.height = `${radius}px`;
            ripple.style.left = `${x - radius / 2}px`;
            ripple.style.top = `${y - radius / 2}px`;

            this.appendChild(ripple);

            setTimeout(() => {
                ripple.remove();
            }, 6000);
        });

        // ✅ 3. ADD NAVIGATION (NEW)
        btn.addEventListener('click', function () {
            // Optional smooth fade-out
            document.body.style.opacity = "0";

            setTimeout(() => {
                window.location.href = btn.dataset.url;
            }, 300);
        });
    }

    // 4. AI-Tech Canvas Background Animation (Neural Network effect)
    const canvas = document.getElementById('bg-canvas');

    if (canvas) {
        const ctx = canvas.getContext('2d');

         let width, height;
        let particles = [];
    
        const isMobile = window.innerWidth < 768;
        const maxParticles = isMobile ? 50 : 100;
        const connectionDistance = isMobile ? 120 : 180;

        function resizeCanvas() {
         width = window.innerWidth;
         height = window.innerHeight;
         canvas.width = width;
         canvas.height = height;
    }

    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    class Particle {
        constructor() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.vx = (Math.random() - 0.5) * 1.5;
            this.vy = (Math.random() - 0.5) * 1.5;
            this.radius = Math.random() * 1.5 + 0.5;
            this.color = Math.random() > 0.8 
                ? 'rgba(138, 43, 226, 0.8)' 
                : 'rgba(0, 243, 255, 0.6)';
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;

            if (this.x < 0 || this.x > width) this.vx *= -1;
            if (this.y < 0 || this.y > height) this.vy *= -1;
        }

        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = this.color;
            ctx.fill();
        }
    }

    function initParticles() {
        particles = [];
        for (let i = 0; i < maxParticles; i++) {
            particles.push(new Particle());
        }
    }

    function animateParticles() {
        ctx.clearRect(0, 0, width, height);

        for (let i = 0; i < particles.length; i++) {
            particles[i].update();
            particles[i].draw();

            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < connectionDistance) {
                    ctx.beginPath();
                    const opacity = 1 - (dist / connectionDistance);
                    ctx.strokeStyle = `rgba(0, 243, 255, ${opacity * 0.4})`; 
                    ctx.lineWidth = 0.8;
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }
        requestAnimationFrame(animateParticles);
    }

    initParticles();
    animateParticles();
}

    let width, height;
    let particles = [];
    
    const isMobile = window.innerWidth < 768;
    const maxParticles = isMobile ? 50 : 100;
    const connectionDistance = isMobile ? 120 : 180;

    function resizeCanvas() {
        width = window.innerWidth;
        height = window.innerHeight;
        canvas.width = width;
        canvas.height = height;
    }

    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    class Particle {
        constructor() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.vx = (Math.random() - 0.5) * 1.5;
            this.vy = (Math.random() - 0.5) * 1.5;
            this.radius = Math.random() * 1.5 + 0.5;
            this.color = Math.random() > 0.8 
                ? 'rgba(138, 43, 226, 0.8)' 
                : 'rgba(0, 243, 255, 0.6)';
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;

            if (this.x < 0 || this.x > width) this.vx *= -1;
            if (this.y < 0 || this.y > height) this.vy *= -1;
        }

        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = this.color;
            ctx.fill();
        }
    }

    function initParticles() {
        particles = [];
        for (let i = 0; i < maxParticles; i++) {
            particles.push(new Particle());
        }
    }

    function animateParticles() {
        ctx.clearRect(0, 0, width, height);

        for (let i = 0; i < particles.length; i++) {
            particles[i].update();
            particles[i].draw();

            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < connectionDistance) {
                    ctx.beginPath();
                    const opacity = 1 - (dist / connectionDistance);
                    ctx.strokeStyle = `rgba(0, 243, 255, ${opacity * 0.4})`; 
                    ctx.lineWidth = 0.8;
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }
        requestAnimationFrame(animateParticles);
    }

    initParticles();
    animateParticles();
});