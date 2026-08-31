// Mode key → frame painter mapping.

import { drawBraid } from './braid.js';
import { drawGlobe, drawRubik, drawWave } from './lattice.js';
import { drawMorph } from './morph.js';
import { drawOrbits } from './orbits.js';
import { drawRibbon } from './ribbon.js';
import { drawWeb } from './web.js';

export const MODE_DRAWS = {
  orbits: drawOrbits,
  globe: drawGlobe,
  rubik: drawRubik,
  wave: drawWave,
  web: drawWeb,
  braid: drawBraid,
  ribbon: drawRibbon,
  ring: drawRibbon,
  morph: drawMorph,
};
