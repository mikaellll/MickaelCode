/**
 * 3D Interactive Cyber Globe for MickaelCode (About Page)
 * Features exclusively the glowing world continents with crisp outlines.
 * Pure minimalist 3D floating continents — no black background sphere, no extra rings/grids.
 * Two-pass rendering: crisp foreground continents with subtle translucent background continents
 * for breathtaking holographic 3D depth perception.
 * Strictly adheres to Graphic Charter:
 * Pure Black (#000000), Neon Cyan (#00FFFF).
 */

(function () {
    const container = document.getElementById('globe-container');
    const canvas = document.getElementById('globe-canvas');
    if (!container || !canvas || typeof THREE === 'undefined') return;

    let scene, camera, renderer, globeGroup;
    let width = 560;
    let height = 560;
    const GLOBE_RADIUS = 165;

    // Interaction & Animation state
    let isDragging = false;
    let prevMouseX = 0;
    let prevMouseY = 0;
    let rotationVelocityX = 0;
    let rotationVelocityY = 0.0018; // Slow majestic planetary rotation
    let targetTiltX = 0.28;
    let targetTiltZ = -0.12;

    function init() {
        width = container.clientWidth || 560;
        height = container.clientHeight || 560;

        // 1. Scene
        scene = new THREE.Scene();

        // 2. Camera
        const isMobile = window.innerWidth <= 768;
        camera = new THREE.PerspectiveCamera(45, width / height, 1, 2000);
        camera.position.set(0, isMobile ? 0 : 20, isMobile ? 380 : 500);

        // 3. WebGL Renderer
        renderer = new THREE.WebGLRenderer({
            canvas: canvas,
            antialias: true,
            alpha: true,
            powerPreference: 'high-performance'
        });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.setSize(width, height, false);
        renderer.setClearColor(0x000000, 0);

        // 4. Main Globe Pivot Group
        globeGroup = new THREE.Group();
        globeGroup.rotation.x = targetTiltX;
        globeGroup.rotation.y = Math.PI * 0.65; // Present continents immediately on load
        globeGroup.rotation.z = targetTiltZ;
        scene.add(globeGroup);

        // 5. Load ONLY the Continents (No black ocean sphere, no background ball)
        loadContinentSphere();

        // 6. Event Listeners
        bindEvents();

        // 7. Responsive sizing
        onWindowResize();

        // 8. Animation Loop
        animate();
    }

    // Ultra-Sharp Floating Continents (Two-pass depth: subtle back continents + bright front continents)
    function loadContinentSphere() {
        const textureUrl = container.dataset.texture || '/static/img/world-continents-sharp.png';
        const loader = new THREE.TextureLoader();

        loader.load(textureUrl, (texture) => {
            texture.generateMipmaps = true;
            texture.minFilter = THREE.LinearMipmapLinearFilter;
            texture.magFilter = THREE.LinearFilter;
            if (renderer && renderer.capabilities && renderer.capabilities.getMaxAnisotropy) {
                texture.anisotropy = renderer.capabilities.getMaxAnisotropy();
            }

            const sphereGeo = new THREE.SphereGeometry(GLOBE_RADIUS, 64, 64);

            // Pass 1: Distant rear continents seen through transparent oceans (subtle, semi-translucent)
            const backMat = new THREE.MeshBasicMaterial({
                map: texture,
                transparent: true,
                opacity: 0.22,
                side: THREE.BackSide,
                depthWrite: false
            });
            const backMesh = new THREE.Mesh(sphereGeo, backMat);
            globeGroup.add(backMesh);

            // Pass 2: Foreground continents facing the user (bright, crisp, intense neon cyan)
            const frontMat = new THREE.MeshBasicMaterial({
                map: texture,
                transparent: true,
                opacity: 0.98,
                side: THREE.FrontSide,
                depthWrite: true
            });
            const frontMesh = new THREE.Mesh(sphereGeo, frontMat);
            globeGroup.add(frontMesh);
        });
    }

    // User Interactions
    function bindEvents() {
        const dom = canvas;

        dom.addEventListener('pointerdown', (e) => {
            isDragging = true;
            prevMouseX = e.clientX;
            prevMouseY = e.clientY;
            rotationVelocityY = 0;
            rotationVelocityX = 0;
        });

        window.addEventListener('pointermove', (e) => {
            if (isDragging) {
                const deltaX = e.clientX - prevMouseX;
                const deltaY = e.clientY - prevMouseY;
                prevMouseX = e.clientX;
                prevMouseY = e.clientY;

                globeGroup.rotation.y += deltaX * 0.005;
                globeGroup.rotation.x += deltaY * 0.005;

                rotationVelocityY = deltaX * 0.005;
                rotationVelocityX = deltaY * 0.005;
            } else {
                // Subtle hover tilt responding to mouse cursor
                const rect = dom.getBoundingClientRect();
                const mouseX = (e.clientX - rect.left) / (rect.width || 500) - 0.5;
                const mouseY = (e.clientY - rect.top) / (rect.height || 500) - 0.5;
                targetTiltX = 0.28 + mouseY * 0.12;
            }
        });

        window.addEventListener('pointerup', () => {
            isDragging = false;
        });

        window.addEventListener('resize', onWindowResize);
    }

    function onWindowResize() {
        if (!container || !renderer || !camera) return;
        const rect = container.getBoundingClientRect();
        width = rect.width || container.clientWidth || 560;
        height = rect.height || container.clientHeight || 560;

        const isMobile = window.innerWidth <= 768;
        camera.position.set(0, isMobile ? 0 : 20, isMobile ? 380 : 500);
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height, false);
    }

    // Animation Loop
    function animate() {
        requestAnimationFrame(animate);

        // Smooth rotation with inertia
        if (!isDragging) {
            rotationVelocityY += (0.0018 - rotationVelocityY) * 0.02;
            rotationVelocityX += (0 - rotationVelocityX) * 0.05;

            globeGroup.rotation.y += rotationVelocityY;
            globeGroup.rotation.x += rotationVelocityX;

            globeGroup.rotation.x += (targetTiltX - globeGroup.rotation.x) * 0.025;
        }

        renderer.render(scene, camera);
    }

    // Bootstrap
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
