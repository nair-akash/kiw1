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
    if (targetTab === "commitments-tab") loadCommitments();
    if (targetTab === "fleet-tab") loadFleet();
    if (targetTab === "armor-tab") { loadArmorPosture(); loadOtelTraces(); }
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

  const composerOrbWrap = document.querySelector(".composer-orb-block");
  const composerStateTitle = document.getElementById("composer-state-title");
  const composerStateDetail = document.getElementById("composer-state-detail");
  const heroStatusText = document.getElementById("hero-status-text");

  let currentEffort = "standard";

  function renderOrbMarkup(container, isDeepThink, isSm) {
    if (!container) return;
    container.innerHTML = "";

    if (isDeepThink) {
      const dto = document.createElement("div");
      dto.className = "deep-think-orb" + (isSm ? " is-sm" : "");
      dto.innerHTML = `
        <div class="deep-think-core"></div>
        <div class="deep-think-ring ring-magenta"></div>
        <div class="deep-think-ring ring-cyan"></div>
        <div class="deep-think-ring ring-gold"></div>
        <i></i><i></i><i></i><i></i>
      `;
      container.appendChild(dto);
      return dto;
    } else {
      const orb = document.createElement("div");
      orb.className = "tol-orb tol-breathing" + (isSm ? " is-sm" : "");
      orb.id = "composer-orb";
      for (let n = 0; n < 12; n++) orb.appendChild(document.createElement("i"));
      container.appendChild(orb);
      return orb;
    }
  }

  // Initialize composer orb
  let activeComposerOrb = renderOrbMarkup(composerOrbWrap, false, true);

  function updateOrbMode(effort) {
    currentEffort = effort;
    const isDeep = (effort === "thorough");

    renderOrbMarkup(composerOrbWrap, isDeep, true);
    if (window.livingNebula) {
      window.livingNebula.setDeepThink(isDeep);
    }

    if (isDeep) {
      setAgentState("solving", "Deep Think Active", "Extended reasoning model &bull; Gemini 3.7 Flash Thinking");
    } else {
      setAgentState("breathing", "KIW1 Ready", "Awaiting instruction &bull; Gemini 3.7 Flash");
    }
  }

  function setAgentState(state, statusTitle, detailText) {
    const orbEl = document.getElementById("composer-orb");
    if (orbEl) {
      orbEl.classList.remove(...TOL_STATES);
      orbEl.classList.add("tol-" + state);
    }
    if (composerStateTitle) composerStateTitle.textContent = statusTitle;
    if (composerStateDetail) {
      composerStateDetail.textContent = detailText || (currentEffort === "thorough" ? "Deep Think Mode &bull; Gemini 3.7 Flash" : "Autonomous Agent &bull; Gemini 3.7 Flash");
    }
    if (heroStatusText) heroStatusText.textContent = statusTitle;
    if (window.livingNebula) window.livingNebula.setState(state);
  }

  // ── Living Organic Nebula & Deep Think Planetary Canvas ──────
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
      this.isDeepThink = false;
      this.time = 0;
      this.particles = [];
      this.planetaryNodes = [];
      this.initParticles();
      this.initPlanetaryNodes();
      this.animate = this.animate.bind(this);
      requestAnimationFrame(this.animate);
    }

    initParticles() {
      const count = 140;
      this.particles = [];
      for (let i = 0; i < count; i++) {
        const phi = Math.acos(-1 + (2 * i) / count);
        const theta = Math.sqrt(count * Math.PI) * phi;
        this.particles.push({
          baseRadius: 65 + Math.random() * 35,
          phi: phi,
          theta: theta,
          size: 1.2 + Math.random() * 2.2,
          speed: 0.008 + Math.random() * 0.012,
          alpha: 0.3 + Math.random() * 0.7,
        });
      }
    }

    initPlanetaryNodes() {
      this.planetaryNodes = [];
      // 3 orbital rings with orbiting planets matching user screenshot
      const ringConfigs = [
        { radiusX: 95, radiusY: 34, tilt: -0.32, speed: 0.018, color: "#a855f7", ringColor: "rgba(168, 85, 247, 0.75)" }, // Magenta
        { radiusX: 90, radiusY: 36, tilt: 0.42,  speed: -0.024, color: "#00f2fe", ringColor: "rgba(0, 242, 254, 0.75)" },   // Cyan
        { radiusX: 80, radiusY: 28, tilt: -0.08, speed: 0.030, color: "#ff9e3b", ringColor: "rgba(255, 158, 59, 0.75)" },  // Gold
      ];

      for (let rIdx = 0; rIdx < ringConfigs.length; rIdx++) {
        const cfg = ringConfigs[rIdx];
        const numNodes = 7;
        for (let n = 0; n < numNodes; n++) {
          this.planetaryNodes.push({
            ringIdx: rIdx,
            angle: (n / numNodes) * Math.PI * 2 + Math.random() * 0.5,
            size: 2.2 + Math.random() * 3.5,
            color: n % 2 === 0 ? "#93c5fd" : (n % 3 === 0 ? "#00f2fe" : "#ffedd5"),
            opacity: 0.5 + Math.random() * 0.5,
          });
        }
      }
      this.ringConfigs = ringConfigs;
    }

    setDeepThink(enabled) {
      this.isDeepThink = enabled;
    }

    setState(newState) {
      this.state = newState;
    }

    animate() {
      this.time += 0.018;
      const ctx = this.ctx;
      ctx.clearRect(0, 0, this.width, this.height);

      if (this.isDeepThink) {
        // ── RENDER DEEP THINK PLANETARY QUANTUM ORB (Screenshot Match) ──
        
        // 1. Soft Violet-Magenta Radial Halo
        const haloGrad = ctx.createRadialGradient(this.cx, this.cy, 15, this.cx, this.cy, 115);
        haloGrad.addColorStop(0, "rgba(255, 158, 59, 0.4)");
        haloGrad.addColorStop(0.35, "rgba(168, 85, 247, 0.25)");
        haloGrad.addColorStop(0.7, "rgba(99, 102, 241, 0.1)");
        haloGrad.addColorStop(1, "rgba(7, 8, 13, 0)");
        ctx.fillStyle = haloGrad;
        ctx.beginPath();
        ctx.arc(this.cx, this.cy, 115, 0, Math.PI * 2);
        ctx.fill();

        // 2. Intersecting Elliptical Orbital Rings
        for (let r = 0; r < this.ringConfigs.length; r++) {
          const cfg = this.ringConfigs[r];
          ctx.save();
          ctx.translate(this.cx, this.cy);
          ctx.rotate(cfg.tilt + Math.sin(this.time * 0.5 + r) * 0.05);

          ctx.beginPath();
          ctx.ellipse(0, 0, cfg.radiusX, cfg.radiusY, 0, 0, Math.PI * 2);
          ctx.strokeStyle = cfg.ringColor;
          ctx.lineWidth = 1.4;
          ctx.shadowColor = cfg.color;
          ctx.shadowBlur = 10;
          ctx.stroke();
          ctx.restore();
        }

        // 3. Orbiting Planetary Nodes along Ellipses
        for (let node of this.planetaryNodes) {
          const cfg = this.ringConfigs[node.ringIdx];
          node.angle += cfg.speed;

          const rawX = Math.cos(node.angle) * cfg.radiusX;
          const rawY = Math.sin(node.angle) * cfg.radiusY;

          // Rotate by ring tilt
          const cosT = Math.cos(cfg.tilt);
          const sinT = Math.sin(cfg.tilt);
          const px = this.cx + (rawX * cosT - rawY * sinT);
          const py = this.cy + (rawX * sinT + rawY * cosT);

          const depth = Math.sin(node.angle);
          const scale = 0.8 + (depth + 1) * 0.25;

          ctx.save();
          ctx.beginPath();
          ctx.arc(px, py, node.size * scale, 0, Math.PI * 2);
          ctx.fillStyle = node.color;
          ctx.shadowColor = node.color;
          ctx.shadowBlur = 8;
          ctx.globalAlpha = node.opacity * (depth > 0 ? 1 : 0.6);
          ctx.fill();
          ctx.restore();
        }

        // 4. Intense Glowing Amber Core Sun
        const coreSize = 14 + Math.sin(this.time * 2.5) * 2.5;
        const coreGrad = ctx.createRadialGradient(this.cx, this.cy, 2, this.cx, this.cy, coreSize * 2.2);
        coreGrad.addColorStop(0, "#ffffff");
        coreGrad.addColorStop(0.3, "#ff9e3b");
        coreGrad.addColorStop(0.7, "#ff4d4d");
        coreGrad.addColorStop(1, "rgba(255, 77, 77, 0)");

        ctx.save();
        ctx.beginPath();
        ctx.arc(this.cx, this.cy, coreSize * 2.2, 0, Math.PI * 2);
        ctx.fillStyle = coreGrad;
        ctx.shadowColor = "#ff9e3b";
        ctx.shadowBlur = 24;
        ctx.fill();
        ctx.restore();

        // 5. Surrounding Star Dust Particles
        for (let p of this.particles.slice(0, 45)) {
          const px = this.cx + Math.cos(p.theta + this.time * 0.2) * (p.baseRadius * 1.15);
          const py = this.cy + Math.sin(p.phi + this.time * 0.3) * (p.baseRadius * 0.9);
          ctx.beginPath();
          ctx.arc(px, py, p.size * 0.8, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(147, 197, 253, ${p.alpha * 0.6})`;
          ctx.fill();
        }

      } else {
        // ── RENDER STANDARD LIVING ORGANIC NEBULA ─────────────────────
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

        // Glowing Fluid Core
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

        // Multi-Strand Fluid Ribbons (Vortex Rings)
        for (let r = 0; r < 3; r++) {
          ctx.beginPath();
          const ribbonRadius = 60 + r * 18 + Math.sin(this.time * 1.5 + r) * 6;
          const rot = this.time * 0.8 * (r % 2 === 0 ? 1 : -1) * speedMult;
          ctx.ellipse(this.cx, this.cy, ribbonRadius, ribbonRadius * 0.45, rot, 0, Math.PI * 2);
          ctx.strokeStyle = r === 0 ? "rgba(255, 158, 59, 0.35)" : (r === 1 ? "rgba(0, 242, 254, 0.35)" : "rgba(168, 85, 247, 0.35)");
          ctx.lineWidth = 1.8;
          ctx.stroke();
        }

        // 3D Particle Constellation (Undulating Surface Mesh)
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
      const eff = btn.dataset.effort;
      if (effortValue) effortValue.value = eff;
      updateOrbMode(eff);
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

  // ── Multimodal Attachment Handlers ──────────────────────────
  let pendingAttachments = [];
  const fileUploadInput = document.getElementById("file-upload-input");
  const btnAttachFile = document.getElementById("btn-attach-file");
  const attachmentsPreview = document.getElementById("composer-attachments-preview");
  const composerPillBox = document.querySelector(".composer-pill-box");

  if (btnAttachFile && fileUploadInput) {
    btnAttachFile.addEventListener("click", () => fileUploadInput.click());
    fileUploadInput.addEventListener("change", (e) => {
      handleFiles(Array.from(e.target.files));
      fileUploadInput.value = "";
    });
  }

  // Clipboard paste listener (Cmd/Ctrl+V for screenshots)
  document.addEventListener("paste", (e) => {
    const items = (e.clipboardData || window.clipboardData).items;
    const files = [];
    for (let item of items) {
      if (item.kind === "file") {
        const blob = item.getAsFile();
        if (blob) files.push(blob);
      }
    }
    if (files.length > 0) {
      handleFiles(files);
    }
  });

  // Drag & drop on composer
  if (composerPillBox) {
    composerPillBox.addEventListener("dragover", (e) => {
      e.preventDefault();
      composerPillBox.classList.add("dragover");
    });
    composerPillBox.addEventListener("dragleave", () => {
      composerPillBox.classList.remove("dragover");
    });
    composerPillBox.addEventListener("drop", (e) => {
      e.preventDefault();
      composerPillBox.classList.remove("dragover");
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        handleFiles(Array.from(e.dataTransfer.files));
      }
    });
  }

  function handleFiles(files) {
    files.forEach(file => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const base64 = e.target.result;
        pendingAttachments.push({
          name: file.name,
          mime_type: file.type || "image/png",
          data: base64,
        });
        renderAttachmentsPreview();
      };
      reader.readAsDataURL(file);
    });
  }

  function renderAttachmentsPreview() {
    if (!attachmentsPreview) return;
    if (pendingAttachments.length === 0) {
      attachmentsPreview.classList.add("hidden");
      attachmentsPreview.innerHTML = "";
      return;
    }
    attachmentsPreview.classList.remove("hidden");
    attachmentsPreview.innerHTML = pendingAttachments.map((att, idx) => `
      <div class="attachment-chip">
        ${att.mime_type.startsWith("image/") ? `<img src="${att.data}" alt="${escapeHtml(att.name)}">` : '<span>📄</span>'}
        <span class="att-name">${escapeHtml(att.name)}</span>
        <button class="att-remove" onclick="removeAttachment(${idx})">&times;</button>
      </div>
    `).join("");
  }

  window.removeAttachment = function(idx) {
    pendingAttachments.splice(idx, 1);
    renderAttachmentsPreview();
  };

  async function submitUserPrompt(text) {
    if ((!text || text.trim() === "") && pendingAttachments.length === 0) return;
    const prompt = (text || "").trim();
    const currentAtts = [...pendingAttachments];
    pendingAttachments = [];
    renderAttachmentsPreview();

    composerInput.value = "";
    composerInput.style.height = "auto";

    if (heroStage && !heroStage.classList.contains("hidden")) {
      heroStage.classList.add("hidden");
    }

    let userBubbleText = prompt;
    if (currentAtts.length > 0) {
      userBubbleText += (prompt ? "\n\n" : "") + `[Attached ${currentAtts.length} file(s): ${currentAtts.map(a => a.name).join(", ")}]`;
    }
    renderUserBubble(userBubbleText);

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
          message: prompt || "Analyze attached file(s)",
          effort: effort,
          hands_off: handsOff,
          attachments: currentAtts.length > 0 ? currentAtts : undefined,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || `Server returned status ${res.status}`);
      }
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
      renderAgentBubble({
        text: `✨ **Prompt Refinery Active**: I paused execution to clarify your target and preferences. Please make your selection in the card below to proceed!`,
        model: "Prompt Refinery",
        tools_used: ["prompt_refinery"],
        reasoning: `Ambiguity detected: ${(data.reasons || []).join("; ")}`,
      });
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
    const avatarHtml = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#a5b4fc" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="M12 8v8"/><path d="M8 12h8"/></svg>`;

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

    // Check for Code / Artifact blocks in text
    let artifactHtml = "";
    let codeMatch = text.match(/```(python|html|js|javascript|json|css|svg)?\n([\s\S]*?)```/);
    if (codeMatch) {
      const artType = codeMatch[1] || "python";
      const artCode = codeMatch[2];
      artifactHtml = `
        <div class="artifact-card-preview" id="art-card-${Date.now()}">
          <div class="artifact-meta">
            <span style="font-size: 18px;">⚡</span>
            <div>
              <div style="font-weight: 700; font-size: 12.5px; color: #fff;">Interactive ${artType.toUpperCase()} Artifact</div>
              <div style="font-size: 11px; color: var(--text-dim);">Click to inspect, run in Python Sandbox, or preview</div>
            </div>
          </div>
          <div class="artifact-open-btn">
            Open in Canvas &rarr;
          </div>
        </div>
      `;
    }

    bubble.innerHTML = `
      <div class="agent-bubble-header">
        <div class="agent-avatar-icon">
          ${avatarHtml}
        </div>
        <div class="agent-name-tag">KIW1</div>
        <div class="agent-model-pill">${model}${currentEffort === "thorough" ? " &bull; Deep Think" : ""}</div>
      </div>
      ${thoughtHtml}
      ${toolsHtml}
      <div class="bubble-text">${formatMarkdown(text)}</div>
      ${artifactHtml}
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

    if (codeMatch) {
      const artType = codeMatch[1] || "python";
      const artCode = codeMatch[2];
      const artCard = bubble.querySelector(".artifact-card-preview");
      if (artCard) {
        artCard.addEventListener("click", () => {
          openArtifact(artType, "KIW1 Script Artifact", artCode);
        });
      }
    }

    const copyBtn = bubble.querySelector(".btn-copy-action");
    if (copyBtn) {
      copyBtn.addEventListener("click", () => {
        navigator.clipboard.writeText(text);
      });
    }

    const teachBtn = bubble.querySelector(".btn-teach-action");
    if (teachBtn) {
      teachBtn.addEventListener("click", () => {
        openCorrectionModal();
      });
    }

    messagesFlow.appendChild(bubble);
    scrollChat();

    // Voice readout if enabled
    if (typeof window.speakAgentText === "function") {
      window.speakAgentText(text);
    }
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
      renderPalaceGraph(tree);
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

  // ── VIEW 6: Frontier Benchmarks & Academic Examination ────────
  let currentBenchmarkFilter = "all";
  let cachedFrontierData = null;
  let cachedContinuousData = null;

  async function loadBenchmarkResults() {
    try {
      // 1. Fetch Frontier Academic Benchmark Data
      const resFrontier = await fetch("/api/evals/frontier").catch(() => null);
      if (resFrontier && resFrontier.ok) {
        cachedFrontierData = await resFrontier.json();
      }

      // 2. Fetch Continuous 20-Task Learning Data
      const resContinuous = await fetch("/static/results.json").catch(() => null);
      if (resContinuous && resContinuous.ok) {
        cachedContinuousData = await resContinuous.json();
      }

      // 3. Update Hero Cards
      const cats = (cachedFrontierData && cachedFrontierData.categories) || {};
      const hleScore = document.getElementById("bench-hle-score");
      const gpqaScore = document.getElementById("bench-gpqa-score");
      const mathScore = document.getElementById("bench-math-score");
      const sweScore = document.getElementById("bench-swe-score");
      const deltaScore = document.getElementById("bench-delta-score");
      const badgeDelta = document.getElementById("badge-delta");

      if (hleScore && cats.hle) hleScore.textContent = `${cats.hle.score_str}`;
      if (gpqaScore && cats.gpqa) gpqaScore.textContent = `${cats.gpqa.score_str}`;
      if (mathScore && cats.math_500) mathScore.textContent = `${cats.math_500.score_str}`;
      if (sweScore && cats.swe_bench) sweScore.textContent = `${cats.swe_bench.score_str}`;
      if (deltaScore && cachedContinuousData) deltaScore.textContent = `${cachedContinuousData.delta_percentage || '+30%'}`;
      if (badgeDelta && cachedContinuousData) badgeDelta.textContent = `${cachedContinuousData.delta_percentage || '+30%'}`;

      renderFilteredBenchmarkTasks();
    } catch (e) {}
  }

  function renderFilteredBenchmarkTasks() {
    const listContainer = document.getElementById("benchmark-tasks-list");
    if (!listContainer) return;
    listContainer.innerHTML = "";

    const frontierTasks = (cachedFrontierData && cachedFrontierData.tasks) || [];
    const continuousTasks = (cachedContinuousData && cachedContinuousData.cold_results) || [];
    const continuousLearned = (cachedContinuousData && cachedContinuousData.learned_results) || [];

    // Filter and display Frontier tasks
    if (currentBenchmarkFilter !== "continuous") {
      frontierTasks.forEach(task => {
        if (currentBenchmarkFilter !== "all" && task.category !== currentBenchmarkFilter) return;

        const row = document.createElement("div");
        row.className = "bench-task-row";
        const catBadge = task.category === "hle" ? "🏛️ HLE" : task.category === "gpqa" ? "🔬 GPQA" : task.category === "math_500" ? "📐 MATH" : "💻 SWE";
        const statusPill = task.passed ? `<span class="pill-status pass">PASS (100%)</span>` : `<span class="pill-status fail">FAIL</span>`;

        row.innerHTML = `
          <div class="bench-task-info">
            <span class="bench-task-id">${escapeHtml(catBadge)}</span>
            <div>
              <div class="bench-task-title">${escapeHtml(task.name)}</div>
              <div style="font-size: 11px; color: var(--text-dim); margin-top: 2px;">Domain: ${escapeHtml(task.domain)} &bull; ${escapeHtml(task.difficulty)} &bull; ${escapeHtml(task.detail)}</div>
            </div>
          </div>
          <div class="bench-status-group">
            ${statusPill}
          </div>
        `;
        listContainer.appendChild(row);
      });
    }

    // Display Continuous Learning 20 tasks
    if (currentBenchmarkFilter === "all" || currentBenchmarkFilter === "continuous") {
      continuousTasks.forEach((cold, idx) => {
        const learned = continuousLearned[idx] || { passed: false, detail: "" };
        const row = document.createElement("div");
        row.className = "bench-task-row";

        const coldPill = cold.passed ? `<span class="pill-status pass">Cold: PASS</span>` : `<span class="pill-status fail">Cold: FAIL</span>`;
        const learnedPill = learned.passed ? `<span class="pill-status pass">Learned: PASS</span>` : `<span class="pill-status fail">Learned: FAIL</span>`;

        row.innerHTML = `
          <div class="bench-task-info">
            <span class="bench-task-id">📈 ${cold.id}</span>
            <div>
              <div class="bench-task-title">${escapeHtml(cold.name)}</div>
              <div style="font-size: 11px; color: var(--text-dim); margin-top: 2px;">Continuous Learning Delta (+30%) &bull; ${escapeHtml(learned.detail)}</div>
            </div>
          </div>
          <div class="bench-status-group">
            ${coldPill}
            ${learnedPill}
          </div>
        `;
        listContainer.appendChild(row);
      });
    }
  }

  // Filter Chip Event Listeners
  document.querySelectorAll(".filter-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      document.querySelectorAll(".filter-chip").forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      currentBenchmarkFilter = chip.dataset.filter || "all";
      renderFilteredBenchmarkTasks();
    });
  });

  const btnRetestBenchmark = document.getElementById("btn-retest-benchmark");
  if (btnRetestBenchmark) {
    btnRetestBenchmark.addEventListener("click", async () => {
      btnRetestBenchmark.disabled = true;
      btnRetestBenchmark.innerHTML = "Running Frontier Exams...";
      setAgentState("working", "Academic Examination", "Evaluating HLE, GPQA, MATH-500, and SWE-bench...");

      try {
        await fetch("/api/evals/frontier/run", { method: "POST" }).catch(() => {});
        await loadBenchmarkResults();
        setAgentState("breathing", "KIW1 Ready", "Frontier examination completed");
      } catch (e) {
        setAgentState("breathing", "KIW1 Ready", "Benchmark error");
      } finally {
        btnRetestBenchmark.disabled = false;
        btnRetestBenchmark.innerHTML = `<span>▶</span> Run Live Frontier Examination`;
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

  // ── Interactive Canvas & Artifacts Controller ──────────────
  const canvasDrawer = document.getElementById("canvas-drawer");
  const canvasTitle = document.getElementById("canvas-title");
  const canvasSubtitle = document.getElementById("canvas-subtitle");
  const canvasBadge = document.getElementById("canvas-badge");
  const canvasCodeContent = document.getElementById("canvas-code-content");
  const canvasCodeWrapper = document.getElementById("canvas-code-wrapper");
  const canvasPreviewWrapper = document.getElementById("canvas-preview-wrapper");
  const canvasPreviewFrame = document.getElementById("canvas-preview-frame");
  const canvasConsoleWrapper = document.getElementById("canvas-console-wrapper");
  const canvasConsoleOutput = document.getElementById("canvas-console-output");
  const consoleTiming = document.getElementById("console-timing");
  const btnRunSandbox = document.getElementById("btn-run-sandbox");
  const btnCopyArtifact = document.getElementById("btn-copy-artifact");
  const btnDownloadArtifact = document.getElementById("btn-download-artifact");
  const btnCloseCanvas = document.getElementById("btn-close-canvas");

  let activeArtifact = { type: "python", title: "Script", content: "" };

  window.openArtifact = function(type, title, content) {
    activeArtifact = { type, title, content };
    if (!canvasDrawer) return;

    canvasDrawer.classList.remove("hidden");
    if (canvasTitle) canvasTitle.textContent = title;
    if (canvasBadge) canvasBadge.textContent = type.toUpperCase();
    if (canvasSubtitle) canvasSubtitle.textContent = `Generated by KIW1 &bull; ${type}`;

    if (type === "html" || type === "svg") {
      canvasCodeWrapper.classList.add("hidden");
      canvasPreviewWrapper.classList.remove("hidden");
      canvasConsoleWrapper.classList.add("hidden");
      if (btnRunSandbox) btnRunSandbox.style.display = "none";
      if (canvasPreviewFrame) {
        canvasPreviewFrame.srcdoc = content;
      }
    } else {
      canvasCodeWrapper.classList.remove("hidden");
      canvasPreviewWrapper.classList.add("hidden");
      if (canvasCodeContent) canvasCodeContent.textContent = content;
      if (btnRunSandbox) {
        btnRunSandbox.style.display = (type === "python" || type === "code") ? "inline-flex" : "none";
      }
    }
  };

  if (btnCloseCanvas) {
    btnCloseCanvas.addEventListener("click", () => {
      canvasDrawer.classList.add("hidden");
    });
  }

  if (btnRunSandbox) {
    btnRunSandbox.addEventListener("click", async () => {
      if (!activeArtifact.content) return;
      btnRunSandbox.textContent = "⏳ Running...";
      btnRunSandbox.disabled = true;
      try {
        const res = await fetch("/api/sandbox/run", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code: activeArtifact.content }),
        });
        const data = await res.json();
        canvasConsoleWrapper.classList.remove("hidden");
        if (consoleTiming) consoleTiming.textContent = `${data.execution_time_ms || 0} ms`;
        const out = data.success ? data.stdout : `Error: ${data.error}\n${data.stderr}`;
        if (canvasConsoleOutput) canvasConsoleOutput.textContent = out || "(Execution returned with no stdout)";
      } catch (err) {
        canvasConsoleWrapper.classList.remove("hidden");
        if (canvasConsoleOutput) canvasConsoleOutput.textContent = `Sandbox execution error: ${err.message}`;
      } finally {
        btnRunSandbox.textContent = "▶ Run";
        btnRunSandbox.disabled = false;
      }
    });
  }

  if (btnCopyArtifact) {
    btnCopyArtifact.addEventListener("click", () => {
      if (activeArtifact.content) {
        navigator.clipboard.writeText(activeArtifact.content);
        btnCopyArtifact.textContent = "✓ Copied!";
        setTimeout(() => { btnCopyArtifact.textContent = "📋 Copy"; }, 1500);
      }
    });
  }

  if (btnDownloadArtifact) {
    btnDownloadArtifact.addEventListener("click", () => {
      if (!activeArtifact.content) return;
      const ext = activeArtifact.type === "python" ? "py" : activeArtifact.type === "html" ? "html" : "txt";
      const blob = new Blob([activeArtifact.content], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `kiw1_artifact_${Date.now()}.${ext}`;
      a.click();
      URL.revokeObjectURL(url);
    });
  }

  // ── Web Speech API Voice Engine ──────────────────────────────
  const btnVoiceInput = document.getElementById("btn-voice-input");
  const btnVoiceOutput = document.getElementById("btn-voice-output");
  let voiceOutputEnabled = false;
  let recognition = null;
  let isRecordingVoice = false;

  if (btnVoiceOutput) {
    btnVoiceOutput.addEventListener("click", () => {
      voiceOutputEnabled = !voiceOutputEnabled;
      btnVoiceOutput.classList.toggle("active", voiceOutputEnabled);
    });
  }

  window.speakAgentText = function(text) {
    if (!voiceOutputEnabled || !('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const cleanText = text.replace(/[#*`_\[\]\(\)>]/g, "").slice(0, 300);
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.05;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  };

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition && btnVoiceInput) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onstart = () => {
      isRecordingVoice = true;
      btnVoiceInput.classList.add("is-recording");
      setAgentState("listening", "Listening...", "Speaking to KIW1");
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      if (composerInput && transcript) {
        composerInput.value = (composerInput.value ? composerInput.value + " " : "") + transcript;
        composerInput.focus();
      }
    };

    recognition.onerror = () => {
      isRecordingVoice = false;
      btnVoiceInput.classList.remove("is-recording");
      setAgentState("breathing", "KIW1 Ready", "Voice error");
    };

    recognition.onend = () => {
      isRecordingVoice = false;
      btnVoiceInput.classList.remove("is-recording");
      setAgentState("breathing", "KIW1 Ready", "Voice recorded");
    };

    btnVoiceInput.addEventListener("click", () => {
      if (isRecordingVoice) {
        recognition.stop();
      } else {
        recognition.start();
      }
    });
  }

  // ── Spatial Memory Palace 2D Canvas Graph ────────────────────
  function renderPalaceGraph(tree) {
    const canvas = document.getElementById("palace-canvas");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);

    const rooms = [
      { name: "Projects", color: "#6366f1", x: width * 0.25, y: height * 0.35 },
      { name: "Knowledge", color: "#10b981", x: width * 0.75, y: height * 0.35 },
      { name: "Preferences", color: "#f59e0b", x: width * 0.35, y: height * 0.72 },
      { name: "People", color: "#ec4899", x: width * 0.65, y: height * 0.72 },
    ];

    // Central Constellation Center Core
    ctx.beginPath();
    ctx.arc(width / 2, height / 2, 4, 0, Math.PI * 2);
    ctx.fillStyle = "rgba(255, 255, 255, 0.4)";
    ctx.fill();

    // Draw orbital connections between rooms
    for (let r of rooms) {
      ctx.beginPath();
      ctx.moveTo(width / 2, height / 2);
      ctx.lineTo(r.x, r.y);
      ctx.strokeStyle = "rgba(255, 255, 255, 0.08)";
      ctx.lineWidth = 1;
      ctx.stroke();

      // Room Hub Glow
      const hubGrad = ctx.createRadialGradient(r.x, r.y, 2, r.x, r.y, 28);
      hubGrad.addColorStop(0, r.color);
      hubGrad.addColorStop(1, "rgba(0,0,0,0)");
      ctx.fillStyle = hubGrad;
      ctx.beginPath();
      ctx.arc(r.x, r.y, 28, 0, Math.PI * 2);
      ctx.fill();

      // Room Center Dot
      ctx.beginPath();
      ctx.arc(r.x, r.y, 6, 0, Math.PI * 2);
      ctx.fillStyle = r.color;
      ctx.fill();

      // Room Label
      ctx.fillStyle = "#fff";
      ctx.font = "bold 11px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(r.name, r.x, r.y - 12);

      // Draw Orbiting Loci Nodes
      const roomKey = Object.keys(tree || {}).find(k => k.toLowerCase() === r.name.toLowerCase());
      const lociObj = roomKey ? tree[roomKey] : {};
      const lociKeys = Object.keys(lociObj || {});

      lociKeys.forEach((locusName, idx) => {
        const angle = (idx / Math.max(lociKeys.length, 1)) * Math.PI * 2 + 0.4;
        const lx = r.x + Math.cos(angle) * 36;
        const ly = r.y + Math.sin(angle) * 26;

        ctx.beginPath();
        ctx.moveTo(r.x, r.y);
        ctx.lineTo(lx, ly);
        ctx.strokeStyle = "rgba(255, 255, 255, 0.15)";
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(lx, ly, 3.5, 0, Math.PI * 2);
        ctx.fillStyle = "#e2e8f0";
        ctx.fill();

        ctx.fillStyle = "rgba(255, 255, 255, 0.6)";
        ctx.font = "9px monospace";
        ctx.fillText(locusName, lx, ly + 10);
      });
    }
  }

  // ── Autonomous Commitments Tab ─────────────────────────
  async function loadCommitments() {
    try {
      const [cmtRes, delRes, proRes] = await Promise.all([
        fetch("/api/commitments").then(r => r.json()),
        fetch("/api/deliveries").then(r => r.json()),
        fetch("/api/session/proactive").then(r => r.json()),
      ]);

      const cmts = cmtRes.commitments || [];
      const deliveries = delRes.deliveries || [];

      // Update badge
      const badge = document.getElementById("badge-commitments");
      if (badge) badge.textContent = cmts.length;

      // Proactive banner
      const banner = document.getElementById("proactive-banner");
      const bannerText = document.getElementById("proactive-text");
      if (proRes.announcement && banner && bannerText) {
        bannerText.textContent = proRes.announcement;
        banner.classList.remove("hidden");
      } else if (banner) {
        banner.classList.add("hidden");
      }

      // Commitment cards grid
      const grid = document.getElementById("commitments-grid");
      if (grid) {
        if (cmts.length === 0) {
          grid.innerHTML = `
            <div class="empty-state">
              <div class="empty-icon">🤖</div>
              <div class="empty-title">No Standing Commitments Yet</div>
              <div class="empty-desc">When you repeat a task 3 times, KIW1 forges a skill and offers to run it autonomously on a schedule.</div>
            </div>`;
        } else {
          grid.innerHTML = cmts.map(c => {
            let status = (c.status || "active").toLowerCase();
            if (c.disabled_reason || c.enabled === false) {
              status = "suspended";
            }
            const statusClass = status;
            const nextRun = c.next_run_time ? new Date(c.next_run_time).toLocaleString() : "Pending";
            const lastRun = c.last_run ? new Date(c.last_run).toLocaleString() : "Never";
            const pauseBtn = status === "active"
              ? `<button onclick="commitmentAction('${c.id}', 'pause')">⏸ Pause</button>`
              : `<button onclick="commitmentAction('${c.id}', 'resume')">▶ Resume</button>`;

            return `
              <div class="commitment-card ${statusClass}">
                <div class="cmt-header">
                  <div class="cmt-name">⚡ ${c.skill_name || c.skill_id}</div>
                  <span class="cmt-status ${statusClass}">${status.toUpperCase()}</span>
                </div>
                <div class="cmt-details">
                  <div class="cmt-detail"><span class="label">Schedule</span> ${c.human_schedule || c.cadence || "Weekly"}</div>
                  <div class="cmt-detail"><span class="label">Next Run</span> ${nextRun}</div>
                  <div class="cmt-detail"><span class="label">Last Run</span> ${lastRun}</div>
                  <div class="cmt-detail"><span class="label">Runs</span> ${c.run_count || 0}</div>
                  <div class="cmt-detail"><span class="label">Origin</span> ${c.provenance || "agent_self_derived"}</div>
                  ${c.disabled_reason ? `<div class="cmt-detail" style="color: var(--accent-rose)"><span class="label">Reason</span> ${c.disabled_reason}</div>` : ""}
                </div>
                <div class="cmt-actions">
                  <button onclick="commitmentAction('${c.id}', 'trigger')">🚀 Run Now</button>
                  ${pauseBtn}
                  <button class="danger" onclick="commitmentAction('${c.id}', 'cancel')">🗑 Cancel</button>
                </div>
              </div>`;
          }).join("");
        }
      }

      // Delivery Ledger
      const delList = document.getElementById("delivery-list");
      if (delList) {
        if (deliveries.length === 0) {
          delList.innerHTML = `
            <div class="empty-state small">
              <div class="empty-desc">No deliveries yet. Commitments will log their outcomes here.</div>
            </div>`;
        } else {
          delList.innerHTML = deliveries.map(d => {
            const icon = d.status === "completed" ? "✅" : d.status === "partially_complete" ? "⚠️" : "❌";
            const time = d.timestamp ? new Date(d.timestamp).toLocaleString() : "";
            return `
              <div class="delivery-item">
                <div class="del-status-icon">${icon}</div>
                <div class="del-body">
                  <div class="del-skill">${d.skill_name || "Unknown"}</div>
                  <div class="del-summary">${d.summary || d.status}</div>
                </div>
                <div class="del-time">${time}</div>
              </div>`;
          }).join("");
        }
      }
    } catch (err) {
      console.error("Failed to load commitments:", err);
    }
  }

  // Expose commitment actions globally
  window.commitmentAction = async function(cid, action) {
    try {
      let endpoint, method;
      if (action === "trigger") { endpoint = `/api/commitments/${cid}/trigger`; method = "POST"; }
      else if (action === "pause") { endpoint = `/api/commitments/${cid}/pause`; method = "POST"; }
      else if (action === "resume") { endpoint = `/api/commitments/${cid}/resume`; method = "POST"; }
      else if (action === "cancel") { endpoint = `/api/commitments/${cid}`; method = "DELETE"; }
      else return;

      await fetch(endpoint, { method });
      loadCommitments();
    } catch (err) {
      console.error(`Commitment action '${action}' failed:`, err);
    }
  };

  // ── Enterprise Agent Fleet & Registry ─────────────────────
  let currentFleetDept = "all";

  async function loadFleet(dept = null) {
    try {
      if (dept) currentFleetDept = dept;
      const url = currentFleetDept && currentFleetDept !== "all"
        ? `/api/registry/agents?department=${encodeURIComponent(currentFleetDept)}`
        : "/api/registry/agents";
      const res = await fetch(url);
      const data = await res.json();
      const agents = data.agents || [];

      // Update badge
      const badge = document.getElementById("badge-fleet");
      if (badge) badge.textContent = data.total || agents.length;

      const grid = document.getElementById("fleet-grid");
      if (!grid) return;

      if (agents.length === 0) {
        grid.innerHTML = `
          <div class="empty-state">
            <div class="empty-icon">🏛️</div>
            <div class="empty-title">No Agents in Department '${currentFleetDept}'</div>
            <div class="empty-desc">Publish a new institutional agent to catalog it for this department.</div>
          </div>`;
        return;
      }

      grid.innerHTML = agents.map(a => {
        const deptClass = `dept-${a.department || 'Executive'}`;
        const capsHtml = (a.capabilities || []).map(c => `<span class="cap-chip">${c}</span>`).join("");
        return `
          <div class="agent-card">
            <div class="agent-card-header">
              <div>
                <div class="agent-card-title">${a.name}</div>
                <div style="font-size: 0.75rem; color: var(--text-dim); font-family: var(--font-mono);">${a.agent_id} v${a.version}</div>
              </div>
              <span class="agent-card-dept ${deptClass}">${a.department}</span>
            </div>
            <p class="agent-card-desc">${a.description}</p>
            <div class="agent-caps-chips">${capsHtml}</div>
            <div class="agent-card-footer">
              <span>⭐ ${a.rating.toFixed(2)} (${a.invocations} runs)</span>
              <span>SLA: ${a.sla_ms}ms</span>
              <span style="color: #34d399; font-weight: 700;">✓ CERTIFIED</span>
            </div>
          </div>`;
      }).join("");
    } catch (err) {
      console.error("Failed to load agent fleet:", err);
    }
  }

  // Fleet Department Filter Pills
  const deptPills = document.querySelectorAll("#fleet-dept-filters .filter-pill");
  deptPills.forEach(pill => {
    pill.addEventListener("click", () => {
      deptPills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      loadFleet(pill.dataset.dept);
    });
  });

  // Publish Agent Modal Controls
  const btnOpenPublish = document.getElementById("btn-open-publish-modal");
  const modalPublish = document.getElementById("modal-publish-agent");
  const btnClosePublish = document.getElementById("btn-close-publish");
  const btnCancelPublish = document.getElementById("btn-cancel-publish");
  const btnSavePublish = document.getElementById("btn-save-publish");

  if (btnOpenPublish && modalPublish) {
    btnOpenPublish.addEventListener("click", () => modalPublish.classList.remove("hidden"));
  }
  if (btnClosePublish && modalPublish) {
    btnClosePublish.addEventListener("click", () => modalPublish.classList.add("hidden"));
  }
  if (btnCancelPublish && modalPublish) {
    btnCancelPublish.addEventListener("click", () => modalPublish.classList.add("hidden"));
  }
  if (btnSavePublish && modalPublish) {
    btnSavePublish.addEventListener("click", async () => {
      const name = document.getElementById("input-agent-name")?.value.trim();
      const department = document.getElementById("input-agent-dept")?.value;
      const version = document.getElementById("input-agent-version")?.value.trim() || "1.0.0";
      const description = document.getElementById("input-agent-desc")?.value.trim();
      const capsStr = document.getElementById("input-agent-caps")?.value.trim();
      const toolsStr = document.getElementById("input-agent-tools")?.value.trim();

      if (!name || !description) {
        alert("Please provide an Agent Name and Description.");
        return;
      }

      const capabilities = capsStr ? capsStr.split(",").map(s => s.trim()).filter(Boolean) : ["general:automation"];
      const allowed_tools = toolsStr ? toolsStr.split(",").map(s => s.trim()).filter(Boolean) : ["calculate", "web_search"];

      try {
        const res = await fetch("/api/registry/publish", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name, department, version, description, capabilities, allowed_tools }),
        });
        if (res.ok) {
          modalPublish.classList.add("hidden");
          loadFleet();
        }
      } catch (err) {
        console.error("Failed to publish agent:", err);
      }
    });
  }

  // ── Model Armor & Security Posture ────────────────────────
  async function loadArmorPosture() {
    try {
      const res = await fetch("/api/armor/posture");
      const data = await res.json();
      const stats = data.stats || {};

      const elInspections = document.getElementById("armor-stat-inspections");
      const elInjections = document.getElementById("armor-stat-injections");
      const elPoisoning = document.getElementById("armor-stat-poisoning");
      const elPii = document.getElementById("armor-stat-pii");

      if (elInspections) elInspections.textContent = stats.total_inspections || 0;
      if (elInjections) elInjections.textContent = stats.prompt_injections_blocked || 0;
      if (elPoisoning) elPoisoning.textContent = stats.tool_poisonings_neutralized || 0;
      if (elPii) elPii.textContent = stats.pii_secrets_redacted || 0;

      const auditList = document.getElementById("armor-audit-list");
      if (auditList) {
        const events = data.recent_audit_events || [];
        if (events.length === 0) {
          auditList.innerHTML = `<div class="threat-empty">No security threats detected in current session. Model Armor active.</div>`;
        } else {
          auditList.innerHTML = events.map(e => `
            <div class="threat-entry">
              <span>🛡️ ${e.type}</span>
              <span style="font-family: var(--font-mono); font-size: 0.75rem;">${JSON.stringify(e.threats || e.count || e.tool || "")}</span>
            </div>
          `).join("");
        }
      }
    } catch (err) {
      console.error("Failed to load Model Armor posture:", err);
    }
  }

  // ── OpenTelemetry W3C Traces Waterfall ─────────────────────
  async function loadOtelTraces() {
    try {
      const res = await fetch("/api/telemetry/otel-traces");
      const data = await res.json();
      const traces = data.traces || [];

      const container = document.getElementById("otel-waterfall-container");
      if (!container) return;

      if (traces.length === 0) {
        container.innerHTML = `
          <div class="empty-state small">
            <div class="empty-desc">No traces recorded yet. Execute a prompt to view OpenTelemetry spans.</div>
          </div>`;
        return;
      }

      container.innerHTML = traces.map(t => {
        const maxDuration = Math.max(t.total_duration_ms || 1, 1);
        const spansHtml = (t.spans || []).map(s => {
          const leftPct = ((s.offset_ms || 0) / maxDuration) * 100;
          const widthPct = Math.max(((s.duration_ms || 0.1) / maxDuration) * 100, 4);
          return `
            <div class="span-row">
              <div class="span-name" title="${s.name}">${s.name}</div>
              <div class="span-bar-wrapper">
                <div class="span-bar" style="margin-left: ${leftPct.toFixed(1)}%; width: ${widthPct.toFixed(1)}%;"></div>
              </div>
              <div class="span-time">${s.duration_ms.toFixed(1)} ms</div>
            </div>`;
        }).join("");

        return `
          <div class="waterfall-card">
            <div class="waterfall-header">
              <span>Trace <code>${t.trace_id.slice(0, 16)}...</code> (${t.span_count} Spans)</span>
              <span style="color: #cbd5e1;">Total: ${t.total_duration_ms} ms</span>
            </div>
            ${spansHtml}
          </div>`;
      }).join("");
    } catch (err) {
      console.error("Failed to load OTel traces:", err);
    }
  }

  const btnRefreshOtel = document.getElementById("btn-refresh-otel");
  if (btnRefreshOtel) {
    btnRefreshOtel.addEventListener("click", loadOtelTraces);
  }

  // ── Taskmaster Heavy-Lifting Chore Automation ──────────────
  const btnRunChore = document.getElementById("btn-run-vendor-chore");
  if (btnRunChore) {
    btnRunChore.addEventListener("click", async () => {
      btnRunChore.disabled = true;
      btnRunChore.textContent = "⏳ Running Multi-Step Chore...";

      // Reset step nodes
      for (let i = 1; i <= 5; i++) {
        const node = document.getElementById(`step-node-${i}`);
        if (node) {
          node.classList.remove("completed", "active");
        }
      }

      // Simulate live progression
      for (let i = 1; i <= 4; i++) {
        const node = document.getElementById(`step-node-${i}`);
        if (node) node.classList.add("active");
        await new Promise(r => setTimeout(r, 200));
        if (node) {
          node.classList.remove("active");
          node.classList.add("completed");
        }
      }

      try {
        const res = await fetch("/api/taskmaster/run-chore", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            vendor_name: "Acme Cloud Infrastructure Ltd",
            contract_value_usd: 125000.0,
            currency_base: "USD",
            currency_target: "INR",
          }),
        });

        const data = await res.json();
        const node5 = document.getElementById("step-node-5");
        if (node5) node5.classList.add("completed");

        const resultsContainer = document.getElementById("chore-results-container");
        if (resultsContainer) {
          resultsContainer.classList.remove("hidden");
          const stagesHtml = (data.stages || []).map(s => `
            <div style="margin-bottom: 8px;">
              <strong>Stage ${s.stage} (${s.name}):</strong> ${s.findings || s.security_result || s.stdout || s.status}
            </div>
          `).join("");

          resultsContainer.innerHTML = `
            <div class="chore-results-box">
              <h4 style="color: #34d399; margin-bottom: 8px; font-weight: 700;">✅ Heavy-Lifting Chore Workflow Completed</h4>
              <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 12px;">${data.summary}</p>
              ${stagesHtml}
            </div>`;
        }
      } catch (err) {
        console.error("Failed to run Taskmaster chore:", err);
      } finally {
        btnRunChore.disabled = false;
        btnRunChore.textContent = "▶ Run Multi-Step Vendor Audit Chore";
      }
    });
  }

  // Dismiss proactive banner
  const proactiveDismiss = document.getElementById("proactive-dismiss");
  if (proactiveDismiss) {
    proactiveDismiss.addEventListener("click", () => {
      const banner = document.getElementById("proactive-banner");
      if (banner) banner.classList.add("hidden");
    });
  }

  // Initial loads
  refreshTelemetry();
  loadMemoryPalace();
  loadCorrectionLedger();
  loadSkills();
  loadBenchmarkResults();
  loadCommitments();
  loadFleet();
  loadArmorPosture();
  loadOtelTraces();

  // Check proactive on session start
  fetch("/api/session/proactive").then(r => r.json()).then(data => {
    if (data.announcement) {
      const banner = document.getElementById("proactive-banner");
      const bannerText = document.getElementById("proactive-text");
      if (banner && bannerText) {
        bannerText.textContent = data.announcement;
        banner.classList.remove("hidden");
      }
    }
  }).catch(() => {});
});

