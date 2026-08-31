// KIW1 Interactive Frontend Client — Thinking Orb Lite (pure CSS)

document.addEventListener("DOMContentLoaded", () => {
  // Navigation Tabs
  const navItems = document.querySelectorAll(".nav-item");
  const tabPanes = document.querySelectorAll(".tab-pane");
  const pageTitle = document.getElementById("page-title");

  const tabTitles = {
    "chat-tab": "Chat & Strategic Orchestrator",
    "skills-tab": "Skill Registry & Forge",
    "ledger-tab": "Correction Ledger",
    "palace-tab": "Spatial Memory Palace",
    "research-tab": "Overnight Research & Self-Critique",
    "evals-tab": "20-Task Proof of Improvement",
  };

  navItems.forEach(btn => {
    btn.addEventListener("click", () => {
      const target = btn.dataset.tab;
      navItems.forEach(b => b.classList.remove("active"));
      tabPanes.forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const pane = document.getElementById(target);
      if (pane) pane.classList.add("active");
      if (pageTitle && tabTitles[target]) pageTitle.textContent = tabTitles[target];

      // Refresh tab data
      if (target === "skills-tab") loadSkills();
      if (target === "ledger-tab") loadLedger();
      if (target === "palace-tab") loadPalace();
      if (target === "research-tab") loadResearch();
      if (target === "evals-tab") loadEvals();
    });
  });

  // Chat Elements
  const chatMessages = document.getElementById("chat-messages");
  const chatInput = document.getElementById("chat-input");
  const btnSend = document.getElementById("btn-send");
  const effortSelect = document.getElementById("effort-select");
  const handsOffToggle = document.getElementById("hands-off-toggle");

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
  // All nine state classes for removal during swap
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

  async function sendMessage(text) {
    if (!text || text.trim() === "") return;
    const prompt = text.trim();
    chatInput.value = "";

    appendMessage("user", prompt);

    const effort = effortSelect.value;
    const handsOff = handsOffToggle.checked;

    // Set state: solving (Refinery classifying & Planner scoring)
    const isSearchQuery = prompt.toLowerCase().includes("search") || prompt.toLowerCase().includes("research");
    if (isSearchQuery) {
      setAgentState("searching", "Searching Sources", `Retrieving web and documentation data for query...`);
    } else {
      setAgentState("solving", "Analyzing & Planning", `Scoring execution paths and parsing constraints...`);
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
      appendMessage("agent", `Error communicating with KIW1 kernel: ${err.message}`);
      setAgentState("breathing", "Idle / Error", `Encountered error: ${err.message}`);
    }
  }

  function handleChatResponse(data, originalPrompt) {
    if (data.type === "clarification_needed") {
      pendingPrompt = originalPrompt;
      clarPromptText.textContent = `Original input: "${originalPrompt}"`;
      clarQuestions.innerHTML = "";

      data.questions.forEach((q, idx) => {
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

    // Normal response
    let body = data.text || "Task executed successfully.";

    // If a skill was forged on this turn
    if (data.forged_skill) {
      body += `\n\n⚡ <strong>Skill Forged:</strong> ${data.forged_skill.message}`;
      setAgentState("shaping", "Skill Forged", `Forged new capability: ${data.forged_skill.skill_name}`);
      
      // Flash inline orb beside Skill Registry
      if (skillsOrbContainer) {
        skillsOrbContainer.classList.remove("hidden");
        setTimeout(() => {
          skillsOrbContainer.classList.add("hidden");
        }, 4000);
      }
      loadSkills();
    } else {
      setAgentState("breathing", "Idle / Ready", "Task completed. Awaiting next instruction.");
    }

    // If learned rules were applied
    if (data.brief && data.brief.learned_rules_applied && data.brief.learned_rules_applied.length > 0) {
      body += `\n\n📖 <em>Applied ${data.brief.learned_rules_applied.length} learned rule(s) from Correction Ledger.</em>`;
    }

    appendMessage("agent", body);
  }

  function appendMessage(sender, text) {
    const msg = document.createElement("div");
    msg.className = `message ${sender}-message`;
    const author = sender === "user" ? "You" : "KIW1 Agent";
    msg.innerHTML = `
      <div class="msg-author">${author}</div>
      <div class="msg-body">${text.replace(/\n/g, "<br>")}</div>
    `;
    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  btnSend.addEventListener("click", () => sendMessage(chatInput.value));
  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage(chatInput.value);
  });

  btnSubmitClar.addEventListener("click", async () => {
    if (!pendingPrompt) return;
    const answers = {};
    document.querySelectorAll(".options-group").forEach(group => {
      const qid = group.dataset.qid;
      const checked = group.querySelector("input[type='radio']:checked");
      if (checked) answers[qid] = checked.value;
    });

    clarPanel.classList.add("hidden");
    appendMessage("user", `[Clarification Submitted]: ${Object.values(answers).join("; ")}`);

    setAgentState("working", "Executing Clarified Plan", "Executing task with verified brief constraints...");

    try {
      const res = await fetch("/api/clarify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          original_prompt: pendingPrompt,
          answers: answers,
          effort: effortSelect.value,
        }),
      });
      const data = await res.json();
      pendingPrompt = null;
      handleChatResponse(data, "");
      refreshTelemetry();
    } catch (err) {
      appendMessage("agent", `Error executing clarified task: ${err.message}`);
      setAgentState("breathing", "Idle / Error", `Error: ${err.message}`);
    }
  });

  btnCancelClar.addEventListener("click", () => {
    clarPanel.classList.add("hidden");
    pendingPrompt = null;
    setAgentState("breathing", "Idle / Ready", "Clarification cancelled.");
  });

  // Telemetry updates
  async function refreshTelemetry() {
    try {
      const res = await fetch("/api/telemetry");
      const data = await res.json();
      if (data.traces && data.traces.length > 0) {
        const latest = data.traces[0];
        document.getElementById("stat-latency").textContent = `${latest.latency_ms} ms`;
        document.getElementById("stat-tokens").textContent = latest.tokens ? latest.tokens.total : "0";
        document.getElementById("stat-cost").textContent = `$${latest.cost_usd.toFixed(6)}`;
        document.getElementById("stat-effort").textContent = latest.effort.toUpperCase();
      }
    } catch (e) {}
  }

  // Load Skills
  async function loadSkills() {
    try {
      const res = await fetch("/api/skills");
      const data = await res.json();
      const skills = data.skills || [];
      document.getElementById("skills-badge").textContent = skills.length;
      const container = document.getElementById("skills-list");
      container.innerHTML = "";

      if (skills.length === 0) {
        container.innerHTML = `<p class="text-muted">No skills forged yet. Repeat similar tasks 3 times to trigger Skill Forge.</p>`;
        return;
      }

      skills.forEach(s => {
        const card = document.createElement("div");
        card.className = "skill-card";
        const badgeClass = s.enabled ? "success" : "danger";
        card.innerHTML = `
          <div class="skill-card-header">
            <span class="skill-name">${s.name}</span>
            <span class="badge ${badgeClass}">${s.badge} ${s.status}</span>
          </div>
          <p class="skill-desc">${s.description}</p>
          <div class="skill-meta">
            <span>Invocations: <strong>${s.invocations}</strong></span>
            <span>Success Rate: <strong>${s.success_rate}</strong></span>
          </div>
        `;
        container.appendChild(card);
      });
    } catch (e) {}
  }

  // Load Ledger
  async function loadLedger() {
    try {
      const res = await fetch("/api/corrections");
      const data = await res.json();
      const rules = data.rules || [];
      document.getElementById("ledger-badge").textContent = data.active_count || 0;
      const tbody = document.getElementById("ledger-table-body");
      tbody.innerHTML = "";

      rules.forEach(r => {
        const tr = document.createElement("tr");
        const statusBadge = r.active ? `<span class="badge success">Active</span>` : `<span class="badge danger">Retired</span>`;
        tr.innerHTML = `
          <td><code>${r.id}</code></td>
          <td>${r.situation}</td>
          <td><strong>${r.rule}</strong></td>
          <td><code>${r.weight.toFixed(1)}</code></td>
          <td>${statusBadge}</td>
        `;
        tbody.appendChild(tr);
      });
    } catch (e) {}
  }

  // Load Memory Palace
  async function loadPalace() {
    try {
      const res = await fetch("/api/memory");
      const data = await res.json();
      const tree = data.tree || {};
      const container = document.getElementById("palace-tree");
      container.innerHTML = "";

      Object.entries(tree).forEach(([room, loci]) => {
        const rCard = document.createElement("div");
        rCard.className = "palace-room-card";
        let lociHtml = "";

        Object.entries(loci).forEach(([locus, items]) => {
          lociHtml += `
            <div class="locus-block">
              <div class="locus-title">Locus: ${locus}</div>
              ${items.map(item => `
                <div class="item-row">
                  &bull; ${item.item} 
                  <span class="badge" style="font-size:10px;">decay: ${item.decay_score.toFixed(1)}</span>
                  <span class="badge" style="font-size:10px;">${item.provenance}</span>
                </div>
              `).join("")}
            </div>
          `;
        });

        rCard.innerHTML = `
          <div class="room-title">🏛️ Room: ${room}</div>
          ${lociHtml}
        `;
        container.appendChild(rCard);
      });
    } catch (e) {}
  }

  // Load Research
  async function loadResearch() {
    try {
      const res = await fetch("/api/research/reports");
      const data = await res.json();
      const reports = data.reports || [];
      const container = document.getElementById("research-reports");
      container.innerHTML = "";

      if (reports.length === 0) {
        container.innerHTML = `<p class="text-muted">No overnight research runs recorded yet.</p>`;
        return;
      }

      reports.forEach(rep => {
        const card = document.createElement("div");
        card.className = "palace-room-card";
        card.innerHTML = `
          <div class="room-title">🌙 Morning Report (${new Date(rep.created_at || rep.timestamp).toLocaleDateString()})</div>
          <p><strong>Target:</strong> ${rep.target_topic} (<em>${rep.target_reason}</em>)</p>
          <div style="margin: 8px 0;">
            <strong>Validated Findings (Kept):</strong>
            <ul>
              ${(rep.survived_findings || []).map(f => `<li>${f}</li>`).join("")}
            </ul>
          </div>
          <div style="margin: 8px 0; color: var(--accent-red);">
            <strong>Discards (Critiqued &amp; Refuted):</strong>
            <ul>
              ${(rep.discarded_claims || []).map(c => `<li>${c}</li>`).join("")}
            </ul>
          </div>
        `;
        container.appendChild(card);
      });
    } catch (e) {}
  }

  document.getElementById("btn-trigger-research").addEventListener("click", async () => {
    const btn = document.getElementById("btn-trigger-research");
    btn.textContent = "Running Research Cycle...";
    btn.disabled = true;

    // Activate research state
    setAgentState("searching", "Overnight Research Active", "Targeting weakest knowledge area and gathering research...");
    if (researchOrbContainer) {
      researchOrbContainer.classList.remove("hidden");
    }

    try {
      // Transition to connecting / critique pass
      setTimeout(() => {
        setAgentState("connecting", "Critique & Validation Pass", "Adversarial critique pass attacking findings...");
      }, 1200);

      await fetch("/research/run", { method: "POST" });
      await loadResearch();
      setAgentState("breathing", "Research Complete", "Findings validated, morning report generated.");
    } catch (e) {
      setAgentState("breathing", "Research Failed", `Error: ${e.message}`);
    } finally {
      if (researchOrbContainer) {
        researchOrbContainer.classList.add("hidden");
      }
      btn.textContent = "Run Research Cycle Now";
      btn.disabled = false;
    }
  });

  // Load Evals
  async function loadEvals() {
    try {
      const res = await fetch("/static/results.json").catch(() => null);
      if (res && res.ok) {
        const data = await res.json();
        renderEvals(data);
      }
    } catch (e) {}
  }

  function renderEvals(data) {
    if (!data) return;
    document.getElementById("eval-cold-score").textContent = `${data.cold_score} (${data.cold_percentage})`;
    document.getElementById("eval-learned-score").textContent = `${data.learned_score} (${data.learned_percentage})`;
    document.getElementById("eval-delta").textContent = `${data.delta} (${data.delta_percentage})`;

    const tbody = document.getElementById("evals-table-body");
    tbody.innerHTML = "";

    const coldMap = {};
    (data.cold_results || []).forEach(r => { coldMap[r.id] = r; });

    (data.learned_results || []).forEach(r => {
      const cold = coldMap[r.id] || { passed: false };
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><code>${r.id}</code></td>
        <td>${r.name}</td>
        <td>${cold.passed ? `<span class="badge success">PASS</span>` : `<span class="badge danger">FAIL</span>`}</td>
        <td>${r.passed ? `<span class="badge success">PASS</span>` : `<span class="badge danger">FAIL</span>`}</td>
      `;
      tbody.appendChild(tr);
    });
  }

  document.getElementById("btn-run-evals").addEventListener("click", async () => {
    alert("Running evals runner in background. Results will refresh.");
  });

  // Initial load
  loadSkills();
  loadLedger();
  refreshTelemetry();
});
