APP_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SHL Assessment Recommender</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f5f7f5;
      --surface: #ffffff;
      --surface-2: #eef4f2;
      --ink: #1c2430;
      --muted: #667085;
      --line: #d8e0dc;
      --brand: #0f766e;
      --brand-2: #155e75;
      --accent: #b7791f;
      --danger: #b42318;
      --shadow: 0 18px 60px rgba(30, 41, 59, 0.10);
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        linear-gradient(180deg, rgba(15, 118, 110, 0.08), rgba(245, 247, 245, 0) 280px),
        var(--bg);
    }

    button,
    textarea {
      font: inherit;
    }

    a {
      color: inherit;
    }

    .shell {
      width: min(1440px, 100%);
      min-height: 100vh;
      margin: 0 auto;
      display: grid;
      grid-template-rows: auto 1fr;
    }

    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 18px clamp(16px, 4vw, 44px);
      border-bottom: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.78);
      backdrop-filter: blur(12px);
      position: sticky;
      top: 0;
      z-index: 10;
    }

    .brand {
      min-width: 0;
    }

    .brand h1 {
      margin: 0;
      font-size: clamp(22px, 3vw, 34px);
      line-height: 1.05;
      letter-spacing: 0;
    }

    .brand p {
      margin: 6px 0 0;
      color: var(--muted);
      font-size: 14px;
    }

    .status {
      display: flex;
      align-items: center;
      gap: 10px;
      min-height: 38px;
      padding: 0 13px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface);
      color: var(--muted);
      white-space: nowrap;
      box-shadow: 0 8px 28px rgba(30, 41, 59, 0.06);
    }

    .status-dot {
      width: 9px;
      height: 9px;
      border-radius: 50%;
      background: var(--accent);
    }

    .status.ok .status-dot {
      background: var(--brand);
    }

    .status.error .status-dot {
      background: var(--danger);
    }

    .workspace {
      display: grid;
      grid-template-columns: minmax(240px, 300px) minmax(0, 1fr) minmax(260px, 340px);
      gap: 18px;
      padding: 18px clamp(16px, 4vw, 44px) 28px;
      min-height: 0;
    }

    .panel {
      background: rgba(255, 255, 255, 0.92);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
      min-width: 0;
    }

    .side {
      display: flex;
      flex-direction: column;
      min-height: 0;
      overflow: hidden;
    }

    .panel-header {
      padding: 16px 16px 12px;
      border-bottom: 1px solid var(--line);
    }

    .panel-header h2 {
      margin: 0;
      font-size: 16px;
      line-height: 1.2;
      letter-spacing: 0;
    }

    .panel-header p {
      margin: 5px 0 0;
      color: var(--muted);
      font-size: 13px;
    }

    .examples,
    .catalog,
    .recommendations {
      display: grid;
      gap: 10px;
      padding: 14px;
      overflow: auto;
    }

    .example-btn,
    .secondary-btn,
    .send-btn {
      min-height: 40px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface);
      color: var(--ink);
      cursor: pointer;
      transition: border-color 140ms ease, transform 140ms ease, background 140ms ease;
    }

    .example-btn {
      text-align: left;
      padding: 11px 12px;
      line-height: 1.35;
    }

    .example-btn:hover,
    .secondary-btn:hover {
      border-color: rgba(15, 118, 110, 0.45);
      background: #f9fcfb;
      transform: translateY(-1px);
    }

    .catalog-item,
    .rec-card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface);
      padding: 12px;
    }

    .catalog-item h3,
    .rec-card h3 {
      margin: 0;
      font-size: 14px;
      line-height: 1.25;
    }

    .catalog-item p,
    .rec-card p {
      margin: 8px 0 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }

    .meta-row {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 10px;
    }

    .tag {
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      padding: 0 8px;
      border-radius: 999px;
      background: var(--surface-2);
      color: #37534e;
      font-size: 12px;
      font-weight: 650;
    }

    .chat {
      display: grid;
      grid-template-rows: auto 1fr auto;
      min-height: 640px;
      overflow: hidden;
    }

    .chat-stream {
      padding: 18px;
      overflow: auto;
      display: flex;
      flex-direction: column;
      gap: 12px;
      background:
        linear-gradient(180deg, rgba(238, 244, 242, 0.72), rgba(255, 255, 255, 0) 180px),
        var(--surface);
    }

    .message {
      max-width: min(760px, 86%);
      border-radius: 8px;
      padding: 12px 14px;
      line-height: 1.48;
      white-space: pre-wrap;
      word-break: break-word;
      border: 1px solid var(--line);
    }

    .message.user {
      align-self: flex-end;
      background: #e8f3f0;
      border-color: rgba(15, 118, 110, 0.24);
    }

    .message.assistant {
      align-self: flex-start;
      background: var(--surface);
    }

    .composer {
      border-top: 1px solid var(--line);
      background: #fbfcfb;
      padding: 14px;
      display: grid;
      gap: 10px;
    }

    .input-wrap {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
      align-items: end;
    }

    textarea {
      width: 100%;
      min-height: 74px;
      max-height: 180px;
      resize: vertical;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      color: var(--ink);
      background: var(--surface);
      outline: none;
    }

    textarea:focus {
      border-color: var(--brand);
      box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.14);
    }

    .send-btn {
      width: 96px;
      min-height: 74px;
      background: var(--brand);
      color: white;
      border-color: var(--brand);
      font-weight: 750;
    }

    .send-btn:hover {
      background: #0d665f;
    }

    .send-btn:disabled {
      opacity: 0.55;
      cursor: not-allowed;
    }

    .composer-actions {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      align-items: center;
      color: var(--muted);
      font-size: 13px;
    }

    .secondary-btn {
      padding: 0 12px;
      color: var(--brand-2);
      font-weight: 650;
    }

    .rec-card a {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 36px;
      margin-top: 12px;
      padding: 0 12px;
      border-radius: 8px;
      background: #103b35;
      color: white;
      text-decoration: none;
      font-weight: 700;
      font-size: 13px;
    }

    .empty-state {
      color: var(--muted);
      font-size: 14px;
      line-height: 1.5;
      padding: 14px;
    }

    .error-text {
      color: var(--danger);
    }

    @media (max-width: 1080px) {
      .workspace {
        grid-template-columns: minmax(0, 1fr);
      }

      .chat {
        min-height: 620px;
      }

      .side {
        max-height: none;
      }
    }

    @media (max-width: 640px) {
      .topbar {
        align-items: flex-start;
        flex-direction: column;
      }

      .status {
        width: 100%;
        justify-content: flex-start;
      }

      .workspace {
        padding: 12px;
        gap: 12px;
      }

      .chat {
        min-height: 560px;
      }

      .input-wrap {
        grid-template-columns: 1fr;
      }

      .send-btn {
        width: 100%;
        min-height: 46px;
      }

      .message {
        max-width: 94%;
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <header class="topbar">
      <div class="brand">
        <h1>SHL Assessment Recommender</h1>
        <p>Match roles to assessments from the local SHL catalog.</p>
      </div>
      <div id="status" class="status">
        <span class="status-dot"></span>
        <span id="statusText">Checking API</span>
      </div>
    </header>

    <main class="workspace">
      <aside class="panel side">
        <div class="panel-header">
          <h2>Search Starters</h2>
          <p>Role prompts</p>
        </div>
        <div class="examples">
          <button class="example-btn" data-prompt="Hiring a mid-level Python developer with strong SQL">Mid-level Python developer with SQL</button>
          <button class="example-btn" data-prompt="I need an assessment for a Java developer who works with stakeholders">Java developer with stakeholders</button>
          <button class="example-btn" data-prompt="Compare OPQ32r and the General Ability Test">Compare OPQ32r and ability testing</button>
          <button class="example-btn" data-prompt="Add a personality assessment for stakeholder management">Stakeholder management personality fit</button>
        </div>
        <div class="panel-header">
          <h2>Catalog</h2>
          <p id="catalogCount">Loading</p>
        </div>
        <div id="catalogList" class="catalog"></div>
      </aside>

      <section class="panel chat">
        <div class="panel-header">
          <h2>Conversation</h2>
          <p id="turnCount">0 turns</p>
        </div>
        <div id="chatStream" class="chat-stream" aria-live="polite"></div>
        <form id="chatForm" class="composer">
          <div class="input-wrap">
            <textarea id="messageInput" name="message" placeholder="Describe the role, skills, seniority, or assessment need." required></textarea>
            <button id="sendButton" class="send-btn" type="submit">Send</button>
          </div>
          <div class="composer-actions">
            <span id="requestState">Ready</span>
            <button id="resetButton" class="secondary-btn" type="button">Reset</button>
          </div>
        </form>
      </section>

      <aside class="panel side">
        <div class="panel-header">
          <h2>Recommendations</h2>
          <p id="recCount">No shortlist yet</p>
        </div>
        <div id="recommendations" class="recommendations">
          <div class="empty-state">Recommendations will appear after the first matching request.</div>
        </div>
      </aside>
    </main>
  </div>

  <script>
    const chatStream = document.querySelector("#chatStream");
    const chatForm = document.querySelector("#chatForm");
    const messageInput = document.querySelector("#messageInput");
    const sendButton = document.querySelector("#sendButton");
    const resetButton = document.querySelector("#resetButton");
    const requestState = document.querySelector("#requestState");
    const recommendations = document.querySelector("#recommendations");
    const recCount = document.querySelector("#recCount");
    const statusBox = document.querySelector("#status");
    const statusText = document.querySelector("#statusText");
    const turnCount = document.querySelector("#turnCount");
    const catalogList = document.querySelector("#catalogList");
    const catalogCount = document.querySelector("#catalogCount");
    const examples = document.querySelectorAll(".example-btn");

    let messages = [];
    let catalogByName = new Map();
    let isSubmitting = false;

    function setStatus(mode, text) {
      statusBox.className = "status " + mode;
      statusText.textContent = text;
    }

    function setBusy(isBusy) {
      sendButton.disabled = isBusy;
      requestState.textContent = isBusy ? "Thinking" : "Ready";
    }

    function escapeHtml(value) {
      return value
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function renderMessages() {
      chatStream.innerHTML = messages.map((message) => {
        const role = message.role === "user" ? "user" : "assistant";
        return `<div class="message ${role}">${escapeHtml(message.content)}</div>`;
      }).join("");
      chatStream.scrollTop = chatStream.scrollHeight;
      const userTurns = messages.filter((message) => message.role === "user").length;
      turnCount.textContent = `${userTurns} ${userTurns === 1 ? "turn" : "turns"}`;
    }

    function renderRecommendations(items) {
      if (!items.length) {
        recCount.textContent = "No shortlist yet";
        recommendations.innerHTML = `<div class="empty-state">Recommendations will appear after the first matching request.</div>`;
        return;
      }

      recCount.textContent = `${items.length} ${items.length === 1 ? "assessment" : "assessments"}`;
      recommendations.innerHTML = items.map((item) => {
        const catalogItem = catalogByName.get(item.name) || {};
        const duration = catalogItem.duration_minutes ? `${catalogItem.duration_minutes} min` : "Duration varies";
        const remote = catalogItem.remote_testing ? "Remote" : "Onsite";
        const adaptive = catalogItem.adaptive_irt ? "Adaptive" : "Fixed";
        return `
          <article class="rec-card">
            <h3>${escapeHtml(item.name)}</h3>
            <p>${escapeHtml(catalogItem.description || "Recommended from the SHL catalog.")}</p>
            <div class="meta-row">
              <span class="tag">${escapeHtml(item.test_type)}</span>
              <span class="tag">${escapeHtml(duration)}</span>
              <span class="tag">${escapeHtml(remote)}</span>
              <span class="tag">${escapeHtml(adaptive)}</span>
            </div>
            <a href="${escapeHtml(item.url)}" target="_blank" rel="noreferrer">Open assessment</a>
          </article>
        `;
      }).join("");
    }

    function renderCatalog(items) {
      catalogByName = new Map(items.map((item) => [item.name, item]));
      catalogCount.textContent = `${items.length} assessments`;
      catalogList.innerHTML = items.map((item) => `
        <article class="catalog-item">
          <h3>${escapeHtml(item.name)}</h3>
          <p>${escapeHtml(item.description)}</p>
          <div class="meta-row">
            ${item.test_type.map((type) => `<span class="tag">${escapeHtml(type)}</span>`).join("")}
            <span class="tag">${escapeHtml(String(item.duration_minutes))} min</span>
          </div>
        </article>
      `).join("");
    }

    async function loadCatalog() {
      try {
        const response = await fetch("/catalog");
        if (!response.ok) throw new Error("Catalog request failed");
        renderCatalog(await response.json());
      } catch (error) {
        catalogCount.textContent = "Unavailable";
        catalogList.innerHTML = `<div class="empty-state error-text">Catalog could not be loaded.</div>`;
      }
    }

    async function checkHealth() {
      try {
        const response = await fetch("/health");
        if (!response.ok) throw new Error("Health request failed");
        setStatus("ok", "API online");
      } catch (error) {
        setStatus("error", "API offline");
      }
    }

    async function sendMessage(content) {
      if (isSubmitting) return;

      const text = content.trim();
      if (!text) return;

      isSubmitting = true;
      messages.push({ role: "user", content: text });
      renderMessages();
      messageInput.value = "";
      setBusy(true);

      try {
        const response = await fetch("/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ messages }),
        });

        if (!response.ok) {
          const detail = await response.text();
          throw new Error(detail || "Request failed");
        }

        const result = await response.json();
        messages.push({ role: "assistant", content: result.reply });
        renderMessages();
        renderRecommendations(result.recommendations || []);
        setStatus("ok", "API online");
      } catch (error) {
        messages.push({
          role: "assistant",
          content: "The local API did not return a response. Restart the server and try again.",
        });
        renderMessages();
        setStatus("error", "API offline");
      } finally {
        isSubmitting = false;
        setBusy(false);
        messageInput.focus();
      }
    }

    chatForm.addEventListener("submit", (event) => {
      event.preventDefault();
      sendMessage(messageInput.value);
    });

    resetButton.addEventListener("click", () => {
      messages = [];
      renderMessages();
      renderRecommendations([]);
      messageInput.focus();
    });

    examples.forEach((button) => {
      button.addEventListener("click", () => {
        messageInput.value = button.dataset.prompt;
        messageInput.focus();
      });
    });

    messageInput.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        chatForm.requestSubmit();
      }
    });

    messages = [{
      role: "assistant",
      content: "Tell me what role you are hiring for and I will shortlist matching SHL assessments.",
    }];
    renderMessages();
    renderRecommendations([]);
    checkHealth();
    loadCatalog();
  </script>
</body>
</html>
"""
