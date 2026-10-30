// Footballer figure: Mixamo skeleton + animations (Xbot rig), with sculpted body segments attached to bones.
import * as THREE from 'three';
import * as SU from 'three/addons/utils/SkeletonUtils.js';

const UP = new THREE.Vector3(0, 1, 0);

// radius profile along a segment, t in [0,1] -> r (meters); lathe around local +Y
function latheSeg(len, prof, sx = 1, sz = 1, seg = 18) {
  const pts = prof.map(([t, r]) => new THREE.Vector2(Math.max(r, 0.0005), t * len));
  // smooth the profile
  const sm = new THREE.SplineCurve(pts).getPoints(Math.max(8, prof.length * 4));
  pts.length = 0; pts.push(...sm);
  const g = new THREE.LatheGeometry(pts, seg);
  g.scale(sx, 1, sz);
  g.computeVertexNormals();
  return g;
}
function ellipsoid(rx, ry, rz) {
  const g = new THREE.SphereGeometry(1, 20, 14);
  g.scale(rx, ry, rz);
  return g;
}

export class Footballer {
  constructor(gltf, scene, opts) {
    this.root = SU.clone(gltf.scene);
    this.root.traverse(n => { if (n.isMesh) n.visible = false; });
    this.bones = {};
    this.root.traverse(n => { if (n.isBone) this.bones[n.name.replace('mixamorig', '').replace(':', '')] = n; });
    this.scale = opts.height / 1.8;
    this.wrap = new THREE.Group();
    this.wrap.add(this.root);
    this.wrap.scale.setScalar(this.scale);
    scene.add(this.wrap);
    this.root.updateMatrixWorld(true);
    const c = opts.colors;
    const mat = col => new THREE.MeshStandardMaterial({ color: col, roughness: 0.78, metalness: 0, transparent: opts.opacity < 1, opacity: opts.opacity ?? 1 });
    const shirtMat = mat(c.shirt);
    if (c.stripe) { // vertical stripes (lathe u runs around the body)
      const cv = document.createElement('canvas'); cv.width = 512; cv.height = 8; const g = cv.getContext('2d');
      const n = c.stripes || 10, w = cv.width / n;
      for (let i = 0; i < n; i++) { g.fillStyle = '#' + new THREE.Color(i % 2 ? c.stripe : c.shirt).getHexString(); g.fillRect(i * w, 0, w + 1, 8); }
      const tx = new THREE.CanvasTexture(cv); tx.colorSpace = THREE.SRGBColorSpace; tx.anisotropy = 8;
      shirtMat.map = tx; shirtMat.color.set(0xffffff);
    }
    this.mats = { shirt: shirtMat, shorts: mat(c.shorts), skin: mat(c.skin), socks: mat(c.socks), boots: mat(c.boots), hair: mat(c.hair) };
    this.jointMat = new THREE.MeshStandardMaterial({ color: 0xe8243c, emissive: 0x3a0008, roughness: 0.5 });
    const B = this.bones, M = this.mats;
    // attach helper: geometry built in meters along +Y, oriented toward child bone
    const att = (bone, child, geo, m, { off = 0 } = {}) => {
      const ws = new THREE.Vector3(); bone.getWorldScale(ws);
      const mesh = new THREE.Mesh(geo, m);
      mesh.castShadow = true;
      const dir = child ? child.position.clone().normalize() : UP.clone();
      mesh.quaternion.setFromUnitVectors(UP, dir);
      mesh.scale.setScalar(1 / ws.x);
      if (off) mesh.position.copy(dir.clone().multiplyScalar(off / ws.x));
      bone.add(mesh);
      return mesh;
    };
    const len = (a, b) => { const p = new THREE.Vector3(), q = new THREE.Vector3(); a.getWorldPosition(p); b.getWorldPosition(q); return p.distanceTo(q); };
    this.len = len;
    // torso: pelvis (shorts), abdomen + chest (shirt)
    const Lp = len(B.Hips, B.Spine), La = len(B.Spine, B.Spine2), Lc = len(B.Spine2, B.Neck);
    att(B.Hips, B.Spine, latheSeg(Lp + 0.06, [[0, 0.06], [0.15, 0.155], [0.55, 0.165], [1, 0.158]], 1.12, 0.78), M.shorts, { off: -0.08 });
    // one continuous shirt from waist to neck (smooth silhouette)
    const Lt0 = La + Lc + 0.06;
    att(B.Spine, B.Neck, latheSeg(Lt0, [[0, 0.168], [0.25, 0.164], [0.5, 0.178], [0.72, 0.195], [0.86, 0.18], [0.95, 0.12], [1, 0.06]], 1.18, 0.72, 28), M.shirt, { off: -0.04 });
    // neck + head
    att(B.Neck, B.Head, latheSeg(len(B.Neck, B.Head) + 0.03, [[0, 0.055], [1, 0.05]]), M.skin, { off: -0.01 });
    const Lh = len(B.Head, B.HeadTop_End);
    this.headMesh = att(B.Head, B.HeadTop_End, ellipsoid(0.088, Lh * 0.55, 0.1), M.skin, { off: Lh * 0.48 });
    this.hairMesh = att(B.Head, B.HeadTop_End, (() => { const g = new THREE.SphereGeometry(1, 20, 12, 0, Math.PI * 2, 0, Math.PI * 0.5); g.scale(0.094, Lh * 0.5, 0.106); return g; })(), M.hair, { off: Lh * 0.55 });
    // arms
    for (const s of ['Left', 'Right']) {
      const Lu = len(B[s + 'Arm'], B[s + 'ForeArm']), Lf = len(B[s + 'ForeArm'], B[s + 'Hand']);
      att(B[s + 'Arm'], B[s + 'ForeArm'], ellipsoid(0.075, 0.085, 0.07), M.shirt, { off: 0.02 }); // deltoid
      att(B[s + 'Arm'], B[s + 'ForeArm'], latheSeg(Lu * 0.48, [[0, 0.068], [1, 0.062]]), M.shirt);   // sleeve
      att(B[s + 'Arm'], B[s + 'ForeArm'], latheSeg(Lu * 0.62, [[0, 0.055], [0.5, 0.052], [1, 0.042]]), M.skin, { off: Lu * 0.4 });
      att(B[s + 'ForeArm'], B[s + 'Hand'], latheSeg(Lf + 0.02, [[0, 0.043], [0.3, 0.046], [1, 0.03]]), M.skin, { off: -0.01 });
      att(B[s + 'Hand'], B[s + 'HandMiddle1'], ellipsoid(0.026, 0.05, 0.042), M.skin, { off: 0.04 });
      this[s + 'Elbow'] = att(B[s + 'ForeArm'], null, ellipsoid(0.018, 0.018, 0.018), this.jointMat);
      // legs
      const Lt = len(B[s + 'UpLeg'], B[s + 'Leg']), Lk = len(B[s + 'Leg'], B[s + 'Foot']);
      att(B[s + 'UpLeg'], B[s + 'Leg'], latheSeg(Lt * 0.48, [[0, 0.108], [1, 0.104]]), M.shorts, { off: -0.02 }); // shorts leg
      att(B[s + 'UpLeg'], B[s + 'Leg'], latheSeg(Lt + 0.02, [[0, 0.098], [0.4, 0.09], [0.8, 0.066], [1, 0.052]]), M.skin);
      att(B[s + 'Leg'], B[s + 'Foot'], latheSeg(Lk * 0.22, [[0, 0.05], [1, 0.052]]), M.skin, { off: -0.01 }); // knee
      att(B[s + 'Leg'], B[s + 'Foot'], latheSeg(Lk * 0.84, [[0, 0.054], [0.25, 0.058], [0.7, 0.042], [1, 0.034]]), M.socks, { off: Lk * 0.16 });
      this[s + 'Knee'] = att(B[s + 'Leg'], null, ellipsoid(0.02, 0.02, 0.02), this.jointMat);
      const Lfoot = len(B[s + 'Foot'], B[s + 'ToeBase']), Ltoe = len(B[s + 'ToeBase'], B[s + 'Toe_End']);
      att(B[s + 'Foot'], B[s + 'ToeBase'], latheSeg(Lfoot + 0.02, [[0, 0.04], [0.5, 0.045], [1, 0.038]], 0.85, 1.05), M.boots, { off: -0.03 });
      att(B[s + 'ToeBase'], B[s + 'Toe_End'], latheSeg(Ltoe + 0.01, [[0, 0.038], [0.7, 0.032], [1, 0.012]], 0.8, 1.15), M.boots);
    }
    // face sprite
    if (opts.faceTex) {
      this.face = new THREE.Sprite(new THREE.SpriteMaterial({ map: opts.faceTex }));
      this.face.scale.setScalar(0.34 * this.scale);
      scene.add(this.face);
      this.headMesh.visible = false; this.hairMesh.visible = false;
    }
    // animation
    this.mixer = new THREE.AnimationMixer(this.root);
    this.actions = {};
    for (const name of ['idle', 'walk', 'run']) {
      const clip = gltf.animations.find(c => c.name === name).clone();
      for (const t of clip.tracks) if (t.name.endsWith('Hips.position')) { for (let i = 0; i < t.values.length; i += 3) { t.values[i] = 0; t.values[i + 2] = 0; } }
      const a = this.mixer.clipAction(clip); a.play(); a.setEffectiveWeight(0); this.actions[name] = a;
    }
    this.dist = 0;
  }
  // phaseDist: cumulative distance travelled (m); speed m/s
  pose({ x, z, heading, speed, dist, t = 0, kick = 0, lunge = 0, celebrate = 0, crouch = 0, dive = 0, diveDir = 1 }) {
    const w = this.wrap;
    w.position.set(x, 0, z);
    w.rotation.set(0, Math.PI / 2 - heading, 0);
    const run = THREE.MathUtils.smoothstep(speed, 2.2, 4.5), walk = THREE.MathUtils.smoothstep(speed, 0.25, 1.2) * (1 - run), idle = 1 - run - walk;
    const A = this.actions;
    A.run.setEffectiveWeight(run); A.walk.setEffectiveWeight(walk); A.idle.setEffectiveWeight(idle);
    A.run.time = ((dist / 3.4) % 1) * A.run.getClip().duration;
    A.walk.time = ((dist / 1.5) % 1) * A.walk.getClip().duration;
    A.idle.time = (t % A.idle.getClip().duration);
    this.mixer.update(0);
    const B = this.bones;
    // overlays in character space (X = character's left, Z = forward), applied on top of the clip pose
    const X = new THREE.Vector3(1, 0, 0), Z = new THREE.Vector3(0, 0, 1);
    const wq = this.wrap.quaternion;
    const pq = new THREE.Quaternion(), q = new THREE.Quaternion();
    const rot = (bone, axis, ang) => {
      if (!ang) return;
      bone.parent.updateWorldMatrix(true, false);
      bone.parent.getWorldQuaternion(pq);
      q.setFromAxisAngle(axis.clone().applyQuaternion(wq), ang);
      bone.quaternion.premultiply(pq.clone().invert().multiply(q).multiply(pq));
    };
    let drop = 0;
    if (crouch) { rot(B.Spine, X, 0.3 * crouch); for (const s of ['Left', 'Right']) { rot(B[s + 'UpLeg'], X, -0.55 * crouch); rot(B[s + 'Leg'], X, 1.0 * crouch); } drop += 0.12 * crouch; }
    if (lunge) { rot(B.Spine, X, 0.45 * lunge); rot(B.RightUpLeg, X, -1.0 * lunge); rot(B.RightLeg, X, 0.25 * lunge); rot(B.LeftUpLeg, X, 0.35 * lunge); rot(B.LeftLeg, X, 0.8 * lunge); drop += 0.15 * lunge; }
    if (kick) {
      rot(B.Spine, X, -0.1 * kick);
      rot(B.LeftUpLeg, X, THREE.MathUtils.lerp(0.75, -1.25, kick));
      rot(B.LeftLeg, X, THREE.MathUtils.lerp(1.6, 0.1, kick));
      rot(B.LeftArm, Z, 0.7); rot(B.RightArm, Z, -0.6);
    }
    if (celebrate) { rot(B.LeftArm, Z, 2.2 * celebrate); rot(B.RightArm, Z, -2.2 * celebrate); rot(B.LeftForeArm, Z, 0.4 * celebrate); rot(B.RightForeArm, Z, -0.4 * celebrate); }
    w.position.y = -drop * this.scale;
    if (dive) { w.rotateZ(diveDir * dive * 1.35); w.position.y = dive * 0.28; }
    this.root.updateMatrixWorld(true);
    if (this.face) { const p = new THREE.Vector3(); B.Head.getWorldPosition(p); p.y += 0.1 * this.scale; this.face.position.copy(p); }
  }
  nudge(dx, dz) { this.wrap.position.x += dx; this.wrap.position.z += dz; this.root.updateMatrixWorld(true); if (this.face) { this.face.position.x += dx; this.face.position.z += dz; } }
  footPos(side = 'Left') { const p = new THREE.Vector3(); this.bones[side + 'ToeBase'].getWorldPosition(p); return p; }
  headPos() { const p = new THREE.Vector3(); this.bones.Head.getWorldPosition(p); return p; }
}
