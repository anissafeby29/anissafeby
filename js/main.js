import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { buildAnatomy, orientAlong } from './anatomy.js';
import { STRUCTURES, PORTALS, PATHOLOGIES } from './data.js';

// ============================================================================
// DOM references
// ============================================================================
const viewport = document.getElementById('viewport');
const canvas = document.getElementById('three-canvas');
const loadingEl = document.getElementById('loading');
const scopeOverlay = document.getElementById('scopeOverlay');
const hudPortal = document.getElementById('hudPortal');
const hudStructure = document.getElementById('hudStructure');
const depthFill = document.getElementById('depthFill');

const modeExternalBtn = document.getElementById('modeExternalBtn');
const modeArthroBtn = document.getElementById('modeArthroBtn');
const panelToggle = document.getElementById('panelToggle');
const leftPanel = document.getElementById('leftPanel');
const rightPanel = document.getElementById('rightPanel');
const helpText = document.getElementById('helpText');

const infoCard = document.getElementById('infoCard');
const infoName = document.getElementById('infoName');
const infoNote = document.getElementById('infoNote');

const pathologySelect = document.getElementById('pathologySelect');
const pathologySummary = document.getElementById('pathologySummary');

const portalDesc = document.getElementById('portalDesc');
const depthSlider = document.getElementById('depthSlider');
const probeToggle = document.getElementById('probeToggle');
const probeDepthSlider = document.getElementById('probeDepthSlider');

// ============================================================================
// Renderer / scene / camera
// ============================================================================
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = false;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x070a0d);
scene.fog = new THREE.Fog(0x070a0d, 7, 17);

const EXTERNAL_FOV = 45;
const ARTHRO_FOV = 82;
const camera = new THREE.PerspectiveCamera(EXTERNAL_FOV, 1, 0.03, 100);
const EXTERNAL_START = new THREE.Vector3(4.6, 3.2, 6.1);
camera.position.copy(EXTERNAL_START);

function resize() {
  const w = viewport.clientWidth || 1;
  const h = viewport.clientHeight || 1;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
window.addEventListener('resize', resize);
new ResizeObserver(resize).observe(viewport);

// ---- Lights -----------------------------------------------------------------
scene.add(new THREE.HemisphereLight(0xbdd6ff, 0x1a140f, 0.55));
const keyLight = new THREE.DirectionalLight(0xffffff, 1.15);
keyLight.position.set(4, 6, 3);
scene.add(keyLight);
const fillLight = new THREE.DirectionalLight(0x88aaff, 0.35);
fillLight.position.set(-5, 2, -4);
scene.add(fillLight);
const rimLight = new THREE.PointLight(0x3ea6ff, 0.5, 12);
rimLight.position.set(-2, 1, -3);
scene.add(rimLight);

const scopeLight = new THREE.SpotLight(0xfff7e8, 0, 9, Math.PI / 4.6, 0.55, 1.1);
scopeLight.visible = false;
scene.add(scopeLight, scopeLight.target);

// ============================================================================
// Anatomy
// ============================================================================
const anatomy = buildAnatomy(THREE);
scene.add(anatomy.group);

const probe = anatomy.buildProbe();
probe.visible = false;
scene.add(probe);

const orbit = new OrbitControls(camera, renderer.domElement);
orbit.target.copy(anatomy.jointCenter);
orbit.enableDamping = true;
orbit.dampingFactor = 0.08;
orbit.minDistance = 2.4;
orbit.maxDistance = 11;
orbit.update();

// ============================================================================
// Application state
// ============================================================================
const structureState = { bone: true, labrum: true, capsule: true, cuff: true, biceps: true };

const state = {
  mode: 'external',
  portalKey: 'posterior',
  pathologyKey: 'normal',
  transition: null,
  arthro: {
    yaw: 0, pitch: 0, depthT: 0.32,
    pivot: new THREE.Vector3(), insertionDir: new THREE.Vector3(0, 0, -1),
    minDepth: 0.5, maxDepth: 2,
    right: new THREE.Vector3(1, 0, 0), up: new THREE.Vector3(0, 1, 0)
  },
  probe: { show: false, depthT: 0.5 }
};

let savedExternal = { pos: EXTERNAL_START.clone(), target: anatomy.jointCenter.clone() };

// ============================================================================
// Visibility / pathology
// ============================================================================
function applyPathology() {
  const p = state.pathologyKey;
  const labrumOn = structureState.labrum;
  const cuffOn = structureState.cuff;

  anatomy.pathology.labrum.normal.visible = labrumOn && p !== 'bankart';
  anatomy.pathology.labrum.bankart.visible = labrumOn && p === 'bankart';

  anatomy.pathology.supraspinatus.normal.visible = cuffOn && p !== 'cuffTear';
  anatomy.pathology.supraspinatus.tear.visible = cuffOn && p === 'cuffTear';
  anatomy.otherCuff.forEach((m) => { m.visible = cuffOn; });

  pathologySummary.textContent = PATHOLOGIES[p].summary;
}

document.querySelectorAll('[data-structure]').forEach((el) => {
  el.addEventListener('change', () => {
    const key = el.dataset.structure;
    structureState[key] = el.checked;
    if (key === 'labrum' || key === 'cuff') {
      applyPathology();
    } else if (anatomy.structureGroups[key]) {
      anatomy.structureGroups[key].forEach((m) => { m.visible = el.checked; });
    }
  });
});

pathologySelect.addEventListener('change', () => {
  state.pathologyKey = pathologySelect.value;
  applyPathology();
});

// ============================================================================
// Structure picking (external click + arthroscopic crosshair)
// ============================================================================
const raycaster = new THREE.Raycaster();
const ndc = new THREE.Vector2();
const activeHighlights = [];

function isVisibleInHierarchy(obj) {
  let o = obj;
  while (o) {
    if (!o.visible) return false;
    o = o.parent;
  }
  return true;
}

function pickCandidates() {
  return anatomy.pick.filter(isVisibleInHierarchy);
}

function highlightMesh(mesh) {
  if (!mesh.material || mesh.material.emissive === undefined) return;
  activeHighlights.push({ mesh, start: performance.now() });
}

function updateHighlights(now) {
  for (let i = activeHighlights.length - 1; i >= 0; i--) {
    const h = activeHighlights[i];
    const t = (now - h.start) / 700;
    if (t >= 1) {
      h.mesh.material.emissiveIntensity = 0;
      activeHighlights.splice(i, 1);
      continue;
    }
    h.mesh.material.emissive.set(0x3ea6ff);
    h.mesh.material.emissiveIntensity = 0.85 * (1 - t);
  }
}

function selectStructure(mesh) {
  const info = STRUCTURES[mesh.userData.structureKey];
  if (!info) return;
  infoCard.classList.remove('hidden');
  infoName.textContent = info.name;
  infoNote.textContent = info.note;
  highlightMesh(mesh);
}

canvas.addEventListener('click', (e) => {
  if (state.mode !== 'external' || state.transition) return;
  const rect = canvas.getBoundingClientRect();
  ndc.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
  ndc.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
  raycaster.setFromCamera(ndc, camera);
  const hits = raycaster.intersectObjects(pickCandidates(), false);
  if (hits.length) selectStructure(hits[0].object);
});

let lastHudCheck = 0;
function updateArthroHud(now) {
  if (now - lastHudCheck < 140) return;
  lastHudCheck = now;
  raycaster.setFromCamera({ x: 0, y: 0 }, camera);
  const hits = raycaster.intersectObjects(pickCandidates(), false);
  if (hits.length && hits[0].distance < 3.2) {
    const info = STRUCTURES[hits[0].object.userData.structureKey];
    hudStructure.textContent = info ? info.name : '—';
  } else {
    hudStructure.textContent = '—';
  }
}

// ============================================================================
// Camera transitions
// ============================================================================
function easeInOutCubic(t) {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

function animateCameraTo(pos, lookAt, duration, opts = {}) {
  const dummy = new THREE.Object3D();
  dummy.position.copy(pos);
  dummy.lookAt(lookAt);
  state.transition = {
    startPos: camera.position.clone(),
    startQuat: camera.quaternion.clone(),
    endPos: pos.clone(),
    endQuat: dummy.quaternion.clone(),
    startFov: camera.fov,
    endFov: opts.fov !== undefined ? opts.fov : camera.fov,
    t0: performance.now(),
    duration,
    onDone: opts.onDone
  };
}

function updateTransition(now) {
  const tr = state.transition;
  if (!tr) return false;
  const t = Math.min(1, (now - tr.t0) / tr.duration);
  const e = easeInOutCubic(t);
  camera.position.lerpVectors(tr.startPos, tr.endPos, e);
  camera.quaternion.slerpQuaternions(tr.startQuat, tr.endQuat, e);
  if (tr.startFov !== tr.endFov) {
    camera.fov = THREE.MathUtils.lerp(tr.startFov, tr.endFov, e);
    camera.updateProjectionMatrix();
  }
  if (t >= 1) {
    state.transition = null;
    if (tr.onDone) tr.onDone();
    return false;
  }
  return true;
}

// ============================================================================
// Arthroscopic scope controller
// ============================================================================
function computeArthroBasis() {
  const dir = state.arthro.insertionDir;
  const worldUp = Math.abs(dir.y) > 0.92 ? new THREE.Vector3(1, 0, 0) : new THREE.Vector3(0, 1, 0);
  const right = new THREE.Vector3().crossVectors(dir, worldUp).normalize();
  const up = new THREE.Vector3().crossVectors(right, dir).normalize();
  state.arthro.right = right;
  state.arthro.up = up;
}

function arthroLookDir() {
  const { insertionDir, right, up, yaw, pitch } = state.arthro;
  return insertionDir.clone().applyAxisAngle(up, yaw).applyAxisAngle(right, pitch).normalize();
}

function arthroCamPos() {
  const { pivot, insertionDir, minDepth, maxDepth, depthT } = state.arthro;
  const depth = THREE.MathUtils.lerp(minDepth, maxDepth, depthT);
  return pivot.clone().addScaledVector(insertionDir, depth);
}

function updateArthroCameraLive() {
  const pos = arthroCamPos();
  camera.position.copy(pos);
  camera.lookAt(pos.clone().add(arthroLookDir()));
}

function setupPortalState(portalKey) {
  state.portalKey = portalKey;
  const portal = PORTALS[portalKey];
  const pivot = new THREE.Vector3(...portal.position);
  const target = new THREE.Vector3(...portal.target);
  const dist = pivot.distanceTo(target);
  state.arthro.pivot = pivot;
  state.arthro.insertionDir = target.clone().sub(pivot).normalize();
  state.arthro.minDepth = dist * 0.35;
  state.arthro.maxDepth = dist * 1.6;
  state.arthro.yaw = 0;
  state.arthro.pitch = 0;
  state.arthro.depthT = 0.16;
  computeArthroBasis();
}

function flyToArthroPose(duration) {
  const pos = arthroCamPos();
  const look = pos.clone().add(arthroLookDir());
  animateCameraTo(pos, look, duration, { fov: ARTHRO_FOV });
}

function updatePortalUI() {
  const portal = PORTALS[state.portalKey];
  document.querySelectorAll('.portal-btn').forEach((b) => b.classList.toggle('active', b.dataset.portal === state.portalKey));
  document.querySelectorAll('.pd-dot').forEach((d) => d.classList.toggle('active', d.dataset.portal === state.portalKey));
  portalDesc.textContent = portal.desc;
  hudPortal.textContent = portal.name;
  depthSlider.value = String(Math.round(state.arthro.depthT * 100));
}

function setModeButtons() {
  const ext = state.mode === 'external';
  modeExternalBtn.classList.toggle('active', ext);
  modeExternalBtn.setAttribute('aria-selected', String(ext));
  modeArthroBtn.classList.toggle('active', !ext);
  modeArthroBtn.setAttribute('aria-selected', String(!ext));
  rightPanel.classList.toggle('hidden', ext);
  helpText.textContent = ext
    ? 'Drag to orbit · Scroll to zoom · Click a structure for info'
    : 'Drag to look around · Scroll to advance the scope · Switch portals on the right';
}

function enterArthroMode(portalKey) {
  if (state.mode === 'external') {
    savedExternal = { pos: camera.position.clone(), target: orbit.target.clone() };
  }
  state.mode = 'arthroscopic';
  orbit.enabled = false;
  scopeOverlay.classList.remove('hidden');
  scopeLight.visible = true;
  setModeButtons();
  setupPortalState(portalKey);
  flyToArthroPose(900);
  updatePortalUI();
  syncProbeVisibility();
}

function exitToExternal() {
  state.mode = 'external';
  orbit.enabled = false;
  scopeOverlay.classList.add('hidden');
  scopeLight.visible = false;
  setModeButtons();
  probe.visible = false;
  animateCameraTo(savedExternal.pos, savedExternal.target, 900, {
    fov: EXTERNAL_FOV,
    onDone: () => {
      orbit.enabled = true;
      orbit.target.copy(savedExternal.target);
      orbit.update();
    }
  });
}

function switchPortal(portalKey) {
  setupPortalState(portalKey);
  flyToArthroPose(700);
  updatePortalUI();
  syncProbeVisibility();
}

modeExternalBtn.addEventListener('click', () => { if (state.mode !== 'external') exitToExternal(); });
modeArthroBtn.addEventListener('click', () => { if (state.mode !== 'arthroscopic') enterArthroMode(state.portalKey); });

document.querySelectorAll('.portal-btn').forEach((btn) => {
  btn.addEventListener('click', () => {
    if (state.mode !== 'arthroscopic' || state.transition) return;
    if (btn.dataset.portal !== state.portalKey) switchPortal(btn.dataset.portal);
  });
});

document.querySelectorAll('.pd-dot').forEach((dot) => {
  dot.addEventListener('click', () => {
    if (state.transition) return;
    if (state.mode !== 'arthroscopic') enterArthroMode(dot.dataset.portal);
    else if (dot.dataset.portal !== state.portalKey) switchPortal(dot.dataset.portal);
  });
});

// ---- Pointer / wheel look & depth control ------------------------------------
let dragging = false;
let lastX = 0;
let lastY = 0;

canvas.addEventListener('pointerdown', (e) => {
  if (state.mode !== 'arthroscopic') return;
  dragging = true;
  lastX = e.clientX;
  lastY = e.clientY;
});
window.addEventListener('pointermove', (e) => {
  if (!dragging || state.mode !== 'arthroscopic') return;
  const dx = e.clientX - lastX;
  const dy = e.clientY - lastY;
  lastX = e.clientX;
  lastY = e.clientY;
  const s = 0.0045;
  state.arthro.yaw = THREE.MathUtils.clamp(state.arthro.yaw - dx * s, -1.05, 1.05);
  state.arthro.pitch = THREE.MathUtils.clamp(state.arthro.pitch - dy * s, -1.05, 1.05);
});
window.addEventListener('pointerup', () => { dragging = false; });

canvas.addEventListener('wheel', (e) => {
  if (state.mode !== 'arthroscopic') return;
  e.preventDefault();
  state.arthro.depthT = THREE.MathUtils.clamp(state.arthro.depthT + e.deltaY * 0.0006, 0, 1);
  depthSlider.value = String(Math.round(state.arthro.depthT * 100));
}, { passive: false });

depthSlider.addEventListener('input', () => {
  state.arthro.depthT = Number(depthSlider.value) / 100;
});

// ============================================================================
// Working-portal probe
// ============================================================================
function updateProbeTransform() {
  const portal = PORTALS[state.portalKey];
  const working = PORTALS[portal.workingPortal];
  const pivot = new THREE.Vector3(...working.position);
  const target = new THREE.Vector3(...working.target);
  const dir = target.clone().sub(pivot).normalize();
  const dist = pivot.distanceTo(target);
  const depth = THREE.MathUtils.lerp(dist * 0.25, dist * 1.5, state.probe.depthT);
  const tipPos = pivot.clone().addScaledVector(dir, depth);
  const shaft = probe.userData.shaftMesh;
  const len = orientAlong(shaft, pivot, tipPos, THREE);
  shaft.scale.set(1, len, 1);
  probe.userData.tip.position.copy(tipPos);
}

function syncProbeVisibility() {
  probe.visible = state.probe.show && state.mode === 'arthroscopic';
  if (probe.visible) updateProbeTransform();
}

probeToggle.addEventListener('change', () => {
  state.probe.show = probeToggle.checked;
  syncProbeVisibility();
});
probeDepthSlider.addEventListener('input', () => {
  state.probe.depthT = Number(probeDepthSlider.value) / 100;
  if (probe.visible) updateProbeTransform();
});

// ============================================================================
// Mobile panel toggle
// ============================================================================
panelToggle.addEventListener('click', () => {
  leftPanel.classList.toggle('open');
  rightPanel.classList.toggle('open');
});

// ============================================================================
// Render loop
// ============================================================================
function animateFragmentFloat(now) {
  const frag = anatomy.pathology.labrum.fragment;
  const t = now * 0.0016;
  frag.position.y = -0.06 + Math.sin(t) * 0.025;
  frag.position.x = anatomy.pathology.labrum.normal.position.x - 0.14 + Math.sin(t * 0.7) * 0.015;
}

function animate() {
  requestAnimationFrame(animate);
  const now = performance.now();
  const transitioning = updateTransition(now);

  if (!transitioning) {
    if (state.mode === 'external') {
      orbit.update();
    } else {
      updateArthroCameraLive();
      updateArthroHud(now);
    }
  }

  if (scopeLight.visible) {
    scopeLight.position.copy(camera.position);
    scopeLight.target.position.copy(camera.position.clone().add(arthroLookDir()));
  }

  updateHighlights(now);
  animateFragmentFloat(now);

  if (state.mode === 'arthroscopic') {
    depthFill.style.width = `${Math.round(state.arthro.depthT * 100)}%`;
  }

  renderer.render(scene, camera);
}

// ============================================================================
// Init
// ============================================================================
applyPathology();
updatePortalUI();
resize();
requestAnimationFrame(() => loadingEl.classList.add('hidden'));
animate();
