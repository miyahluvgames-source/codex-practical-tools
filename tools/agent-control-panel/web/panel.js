const data = window.AgentControlPanelData || null;

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function copyText(value, button) {
  navigator.clipboard.writeText(value).then(() => {
    const old = button.textContent;
    button.textContent = "Copied";
    setTimeout(() => { button.textContent = old; }, 900);
  }).catch(() => {});
}

function ensureData() {
  if (data) return true;
  document.body.innerHTML = "<main style='padding:48px;color:#fff;font-family:Segoe UI,sans-serif'>Missing <code>panel-data.js</code>. Generate a snapshot or keep the demo file in place.</main>";
  return false;
}

function renderMeta() {
  document.title = data.meta.title || "Agent Control Panel";
  document.getElementById("navSummary").textContent = data.meta.operatorNote || data.meta.subtitle || "";

  const heroBadges = document.getElementById("heroBadges");
  [
    data.meta.agentFamily,
    data.meta.generatedAt,
    data.meta.stackRoot,
  ].filter(Boolean).forEach((item) => heroBadges.append(el("span", "badge", item)));

  const metricGrid = document.getElementById("metricGrid");
  [
    [String(data.lanes.length), "Execution lanes"],
    [String(data.helpers.length), "Helpers"],
    [String(data.skills.length), "Skills"],
    [String(data.prompts.length), "Startup prompts"],
  ].forEach(([value, label]) => {
    const card = el("div", "metric");
    card.append(el("strong", "", value), el("span", "", label));
    metricGrid.append(card);
  });

  const metaList = document.getElementById("metaList");
  [
    ["Agent family", data.meta.agentFamily],
    ["Generated", data.meta.generatedAt],
    ["Stack root", data.meta.stackRoot],
    ["Backup root", data.meta.backupRoot],
  ].forEach(([label, value]) => {
    if (!value) return;
    const card = el("div", "meta-card");
    card.append(el("span", "meta-label", label), el("span", "meta-value", value));
    metaList.append(card);
  });
}

function renderStatus() {
  const grid = document.getElementById("statusGrid");
  data.status.forEach((item) => {
    const card = el("div", "status-card");
    const tags = el("div", "status-tags");
    tags.append(el("span", `tag ${item.tone || "neutral"}`, item.label));
    card.append(tags, el("strong", "", item.value), el("span", "", item.note || ""));
    grid.append(card);
  });
}

function renderLanes() {
  const grid = document.getElementById("laneGrid");
  data.lanes.forEach((lane) => {
    const card = el("article", "lane");
    const name = el("div", "lane-name");
    name.append(el("span", `lane-dot ${lane.accent || "browser"}`), document.createTextNode(lane.name));
    const list = el("ul");
    (lane.useWhen || []).forEach((item) => list.append(el("li", "", item)));
    card.append(name, el("p", "", lane.summary || ""), list, el("p", "footer-note", lane.escalateWhen || ""));
    grid.append(card);
  });
}

function renderPrinciples() {
  const grid = document.getElementById("principleGrid");
  data.principles.forEach((item) => {
    const card = el("article", "card");
    card.append(el("h4", "", item.title), el("p", "", item.body));
    grid.append(card);
  });
}

function renderPrompts() {
  const grid = document.getElementById("promptGrid");
  data.prompts.forEach((prompt) => {
    const details = document.createElement("details");
    details.className = "card prompt";
    const summary = document.createElement("summary");
    const left = el("div");
    left.append(el("h4", "", prompt.title), el("p", "", prompt.summary));
    summary.append(left, el("span", "tag neutral", "Prompt"));
    const pre = el("pre");
    pre.textContent = prompt.body;
    details.append(summary, pre);
    grid.append(details);
  });
}

function renderHelpers() {
  const grid = document.getElementById("helperGrid");
  const filter = document.getElementById("helperFilter");
  function draw(query = "") {
    grid.innerHTML = "";
    const q = query.trim().toLowerCase();
    data.helpers
      .filter((item) => !q || `${item.name} ${item.lane} ${item.summary} ${item.path || ""}`.toLowerCase().includes(q))
      .forEach((item) => {
        const card = el("article", "card");
        const meta = el("div", "helper-meta");
        meta.append(el("span", "tag neutral", item.lane), el("span", `tag ${item.exists ? "good" : "warn"}`, item.exists ? "Present" : "Missing"));
        card.append(el("h4", "", item.name), el("p", "", item.summary), meta);
        if (item.path) {
          const row = el("div", "path-row");
          const code = el("code", "", item.path);
          const button = el("button", "copy-btn", "Copy path");
          button.addEventListener("click", () => copyText(item.path, button));
          row.append(code, button);
          card.append(row);
        }
        grid.append(card);
      });
  }
  filter.addEventListener("input", () => draw(filter.value));
  draw();
}

function renderSkills() {
  const grid = document.getElementById("skillsGrid");
  const filter = document.getElementById("skillFilter");
  function draw(query = "") {
    grid.innerHTML = "";
    const q = query.trim().toLowerCase();
    data.skills
      .filter((item) => !q || `${item.name} ${item.summary} ${item.group || ""}`.toLowerCase().includes(q))
      .forEach((item) => {
        const card = el("article", "card");
        card.append(el("h4", "", item.name), el("p", "", item.summary));
        const meta = el("div", "helper-meta");
        meta.append(el("span", "tag neutral", item.group || "installed"));
        card.append(meta);
        if (item.path) {
          const row = el("div", "path-row");
          const code = el("code", "", item.path);
          const button = el("button", "copy-btn", "Copy path");
          button.addEventListener("click", () => copyText(item.path, button));
          row.append(code, button);
          card.append(row);
        }
        grid.append(card);
      });
  }
  filter.addEventListener("input", () => draw(filter.value));
  draw();
}

function renderParameterGroups() {
  const grid = document.getElementById("paramGrid");
  data.parameters.forEach((group) => {
    const card = el("article", "card");
    card.append(el("h4", "", group.group));
    group.items.forEach((item) => {
      const wrap = el("div", "path-row");
      wrap.append(el("span", "tag neutral", item.label), el("code", "", item.value));
      card.append(wrap);
    });
    grid.append(card);
  });
}

function renderDocs() {
  const grid = document.getElementById("docGrid");
  data.docs.forEach((doc) => {
    const card = el("article", "card");
    card.append(el("h4", "", doc.title), el("p", "", doc.summary));
    if (doc.path) {
      const row = el("div", "path-row");
      const code = el("code", "", doc.path);
      const button = el("button", "copy-btn", "Copy path");
      button.addEventListener("click", () => copyText(doc.path, button));
      row.append(code, button);
      card.append(row);
    }
    grid.append(card);
  });
}

function renderAdapters() {
  const grid = document.getElementById("adapterGrid");
  data.adapters.forEach((adapter) => {
    const card = el("article", "card");
    card.append(el("h4", "", adapter.name), el("p", "", adapter.summary));
    if (adapter.path) {
      const row = el("div", "path-row");
      const code = el("code", "", adapter.path);
      const button = el("button", "copy-btn", "Copy path");
      button.addEventListener("click", () => copyText(adapter.path, button));
      row.append(code, button);
      card.append(row);
    }
    grid.append(card);
  });
}

if (ensureData()) {
  renderMeta();
  renderStatus();
  renderLanes();
  renderPrinciples();
  renderPrompts();
  renderHelpers();
  renderSkills();
  renderParameterGroups();
  renderDocs();
  renderAdapters();
}
