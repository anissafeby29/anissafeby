// Procedural, stylized glenohumeral joint anatomy for the arthroscopy simulator.
// Nothing here is loaded from external model files — every structure is built from
// Three.js primitives so the whole app stays a handful of static files.
//
// Coordinate convention used throughout this module and main.js:
//   +X  lateral / toward the scapula body      -X toward the arm / humeral shaft
//   +Y  superior                                 -Y inferior
//   +Z  anterior                                  -Z posterior

const COLORS = {
  bone: 0xede3d0,
  cartilage: 0xe4edef,
  labrum: 0xe3b0a8,
  labrumTorn: 0xd98f86,
  capsule: 0xf5f5f2,
  muscle: 0x8f3636,
  tendon: 0xe9dcc0,
  biceps: 0xe8dcb8,
  footprint: 0xc9b89a,
  metal: 0xcdd3d8
};

/** Orient a Y-aligned object so its local +Y axis points from `from` to `to`. */
export function orientAlong(obj, from, to, THREE) {
  const dir = new THREE.Vector3().subVectors(to, from);
  const len = dir.length();
  dir.normalize();
  const quat = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir);
  obj.quaternion.copy(quat);
  obj.position.copy(from).addScaledVector(dir, len / 2);
  return len;
}

/** Build a tendon/muscle tube along a Catmull-Rom path with a muscle->tendon color gradient. */
function buildFiber(points, radius, THREE, { reverse = false, tendonOnly = false } = {}) {
  const curve = new THREE.CatmullRomCurve3(points.map((p) => new THREE.Vector3(...p)));
  const segments = 32;
  const geometry = new THREE.TubeGeometry(curve, segments, radius, 10, false);
  const uv = geometry.attributes.uv;
  const colorMuscle = new THREE.Color(COLORS.muscle);
  const colorTendon = new THREE.Color(COLORS.tendon);
  const colors = new Float32Array(geometry.attributes.position.count * 3);
  for (let i = 0; i < uv.count; i++) {
    let t = uv.getX(i); // 0 at curve start, 1 at curve end
    if (reverse) t = 1 - t;
    const c = tendonOnly ? colorTendon : colorMuscle.clone().lerp(colorTendon, Math.min(1, t * 1.35));
    colors[i * 3] = c.r;
    colors[i * 3 + 1] = c.g;
    colors[i * 3 + 2] = c.b;
  }
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  const material = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.7, metalness: 0.02 });
  const mesh = new THREE.Mesh(geometry, material);
  mesh.castShadow = true;
  return mesh;
}

function truncateCurve(points, t) {
  // Returns a shortened point list covering [0, t] of the original path (linear param over segments).
  const n = points.length - 1;
  const pos = t * n;
  const idx = Math.floor(pos);
  const frac = pos - idx;
  const out = points.slice(0, idx + 1);
  if (idx < n) {
    const a = points[idx];
    const b = points[idx + 1];
    out.push([a[0] + (b[0] - a[0]) * frac, a[1] + (b[1] - a[1]) * frac, a[2] + (b[2] - a[2]) * frac]);
  }
  return out;
}

export function buildAnatomy(THREE) {
  const group = new THREE.Group();
  const pick = []; // { mesh, key } for raycasting
  const structureGroups = { bone: [], labrum: [], capsule: [], cuff: [], biceps: [] };
  const pathology = {}; // labrum: {normal, bankart}, supraspinatus: {normal, tear}

  const tag = (mesh, key, groupKey) => {
    mesh.userData.structureKey = key;
    pick.push(mesh);
    structureGroups[groupKey].push(mesh);
    group.add(mesh);
    return mesh;
  };

  // ---- Scapula body (extruded blade shape) -------------------------------------------------
  const scapulaShape = new THREE.Shape();
  const scapulaPts = [
    [1.5, 0.85], [1.4, 0.5], [1.5, -0.55], [2.25, -1.5],
    [2.95, -0.55], [3.05, 1.0], [2.35, 1.5], [1.85, 1.15]
  ];
  scapulaShape.moveTo(...scapulaPts[0]);
  scapulaPts.slice(1).forEach((p) => scapulaShape.lineTo(...p));
  scapulaShape.closePath();
  const scapulaGeo = new THREE.ExtrudeGeometry(scapulaShape, { depth: 0.3, bevelEnabled: true, bevelThickness: 0.04, bevelSize: 0.04, bevelSegments: 2 });
  scapulaGeo.translate(0, 0, -0.15);
  const scapula = new THREE.Mesh(scapulaGeo, new THREE.MeshStandardMaterial({ color: COLORS.bone, roughness: 0.85 }));
  scapula.rotation.y = -0.2;
  scapula.rotation.x = 0.08;
  scapula.castShadow = scapula.receiveShadow = true;
  tag(scapula, 'bone', 'bone');

  // ---- Glenoid articular cap (concave "socket") ---------------------------------------------
  const dishCenter = new THREE.Vector3(-0.65, 0, 0);
  const dishRadius = 2.0;
  const dishThetaLength = 0.5;
  const glenoidGeo = new THREE.SphereGeometry(dishRadius, 40, 24, 0, Math.PI * 2, 0, dishThetaLength);
  glenoidGeo.rotateZ(-Math.PI / 2);
  const glenoid = new THREE.Mesh(glenoidGeo, new THREE.MeshStandardMaterial({ color: COLORS.cartilage, roughness: 0.3, side: THREE.DoubleSide }));
  glenoid.position.copy(dishCenter);
  tag(glenoid, 'bone', 'bone');

  const rimX = dishCenter.x + dishRadius * Math.cos(dishThetaLength);
  const rimRadius = dishRadius * Math.sin(dishThetaLength);

  // ---- Humeral head, tuberosities & shaft ----------------------------------------------------
  const headCenter = new THREE.Vector3(-0.15, 0, 0);
  const headRadius = 1.05;
  const head = new THREE.Mesh(
    new THREE.SphereGeometry(headRadius, 48, 32),
    new THREE.MeshStandardMaterial({ color: COLORS.cartilage, roughness: 0.3 })
  );
  head.position.copy(headCenter);
  head.castShadow = true;
  tag(head, 'bone', 'bone');

  const greaterTub = new THREE.Mesh(new THREE.SphereGeometry(0.32, 20, 16), new THREE.MeshStandardMaterial({ color: COLORS.bone, roughness: 0.85 }));
  greaterTub.position.set(-0.55, 0.75, -0.55);
  tag(greaterTub, 'bone', 'bone');

  const lesserTub = new THREE.Mesh(new THREE.SphereGeometry(0.26, 20, 16), new THREE.MeshStandardMaterial({ color: COLORS.bone, roughness: 0.85 }));
  lesserTub.position.set(-0.85, 0.05, 0.65);
  tag(lesserTub, 'bone', 'bone');

  const shaft = new THREE.Mesh(
    new THREE.CylinderGeometry(0.52, 0.4, 3.4, 24),
    new THREE.MeshStandardMaterial({ color: COLORS.bone, roughness: 0.85 })
  );
  orientAlong(shaft, new THREE.Vector3(-0.35, -0.85, 0.08), new THREE.Vector3(-1.35, -3.7, 0.22), THREE);
  shaft.castShadow = shaft.receiveShadow = true;
  tag(shaft, 'bone', 'bone');

  // ---- Acromion, coracoid, clavicle ------------------------------------------------------------
  const acromionCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(2.2, 1.9, 0.1), new THREE.Vector3(0.9, 2.05, -0.35), new THREE.Vector3(-0.35, 1.65, -0.4)
  ]);
  const acromion = new THREE.Mesh(new THREE.TubeGeometry(acromionCurve, 20, 0.28, 10, false), new THREE.MeshStandardMaterial({ color: COLORS.bone, roughness: 0.85 }));
  acromion.castShadow = true;
  tag(acromion, 'bone', 'bone');

  const coracoidCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(1.6, 0.95, 0.55), new THREE.Vector3(0.75, 0.75, 0.95), new THREE.Vector3(0.2, 0.5, 1.05)
  ]);
  const coracoid = new THREE.Mesh(new THREE.TubeGeometry(coracoidCurve, 14, 0.17, 8, false), new THREE.MeshStandardMaterial({ color: COLORS.bone, roughness: 0.85 }));
  tag(coracoid, 'bone', 'bone');

  const clavicleCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(3.0, 3.0, -1.6), new THREE.Vector3(2.6, 2.4, -0.5), new THREE.Vector3(2.25, 2.0, 0.15)
  ]);
  const clavicle = new THREE.Mesh(new THREE.TubeGeometry(clavicleCurve, 16, 0.22, 8, false), new THREE.MeshStandardMaterial({ color: COLORS.bone, roughness: 0.85 }));
  tag(clavicle, 'bone', 'bone');

  // ---- Joint capsule (translucent shell) ------------------------------------------------------
  const capsule = new THREE.Mesh(
    new THREE.SphereGeometry(1.85, 32, 24),
    new THREE.MeshStandardMaterial({ color: COLORS.capsule, roughness: 0.9, transparent: true, opacity: 0.13, side: THREE.DoubleSide, depthWrite: false })
  );
  capsule.position.set(0.4, 0, -0.1);
  capsule.scale.set(1, 0.95, 1.05);
  tag(capsule, 'capsule', 'capsule');

  // ---- Glenoid labrum: normal + Bankart lesion variants ---------------------------------------
  const labrumNormal = new THREE.Mesh(
    new THREE.TorusGeometry(rimRadius, 0.09, 14, 48),
    new THREE.MeshStandardMaterial({ color: COLORS.labrum, roughness: 0.55 })
  );
  labrumNormal.rotation.y = Math.PI / 2;
  labrumNormal.position.set(rimX, 0, 0);
  labrumNormal.userData.structureKey = 'labrum';

  const gapAngle = 1.35; // ~77 degrees missing anteroinferiorly
  const labrumBankartGroup = new THREE.Group();
  const tornArc = new THREE.Mesh(
    new THREE.TorusGeometry(rimRadius, 0.09, 14, 48, Math.PI * 2 - gapAngle),
    new THREE.MeshStandardMaterial({ color: COLORS.labrum, roughness: 0.55 })
  );
  tornArc.rotation.y = Math.PI / 2;
  tornArc.rotation.x = gapAngle / 2 + 3.5; // rotate gap toward the anteroinferior quadrant
  tornArc.position.set(rimX, 0, 0);
  tornArc.userData.structureKey = 'labrum';
  const fragment = new THREE.Mesh(
    new THREE.TorusGeometry(rimRadius * 0.92, 0.075, 10, 24, gapAngle * 0.9),
    new THREE.MeshStandardMaterial({ color: COLORS.labrumTorn, roughness: 0.6 })
  );
  fragment.rotation.y = Math.PI / 2;
  fragment.rotation.x = tornArc.rotation.x - gapAngle * 1.05;
  fragment.position.set(rimX - 0.14, -0.06, 0.02);
  fragment.userData.structureKey = 'labrum';
  fragment.userData.floats = true; // gently animated in the render loop to read as "unstable"
  labrumBankartGroup.add(tornArc, fragment);

  [labrumNormal, tornArc, fragment].forEach((m) => pick.push(m));
  structureGroups.labrum.push(labrumNormal, labrumBankartGroup);
  group.add(labrumNormal, labrumBankartGroup);
  labrumBankartGroup.visible = false;
  pathology.labrum = { normal: labrumNormal, bankart: labrumBankartGroup, fragment };

  // ---- Rotator cuff tendons ---------------------------------------------------------------------
  const supraPts = [[2.0, 1.6, -0.3], [0.9, 1.75, -0.5], [-0.15, 1.35, -0.6], [-0.55, 0.85, -0.55]];
  const infraPts = [[2.3, 0.4, -1.7], [1.0, 0.5, -1.5], [-0.1, 0.55, -0.95], [-0.5, 0.55, -0.75]];
  const teresPts = [[2.2, -0.4, -1.7], [1.0, -0.3, -1.55], [0.0, -0.05, -1.0], [-0.45, -0.05, -0.8]];
  const subscapPts = [[2.4, 0.2, 1.6], [1.2, 0.15, 1.3], [0.0, 0.1, 0.9], [-0.85, 0.1, 0.65]];

  const supraNormal = buildFiber(supraPts, 0.16, THREE);
  supraNormal.userData.structureKey = 'cuff_supraspinatus';
  const infra = buildFiber(infraPts, 0.15, THREE);
  infra.userData.structureKey = 'cuff_infraspinatus';
  const teres = buildFiber(teresPts, 0.12, THREE);
  teres.userData.structureKey = 'cuff_teresMinor';
  const subscap = buildFiber(subscapPts, 0.17, THREE);
  subscap.userData.structureKey = 'cuff_subscapularis';

  [supraNormal, infra, teres, subscap].forEach((m) => pick.push(m));
  structureGroups.cuff.push(infra, teres, subscap); // always-visible members of the cuff toggle

  // Torn supraspinatus: retracted stump + frayed burst + exposed bare footprint on the tuberosity.
  const stumpPts = truncateCurve(supraPts, 0.62);
  const supraTear = new THREE.Group();
  const stump = buildFiber(stumpPts, 0.17, THREE);
  const frayEnd = stumpPts[stumpPts.length - 1];
  const fray = new THREE.Mesh(new THREE.IcosahedronGeometry(0.16, 0), new THREE.MeshStandardMaterial({ color: COLORS.tendon, roughness: 0.9, flatShading: true }));
  fray.position.set(...frayEnd);
  const footprint = new THREE.Mesh(
    new THREE.CircleGeometry(0.34, 20),
    new THREE.MeshStandardMaterial({ color: COLORS.footprint, roughness: 1, side: THREE.DoubleSide })
  );
  footprint.position.set(-0.5, 0.82, -0.55);
  footprint.lookAt(footprint.position.clone().add(new THREE.Vector3(-0.55, 0.6, -0.5)));
  supraTear.add(stump, fray, footprint);
  [stump, fray, footprint].forEach((m) => {
    m.userData.structureKey = 'cuff_supraspinatus';
    pick.push(m);
  });

  group.add(supraNormal, infra, teres, subscap, supraTear);
  supraTear.visible = false;
  pathology.supraspinatus = { normal: supraNormal, tear: supraTear };
  structureGroups.cuff.push(supraNormal, supraTear);

  // ---- Long head of biceps tendon ------------------------------------------------------------
  const bicepsPts = [
    [rimX - 0.1, 0.9, 0.05], [0.35, 0.5, 0.15], [-0.35, -0.15, 0.25],
    [-0.75, -1.0, 0.28], [-1.0, -2.2, 0.3], [-1.15, -3.3, 0.32]
  ];
  const biceps = buildFiber(bicepsPts, 0.09, THREE, { tendonOnly: true });
  biceps.userData.structureKey = 'biceps';
  tag(biceps, 'biceps', 'biceps');

  // ---- Simple probe/instrument (built on demand from main.js) --------------------------------
  function buildProbe() {
    const g = new THREE.Group();
    const shaftMesh = new THREE.Mesh(
      new THREE.CylinderGeometry(0.05, 0.05, 1, 12),
      new THREE.MeshStandardMaterial({ color: COLORS.metal, roughness: 0.25, metalness: 0.85 })
    );
    const tip = new THREE.Mesh(
      new THREE.SphereGeometry(0.06, 12, 10),
      new THREE.MeshStandardMaterial({ color: COLORS.metal, roughness: 0.2, metalness: 0.9 })
    );
    g.add(shaftMesh, tip);
    g.userData.shaftMesh = shaftMesh;
    g.userData.tip = tip;
    return g;
  }

  return {
    group,
    pick,
    structureGroups,
    pathology,
    otherCuff: [infra, teres, subscap],
    buildProbe,
    jointCenter: new THREE.Vector3(0.15, 0.05, -0.05)
  };
}
