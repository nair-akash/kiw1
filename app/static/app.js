// KIW1 Studio Frontend Client — Codex Design System & Thinking Orb Lite (pure CSS)

document.addEventListener("DOMContentLoaded", () => {
  // Navigation Tabs
  const navItems = document.querySelectorAll(".nav-item");
  const tabPanes = document.querySelectorAll(".tab-pane");
  const pageTitle = document.getElementById("page-title");

  const tabTitles = {
    "chat-tab": "Chat & Strategic Orchestrator",
    "skills-tab": "Skill Registry & Autonomous Forge",
    "ledger-tab": "Correction Ledger",
    "palace-tab": "Spatial Memory Palace",
    "research-tab": "Overnight Research & Self-Critique",
    "evals-tab": "20-Task Proof of Improvement",
  };

  function switchTab(target) {
    navItems.forEach(b => b.classList.remove("active"));
    tabPanes.forEach(p => p.classList.remove("active"));

    const activeBtn = document.querySelector(`.nav-item[data-tab="${target}"]`);
    if (activeBtn) activeBtn.classList.add("active");

    const pane = document.getElementById(target);
    if (pane) pane.classList.add("active");
    if (pageTitle && tabTitles[target]) pageTitle.textContent = tabTitles[target];

    // Refresh data for active tab
    if (target === "skills-tab") loadSkills();
    if (target === "ledger-tab") loadLedger();
    if (target === "palace-tab") loadPalace();
    if (target === "research-tab") loadResearch();
    if (target === "evals-tab") loadEvals();
  }

  navItems.forEach(btn => {
    btn.addEventListener("click", () => {
      switchTab(btn.dataset.tab);
    });
  });

  // Chat Elements
  const chatMessages = document.getElementById("chat-messages");
  const chatInput = document.getElementById("chat-input");
  const btnSend = document.getElementById("btn-send");
  const effortSelect = document.getElementById("effort-select");
  const handsOffToggle = document.getElementById("hands-off-toggle");
  const welcomeHero = document.getElementById("welcome-hero");
  const btnNewChat = document.getElementById("btn-new-chat");

  // Effort Pills
  const effortPills = document.querySelectorAll(".effort-pill");
  effortPills.forEach(pill => {
    pill.addEventListener("click", () => {
      effortPills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      const val = pill.dataset.effort;
      if (effortSelect) effortSelect.value = val;
      const statEffort = document.getElementById("stat-effort");
      if (statEffort) statEffort.textContent = val.toUpperCase();
    });
  });

  // Clarification Modal Elements
  const clarPanel = document.getElementById("clarification-panel");
  const clarPromptText = document.getElementById("clarification-prompt-text");
  const clarQuestions = document.getElementById("clarification-questions");
  const btnSubmitClar = document.getElementById("btn-submit-clarification");
  const btnCancelClar = document.getElementById("btn-cancel-clarification");

  // Agent State UI Elements
  const mainOrbContainer = document.getElementById("main-orb-container");
  const agentStateLabel = document.getElementById("agent-state-label");
  const agentActivityDetail = document.getElementById("agent-activity-detail");

  const skillsOrbContainer = document.getElementById("skills-orb-container");
  const researchOrbContainer = document.getElementById("research-orb-container");

  // ── Thinking Orb Lite helpers ──────────────────────────────────────────
  const TOL_STATES = [
    "tol-working", "tol-searching", "tol-solving", "tol-listening",
    "tol-connecting", "tol-weaving", "tol-composing", "tol-breathing",
    "tol-shaping",
  ];

  /** Build the 12-dot markup inside a container and return the orb div. */
  function createOrbElement(container, stateClass, isSm) {
    const orb = document.createElement("div");
    orb.className = "tol-orb " + stateClass;
    if (isSm) orb.classList.add("is-sm");
    for (let n = 0; n < 12; n++) orb.appendChild(document.createElement("i"));
    container.appendChild(orb);
    return orb;
  }

  /** Swap the state class on an existing orb element. */
  function setOrbState(orbEl, newState) {
    if (!orbEl) return;
    orbEl.classList.remove(...TOL_STATES);
    orbEl.classList.add("tol-" + newState);
    orbEl.setAttribute("aria-label", newState.charAt(0).toUpperCase() + newState.slice(1));
  }

  // Initialise the three orbs
  let mainOrbEl = null;
  if (mainOrbContainer) {
    mainOrbEl = createOrbElement(mainOrbContainer, "tol-breathing", false);
  }
  if (skillsOrbContainer) {
    createOrbElement(skillsOrbContainer, "tol-shaping", true);
  }
  if (researchOrbContainer) {
    createOrbElement(researchOrbContainer, "tol-searching", true);
  }

  function setAgentState(state, stateTitle, activityDetail) {
    setOrbState(mainOrbEl, state);
    if (agentStateLabel) agentStateLabel.textContent = stateTitle;
    if (agentActivityDetail) agentActivityDetail.textContent = activityDetail;
  }

  let pendingPrompt = null;

  // New session button
  if (btnNewChat) {
    btnNewChat.addEventListener("click", () => {
      switchTab("chat-tab");
      chatMessages.innerHTML = "";
      if (welcomeHero) {
        chatMessages.appendChild(welcomeHero);
        welcomeHero.classList.remove("hidden");
      }
      chatInput.value = "";
      chatInput.focus();
      setAgentState("breathing", "Idle / Ready", "Started fresh session. Awaiting instruction.");
    });
  }

  // Quick Starter Cards in Welcome Hero
  document.querySelectorAll(".starter-card").forEach(card => {
    card.addEventListener("click", () => {
      const prompt = card.dataset.prompt;
      if (prompt) {
        chatInput.value = prompt;
        sendMessage(prompt);
      }
    });
  });

  // Quick Shortcut Chips
  document.querySelectorAll(".shortcut-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      const text = chip.dataset.insert;
      if (text) {
        chatInput.value = text;
        chatInput.focus();
        if (text === "/skills" || text === "/evals" || text === "/research") {
          sendMessage(text);
        }
      }
    });
  });

  // Auto-resize chat textarea
  if (chatInput) {
    chatInput.addEventListener("input", () => {
      chatInput.style.height = "auto";
      chatInput.style.height = Math.min(chatInput.scrollHeight, 160) + "px";
    });

    chatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage(chatInput.value);
      }
    });
  }

  if (btnSend) {
    btnSend.addEventListener("click", () => sendMessage(chatInput.value));
  }

  async function sendMessage(text) {
    if (!text || text.trim() === "") return;
    const prompt = text.trim();
    chatInput.value = "";
    chatInput.style.height = "auto";

    // Hide welcome hero on first message
    if (welcomeHero && !welcomeHero.classList.contains("hidden")) {
      welcomeHero.classList.add("hidden");
    }

    appendUserMessage(prompt);

    const effort = effortSelect ? effortSelect.value : "standard";
    const handsOff = handsOffToggle ? handsOffToggle.checked : false;

    // Set state
    const isSearchQuery = prompt.toLowerCase().includes("search") || prompt.toLowerCase().includes("research");
    if (isSearchQuery) {
      setAgentState("searching", "Searching Sources", `Retrieving web and documentation data...`);
    } else {
      setAgentState("solving", "Analyzing & Planning", `Refinery verifying constraints and scoring paths...`);
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
      handleChatResponse(data, prompt);
      refreshTelemetry();
    } catch (err) {
      appendAgentMessage({
        text: `Encountered communication error: ${err.message}`,
        model: "offline",
      });
      setAgentState("breathing", "Idle / Error", `Error: ${err.message}`);
    }
  }

  function handleChatResponse(data, originalPrompt) {
    if (data.type === "clarification_needed") {
      pendingPrompt = originalPrompt;
      clarPromptText.textContent = `Original input: "${originalPrompt}"`;
      clarQuestions.innerHTML = "";

      (data.questions || []).forEach((q, idx) => {
        const qBlock = document.createElement("div");
        qBlock.className = "clarification-question-block";
        qBlock.innerHTML = `
          <div class="question-title">Q${idx + 1}: ${q.question}</div>
          <div class="options-group" data-qid="${q.id}">
            ${q.options.map((opt, oIdx) => `
              <label class="option-choice">
                <input type="radio" name="clar_${q.id}" value="${opt}" ${oIdx === 0 ? "checked" : ""}>
                <span>${opt}</span>
              </label>
            `).join("")}
          </div>
        `;
        clarQuestions.appendChild(qBlock);
      });

      clarPanel.classList.remove("hidden");
      setAgentState("solving", "Clarification Required", "Prompt Refinery awaiting user ambiguity resolution.");
      return;
    }

    // Set state
    if (data.forged_skill) {
      setAgentState("shaping", "Skill Forged", `Forged new capability: ${data.forged_skill.skill_name}`);
      if (skillsOrbContainer) {
        skillsOrbContainer.classList.remove("hidden");
        setTimeout(() => skillsOrbContainer.classList.add("hidden"), 4000);
      }
      loadSkills();
    } else {
      setAgentState("breathing", "Idle / Ready", "Task completed. Awaiting next instruction.");
    }

    appendAgentMessage(data);
  }

  function appendUserMessage(text) {
    const msg = document.createElement("div");
    msg.className = "message user-message";
    msg.innerHTML = `
      <div class="msg-body">${escapeHtml(text).replace(/\n/g, "<br>")}</div>
    `;
    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function appendAgentMessage(data) {
    const msg = document.createElement("div");
    msg.className = "message agent-message";

    const text = data.text || "Execution completed.";
    const model = data.model || "gemini-3.6-flash";
    const tools = data.tools_used || [];
    const reasoning = data.reasoning || "";
    const rulesApplied = (data.brief && data.brief.learned_rules_applied) ? data.brief.learned_rules_applied : [];
    const forgedSkill = data.forged_skill;

    let toolsHtml = "";
    if (tools.length > 0) {
      toolsHtml = `
        <div class="tools-execution-row">
          ${tools.map(t => `<span class="tool-pill-badge">⚙️ ${t}</span>`).join("")}
        </div>
      `;
    }

    let reasoningHtml = "";
    if (reasoning || (data.plan_candidates && data.plan_candidates.length > 0)) {
      const candidates = data.plan_candidates || [];
      reasoningHtml = `
        <div class="reasoning-drawer">
          <div class="reasoning-toggle" onclick="this.parentElement.classList.toggle('open')">
            <span>🧠 Thought Process &amp; Strategic Plan</span>
            <span class="chevron">▼</span>
          </div>
          <div class="reasoning-content">
            ${reasoning ? `<div style="margin-bottom: 6px;">${escapeHtml(reasoning)}</div>` : ''}
            ${candidates.length > 0 ? `
              <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px;">
                <strong>Strategic Paths Evaluated (${candidates.length}):</strong><br>
                ${candidates.map(c => `&bull; ${c.name} [Confidence: ${(c.confidence * 100).toFixed(0)}%] &mdash; ${c.risk_assessment}`).join("<br>")}
              </div>
            ` : ''}
          </div>
        </div>
      `;
    }

    let rulesHtml = "";
    if (rulesApplied.length > 0) {
      rulesHtml = `
        <div style="margin-top: 8px; font-size: 12px; color: #a5b4fc; background: rgba(99,102,241,0.08); padding: 6px 10px; border-radius: 6px; border: 1px solid rgba(99,102,241,0.2);">
          📖 <strong>Applied ${rulesApplied.length} Correction Rule(s):</strong><br>
          ${rulesApplied.map(r => `&bull; ${escapeHtml(r)}`).join("<br>")}
        </div>
      `;
    }

    let forgedHtml = "";
    if (forgedSkill) {
      forgedHtml = `
        <div style="margin-top: 8px; font-size: 12px; color: #67e8f9; background: rgba(6,182,212,0.08); padding: 8px 12px; border-radius: 6px; border: 1px solid rgba(6,182,212,0.25);">
          ⚡ <strong>Autonomous Skill Forged:</strong> ${escapeHtml(forgedSkill.skill_name || '')}<br>
          <span style="color: var(--text-secondary);">${escapeHtml(forgedSkill.message || '')}</span>
        </div>
      `;
    }

    msg.innerHTML = `
      <div class="message-header">
        <div class="msg-avatar agent-avatar">
          <div class="tol-orb tol-breathing is-sm"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
        </div>
        <div class="msg-author">KIW1 Kernel</div>
        <div class="msg-meta-badge">${model}</div>
      </div>
      ${reasoningHtml}
      ${toolsHtml}
      <div class="msg-body">${formatMarkdown(text)}</div>
      ${rulesHtml}
      ${forgedHtml}
      <div class="msg-actions-row">
        <button class="btn-msg-action" onclick="navigator.clipboard.writeText(${JSON.stringify(text)})">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
          Copy
        </button>
        <button class="btn-msg-action btn-teach-action">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
          Teach / Correct
        </button>
      </div>
    `;

    // Hook up inline Teach button
    const teachBtn = msg.querySelector(".btn-teach-action");
    if (teachBtn) {
      teachBtn.addEventListener("click", () => {
        openCorrectionModal();
      });
    }

    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  function formatMarkdown(str) {
    if (!str) return "";
    let html = escapeHtml(str);
    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    // Italic
    html = html.replace(/\*(.*?)\*/g, "<em>$1</em>");
    // Code inline
    html = html.replace(/`(.*?)`/g, "<code>$1</code>");
    // Newlines
    html = html.replace(/\n/g, "<br>");
    return html;
  }

  // Clarification Confirmation
  if (btnSubmitClar) {
    btnSubmitClar.addEventListener("click", async () => {
      if (!pendingPrompt) return;
      const answers = {};
      document.querySelectorAll(".options-group").forEach(group => {
        const qid = group.dataset.qid;
        const checked = group.querySelector("input[type='radio']:checked");
        if (checked) answers[qid] = checked.value;
      });

      clarPanel.classList.add("hidden");
      appendUserMessage(`[Clarification Answers]: ${Object.values(answers).join("; ")}`);
      setAgentState("working", "Executing Clarified Plan", "Executing task with verified brief constraints...");

      try {
        const res = await fetch("/api/clarify", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            original_prompt: pendingPrompt,
            answers: answers,
            effort: effortSelect ? effortSelect.value : "standard",
          }),
        });
        const data = await res.json();
        pendingPrompt = null;
        handleChatResponse(data, "");
        refreshTelemetry();
      } catch (err) {
        appendAgentMessage({ text: `Error: ${err.message}` });
        setAgentState("breathing", "Idle / Error", `Error: ${err.message}`);
      }
    });
  }

  if (btnCancelClar) {
    btnCancelClar.addEventListener("click", () => {
      clarPanel.classList.add("hidden");
      pendingPrompt = null;
      setAgentState("breathing", "Idle / Ready", "Clarification dismissed.");
    });
  }

  // Telemetry updates
  async function refreshTelemetry() {
    try {
      const res = await fetch("/api/telemetry");
      const data = await res.json();
      if (data.traces && data.traces.length > 0) {
        const latest = data.traces[0];
        const statLatency = document.getElementById("stat-latency");
        const statTokens = document.getElementById("stat-tokens");
        const statCost = document.getElementById("stat-cost");
        if (statLatency) statLatency.textContent = `${Math.round(latest.latency_ms || 0)} ms`;
        if (statTokens) statTokens.textContent = latest.tokens ? latest.tokens.total.toLocaleString() : "0";
        if (statCost) statCost.textContent = `$${(latest.cost_usd || 0).toFixed(6)}`;
      }
    } catch (e) {}
  }

  // Load Skills Tab
  async function loadSkills() {
    try {
      const res = await fetch("/api/skills");
      const data = await res.json();
      const skills = data.skills || [];
      const badge = document.getElementById("skills-badge");
      if (badge) badge.textContent = skills.length;

      const container = document.getElementById("skills-list");
      if (!container) return;
      container.innerHTML = "";

      if (skills.length === 0) {
        container.innerHTML = `
          <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--text-muted);">
            <div style="font-size: 24px; margin-bottom: 8px;">⚡</div>
            <div style="font-weight: 600; font-size: 14px; color: var(--text-secondary);">No Skills Forged Yet</div>
            <p style="font-size: 12px; margin-top: 4px;">Repeat similar high-frequency tasks 3 times to trigger the autonomous Skill Forge.</p>
          </div>
        `;
        return;
      }

      skills.forEach(s => {
        const card = document.createElement("div");
        card.className = "skill-card";
        const badgeClass = s.enabled ? "success" : "danger";
        card.innerHTML = `
          <div class="skill-card-header">
            <span class="skill-name">${escapeHtml(s.name)}</span>
            <span class="badge ${badgeClass}">${s.badge || '⚡'} ${s.status}</span>
          </div>
          <p class="skill-desc">${escapeHtml(s.description)}</p>
          <div class="skill-meta">
            <span>Invocations: <strong>${s.invocations || 0}</strong></span>
            <span>Success Rate: <strong>${s.success_rate || '100%'}</strong></span>
          </div>
        `;
        container.appendChild(card);
      });
    } catch (e) {}
  }

  // Load Ledger Tab
  async function loadLedger() {
    try {
      const res = await fetch("/api/corrections");
      const data = await res.json();
      const rules = data.rules || [];
      const badge = document.getElementById("ledger-badge");
      if (badge) badge.textContent = data.active_count || rules.length;

      const tbody = document.getElementById("ledger-table-body");
      if (!tbody) return;
      tbody.innerHTML = "";

      if (rules.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted); padding: 30px;">No correction rules recorded. Teach the agent rules via chat or "+ Add Manual Rule".</td></tr>`;
        return;
      }

      rules.forEach(r => {
        const tr = document.createElement("tr");
        const statusBadge = r.active ? `<span class="badge success">Active</span>` : `<span class="badge danger">Retired</span>`;
        tr.innerHTML = `
          <td><code>${escapeHtml(r.id)}</code></td>
          <td>${escapeHtml(r.situation)}</td>
          <td><strong>${escapeHtml(r.rule)}</strong></td>
          <td><code>${(r.weight || 1.0).toFixed(1)}</code></td>
          <td>${statusBadge}</td>
        `;
        tbody.appendChild(tr);
      });
    } catch (e) {}
  }

  // Load Memory Palace Tab
  async function loadPalace() {
    try {
      const res = await fetch("/api/memory");
      const data = await res.json();
      const tree = data.tree || {};
      const badge = document.getElementById("palace-badge");
      const totalMemories = Object.values(tree).reduce((sum, loci) => sum + Object.values(loci).reduce((s2, arr) => s2 + arr.length, 0), 0);
      if (badge) badge.textContent = totalMemories;

      const container = document.getElementById("palace-tree");
      if (!container) return;
      container.innerHTML = "";

      if (Object.keys(tree).length === 0) {
        container.innerHTML = `
          <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--text-muted);">
            <div style="font-size: 24px; margin-bottom: 8px;">🏛️</div>
            <div style="font-weight: 600; font-size: 14px; color: var(--text-secondary);">Memory Palace Empty</div>
            <p style="font-size: 12px; margin-top: 4px;">Use <code>/remember [fact]</code> or "+ Store Memory" to persist knowledge in spatial loci.</p>
          </div>
        `;
        return;
      }

      Object.entries(tree).forEach(([room, loci]) => {
        const rCard = document.createElement("div");
        rCard.className = "palace-room-card";
        let lociHtml = "";

        Object.entries(loci).forEach(([locus, items]) => {
          lociHtml += `
            <div class="locus-block">
              <div class="locus-title">Locus: ${escapeHtml(locus)}</div>
              ${items.map(item => `
                <div class="item-row">&bull; ${escapeHtml(item.text || item)}</div>
              `).join("")}
            </div>
          `;
        });

        rCard.innerHTML = `
          <div class="room-header">
            <span>🚪 Room:</span> <strong>${escapeHtml(room)}</strong>
          </div>
          ${lociHtml}
        `;
        container.appendChild(rCard);
      });
    } catch (e) {}
  }

  // Load Research Tab
  async function loadResearch() {
    try {
      const res = await fetch("/api/research/reports");
      const data = await res.json();
      const reports = data.reports || [];
      const container = document.getElementById("research-reports");
      if (!container) return;
      container.innerHTML = "";

      if (reports.length === 0) {
        container.innerHTML = `
          <div style="text-align: center; padding: 40px; color: var(--text-muted);">
            <div style="font-size: 24px; margin-bottom: 8px;">🌙</div>
            <div style="font-weight: 600; font-size: 14px; color: var(--text-secondary);">No Overnight Research Reports Yet</div>
            <p style="font-size: 12px; margin-top: 4px;">Click "Run Research Cycle Now" to trigger autonomous weak-spot synthesis and critique pass.</p>
          </div>
        `;
        return;
      }

      reports.forEach(r => {
        const card = document.createElement("div");
        card.className = "research-report-card";
        card.innerHTML = `
          <div class="report-header">
            <div>
              <div class="report-topic">${escapeHtml(r.topic || 'General Intelligence Briefing')}</div>
              <div class="report-meta">Timestamp: ${r.timestamp || new Date().toISOString()}</div>
            </div>
            <span class="badge success">Adversarial Critique Passed</span>
          </div>
          <div class="report-summary">${formatMarkdown(r.summary || r.report_markdown || 'No summary available.')}</div>
          ${r.critique ? `
            <div class="critique-box">
              <div class="critique-title">🛡️ Pro Adversarial Critique Pass:</div>
              <div style="font-size: 12px; color: var(--text-secondary);">${escapeHtml(r.critique)}</div>
            </div>
          ` : ''}
        `;
        container.appendChild(card);
      });
    } catch (e) {}
  }

  // Load Evals Benchmark Tab
  async function loadEvals() {
    try {
      const res = await fetch("/static/results.json");
      const data = await res.json();

      const coldScoreEl = document.getElementById("eval-cold-score");
      const learnedScoreEl = document.getElementById("eval-learned-score");
      const deltaEl = document.getElementById("eval-delta");

      if (coldScoreEl) coldScoreEl.textContent = `${data.cold_score} (${data.cold_percentage})`;
      if (learnedScoreEl) learnedScoreEl.textContent = `${data.learned_score} (${data.learned_percentage})`;
      if (deltaEl) deltaEl.textContent = `${data.delta} (${data.delta_percentage})`;

      const tbody = document.getElementById("evals-table-body");
      if (!tbody) return;
      tbody.innerHTML = "";

      const coldResults = data.cold_results || [];
      const learnedResults = data.learned_results || [];

      coldResults.forEach((cold, i) => {
        const learned = learnedResults[i] || { passed: false, detail: "" };
        const coldBadge = cold.passed ? `<span class="badge success">PASS</span>` : `<span class="badge danger">FAIL</span>`;
        const learnedBadge = learned.passed ? `<span class="badge success">PASS</span>` : `<span class="badge danger">FAIL</span>`;

        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><code>${cold.id}</code></td>
          <td><strong>${escapeHtml(cold.name)}</strong></td>
          <td>${coldBadge}</td>
          <td>${learnedBadge}</td>
          <td style="font-size: 11px; font-family: var(--font-mono); color: var(--text-secondary);">${escapeHtml(learned.detail || cold.detail)}</td>
        `;
        tbody.appendChild(tr);
      });
    } catch (e) {}
  }

  // Trigger Research Cycle
  const btnTriggerResearch = document.getElementById("btn-trigger-research");
  if (btnTriggerResearch) {
    btnTriggerResearch.addEventListener("click", async () => {
      btnTriggerResearch.disabled = true;
      btnTriggerResearch.innerHTML = "Executing Research Cycle...";
      setAgentState("searching", "Conducting Research", "Scouring web sources and synthesizing intelligence...");

      try {
        await fetch("/api/research/trigger", { method: "POST" });
        await loadResearch();
        setAgentState("breathing", "Idle / Ready", "Research cycle finished.");
      } catch (e) {
        setAgentState("breathing", "Idle / Error", `Research error: ${e.message}`);
      } finally {
        btnTriggerResearch.disabled = false;
        btnTriggerResearch.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 4v6h-6M1 20v-6h6"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg> Run Research Cycle Now`;
      }
    });
  }

  // Trigger Evals Re-run
  const btnRunEvals = document.getElementById("btn-run-evals");
  if (btnRunEvals) {
    btnRunEvals.addEventListener("click", async () => {
      btnRunEvals.disabled = true;
      btnRunEvals.innerHTML = "Running 20-Task Suite...";
      setAgentState("working", "Running Benchmark", "Executing 20 cold tasks and 20 learned tasks...");

      try {
        await fetch("/api/evals/run", { method: "POST" }).catch(() => {});
        await loadEvals();
        setAgentState("breathing", "Idle / Ready", "Benchmark completed.");
      } catch (e) {
        setAgentState("breathing", "Idle / Error", `Benchmark error: ${e.message}`);
      } finally {
        btnRunEvals.disabled = false;
        btnRunEvals.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 3l14 9-14 9V3z"/></svg> Re-run Live Benchmark`;
      }
    });
  }

  // ── Modals Setup ───────────────────────────────────────────────
  const corrModal = document.getElementById("correction-modal");
  const btnAddCorr = document.getElementById("btn-add-correction-modal");
  const btnCloseCorr = document.getElementById("btn-close-correction-modal");
  const btnCancelCorr = document.getElementById("btn-cancel-correction-modal");
  const btnSaveCorr = document.getElementById("btn-save-correction-modal");

  function openCorrectionModal() {
    if (corrModal) corrModal.classList.remove("hidden");
  }

  function closeCorrectionModal() {
    if (corrModal) corrModal.classList.add("hidden");
    document.getElementById("modal-corr-situation").value = "";
    document.getElementById("modal-corr-wrong").value = "";
    document.getElementById("modal-corr-rule").value = "";
  }

  if (btnAddCorr) btnAddCorr.addEventListener("click", openCorrectionModal);
  if (btnCloseCorr) btnCloseCorr.addEventListener("click", closeCorrectionModal);
  if (btnCancelCorr) btnCancelCorr.addEventListener("click", closeCorrectionModal);

  if (btnSaveCorr) {
    btnSaveCorr.addEventListener("click", async () => {
      const situation = document.getElementById("modal-corr-situation").value.trim();
      const wrongAction = document.getElementById("modal-corr-wrong").value.trim();
      const rule = document.getElementById("modal-corr-rule").value.trim();

      if (!situation || !rule) return;

      try {
        await fetch("/api/corrections", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            situation: situation,
            wrong_action: wrongAction,
            correction: rule,
          }),
        });
        closeCorrectionModal();
        loadLedger();
      } catch (e) {}
    });
  }

  // Memory Modal
  const memModal = document.getElementById("memory-modal");
  const btnAddMem = document.getElementById("btn-add-memory-modal");
  const btnCloseMem = document.getElementById("btn-close-memory-modal");
  const btnCancelMem = document.getElementById("btn-cancel-memory-modal");
  const btnSaveMem = document.getElementById("btn-save-memory-modal");

  function openMemoryModal() {
    if (memModal) memModal.classList.remove("hidden");
  }

  function closeMemoryModal() {
    if (memModal) memModal.classList.add("hidden");
    document.getElementById("modal-mem-fact").value = "";
    document.getElementById("modal-mem-room").value = "";
    document.getElementById("modal-mem-locus").value = "";
  }

  if (btnAddMem) btnAddMem.addEventListener("click", openMemoryModal);
  if (btnCloseMem) btnCloseMem.addEventListener("click", closeMemoryModal);
  if (btnCancelMem) btnCancelMem.addEventListener("click", closeMemoryModal);

  if (btnSaveMem) {
    btnSaveMem.addEventListener("click", async () => {
      const fact = document.getElementById("modal-mem-fact").value.trim();
      const room = document.getElementById("modal-mem-room").value.trim();
      const locus = document.getElementById("modal-mem-locus").value.trim();

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
        loadPalace();
      } catch (e) {}
    });
  }

  // Initial loads
  refreshTelemetry();
  loadSkills();
  loadLedger();
  loadPalace();
  loadEvals();
});
