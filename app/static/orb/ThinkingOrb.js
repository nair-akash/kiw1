// Vanilla ES Module Thinking Orb Wrapper
// Shares one clock (performance.now) so all mounted orbs stay in phase.
// Auto-pauses offscreen via IntersectionObserver and when tab is hidden.
// Respects prefers-reduced-motion by painting one static frame.

import { MODE_DRAWS } from './engine/registry.js';
import { resolvePreset } from './presets.js';
import { isDarkTheme, isReducedMotion } from './theme.js';

export const ORB_LABELS = {
  working: 'Working…',
  searching: 'Searching…',
  solving: 'Solving…',
  listening: 'Listening…',
  connecting: 'Connecting…',
  weaving: 'Weaving…',
  composing: 'Composing…',
  breathing: 'Breathing…',
  shaping: 'Shaping…'
};

export class ThinkingOrbInstance {
  constructor(container, options = {}) {
    this.container = container;
    this.state = options.state || 'working';
    this.size = options.size || 64;
    this.theme = options.theme || 'auto';
    this.speed = options.speed || 1;
    this.ariaLabel = options.ariaLabel || ORB_LABELS[this.state];
    this.running = false;
    this.visible = true;
    this.rafId = 0;

    this._initCanvas();
    this._setupObservers();
    this.render();
  }

  _initCanvas() {
    this.canvas = document.createElement('canvas');
    this.canvas.setAttribute('role', 'img');
    this.canvas.setAttribute('aria-label', this.ariaLabel);
    this.canvas.style.width = `${this.size}px`;
    this.canvas.style.height = `${this.size}px`;
    this.canvas.style.display = 'block';

    const dpr = Math.min(2, (typeof window !== 'undefined' && window.devicePixelRatio) || 1);
    this.dpr = dpr;
    this.canvas.width = Math.round(this.size * dpr);
    this.canvas.height = Math.round(this.size * dpr);
    this.ctx = this.canvas.getContext('2d');

    this.container.appendChild(this.canvas);
  }

  setState(newState, newLabel) {
    this.state = newState;
    if (newLabel) {
      this.ariaLabel = newLabel;
      this.canvas.setAttribute('aria-label', newLabel);
    } else {
      this.ariaLabel = ORB_LABELS[newState] || newState;
      this.canvas.setAttribute('aria-label', this.ariaLabel);
    }
    // Re-render immediate frame
    this.drawFrame();
  }

  drawFrame(customTime) {
    if (!this.ctx) return;
    const dark = isDarkTheme(this.canvas, this.theme);
    const { mode, speed: baseSpeed, opts } = resolvePreset(this.state, this.size);
    const draw = MODE_DRAWS[mode] || MODE_DRAWS.orbits;
    const effSpeed = baseSpeed * this.speed;

    const tSec = customTime !== undefined ? customTime : (performance.now() / 1000) * effSpeed;

    this.ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    this.ctx.clearRect(0, 0, this.size, this.size);
    draw(this.ctx, this.size, tSec, dark, opts);
  }

  render() {
    if (isReducedMotion()) {
      // Reduced motion: draw one static representative frame at t = 0.6s
      this.drawFrame(0.6);
      return;
    }

    const loop = () => {
      this.drawFrame();
      if (this.running) {
        this.rafId = requestAnimationFrame(loop);
      }
    };

    this._startLoop = () => {
      if (this.running || isReducedMotion()) return;
      this.running = true;
      this.rafId = requestAnimationFrame(loop);
    };

    this._stopLoop = () => {
      this.running = false;
      if (this.rafId) {
        cancelAnimationFrame(this.rafId);
        this.rafId = 0;
      }
    };

    // Draw initial frame
    this.drawFrame();
    if (this.visible && document.visibilityState !== 'hidden') {
      this._startLoop();
    }
  }

  _setupObservers() {
    if (typeof IntersectionObserver !== 'undefined') {
      this.io = new IntersectionObserver(([entry]) => {
        this.visible = entry.isIntersecting;
        if (this.visible && document.visibilityState !== 'hidden') {
          if (this._startLoop) this._startLoop();
        } else {
          if (this._stopLoop) this._stopLoop();
        }
      });
      this.io.observe(this.canvas);
    }

    this.onVisibilityChange = () => {
      if (document.visibilityState === 'hidden') {
        if (this._stopLoop) this._stopLoop();
      } else if (this.visible) {
        if (this._startLoop) this._startLoop();
      }
    };
    document.addEventListener('visibilitychange', this.onVisibilityChange);
  }

  destroy() {
    if (this._stopLoop) this._stopLoop();
    if (this.io) {
      this.io.disconnect();
      this.io = null;
    }
    document.removeEventListener('visibilitychange', this.onVisibilityChange);
    if (this.canvas && this.canvas.parentElement) {
      this.canvas.parentElement.removeChild(this.canvas);
    }
  }
}

/** Mount an orb instance into a container DOM element. */
export function mountOrb(container, options = {}) {
  return new ThinkingOrbInstance(container, options);
}
