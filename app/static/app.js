// KIW1 Companion Studio — Living Organic Nebula & Human-Centered UX

document.addEventListener("DOMContentLoaded", () => {
  // ── Navigation Tabs ──────────────────────────────────────────
  const navTabs = document.querySelectorAll(".nav-tab");
  const viewPanels = document.querySelectorAll(".view-panel");

  function switchTab(targetTab) {
    navTabs.forEach(t => t.classList.remove("active"));
    viewPanels.forEach(p => p.classList.remove("active"));

    const activeBtn = document.querySelector(`.nav-tab[data-tab="${targetTab}"]`);
    if (activeBtn) activeBtn.classList.add("active");

    const targetPanel = document.getElementById(targetTab);
    if (targetPanel) targetPanel.classList.add("active");

    if (targetTab === "memory-tab") loadMemoryPalace();
    if (targetTab === "ledger-tab") loadCorrectionLedger();
    if (targetTab === "skills-tab") loadSkills();
    if (targetTab === "research-tab") loadResearchBriefs();
    if (targetTab === "benchmark-tab") loadBenchmarkResults();
  }

  navTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      switchTab(tab.dataset.tab);
    });
  });

  // ── Thinking Orb Lite & Composer Status Bar ──────────────────
  const TOL_STATES = [
    "tol-working", "tol-searching", "tol-solving", "tol-listening",
    "tol-connecting", "tol-weaving", "tol-composing", "tol-breathing",
    "tol-shaping",
  ];

  const composerOrbEl = document.getElementById("composer-orb");
  const composerStateTitle = document.getElementById("composer-state-title");
  const composerStateDetail = document.getElementById("composer-state-detail");
  const heroStatusText = document.getElementById("hero-status-text");

  function setAgentState(state, statusTitle, detailText) {
    if (composerOrbEl) {
      composerOrbEl.classList.remove(...TOL_STATES);
      composerOrbEl.classList.add("tol-" + state);
    }
    if (composerStateTitle) composerStateTitle.textContent = statusTitle;
    if (composerStateDetail) {
      composerStateDetail.textContent = detailText || "Autonomous Agent &bull; Gemini 3.7 Flash";
    }
    if (heroStatusText) heroStatusText.textContent = statusTitle;
    if (window.livingNebula) window.livingNebula.setState(state);
  }

  // ── Living Organic Nebula Canvas Renderer ────────────────────
  class LivingNebulaOrb {
    constructor(canvasId) {
      this.canvas = document.getElementById(canvasId);
      if (!this.canvas) return;
      this.ctx = this.canvas.getContext("2d");
      this.width = this.canvas.width = 340;
      this.height = this.canvas.height = 340;
      this.cx = this.width / 2;
      this.cy = this.height / 2;
      this.state = "breathing";
      this.time = 0;
      this.particles = [];
      this.initParticles();
      this.animate = this.animate.bind(this);
      requestAnimationFrame(this.animate);
    }

    initParticles() {
      const count = 140;
      for (let i = 0; i < count; i++) {
        const phi = Math.acos(-1 + (2 * i) / count);
        const theta = Math.sqrt(count * Math.PI) * phi;
        this.particles.push({
          x: 0,
          y: 0,
          baseRadius: 65 + Math.random() * 35,
          phi: phi,
          theta: theta,
          size: 1.2 + Math.random() * 2.2,
          speed: 0.008 + Math.random() * 0.012,
          hueOffset: Math.random() * 60,
          alpha: 0.3 + Math.random() * 0.7,
        });
      }
    }

    setState(newState) {
      this.state = newState;
    }

    animate() {
      this.time += 0.018;
      const ctx = this.ctx;
      ctx.clearRect(0, 0, this.width, this.height);

      let coreColor1 = "rgba(255, 158, 59, 0.85)";  // warm sunset gold
      let coreColor2 = "rgba(168, 85, 247, 0.4)";   // cosmic violet
      let speedMult = 1.0;

      if (this.state === "searching") {
        coreColor1 = "rgba(0, 242, 254, 0.85)";
        coreColor2 = "rgba(99, 102, 241, 0.5)";
        speedMult = 2.0;
      } else if (this.state === "solving" || this.state === "working") {
        coreColor1 = "rgba(255, 77, 77, 0.9)";
        coreColor2 = "rgba(255, 158, 59, 0.6)";
        speedMult = 2.5;
      } else if (this.state === "shaping") {
        coreColor1 = "rgba(16, 185, 129, 0.85)";
        coreColor2 = "rgba(0, 242, 254, 0.5)";
        speedMult = 1.6;
      }

      // 1. Glowing Fluid Core
      const glowGrad = ctx.createRadialGradient(
        this.cx, this.cy, 10,
        this.cx, this.cy, 110 + Math.sin(this.time * 2) * 8
      );
      glowGrad.addColorStop(0, coreColor1);
      glowGrad.addColorStop(0.4, coreColor2);
      glowGrad.addColorStop(1, "rgba(7, 8, 13, 0)");

      ctx.fillStyle = glowGrad;
      ctx.beginPath();
      ctx.arc(this.cx, this.cy, 110, 0, Math.PI * 2);
      ctx.fill();

      // 2. Multi-Strand Fluid Ribbons (Vortex Rings)
      for (let r = 0; r < 3; r++) {
        ctx.beginPath();
        const ribbonRadius = 60 + r * 18 + Math.sin(this.time * 1.5 + r) * 6;
        const rot = this.time * 0.8 * (r % 2 === 0 ? 1 : -1) * speedMult;
        ctx.ellipse(this.cx, this.cy, ribbonRadius, ribbonRadius * 0.45, rot, 0, Math.PI * 2);
        ctx.strokeStyle = r === 0 ? "rgba(255, 158, 59, 0.35)" : (r === 1 ? "rgba(0, 242, 254, 0.35)" : "rgba(168, 85, 247, 0.35)");
        ctx.lineWidth = 1.8;
        ctx.stroke();
      }

      // 3. 3D Particle Constellation (Undulating Surface Mesh)
      for (let p of this.particles) {
        const radNoise = Math.sin(this.time * speedMult + p.theta * 2) * 12 + Math.cos(this.time * 1.2 + p.phi * 3) * 8;
        const currentRad = p.baseRadius + radNoise;

        const currentTheta = p.theta + this.time * p.speed * speedMult;
        const x3d = currentRad * Math.sin(p.phi) * Math.cos(currentTheta);
        const y3d = currentRad * Math.sin(p.phi) * Math.sin(currentTheta);
        const z3d = currentRad * Math.cos(p.phi);

        const k = 220 / (220 + z3d);
        const px = this.cx + x3d * k;
        const py = this.cy + y3d * k;
        const size = Math.max(0.6, p.size * k);
        const alpha = Math.max(0.1, (k - 0.4) * p.alpha);

        ctx.beginPath();
        ctx.arc(px, py, size, 0, Math.PI * 2);
        ctx.fillStyle = z3d > 0 ? `rgba(255, 220, 150, ${alpha})` : `rgba(130, 180, 255, ${alpha * 0.7})`;
        ctx.fill();
      }

      requestAnimationFrame(this.animate);
    }
  }

  window.livingNebula = new LivingNebulaOrb("nebula-canvas");

  // ── Telemetry Updates ────────────────────────────────────────
  async function refreshTelemetry() {
    try {
      const res = await fetch("/api/telemetry");
      const data = await res.json();
      if (data.traces && data.traces.length > 0) {
        const latest = data.traces[0];
        const latEl = document.getElementById("telemetry-latency");
        const tokEl = document.getElementById("telemetry-tokens");
        const costEl = document.getElementById("telemetry-cost");

        if (latEl) latEl.textContent = `⏱️ ${Math.round(latest.latency_ms || 0)} ms`;
        if (tokEl) tokEl.textContent = `🔤 ${latest.tokens ? latest.tokens.total.toLocaleString() : 0} tokens`;
        if (costEl) costEl.textContent = `💲 $${(latest.cost_usd || 0).toFixed(4)}`;
      }
    } catch (e) {}
  }

  // ── Chat Composer & Message Stream ───────────────────────────
  const composerInput = document.getElementById("composer-input");
  const btnSendMsg = document.getElementById("btn-send-msg");
  const heroStage = document.getElementById("hero-stage");
  const messagesFlow = document.getElementById("messages-flow");
  const btnNewChat = document.getElementById("btn-new-chat");
  const effortValue = document.getElementById("effort-value");
  const btnHandsOff = document.getElementById("btn-hands-off");

  // Effort Pills
  document.querySelectorAll(".effort-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".effort-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      if (effortValue) effortValue.value = btn.dataset.effort;
    });
  });

  // Hands-off Autonomous Switch
  if (btnHandsOff) {
    btnHandsOff.addEventListener("click", () => {
      btnHandsOff.classList.toggle("active");
    });
  }

  // New Chat
  if (btnNewChat) {
    btnNewChat.addEventListener("click", () => {
      switchTab("chat-tab");
      messagesFlow.innerHTML = "";
      if (heroStage) heroStage.classList.remove("hidden");
      composerInput.value = "";
      composerInput.focus();
      setAgentState("breathing", "KIW1 Ready", "Awaiting instruction &bull; Gemini 3.7 Flash");
    });
  }

  // Quick Starter Prompt Cards
  document.querySelectorAll(".prompt-card").forEach(card => {
    card.addEventListener("click", () => {
      const prompt = card.dataset.prompt;
      if (prompt) {
        composerInput.value = prompt;
        submitUserPrompt(prompt);
      }
    });
  });

  // Shortcut Chips
  document.querySelectorAll(".chip-shortcut").forEach(chip => {
    chip.addEventListener("click", () => {
      const insertText = chip.dataset.insert;
      if (insertText) {
        composerInput.value = insertText;
        composerInput.focus();
        if (insertText === "/skills" || insertText === "/evals" || insertText === "/research") {
          submitUserPrompt(insertText);
        }
      }
    });
  });

  // Textarea auto-height
  if (composerInput) {
    composerInput.addEventListener("input", () => {
      composerInput.style.height = "auto";
      composerInput.style.height = Math.min(composerInput.scrollHeight, 160) + "px";
    });

    composerInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        submitUserPrompt(composerInput.value);
      }
    });
  }

  if (btnSendMsg) {
    btnSendMsg.addEventListener("click", () => submitUserPrompt(composerInput.value));
  }

  async function submitUserPrompt(text) {
    if (!text || text.trim() === "") return;
    const prompt = text.trim();
    composerInput.value = "";
    composerInput.style.height = "auto";

    if (heroStage && !heroStage.classList.contains("hidden")) {
      heroStage.classList.add("hidden");
    }

    renderUserBubble(prompt);

    const effort = effortValue ? effortValue.value : "standard";
    const handsOff = btnHandsOff ? btnHandsOff.classList.contains("active") : false;

    // Set state: searching or solving
    if (prompt.toLowerCase().includes("search") || prompt.toLowerCase().includes("research")) {
      setAgentState("searching", "Searching Sources", "Retrieving web intelligence and local vault items...");
    } else {
      setAgentState("solving", "Analyzing & Planning", "Evaluating constraints and candidate execution paths...");
    }

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: prompt,
          effort: effort,
          hands_off: handsOff,
        }),
      });
      const data = await res.json();
      handleAssistantResponse(data, prompt);
      refreshTelemetry();
    } catch (err) {
      renderAgentBubble({
        text: `Encountered communication error: ${err.message}`,
        model: "offline",
      });
      setAgentState("breathing", "Idle / Error", `Error: ${err.message}`);
    }
  }

  // ── Response Handling ────────────────────────────────────────
  let activePendingPrompt = null;
  const clarOverlay = document.getElementById("clarification-overlay");
  const clarOriginalQuery = document.getElementById("clar-original-query");
  const clarQuestionsList = document.getElementById("clar-questions-list");
  const btnConfirmClar = document.getElementById("btn-confirm-clar");
  const btnCancelClar = document.getElementById("btn-cancel-clar");

  function handleAssistantResponse(data, originalPrompt) {
    if (data.type === "clarification_needed") {
      activePendingPrompt = originalPrompt;
      clarOriginalQuery.textContent = `"${originalPrompt}"`;
      clarQuestionsList.innerHTML = "";

      (data.questions || []).forEach((q, idx) => {
        const qBox = document.createElement("div");
        qBox.className = "clar-q-box";
        qBox.innerHTML = `
          <div class="clar-q-title">Q${idx + 1}: ${escapeHtml(q.question)}</div>
          <div class="clar-options-row" data-qid="${q.id}">
            ${q.options.map((opt, oIdx) => `
              <label class="clar-choice-label">
                <input type="radio" name="c_${q.id}" value="${escapeHtml(opt)}" ${oIdx === 0 ? "checked" : ""}>
                <span>${escapeHtml(opt)}</span>
              </label>
            `).join("")}
          </div>
        `;
        clarQuestionsList.appendChild(qBox);
      });

      clarOverlay.classList.remove("hidden");
      setAgentState("solving", "Clarification Needed", "Prompt Refinery awaiting ambiguity choice...");
      return;
    }

    if (data.forged_skill) {
      setAgentState("shaping", "Superpower Forged", `Forged new capability: ${data.forged_skill.skill_name}`);
      loadSkills();
    } else {
      setAgentState("breathing", "KIW1 Ready", "Task completed &bull; Gemini 3.7 Flash");
    }

    renderAgentBubble(data);
  }

  // Confirm Clarification
  if (btnConfirmClar) {
    btnConfirmClar.addEventListener("click", async () => {
      if (!activePendingPrompt) return;
      const answers = {};
      document.querySelectorAll(".clar-options-row").forEach(row => {
        const qid = row.dataset.qid;
        const checked = row.querySelector("input[type='radio']:checked");
        if (checked) answers[qid] = checked.value;
      });

      clarOverlay.classList.add("hidden");
      renderUserBubble(`[Clarification Answers]: ${Object.values(answers).join("; ")}`);
      setAgentState("working", "Executing Clarified Plan", "Executing plan with verified brief constraints...");

      try {
        const res = await fetch("/api/clarify", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            original_prompt: activePendingPrompt,
            answers: answers,
            effort: effortValue ? effortValue.value : "standard",
          }),
        });
        const data = await res.json();
        activePendingPrompt = null;
        handleAssistantResponse(data, "");
        refreshTelemetry();
      } catch (err) {
        renderAgentBubble({ text: `Error executing clarified task: ${err.message}` });
        setAgentState("breathing", "Idle / Error", `Error: ${err.message}`);
      }
    });
  }

  if (btnCancelClar) {
    btnCancelClar.addEventListener("click", () => {
      clarOverlay.classList.add("hidden");
      activePendingPrompt = null;
      setAgentState("breathing", "KIW1 Ready", "Clarification dismissed");
    });
  }

  function renderUserBubble(text) {
    const bubble = document.createElement("div");
    bubble.className = "chat-bubble user-bubble";
    bubble.innerHTML = escapeHtml(text).replace(/\n/g, "<br>");
    messagesFlow.appendChild(bubble);
    scrollChat();
  }

  function renderAgentBubble(data) {
    const bubble = document.createElement("div");
    bubble.className = "chat-bubble agent-bubble";

    const text = data.text || "Task executed successfully.";
    const model = data.model || "Gemini 3.7 Flash";
    const tools = data.tools_used || [];
    const reasoning = data.reasoning || "";
    const rules = (data.brief && data.brief.learned_rules_applied) ? data.brief.learned_rules_applied : [];
    const skill = data.forged_skill;

    let toolsHtml = "";
    if (tools.length > 0) {
      toolsHtml = `
        <div style="margin-bottom: 6px;">
          ${tools.map(t => `<span class="tool-tag">⚡ ${t}</span>`).join("")}
        </div>
      `;
    }

    let thoughtHtml = "";
    if (reasoning || (data.plan_candidates && data.plan_candidates.length > 0)) {
      const candidates = data.plan_candidates || [];
      thoughtHtml = `
        <div class="thought-card">
          <div class="thought-trigger" onclick="this.parentElement.classList.toggle('open')">
            <span>🧠 Strategic Reasoning &amp; Thought Process</span>
            <span>▼</span>
          </div>
          <div class="thought-content">
            ${reasoning ? `<div style="margin-bottom: 8px;">${escapeHtml(reasoning)}</div>` : ''}
            ${candidates.length > 0 ? `
              <div style="font-size: 11px; color: var(--text-dim);">
                <strong>Evaluated Paths (${candidates.length}):</strong><br>
                ${candidates.map(c => `&bull; ${c.name} [Confidence: ${(c.confidence * 100).toFixed(0)}%] &mdash; ${c.risk_assessment}`).join("<br>")}
              </div>
            ` : ''}
          </div>
        </div>
      `;
    }

    let rulesHtml = "";
    if (rules.length > 0) {
      rulesHtml = `
        <div style="margin-top: 10px; font-size: 12px; color: #a5b4fc; background: rgba(99,102,241,0.1); padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(99,102,241,0.25);">
          📖 <strong>Applied ${rules.length} Learned Rule(s):</strong><br>
          ${rules.map(r => `&bull; ${escapeHtml(r)}`).join("<br>")}
        </div>
      `;
    }

    let skillHtml = "";
    if (skill) {
      skillHtml = `
        <div style="margin-top: 10px; font-size: 12px; color: #6ee7b7; background: rgba(16,185,129,0.1); padding: 10px 14px; border-radius: 8px; border: 1px solid rgba(16,185,129,0.3);">
          ⚡ <strong>Self-Taught Superpower Forged:</strong> ${escapeHtml(skill.skill_name || '')}<br>
          <span style="color: var(--text-muted);">${escapeHtml(skill.message || '')}</span>
        </div>
      `;
    }

    bubble.innerHTML = `
      <div class="agent-bubble-header">
        <div class="agent-avatar-icon">
          <div class="tol-orb tol-breathing is-sm"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
        </div>
        <div class="agent-name-tag">KIW1</div>
        <div class="agent-model-pill">${model}</div>
      </div>
      ${thoughtHtml}
      ${toolsHtml}
      <div class="bubble-text">${formatMarkdown(text)}</div>
      ${rulesHtml}
      ${skillHtml}
      <div class="bubble-footer-actions">
        <button class="btn-bubble-action btn-copy-action">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
          Copy
        </button>
        <button class="btn-bubble-action btn-teach-action">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
          Teach Rule
        </button>
      </div>
    `;

    bubble.querySelector(".btn-copy-action").addEventListener("click", () => {
      navigator.clipboard.writeText(text);
    });

    bubble.querySelector(".btn-teach-action").addEventListener("click", () => {
      openCorrectionModal();
    });

    messagesFlow.appendChild(bubble);
    scrollChat();
  }

  function scrollChat() {
    const viewport = document.querySelector(".chat-viewport");
    if (viewport) viewport.scrollTop = viewport.scrollHeight;
  }

  function escapeHtml(str) {
    return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  function formatMarkdown(str) {
    if (!str) return "";
    let html = escapeHtml(str);
    html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    html = html.replace(/\*(.*?)\*/g, "<em>$1</em>");
    html = html.replace(/`(.*?)`/g, "<code>$1</code>");
    html = html.replace(/\n/g, "<br>");
    return html;
  }

  // ── VIEW 2: Memory Palace ────────────────────────────────────
  async function loadMemoryPalace() {
    try {
      const res = await fetch("/api/memory");
      const data = await res.json();
      const tree = data.tree || {};
      const badge = document.getElementById("badge-memory");
      let count = 0;
      Object.values(tree).forEach(loci => {
        Object.values(loci).forEach(arr => { count += arr.length; });
      });
      if (badge) badge.textContent = count;

      const container = document.getElementById("memory-grid-view");
      if (!container) return;
      container.innerHTML = "";

      if (Object.keys(tree).length === 0) {
        container.innerHTML = `
          <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; color: var(--text-dim);">
            <div style="font-size: 32px; margin-bottom: 10px;">🏛️</div>
            <div style="font-weight: 700; font-size: 16px; color: var(--text-main);">Memory Palace Empty</div>
            <p style="font-size: 13px; margin-top: 4px;">Teach KIW1 facts via chat (e.g. <code>/remember ...</code>) or "+ Teach New Fact".</p>
          </div>
        `;
        return;
      }

      Object.entries(tree).forEach(([room, loci]) => {
        const card = document.createElement("div");
        card.className = "memory-room-card";
        let lociHtml = "";

        Object.entries(loci).forEach(([locus, items]) => {
          lociHtml += `
            <div class="locus-item-box">
              <div class="locus-name">📍 Locus: ${escapeHtml(locus)}</div>
              ${items.map(item => `
                <div class="fact-text">&bull; ${escapeHtml(item.text || item)}</div>
              `).join("")}
            </div>
          `;
        });

        card.innerHTML = `
          <div class="room-badge">🚪 Room &bull; ${escapeHtml(room)}</div>
          ${lociHtml}
        `;
        container.appendChild(card);
      });
    } catch (e) {}
  }

  // ── VIEW 3: Correction Rules Ledger ─────────────────────────
  async function loadCorrectionLedger() {
    try {
      const res = await fetch("/api/corrections");
      const data = await res.json();
      const rules = data.rules || [];
      const badge = document.getElementById("badge-rules");
      if (badge) badge.textContent = data.active_count || rules.length;

      const container = document.getElementById("ledger-rules-view");
      if (!container) return;
      container.innerHTML = "";

      if (rules.length === 0) {
        container.innerHTML = `
          <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; color: var(--text-dim);">
            <div style="font-size: 32px; margin-bottom: 10px;">📖</div>
            <div style="font-weight: 700; font-size: 16px; color: var(--text-main);">No Rules Recorded Yet</div>
            <p style="font-size: 13px; margin-top: 4px;">Teach the agent rules by clicking "+ Add Correction Rule" or via chat corrections.</p>
          </div>
        `;
        return;
      }

      rules.forEach(r => {
        const card = document.createElement("div");
        card.className = "rule-card";
        card.innerHTML = `
          <div class="rule-card-header">
            <span class="rule-id">RULE ${escapeHtml(r.id)}</span>
            <span class="superpower-badge">${r.active ? 'Active' : 'Retired'} &bull; Weight ${r.weight || 1.0}</span>
          </div>
          <div class="rule-situation">When: ${escapeHtml(r.situation)}</div>
          <div class="rule-instruction">${escapeHtml(r.rule)}</div>
        `;
        container.appendChild(card);
      });
    } catch (e) {}
  }

  // ── VIEW 4: Superpowers & Skills ─────────────────────────────
  async function loadSkills() {
    try {
      const res = await fetch("/api/skills");
      const data = await res.json();
      const skills = data.skills || [];
      const badge = document.getElementById("badge-skills");
      if (badge) badge.textContent = skills.length;

      const container = document.getElementById("skills-grid-view");
      if (!container) return;
      container.innerHTML = "";

      if (skills.length === 0) {
        container.innerHTML = `
          <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; color: var(--text-dim);">
            <div style="font-size: 32px; margin-bottom: 10px;">⚡</div>
            <div style="font-weight: 700; font-size: 16px; color: var(--text-main);">No Superpowers Forged Yet</div>
            <p style="font-size: 13px; margin-top: 4px;">Repeat similar requests 3 times to trigger autonomous skill forging.</p>
          </div>
        `;
        return;
      }

      skills.forEach(s => {
        const card = document.createElement("div");
        card.className = "superpower-card";
        card.innerHTML = `
          <div class="superpower-header">
            <span class="superpower-title">${escapeHtml(s.name)}</span>
            <span class="superpower-badge">${s.badge || '⚡'} ${s.status}</span>
          </div>
          <p class="superpower-desc">${escapeHtml(s.description)}</p>
          <div class="superpower-stats">
            <span>Usage Count: <strong>${s.invocations || 0}</strong></span>
            <span>Success Rate: <strong>${s.success_rate || '100%'}</strong></span>
          </div>
          <button class="btn-test-skill" data-skill="${escapeHtml(s.name)}">⚡ Test Superpower in Chat</button>
        `;

        card.querySelector(".btn-test-skill").addEventListener("click", () => {
          switchTab("chat-tab");
          const promptText = `Execute forged superpower: ${s.name}`;
          composerInput.value = promptText;
          submitUserPrompt(promptText);
        });

        container.appendChild(card);
      });
    } catch (e) {}
  }

  // ── VIEW 5: Morning Briefs & Research ────────────────────────
  async function loadResearchBriefs() {
    try {
      const res = await fetch("/api/research/reports");
      const data = await res.json();
      const reports = data.reports || [];
      const container = document.getElementById("research-briefs-view");
      if (!container) return;
      container.innerHTML = "";

      if (reports.length === 0) {
        container.innerHTML = `
          <div style="text-align: center; padding: 60px 20px; color: var(--text-dim);">
            <div style="font-size: 32px; margin-bottom: 10px;">🌙</div>
            <div style="font-weight: 700; font-size: 16px; color: var(--text-main);">No Morning Briefs Yet</div>
            <p style="font-size: 13px; margin-top: 4px;">Click "Run Research Cycle Now" to synthesize intelligence and adversarial critique.</p>
          </div>
        `;
        return;
      }

      reports.forEach(r => {
        const card = document.createElement("div");
        card.className = "brief-card";
        card.innerHTML = `
          <div class="brief-top">
            <div class="brief-topic">${escapeHtml(r.topic || 'General Intelligence Briefing')}</div>
            <span class="superpower-badge">Adversarial Critique Passed</span>
          </div>
          <div class="brief-body">${formatMarkdown(r.summary || r.report_markdown || '')}</div>
          ${r.critique ? `
            <div class="brief-critique">
              <div class="critique-head">🛡️ Pro Critique Pass:</div>
              <div style="font-size: 12px; color: var(--text-muted);">${escapeHtml(r.critique)}</div>
            </div>
          ` : ''}
        `;
        container.appendChild(card);
      });
    } catch (e) {}
  }

  const btnRunResearch = document.getElementById("btn-run-research");
  if (btnRunResearch) {
    btnRunResearch.addEventListener("click", async () => {
      btnRunResearch.disabled = true;
      btnRunResearch.innerHTML = "Synthesizing intelligence...";
      setAgentState("searching", "Nightly Research", "Conducting deep-dive research & critique pass...");

      try {
        await fetch("/api/research/trigger", { method: "POST" });
        await loadResearchBriefs();
        setAgentState("breathing", "KIW1 Ready", "Research cycle finished");
      } catch (e) {
        setAgentState("breathing", "KIW1 Ready", "Research error");
      } finally {
        btnRunResearch.disabled = false;
        btnRunResearch.innerHTML = `<span>⚡</span> Run Research Cycle Now`;
      }
    });
  }

  // ── VIEW 6: Benchmark & Self-Improvement ──────────────────────
  async function loadBenchmarkResults() {
    try {
      const res = await fetch("/static/results.json");
      const data = await res.json();

      const coldScore = document.getElementById("bench-cold-score");
      const learnedScore = document.getElementById("bench-learned-score");
      const deltaScore = document.getElementById("bench-delta-score");
      const badgeDelta = document.getElementById("badge-delta");

      if (coldScore) coldScore.textContent = `${data.cold_score}`;
      if (learnedScore) learnedScore.textContent = `${data.learned_score}`;
      if (deltaScore) deltaScore.textContent = `${data.delta} Tasks`;
      if (badgeDelta) badgeDelta.textContent = `${data.delta_percentage}`;

      const listContainer = document.getElementById("benchmark-tasks-list");
      if (!listContainer) return;
      listContainer.innerHTML = "";

      const coldResults = data.cold_results || [];
      const learnedResults = data.learned_results || [];

      coldResults.forEach((cold, idx) => {
        const learned = learnedResults[idx] || { passed: false, detail: "" };
        const row = document.createElement("div");
        row.className = "bench-task-row";

        const coldPill = cold.passed ? `<span class="pill-status pass">Cold: PASS</span>` : `<span class="pill-status fail">Cold: FAIL</span>`;
        const learnedPill = learned.passed ? `<span class="pill-status pass">Learned: PASS</span>` : `<span class="pill-status fail">Learned: FAIL</span>`;

        row.innerHTML = `
          <div class="bench-task-info">
            <span class="bench-task-id">${cold.id}</span>
            <span class="bench-task-title">${escapeHtml(cold.name)}</span>
          </div>
          <div class="bench-status-group">
            ${coldPill}
            ${learnedPill}
          </div>
        `;
        listContainer.appendChild(row);
      });
    } catch (e) {}
  }

  const btnRetestBenchmark = document.getElementById("btn-retest-benchmark");
  if (btnRetestBenchmark) {
    btnRetestBenchmark.addEventListener("click", async () => {
      btnRetestBenchmark.disabled = true;
      btnRetestBenchmark.innerHTML = "Executing 20 Tasks...";
      setAgentState("working", "Benchmark In Progress", "Executing 20 cold & learned tasks...");

      try {
        await fetch("/api/evals/run", { method: "POST" }).catch(() => {});
        await loadBenchmarkResults();
        setAgentState("breathing", "KIW1 Ready", "Benchmark completed");
      } catch (e) {
        setAgentState("breathing", "KIW1 Ready", "Benchmark error");
      } finally {
        btnRetestBenchmark.disabled = false;
        btnRetestBenchmark.innerHTML = `<span>▶</span> Re-run Live 20 Tasks`;
      }
    });
  }

  // ── Modals: Teach Rule & Add Memory ──────────────────────────
  const modalCorr = document.getElementById("modal-correction");
  const btnOpenCorrModal = document.getElementById("btn-open-corr-modal");
  const btnCloseCorr = document.getElementById("btn-close-corr");
  const btnCancelCorr = document.getElementById("btn-cancel-corr");
  const btnSaveCorr = document.getElementById("btn-save-corr");

  function openCorrectionModal() {
    if (modalCorr) modalCorr.classList.remove("hidden");
  }

  function closeCorrectionModal() {
    if (modalCorr) modalCorr.classList.add("hidden");
    document.getElementById("input-corr-sit").value = "";
    document.getElementById("input-corr-wrong").value = "";
    document.getElementById("input-corr-rule").value = "";
  }

  if (btnOpenCorrModal) btnOpenCorrModal.addEventListener("click", openCorrectionModal);
  if (btnCloseCorr) btnCloseCorr.addEventListener("click", closeCorrectionModal);
  if (btnCancelCorr) btnCancelCorr.addEventListener("click", closeCorrectionModal);

  if (btnSaveCorr) {
    btnSaveCorr.addEventListener("click", async () => {
      const sit = document.getElementById("input-corr-sit").value.trim();
      const wrong = document.getElementById("input-corr-wrong").value.trim();
      const rule = document.getElementById("input-corr-rule").value.trim();

      if (!sit || !rule) return;

      try {
        await fetch("/api/corrections", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            situation: sit,
            wrong_action: wrong,
            correction: rule,
          }),
        });
        closeCorrectionModal();
        loadCorrectionLedger();
      } catch (e) {}
    });
  }

  // Memory Modal
  const modalMem = document.getElementById("modal-memory");
  const btnOpenMemModal = document.getElementById("btn-open-memory-modal");
  const btnCloseMem = document.getElementById("btn-close-mem");
  const btnCancelMem = document.getElementById("btn-cancel-mem");
  const btnSaveMem = document.getElementById("btn-save-mem");

  function openMemoryModal() {
    if (modalMem) modalMem.classList.remove("hidden");
  }

  function closeMemoryModal() {
    if (modalMem) modalMem.classList.add("hidden");
    document.getElementById("input-mem-fact").value = "";
    document.getElementById("input-mem-room").value = "";
    document.getElementById("input-mem-locus").value = "";
  }

  if (btnOpenMemModal) btnOpenMemModal.addEventListener("click", openMemoryModal);
  if (btnCloseMem) btnCloseMem.addEventListener("click", closeMemoryModal);
  if (btnCancelMem) btnCancelMem.addEventListener("click", closeMemoryModal);

  if (btnSaveMem) {
    btnSaveMem.addEventListener("click", async () => {
      const fact = document.getElementById("input-mem-fact").value.trim();
      const room = document.getElementById("input-mem-room").value.trim();
      const locus = document.getElementById("input-mem-locus").value.trim();

      if (!fact) return;

      try {
        await fetch("/api/memory", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            fact: fact,
            room: room || "general",
            locus: locus || "notes",
          }),
        });
        closeMemoryModal();
        loadMemoryPalace();
      } catch (e) {}
    });
  }

  // Initial loads
  refreshTelemetry();
  loadMemoryPalace();
  loadCorrectionLedger();
  loadSkills();
  loadBenchmarkResults();
});
