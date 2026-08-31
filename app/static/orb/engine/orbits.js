// Orbits: particles on tilted orbits — the "working" state.

import { hashD, makeProj, paint, radiusScale } from './core.js';

export const drawOrbits = (ctx, size, t, dark, o) => {
  const cx = size / 2;
  const cy = size / 2;
  const R = (size / 2) * 0.82;
  const pt = makeProj(t * 0.12, 0.3, cx, cy, 1);
  const rs = radiusScale(size, o.rsPow ?? 0.6);

  const dots = [];
  const orbitN = o.orbitN ?? 12;
  const ghostN = o.ghostN ?? 40;
  const particles = o.particles ?? 3;

  for (let k = 0; k < orbitN; k++) {
    const yaw = k * ((2 * Math.PI) / orbitN) + t * 0.18;
    const tilt = 0.55 + 0.3 * Math.sin(k * 1.3 + t * 0.22);
    const ux = Math.cos(yaw);
    const uy = 0;
    const uz = Math.sin(yaw);
    const vx = -uz * Math.sin(tilt);
    const vy = Math.cos(tilt);
    const vz = ux * Math.sin(tilt);
    const ro = R * (0.55 + 0.45 * Math.sin(k * 0.7 + 1.1));

    for (let i = 0; i < ghostN; i++) {
      const a = (i / ghostN) * 2 * Math.PI;
      const [px, py, z] = pt(
        (ux * Math.cos(a) + vx * Math.sin(a)) * ro,
        (uy * Math.cos(a) + vy * Math.sin(a)) * ro,
        (uz * Math.cos(a) + vz * Math.sin(a)) * ro
      );
      const depth = (z / ro + 1) / 2;
      dots.push({
        x: px,
        y: py,
        z,
        r: (o.ghostR ?? 0.9) * rs,
        white: 0.78,
        a: (o.ghostA ?? 0.5) * (0.15 + 0.35 * depth)
      });
    }

    for (let p = 0; p < particles; p++) {
      const seed = k * 17 + p * 31;
      const speed = 1.1 + 0.7 * hashD(seed, 1.1);
      const phase = hashD(seed, 2.7) * 2 * Math.PI;
      const a = t * speed + phase;
      const [px, py, z] = pt(
        (ux * Math.cos(a) + vx * Math.sin(a)) * ro,
        (uy * Math.cos(a) + vy * Math.sin(a)) * ro,
        (uz * Math.cos(a) + vz * Math.sin(a)) * ro
      );
      const depth = (z / ro + 1) / 2;
      dots.push({
        x: px,
        y: py,
        z,
        r: ((o.partR ?? 1.2) + (o.partRDepth ?? 1.6) * depth) * rs,
        white: 0.3 - 0.22 * depth
      });
    }
  }
  paint(ctx, dots, dark, o.rMin);
};
