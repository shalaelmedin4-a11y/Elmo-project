// Stylised human: Mixamo skeleton + clips (Xbot rig) driving sculpted body parts, a face with
// animated eyes/lids/mouth, hair and clothes. Inverted-hull outlines give the clean cartoon line.
import * as THREE from 'three';
import * as SU from 'three/addons/utils/SkeletonUtils.js';

const UP = new THREE.Vector3(0, 1, 0);
const X = new THREE.Vector3(1, 0, 0), Y = new THREE.Vector3(0, 1, 0), Z = new THREE.Vector3(0, 0, 1);

export const OUTLINE = new THREE.MeshBasicMaterial({ color: 0x1d1a22, side: THREE.BackSide });
OUTLINE.onBeforeCompile = sh => {
  sh.uniforms.thick = { value: 0.0055 };
  sh.vertexShader = 'uniform float thick;\n' + sh.vertexShader.replace('#include <begin_vertex>', '#include <begin_vertex>\n transformed += normalize(normal) * thick;');
};
export function outline(mesh, k = 1) {
  const o = new THREE.Mesh(mesh.geometry, OUTLINE);
  o.scale.setScalar(1); o.userData.outline = true; o.renderOrder = -1;
  if (k !== 1) { const m = OUTLINE.clone(); m.onBeforeCompile = sh => { sh.uniforms.thick = { value: 0.0055 * k }; sh.vertexShader = 'uniform float thick;\n' + sh.vertexShader.replace('#include <begin_vertex>', '#include <begin_vertex>\n transformed += normalize(normal) * thick;'); }; o.material = m; }
  mesh.add(o); return o;
}

function latheSeg(len, prof, sx = 1, sz = 1, seg = 22) {
  const raw = prof.map(([t, r]) => new THREE.Vector2(Math.max(r, 0.0005), t * len));
  const pts = new THREE.SplineCurve(raw).getPoints(Math.max(10, prof.length * 5));
  pts.unshift(new THREE.Vector2(0.0001, pts[0].y)); pts.push(new THREE.Vector2(0.0001, pts[pts.length - 1].y)); // closed ends
  const g = new THREE.LatheGeometry(pts, seg); g.scale(sx, 1, sz); g.computeVertexNormals(); return g;
}
const ell = (rx, ry, rz, ws = 24, hs = 16) => { const g = new THREE.SphereGeometry(1, ws, hs); g.scale(rx, ry, rz); return g; };
const mat = (c, rough = 0.85) => new THREE.MeshStandardMaterial({ color: c, roughness: rough, metalness: 0 });

function irisTex(col) {
  const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d');
  g.fillStyle = '#f7f4ef'; g.fillRect(0, 0, 128, 128);
  const gr = g.createRadialGradient(64, 64, 6, 64, 64, 34); const cc = new THREE.Color(col);
  gr.addColorStop(0, '#' + cc.clone().multiplyScalar(1.25).getHexString()); gr.addColorStop(0.75, '#' + cc.getHexString()); gr.addColorStop(1, '#' + cc.clone().multiplyScalar(0.45).getHexString());
  g.fillStyle = gr; g.beginPath(); g.arc(64, 64, 34, 0, 7); g.fill();
  g.strokeStyle = 'rgba(0,0,0,0.25)'; g.lineWidth = 1.2; for (let i = 0; i < 40; i++) { const a = i / 40 * 6.283; g.beginPath(); g.moveTo(64 + Math.cos(a) * 15, 64 + Math.sin(a) * 15); g.lineTo(64 + Math.cos(a) * 32, 64 + Math.sin(a) * 32); g.stroke(); }
  g.fillStyle = '#141216'; g.beginPath(); g.arc(64, 64, 14, 0, 7); g.fill();
  g.fillStyle = 'rgba(255,255,255,0.95)'; g.beginPath(); g.arc(52, 52, 6, 0, 7); g.fill();
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}

export class Person {
  constructor(gltf, scene, o) {
    this.o = o;
    this.root = SU.clone(gltf.scene);
    this.root.traverse(n => { if (n.isMesh) n.visible = false; });
    this.bones = {};
    this.root.traverse(n => { if (n.isBone) this.bones[n.name.replace('mixamorig', '').replace(':', '')] = n; });
    this.scale = (o.height || 1.75) / 1.8;
    this.wrap = new THREE.Group(); this.wrap.add(this.root); this.wrap.scale.setScalar(this.scale); scene.add(this.wrap);
    this.root.updateMatrixWorld(true);
    const C = o.colors, B = this.bones, ol = o.outline !== false;
    const M = { shirt: mat(C.shirt), pants: mat(C.pants), skin: mat(C.skin, 0.7), shoes: mat(C.shoes, 0.6), hair: mat(C.hair, 0.75), skirt: mat(C.skirt || C.pants) };
    this.M = M;
    const att = (bone, child, geo, m, off = 0, line = ol) => {
      const ws = new THREE.Vector3(); bone.getWorldScale(ws);
      const mesh = new THREE.Mesh(geo, m); mesh.castShadow = true; mesh.receiveShadow = true;
      const dir = child ? child.position.clone().normalize() : UP.clone();
      mesh.quaternion.setFromUnitVectors(UP, dir); mesh.scale.setScalar(1 / ws.x);
      if (off) mesh.position.copy(dir.clone().multiplyScalar(off / ws.x));
      bone.add(mesh); if (line) outline(mesh); return mesh;
    };
    const len = (a, b) => { const p = new THREE.Vector3(), q = new THREE.Vector3(); a.getWorldPosition(p); b.getWorldPosition(q); return p.distanceTo(q); };
    const fem = !!o.female;
    // torso
    const Lp = len(B.Hips, B.Spine), La = len(B.Spine, B.Spine2), Lc = len(B.Spine2, B.Neck);
    att(B.Hips, B.Spine, latheSeg(Lp + 0.07, [[0, 0.06], [0.15, fem ? 0.165 : 0.152], [0.55, fem ? 0.172 : 0.158], [1, 0.15]], 1.12, 0.76), fem && o.skirt ? M.skirt : M.pants, -0.09);
    att(B.Spine, B.Neck, latheSeg(La + Lc + 0.06, fem ? [[0, 0.15], [0.3, 0.135], [0.62, 0.165], [0.8, 0.16], [0.93, 0.11], [1, 0.05]] : [[0, 0.155], [0.25, 0.15], [0.55, 0.165], [0.76, 0.18], [0.9, 0.16], [0.97, 0.1], [1, 0.05]], fem ? 1.12 : 1.16, 0.72, 28), M.shirt, -0.04);
    if (fem && o.skirt) att(B.Hips, B.Spine, latheSeg(0.42, [[0, 0.2], [0.5, 0.2], [1, 0.16]], 1.15, 0.85), M.skirt, -0.42);
    // neck, head
    att(B.Neck, B.Head, latheSeg(len(B.Neck, B.Head) + 0.04, [[0, 0.05], [1, 0.047]]), M.skin, -0.02, false);
    const Lh = len(B.Head, B.HeadTop_End);
    // head built in world space (bind pose faces +z) then parented, so the face points forward
    const hp = new THREE.Vector3(); B.Head.getWorldPosition(hp);
    const S = this.scale;
    const place = (mesh, x, y, z) => { mesh.position.set(hp.x + x * S, hp.y + y * S, hp.z + z * S); mesh.scale.multiplyScalar(S); scene.add(mesh); mesh.updateMatrixWorld(); B.Head.attach(mesh); return mesh; };
    // egg-shaped head: narrow chin, wide cranium (lathe profile, deeper front-to-back)
    const headG = (() => { const pr = [[0, 0.002], [0.04, 0.034], [0.1, 0.055], [0.22, 0.072], [0.42, 0.083], [0.62, 0.085], [0.8, 0.078], [0.93, 0.055], [1, 0.002]].map(([t, r]) => new THREE.Vector2(r, t * 0.215));
      const g = new THREE.LatheGeometry(new THREE.SplineCurve(pr).getPoints(40), 40); g.scale(1, 1, 1.12); g.computeVertexNormals(); return g; })();
    const head = new THREE.Mesh(headG, M.skin); head.castShadow = true; place(head, 0, -0.005, 0.004); if (ol) outline(head);
    for (const s of [1, -1]) { const ear = new THREE.Mesh(ell(0.014, 0.026, 0.018), M.skin); place(ear, s * 0.082, 0.095, -0.005); if (ol) outline(ear, 0.6); }
    const nose = new THREE.Mesh(ell(0.011, 0.017, 0.012), M.skin); nose.rotation.x = 0.25; place(nose, 0, 0.088, 0.093);
    // eyes
    this.eyes = []; this.lids = [];
    const irisM = new THREE.MeshStandardMaterial({ map: irisTex(o.eyes || 0x4e6a3a), roughness: 0.25 });
    for (const s of [1, -1]) {
      const eye = new THREE.Mesh(new THREE.SphereGeometry(0.0165, 24, 16), irisM);
      eye.rotation.y = -Math.PI / 2; // texture centre (u=0.5) to the front
      const pivot = new THREE.Group(); pivot.add(eye); eye.rotation.set(0, -Math.PI / 2, 0);
      place(pivot, s * 0.031, 0.113, 0.077); this.eyes.push(pivot);
      const lid = new THREE.Mesh(new THREE.SphereGeometry(0.0182, 20, 10, 0, Math.PI * 2, 0, Math.PI * 0.5), M.skin);
      const lp = new THREE.Group(); lp.add(lid); place(lp, s * 0.031, 0.113, 0.077); lp.rotation.x = -1.25; this.lids.push(lp);
      const brow = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.006, 0.008), M.hair); brow.rotation.z = -s * 0.12; place(brow, s * 0.032, 0.141, 0.088); this.brows = (this.brows || []).concat(brow);
    }
    // mouth: dark ellipse that opens (scale y) when talking
    this.mouth = new THREE.Mesh(ell(0.017, 0.0035, 0.005), new THREE.MeshBasicMaterial({ color: 0x5a2a2a }));
    place(this.mouth, 0, 0.048, 0.086);
    this.headMesh = head;
    // hair
    const hairG = [];
    if (o.hairStyle === 'bun') {
      hairG.push([ell(0.091, 0.1, 0.1, 28, 18), 0, 0.125, -0.016, 0], [ell(0.045, 0.045, 0.045), 0, 0.16, -0.085, 0]);
    } else if (o.hairStyle === 'long') {
      hairG.push([ell(0.092, 0.105, 0.102, 28, 18), 0, 0.125, -0.018, 0], [ell(0.085, 0.13, 0.05), 0, 0.03, -0.06, 0]);
    } else {
      const cap = new THREE.SphereGeometry(1, 28, 16, 0, Math.PI * 2, 0, Math.PI * 0.6); cap.scale(0.092, 0.11, 0.104);
      hairG.push([cap, 0, 0.118, -0.01, 0.12]);
      if (o.hairStyle !== 'buzz') for (let i = 0; i < 9; i++) { const a = (i / 8 - 0.5) * 2.2; hairG.push([ell(0.024, 0.014, 0.03), Math.sin(a) * 0.066, 0.2 - Math.abs(a) * 0.012, 0.035 + Math.cos(a) * 0.02, 0.6]); }
    }
    for (const [g, x, y, z, rx] of hairG) { const h = new THREE.Mesh(g, M.hair); h.rotation.x = rx; h.castShadow = true; place(h, x, y, z); if (ol) outline(h, 0.7); }
    if (o.glasses) {
      const gm = new THREE.MeshStandardMaterial({ color: 0x2b2522, roughness: 0.4 });
      for (const s of [1, -1]) { const r = new THREE.Mesh(new THREE.TorusGeometry(0.022, 0.0028, 8, 24), gm); place(r, s * 0.032, 0.113, 0.098); }
      const br = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.003, 0.003), gm); place(br, 0, 0.116, 0.1);
      for (const s of [1, -1]) { const t = new THREE.Mesh(new THREE.BoxGeometry(0.003, 0.003, 0.09), gm); place(t, s * 0.055, 0.115, 0.055); }
    }
    // arms
    for (const s of ['Left', 'Right']) {
      const Lu = len(B[s + 'Arm'], B[s + 'ForeArm']), Lf = len(B[s + 'ForeArm'], B[s + 'Hand']);
      att(B[s + 'Arm'], B[s + 'ForeArm'], ell(0.068, 0.078, 0.064), M.shirt, 0.02);
      const longSleeve = !!o.longSleeves;
      att(B[s + 'Arm'], B[s + 'ForeArm'], latheSeg(Lu * (longSleeve ? 1.04 : 0.5), [[0, 0.062], [1, longSleeve ? 0.046 : 0.056]]), M.shirt);
      if (!longSleeve) att(B[s + 'Arm'], B[s + 'ForeArm'], latheSeg(Lu * 0.6, [[0, 0.047], [0.5, 0.045], [1, 0.037]]), M.skin, Lu * 0.42);
      att(B[s + 'ForeArm'], B[s + 'Hand'], latheSeg(Lf + 0.02, [[0, 0.04], [0.3, 0.042], [1, 0.029]]), longSleeve ? M.shirt : M.skin, -0.01);
      if (longSleeve) att(B[s + 'ForeArm'], B[s + 'Hand'], latheSeg(0.05, [[0, 0.03], [1, 0.028]]), M.skin, Lf - 0.02, false);
      att(B[s + 'Hand'], B[s + 'HandMiddle1'], ell(0.027, 0.05, 0.043), M.skin, 0.04);
      att(B[s + 'Hand'], B[s + 'HandThumb2'] || B[s + 'HandThumb1'], ell(0.011, 0.028, 0.012), M.skin, 0.02, false);
      // legs
      const Lt = len(B[s + 'UpLeg'], B[s + 'Leg']), Lk = len(B[s + 'Leg'], B[s + 'Foot']);
      const legM = fem && o.skirt ? M.skin : M.pants;
      att(B[s + 'UpLeg'], B[s + 'Leg'], latheSeg(Lt + 0.03, [[0, 0.09], [0.4, 0.084], [0.8, 0.064], [1, 0.054]]), legM, -0.01);
      att(B[s + 'Leg'], B[s + 'Foot'], latheSeg(Lk + 0.02, [[0, 0.054], [0.25, 0.058], [0.7, 0.043], [1, 0.036]]), legM, -0.01);
      const Lfoot = len(B[s + 'Foot'], B[s + 'ToeBase']), Ltoe = len(B[s + 'ToeBase'], B[s + 'Toe_End']);
      att(B[s + 'Foot'], B[s + 'ToeBase'], latheSeg(Lfoot + 0.03, [[0, 0.044], [0.5, 0.048], [1, 0.04]], 0.85, 1.05), M.shoes, -0.035);
      att(B[s + 'ToeBase'], B[s + 'Toe_End'], latheSeg(Ltoe + 0.015, [[0, 0.04], [0.7, 0.034], [1, 0.012]], 0.82, 1.1), M.shoes);
    }
    // animation clips
    this.mixer = new THREE.AnimationMixer(this.root);
    this.actions = {};
    for (const name of ['idle', 'walk', 'run']) {
      const clip = gltf.animations.find(c => c.name === name).clone();
      for (const t of clip.tracks) if (t.name.endsWith('Hips.position')) for (let i = 0; i < t.values.length; i += 3) { t.values[i] = 0; t.values[i + 2] = 0; }
      const a = this.mixer.clipAction(clip); a.play(); a.setEffectiveWeight(0); this.actions[name] = a;
    }
    this.hipY = B.Hips.position.y;
  }
  // p: x,z,y, heading (rad, 0 = +x), speed (m/s), dist (m), t (s) + pose overlays (all 0..1 unless noted)
  pose(p) {
    const { x = 0, z = 0, y = 0, heading = 0, speed = 0, dist = 0, t = 0 } = p;
    const w = this.wrap, B = this.bones;
    w.position.set(x, y, z); w.rotation.set(0, Math.PI / 2 - heading, 0);
    const run = THREE.MathUtils.smoothstep(speed, 2.2, 4.0), walk = THREE.MathUtils.smoothstep(speed, 0.2, 1.0) * (1 - run), idle = 1 - run - walk;
    const A = this.actions;
    A.run.setEffectiveWeight(run); A.walk.setEffectiveWeight(walk); A.idle.setEffectiveWeight(idle);
    A.run.time = ((dist / 3.2) % 1) * A.run.getClip().duration;
    A.walk.time = ((dist / 1.45) % 1) * A.walk.getClip().duration;
    A.idle.time = (p.idleT ?? t) % A.idle.getClip().duration;
    // restore last clean pose: the mixer only rewrites bones whose animated value changed
    if (this.clean) for (const [b, q] of this.clean) b.quaternion.copy(q);
    if (this.cleanHip) B.Hips.position.copy(this.cleanHip);
    this.mixer.update(0);
    if (!this.clean) { this.clean = []; this.root.traverse(n => { if (n.isBone) this.clean.push([n, new THREE.Quaternion()]); }); this.cleanHip = new THREE.Vector3(); }
    for (const [b, q] of this.clean) q.copy(b.quaternion);
    this.cleanHip.copy(B.Hips.position);
    const wq = w.quaternion, pq = new THREE.Quaternion(), q = new THREE.Quaternion();
    const rot = (bone, axis, ang) => { if (!ang) return; bone.parent.updateWorldMatrix(true, false); bone.parent.getWorldQuaternion(pq); q.setFromAxisAngle(axis.clone().applyQuaternion(wq), ang); bone.quaternion.premultiply(pq.clone().invert().multiply(q).multiply(pq)); };
    const k = v => v || 0;
    let drop = 0;
    // sitting on a chair (seat ~0.46 m)
    if (p.sit) { const s = p.sit; rot(B.LeftUpLeg, X, -1.5 * s); rot(B.RightUpLeg, X, -1.5 * s); rot(B.LeftLeg, X, 1.5 * s); rot(B.RightLeg, X, 1.5 * s); rot(B.Spine, X, 0.12 * s); drop += 0.47 * s; }
    if (p.lean) rot(B.Spine, X, p.lean);
    if (p.bend) { rot(B.Spine, X, 0.55 * p.bend); rot(B.Spine1, X, 0.3 * p.bend); rot(B.LeftUpLeg, X, -0.5 * p.bend); rot(B.RightUpLeg, X, -0.5 * p.bend); rot(B.LeftLeg, X, 0.8 * p.bend); rot(B.RightLeg, X, 0.8 * p.bend); drop += 0.2 * p.bend; }
    // head-in-hand: right elbow on the desk, chin on the fist
    if (p.chin) { const c = p.chin; rot(B.Spine, X, 0.32 * c); rot(B.Spine1, X, 0.22 * c); rot(B.RightArm, X, -1.1 * c); rot(B.RightArm, Y, 0.5 * c); rot(B.RightForeArm, X, -2.65 * c); rot(B.RightHand, X, 0.6 * c); rot(B.Neck, X, -0.25 * c); rot(B.Neck, Z, 0.12 * c); rot(B.LeftArm, X, -0.8 * c); rot(B.LeftForeArm, X, -1.3 * c); }
    if (p.armsDesk) { const c = p.armsDesk; for (const [s, sg] of [['Left', 1], ['Right', -1]]) { rot(B[s + 'Arm'], X, -0.75 * c); rot(B[s + 'Arm'], Z, sg * 0.1 * c); rot(B[s + 'ForeArm'], X, -1.1 * c); } }
    if (p.reach) { const c = p.reach; rot(B.RightArm, X, -1.35 * c); rot(B.RightArm, Z, 0.15 * c); rot(B.RightForeArm, X, -0.25 * c); }
    if (p.armsFwd) { const c = p.armsFwd; rot(B.LeftArm, X, -1.2 * c); rot(B.RightArm, X, -1.2 * c); rot(B.LeftForeArm, X, -0.3 * c); rot(B.RightForeArm, X, -0.3 * c); }
    if (p.point) { const c = p.point; rot(B.LeftArm, X, -1.45 * c); rot(B.LeftArm, Z, 0.2 * c); }
    if (p.handsMouth) { const c = p.handsMouth; for (const [s, sg] of [['Left', 1], ['Right', -1]]) { rot(B[s + 'Arm'], X, -0.9 * c); rot(B[s + 'Arm'], Z, -sg * 0.35 * c); rot(B[s + 'ForeArm'], X, -2.2 * c); } }
    if (p.headYaw) rot(B.Head, Y, p.headYaw);
    if (p.headPitch) rot(B.Head, X, p.headPitch);
    if (p.headRoll) rot(B.Head, Z, p.headRoll);
    if (p.torsoYaw) rot(B.Spine1, Y, p.torsoYaw);
    if (p.swim) { const ph = p.swimPh || 0; rot(B.LeftArm, X, Math.PI + Math.sin(ph) * 2.6); rot(B.RightArm, X, Math.PI + Math.sin(ph + Math.PI) * 2.6); rot(B.LeftUpLeg, X, Math.sin(ph * 3) * 0.3); rot(B.RightUpLeg, X, -Math.sin(ph * 3) * 0.3); rot(B.Head, Y, Math.sin(ph) * 0.5); }
    if (p.limp) { const c = p.limp; rot(B.Head, X, 0.5 * c); rot(B.LeftArm, Z, 0.5 * c); rot(B.RightArm, Z, -0.5 * c); }
    w.position.y = y - drop * this.scale;
    if (p.lie) { w.rotateX(-Math.PI / 2 * p.lie); w.position.y = y + 0.13 * p.lie; }
    if (p.tilt) w.rotateX(p.tilt);
    // face
    const blink = p.blink ?? 0, open = 1 - blink;
    this.lids.forEach(l => { l.rotation.x = THREE.MathUtils.lerp(-1.25, 0.15, blink); });
    this.eyes.forEach(e => { e.rotation.set(p.eyePitch || 0, p.eyeYaw || 0, 0); });
    this.mouth.scale.y = 1 + k(p.mouth) * 4.5; this.mouth.scale.x = 1 - k(p.mouth) * 0.25;
    void open;
    this.root.updateMatrixWorld(true);
  }
  headPos() { const v = new THREE.Vector3(); this.bones.Head.getWorldPosition(v); return v.add(new THREE.Vector3(0, 0.1 * this.scale, 0)); }
  handPos(s = 'Right') { const v = new THREE.Vector3(); this.bones[s + 'Hand'].getWorldPosition(v); return v; }
  eyeWorld(i = 0) { const v = new THREE.Vector3(); this.eyes[i].getWorldPosition(v); return v; }
}
