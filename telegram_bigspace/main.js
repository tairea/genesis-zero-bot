import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

const AUTHOR_COLORS = {
    'Genesis': 0x00FF88,
    'Vitali': 0xFFD700,
    'Ian Tairea': 0xFF6B6B,
    'Airic Easm': 0x4ECDC4,
    'Oscar C ii 🔺': 0x9B59B6,
    'Philipp': 0x3498DB,
    'Jacob Foster': 0xE67E22,
    'Carl Welty': 0x1ABC9C,
    'Anabela Gonçalves': 0xE91E63,
    'Stefan': 0x00BCD4,
    'Justin Lofton': 0x8BC34A,
};

let scene, camera, renderer, controls;
let messageMeshes = [];
let labelSprites = [];
let sceneData = null;
let raycaster = new THREE.Raycaster();
let mouse = new THREE.Vector2();
let hoveredMesh = null;
let selectedMesh = null;
let labelThreshold = 80;

async function loadScene() {
    const response = await fetch('/big_space_scene.json');
    if (!response.ok) throw new Error('Failed to load scene data');
    return response.json();
}

function createLabel(text, color) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = 320;
    canvas.height = 64;

    ctx.fillStyle = 'rgba(5, 5, 5, 0.88)';
    ctx.roundRect(0, 0, canvas.width, canvas.height, 6);
    ctx.fill();

    ctx.strokeStyle = '#' + parseInt(color).toString(16).padStart(6, '0');
    ctx.lineWidth = 2;
    ctx.roundRect(1, 1, canvas.width - 2, canvas.height - 2, 6);
    ctx.stroke();

    ctx.fillStyle = '#cccccc';
    ctx.font = '13px JetBrains Mono, Fira Code, monospace';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';

    // Word wrap
    const words = text.split(' ');
    let line = '';
    let y = 8;
    const maxWidth = canvas.width - 16;
    for (const word of words) {
        const test = line + word + ' ';
        if (ctx.measureText(test).width > maxWidth && line !== '') {
            ctx.fillText(line.trim(), 8, y);
            line = word + ' ';
            y += 16;
            if (y > canvas.height - 20) { line += '...'; break; }
        } else {
            line = test;
        }
    }
    ctx.fillText(line.trim(), 8, y);

    const texture = new THREE.CanvasTexture(canvas);
    texture.minFilter = THREE.LinearFilter;
    const mat = new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: false });
    const sprite = new THREE.Sprite(mat);
    sprite.scale.set(50, 10, 1);
    return sprite;
}

function init() {
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x050505);

    camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 100000);
    camera.position.set(0, 0, 300);

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    document.body.appendChild(renderer.domElement);

    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.mouseButtons = {
        LEFT: THREE.MOUSE.ROTATE,
        MIDDLE: THREE.MOUSE.DOLLY,
        RIGHT: THREE.MOUSE.PAN
    };
    controls.minDistance = 5;
    controls.maxDistance = 2000;

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(100, 100, 50);
    scene.add(dirLight);

    window.addEventListener('resize', onWindowResize);
    renderer.domElement.addEventListener('mousemove', onMouseMove);
    renderer.domElement.addEventListener('click', onClick);

    loadScene().then(data => {
        sceneData = data;
        buildScene(data);
        updateUI(data);
        document.getElementById('loading').style.display = 'none';
        document.getElementById('ui').style.display = 'block';
        animate();
    }).catch(err => {
        console.error('Error:', err);
        document.getElementById('loading').textContent = 'Error: ' + err.message;
    });
}

function buildScene(data) {
    const messages = data.messages;
    const authors = data.authors;
    const replyChains = data.reply_chains;

    // Time range
    const times = messages.map(m => m.unixtime);
    const timeMin = Math.min(...times);
    const timeMax = Math.max(...times);
    const timeRange = timeMax - timeMin || 1;

    const sphereGeo = new THREE.SphereGeometry(0.5, 10, 10);
    const posById = new Map();

    // Author Y positions
    const authorY = {};
    authors.forEach((a, i) => {
        authorY[a.name] = (i - authors.length / 2) * 8;
    });

    // Spawn messages
    messages.forEach(msg => {
        const color = AUTHOR_COLORS[msg.author] || 0xffffff;
        const mat = new THREE.MeshStandardMaterial({
            color,
            roughness: 0.7,
            metalness: 0.3,
            emissive: color,
            emissiveIntensity: msg.link_count > 0 ? 0.2 : 0.05,
        });

        const scale = 0.3 + Math.min(msg.link_count * 0.12, 1.2);
        const mesh = new THREE.Mesh(sphereGeo, mat);

        // X = time
        const t = (msg.unixtime - timeMin) / timeRange;
        const x = (t - 0.5) * 1000;
        // Y = author bucket
        const y = authorY[msg.author] || 0;
        // Z = text length
        const z = (msg.text_length % 100) - 50;

        mesh.position.set(x, y, z);
        mesh.scale.setScalar(scale);
        mesh.userData = { msg, author: msg.author, color };

        scene.add(mesh);
        messageMeshes.push(mesh);
        posById.set(msg.msg_id, mesh.position);
    });

    // Reply chain lines
    const maxLines = Math.min(replyChains.length, 800);
    for (let i = 0; i < maxLines; i++) {
        const reply = replyChains[i];
        const from = posById.get(reply.from);
        const to = posById.get(reply.to);
        if (from && to) {
            const color = AUTHOR_COLORS[reply.author] || 0xffffff;
            const lineMat = new THREE.LineBasicMaterial({
                color,
                transparent: true,
                opacity: 0.1
            });
            const geo = new THREE.BufferGeometry().setFromPoints([from, to]);
            scene.add(new THREE.Line(geo, lineMat));
        }
    }

    // Labels for nearby nodes
    messages.forEach(msg => {
        const text = (msg.text_preview || '').replace(/\n/g, ' ').trim();
        if (text.length < 4) return;
        const color = AUTHOR_COLORS[msg.author] || 0xffffff;
        const sprite = createLabel(text.substring(0, 60), color);
        const pos = posById.get(msg.msg_id);
        if (pos) {
            sprite.position.copy(pos);
            sprite.position.y += 3;
            sprite.visible = false;
            sprite.userData = { msgId: msg.msg_id };
            scene.add(sprite);
            labelSprites.push(sprite);
        }
    });

    // Axis arrows
    addAxes(messages.length, authors.length);
}

function addAxes(numMessages, numAuthors) {
    const spread = 520;

    // X axis arrow (time)
    const xArrow = new THREE.ArrowHelper(
        new THREE.Vector3(1, 0, 0),
        new THREE.Vector3(-spread, -numAuthors * 4 - 10, -60),
        900, 0x444444, 20, 10
    );
    scene.add(xArrow);

    const xLabel = makeAxisLabel('TIME (Feb → Apr)');
    xLabel.position.set(400, -numAuthors * 4 - 20, -60);
    scene.add(xLabel);

    // Y axis arrow (author)
    const yArrow = new THREE.ArrowHelper(
        new THREE.Vector3(0, 1, 0),
        new THREE.Vector3(-570, -numAuthors * 4, -60),
        numAuthors * 8 + 20, 0x444444, 20, 10
    );
    scene.add(yArrow);

    const yLabel = makeAxisLabel('AUTHOR');
    yLabel.position.set(-570, 0, -60);
    scene.add(yLabel);

    // Z axis arrow (text length)
    const zArrow = new THREE.ArrowHelper(
        new THREE.Vector3(0, 0, 1),
        new THREE.Vector3(-570, -numAuthors * 4, -100),
        80, 0x333333, 15, 8
    );
    scene.add(zArrow);

    const zLabel = makeAxisLabel('TEXT LENGTH');
    zLabel.position.set(-570, -numAuthors * 4, 40);
    scene.add(zLabel);
}

function makeAxisLabel(text) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = 256;
    canvas.height = 32;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#666666';
    ctx.font = 'bold 16px JetBrains Mono, monospace';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, canvas.width / 2, canvas.height / 2);
    const tex = new THREE.CanvasTexture(canvas);
    const mat = new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false });
    const sprite = new THREE.Sprite(mat);
    sprite.scale.set(80, 10, 1);
    return sprite;
}

function updateLabels() {
    const camPos = camera.position;
    labelSprites.forEach(sprite => {
        if (sprite.userData.msgId) {
            const dist = sprite.position.distanceTo(camPos);
            if (dist < labelThreshold) {
                sprite.visible = true;
                const scale = Math.max(0.4, 1.2 - dist / labelThreshold);
                sprite.scale.set(50 * scale, 10 * scale, 1);
            } else {
                sprite.visible = false;
            }
        }
        sprite.lookAt(camPos);
    });
}

function updateUI(data) {
    document.getElementById('topic-name').textContent = data.meta.name;
    document.getElementById('msg-count').textContent = data.messages.length;
    document.getElementById('author-count').textContent = data.authors.length;
    document.getElementById('link-count').textContent = data.links.length;

    const legend = document.getElementById('legend');
    legend.innerHTML = '';
    data.authors.forEach(a => {
        const c = AUTHOR_COLORS[a.name] || 0xffffff;
        const hex = '#' + c.toString(16).padStart(6, '0');
        legend.innerHTML += `<div class="legend-item">
            <span class="legend-dot" style="background:${hex}"></span>
            ${a.name} (${a.message_count})
        </div>`;
    });
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

function onMouseMove(event) {
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(messageMeshes);

    if (hoveredMesh && hoveredMesh !== selectedMesh) {
        hoveredMesh.material.emissiveIntensity = hoveredMesh.userData.msg.link_count > 0 ? 0.2 : 0.05;
    }

    if (intersects.length > 0) {
        hoveredMesh = intersects[0].object;
        hoveredMesh.material.emissiveIntensity = 0.5;
        document.body.style.cursor = 'pointer';

        const info = document.getElementById('hover-info');
        const msg = hoveredMesh.userData.msg;
        const color = hoveredMesh.userData.color;
        const hexColor = '#' + color.toString(16).padStart(6, '0');

        info.querySelector('.author-dot').style.background = hexColor;
        info.querySelector('.author-name').textContent = msg.author;
        info.querySelector('.date').textContent = msg.date;
        const text = (msg.text_preview || '').replace(/\n/g, ' ');
        info.querySelector('.text').textContent = text.substring(0, 250) + (text.length > 250 ? '...' : '');
        info.querySelector('.links').textContent = msg.link_count > 0 ? `🔗 ${msg.link_count} link(s)` : '';
        info.style.display = 'block';
    } else {
        hoveredMesh = null;
        document.getElementById('hover-info').style.display = 'none';
        document.body.style.cursor = 'default';
    }
}

function onClick(event) {
    if (hoveredMesh) {
        if (selectedMesh) {
            selectedMesh.material.emissiveIntensity = selectedMesh.userData.msg.link_count > 0 ? 0.2 : 0.05;
        }
        selectedMesh = hoveredMesh;
        selectedMesh.material.emissiveIntensity = 1.0;
        controls.target.copy(selectedMesh.position);
        document.getElementById('hover-info').style.borderColor = 'rgba(0,255,136,0.5)';
    }
}

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    updateLabels();
    renderer.render(scene, camera);
}

init();
