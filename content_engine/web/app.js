const API = "/api/v1";
const views = ["compose", "templates", "system"];
let currentRequest = null;
let currentResponse = null;
let templateItems = [];
let selectedTemplate = null;
let toastTimer;

const byId = (id) => document.getElementById(id);
const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);

async function api(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    ...options,
    headers: { ...(options.body ? { "Content-Type": "application/json" } : {}), ...options.headers },
  });
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      message = body.detail || body.message || body.error || message;
      if (typeof message !== "string") message = JSON.stringify(message);
    } catch { /* Keep the HTTP status as the useful fallback. */ }
    throw new Error(message);
  }
  return response;
}

function showToast(message, target = "toast") {
  const toast = byId(target);
  toast.textContent = message;
  toast.classList.remove("is-hidden");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.add("is-hidden"), 2600);
}

function setBusy(busy, label = "WORKING") {
  const button = byId("generate-button");
  button.disabled = busy;
  button.innerHTML = busy ? "◌ Working…" : "<span>✳</span> Generate draft";
  const status = byId("result-status");
  status.textContent = busy ? label : (currentResponse ? "COMPLETE" : "READY");
  status.classList.toggle("busy", busy);
  status.classList.toggle("done", !busy && Boolean(currentResponse));
  byId("error-box").classList.add("is-hidden");
}

function showError(error) {
  byId("error-box").textContent = error.message || String(error);
  byId("error-box").classList.remove("is-hidden");
  byId("result-status").textContent = "ERROR";
  byId("result-status").classList.remove("busy", "done");
}

function buildRequest(promptOverride) {
  const prompt = promptOverride ?? byId("prompt").value.trim();
  const request = {
    prompt,
    content_type: byId("content-type").value,
    quality: byId("quality").value,
    use_markdown: byId("use-markdown").checked,
    use_emojis: byId("use-emojis").checked,
    use_hashtags: byId("use-hashtags").checked,
    include_call_to_action: byId("include-cta").checked,
    include_questions: byId("include-questions").checked,
  };
  const optionalFields = {
    platform: byId("platform").value,
    tone: byId("tone").value,
    style: byId("style").value,
    context: byId("context").value.trim(),
    custom_instructions: byId("custom-instructions").value.trim(),
    provider: byId("provider").value,
    template_id: byId("template-select").value,
  };
  for (const [key, value] of Object.entries(optionalFields)) if (value) request[key] = value;
  const keywords = byId("keywords").value.split(",").map((item) => item.trim()).filter(Boolean);
  if (keywords.length) request.keywords = keywords;
  const minLength = Number(byId("min-length").value);
  const maxLength = Number(byId("max-length").value);
  const hashtagCount = Number(byId("hashtag-count").value);
  const temperature = Number(byId("temperature").value);
  if (minLength > 0) request.min_length = minLength;
  if (maxLength > 0) request.max_length = maxLength;
  if (byId("hashtag-count").value !== "") request.hashtag_count = hashtagCount;
  if (temperature !== 0.7) request.temperature = temperature;
  return request;
}

function renderResponse(response, label = "DRAFT") {
  currentResponse = response;
  const content = response?.content ?? response?.generated_content?.[0] ?? "";
  byId("empty-result").classList.add("is-hidden");
  byId("result-content").classList.remove("is-hidden");
  byId("output-text").textContent = content || "No content was returned by the provider.";
  byId("result-platform").textContent = String(response?.platform || label).replaceAll("_", " ").toUpperCase();
  const metrics = [
    ["words", response?.word_count],
    ["characters", response?.character_count],
    ["time", response?.generation_time ? `${Number(response.generation_time).toFixed(1)}s` : null],
    ["provider", response?.provider],
    ["quality", response?.quality_score == null ? null : `${Math.round(response.quality_score * 100)}%`],
  ].filter(([, value]) => value !== undefined && value !== null && value !== "");
  byId("result-metrics").innerHTML = metrics.map(([name, value]) => `<span class="metric-chip">${escapeHtml(name)} · ${escapeHtml(value)}</span>`).join("");
  byId("analysis-box").classList.add("is-hidden");
  byId("alternatives-box").classList.add("is-hidden");
  byId("result-status").textContent = "COMPLETE";
  byId("result-status").classList.remove("busy");
  byId("result-status").classList.add("done");
}

function renderBatch(responses) {
  const first = responses[0];
  renderResponse(first || {}, "BATCH");
  byId("result-platform").textContent = `${responses.length} BATCH RESULTS`;
  byId("alternatives-box").innerHTML = `<h3>Batch results</h3>${responses.map((item, index) => `<div class="alternative-item"><strong>Draft ${index + 1}</strong><br>${escapeHtml(item.content || "")}</div>`).join("")}`;
  byId("alternatives-box").classList.remove("is-hidden");
}

async function generate(event) {
  event.preventDefault();
  const mode = byId("generation-mode").value;
  const prompts = mode === "batch" ? byId("batch-prompts").value.split("\n").map((item) => item.trim()).filter(Boolean) : [];
  currentRequest = buildRequest();
  if (mode === "batch" && prompts.length === 0) {
    showError(new Error("Add at least one prompt to generate a batch."));
    return;
  }
  setBusy(true, mode === "stream" ? "STREAMING" : "GENERATING");
  try {
    if (mode === "alternatives") {
      const response = await api("/content/alternatives?count=3", { method: "POST", body: JSON.stringify(currentRequest) });
      const results = await response.json();
      renderBatch(results);
      byId("alternatives-box").querySelector("h3").textContent = "Alternative drafts";
    } else if (mode === "batch") {
      const response = await api("/content/generate_batch", { method: "POST", body: JSON.stringify(prompts.map((prompt) => ({ ...currentRequest, prompt }))) });
      renderBatch(await response.json());
    } else if (mode === "stream") {
      const response = await api("/content/stream", { method: "POST", body: JSON.stringify(currentRequest) });
      byId("empty-result").classList.add("is-hidden");
      byId("result-content").classList.remove("is-hidden");
      byId("output-text").textContent = "";
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        byId("output-text").textContent += decoder.decode(value, { stream: true });
      }
      byId("output-text").textContent += decoder.decode();
      const content = byId("output-text").textContent;
      renderResponse({ content, platform: currentRequest.platform, word_count: content.trim() ? content.trim().split(/\s+/).length : 0, character_count: content.length }, "STREAM");
    } else {
      const response = await api("/content/generate", { method: "POST", body: JSON.stringify(currentRequest) });
      renderResponse(await response.json());
    }
  } catch (error) {
    showError(error);
  } finally {
    byId("generate-button").disabled = false;
    byId("generate-button").innerHTML = "<span>✳</span> Generate draft";
    if (currentResponse) byId("result-status").classList.remove("busy");
  }
}

async function regenerate() {
  if (!currentResponse) return;
  setBusy(true, "REGENERATING");
  try {
    const response = await api("/content/regenerate", { method: "POST", body: JSON.stringify(currentResponse) });
    renderResponse(await response.json());
  } catch (error) { showError(error); }
  finally { byId("generate-button").disabled = false; }
}

async function analyze() {
  if (!currentResponse?.content) return;
  const box = byId("analysis-box");
  box.innerHTML = "<h3>Content analysis</h3><p>Analyzing draft…</p>";
  box.classList.remove("is-hidden");
  try {
    const query = new URLSearchParams({ content: currentResponse.content });
    const response = await api(`/content/analyze?${query}`, { method: "POST", body: JSON.stringify(currentRequest || { prompt: "" }) });
    const result = await response.json();
    box.innerHTML = `<h3>Content analysis</h3><pre>${escapeHtml(JSON.stringify(result, null, 2))}</pre>`;
  } catch (error) { box.innerHTML = `<h3>Analysis unavailable</h3><pre>${escapeHtml(error.message)}</pre>`; }
}

async function copyText(text, message) {
  try { await navigator.clipboard.writeText(text); showToast(message); }
  catch { showToast("Clipboard access is unavailable in this browser."); }
}

function updateMode() {
  byId("batch-field").classList.toggle("is-hidden", byId("generation-mode").value !== "batch");
}

function switchView(view) {
  for (const name of views) {
    byId(`view-${name}`).classList.toggle("active", name === view);
    document.querySelector(`[data-view="${name}"]`).classList.toggle("active", name === view);
  }
  byId("current-section").textContent = view[0].toUpperCase() + view.slice(1);
  window.scrollTo({ top: 0, behavior: "smooth" });
  if (view === "templates" && templateItems.length === 0) loadTemplates();
  if (view === "system") refreshSystem();
}

function templateUrl() {
  const params = new URLSearchParams();
  if (byId("template-category").value) params.set("category", byId("template-category").value);
  if (byId("template-type").value) params.set("template_type", byId("template-type").value);
  return `/templates${params.size ? `?${params}` : ""}`;
}

async function loadTemplates(query = "") {
  const list = byId("template-list");
  list.innerHTML = '<div class="loading-state">Loading templates…</div>';
  try {
    let response;
    if (query.trim()) {
      const params = new URLSearchParams({ query: query.trim(), limit: "100" });
      response = await api(`/templates/search?${params}`, { method: "POST" });
    } else {
      response = await api(templateUrl());
    }
    templateItems = await response.json();
    renderTemplateList(templateItems);
    updateTemplateSelect(templateItems);
  } catch (error) { list.innerHTML = `<div class="empty-library">${escapeHtml(error.message)}</div>`; }
}

function renderTemplateList(items) {
  const list = byId("template-list");
  if (!items.length) { list.innerHTML = '<div class="empty-library">No templates found for these filters.</div>'; return; }
  list.innerHTML = items.map((template) => `<button class="template-card${selectedTemplate?.id === template.id ? " selected" : ""}" data-template-id="${escapeHtml(template.id)}" type="button"><strong>${escapeHtml(template.name || template.id)}</strong><span class="tag">${escapeHtml(template.category || "template")}</span><small>${escapeHtml(template.template_type || "text")} · ${escapeHtml(template.id)}</small><p>${escapeHtml(template.description || "No description provided.")}</p></button>`).join("");
  list.querySelectorAll("[data-template-id]").forEach((button) => button.addEventListener("click", () => selectTemplate(button.dataset.templateId)));
}

function updateTemplateSelect(items) {
  const select = byId("template-select");
  const selected = select.value;
  select.innerHTML = '<option value="">No template</option>' + items.map((item) => `<option value="${escapeHtml(item.id)}">${escapeHtml(item.name || item.id)}</option>`).join("");
  if (items.some((item) => item.id === selected)) select.value = selected;
}

async function selectTemplate(templateId) {
  try {
    const response = await api(`/templates/${encodeURIComponent(templateId)}`);
    selectedTemplate = await response.json();
    renderTemplateList(templateItems);
    byId("template-empty").classList.add("is-hidden");
    byId("template-editor").classList.remove("is-hidden");
    byId("selected-template-category").textContent = `${selectedTemplate.category || "Template"} · ${selectedTemplate.template_type || "text"}`;
    byId("selected-template-name").textContent = selectedTemplate.name || selectedTemplate.id;
    byId("selected-template-description").textContent = selectedTemplate.description || "No description provided.";
    const variables = selectedTemplate.variables || [];
    byId("template-fields").innerHTML = variables.length ? variables.map((variable) => {
      const required = variable.required ? "required" : "";
      const defaultValue = variable.default_value == null ? "" : String(variable.default_value);
      if (variable.options?.length) return `<label class="field-label template-field">${escapeHtml(variable.name)}${variable.required ? ' <span class="required-indicator">*</span>' : ""}<select name="${escapeHtml(variable.name)}" ${required}><option value="">Choose…</option>${variable.options.map((option) => `<option>${escapeHtml(option)}</option>`).join("")}</select><small>${escapeHtml(variable.description || "")}</small></label>`;
      return `<label class="field-label template-field">${escapeHtml(variable.name)}${variable.required ? ' <span class="required-indicator">*</span>' : ""}<input name="${escapeHtml(variable.name)}" value="${escapeHtml(defaultValue)}" placeholder="${escapeHtml(variable.description || "Enter ${variable.name}")}" ${required}><small>${escapeHtml(variable.description || "")}</small></label>`;
    }).join("") : '<p class="panel-copy">This template has no variables. Render it as-is.</p>';
    byId("rendered-preview").classList.add("is-hidden");
  } catch (error) { showToast(error.message); }
}

async function renderTemplate(event) {
  event.preventDefault();
  if (!selectedTemplate) return;
  const variables = Object.fromEntries([...byId("template-fields").querySelectorAll("[name]")].map((field) => [field.name, field.value]));
  try {
    const response = await api(`/templates/${encodeURIComponent(selectedTemplate.id)}/render`, { method: "POST", body: JSON.stringify(variables) });
    const result = await response.json();
    byId("rendered-content").textContent = result.content || "";
    byId("rendered-preview").classList.remove("is-hidden");
  } catch (error) { showToast(error.message); }
}

function useTemplate() {
  if (!selectedTemplate) return;
  byId("template-select").value = selectedTemplate.id;
  if (selectedTemplate.platform) byId("platform").value = selectedTemplate.platform;
  switchView("compose");
  byId("prompt").focus();
  showToast("Template selected for your next draft.");
}

function prettifyKey(value) { return String(value).replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase()); }

function renderKeyValues(target, data, emptyText) {
  const entries = Object.entries(data || {}).filter(([, value]) => value !== null && typeof value !== "object");
  target.innerHTML = entries.length ? entries.map(([key, value]) => `<div class="cache-kv"><span>${escapeHtml(prettifyKey(key))}</span><span>${escapeHtml(value)}</span></div>`).join("") : `<span>${escapeHtml(emptyText)}</span>`;
}

async function loadHealth() {
  try {
    const response = await fetch("/health");
    if (!response.ok) throw new Error("Service unavailable");
    const health = await response.json();
    byId("connection-label").textContent = "Engine connected";
    byId("connection-dot").className = "connection-dot online";
    byId("health-label").textContent = `Service ${health.status}`;
    byId("health-detail").textContent = `Version ${health.version} · Engine ${health.engine}`;
    byId("health-dot").className = "health-dot online";
  } catch {
    byId("connection-label").textContent = "Engine unavailable";
    byId("connection-dot").className = "connection-dot offline";
    byId("health-label").textContent = "Service unavailable";
    byId("health-detail").textContent = "Check that the API server is running.";
    byId("health-dot").className = "health-dot offline";
  }
}

async function loadProviders() {
  try {
    const [availableResponse, currentResponse] = await Promise.all([api("/providers"), api("/providers/current")]);
    const available = await availableResponse.json();
    const current = await currentResponse.json();
    const providers = available.providers || [];
    for (const select of [byId("provider"), byId("system-provider")]) {
      const placeholder = select.id === "provider" ? '<option value="">Default provider</option>' : "";
      select.innerHTML = placeholder + providers.map((provider) => `<option value="${escapeHtml(provider)}">${escapeHtml(prettifyKey(provider))}</option>`).join("");
      select.value = current.provider || available.default || providers[0] || "";
    }
    byId("current-provider").textContent = current.provider || available.default || "Unknown";
    byId("current-model").textContent = current.model || "Model information unavailable";
    byId("provider-status").textContent = "CONNECTED";
    byId("provider-status").classList.add("done");
  } catch (error) {
    byId("current-provider").textContent = "Provider unavailable";
    byId("current-model").textContent = error.message;
    byId("provider-status").textContent = "UNAVAILABLE";
  }
}

function updatePromptPresetSelect(prompts = []) {
  const select = byId("prompt-preset");
  if (!select) return;
  select.innerHTML = '<option value="">Use a saved prompt preset</option>' + prompts.map((prompt) => `<option value="${escapeHtml(prompt.id)}">${escapeHtml(prompt.name || prompt.id)}</option>`).join("");
}

async function loadPromptPresets() {
  try {
    const response = await api("/prompts");
    const prompts = (await response.json()).prompts || [];
    updatePromptPresetSelect(prompts);
    return prompts;
  } catch (error) {
    updatePromptPresetSelect([]);
    return [];
  }
}

function applyPromptPreset(preset) {
  if (!preset) return;
  byId("prompt").value = preset.instructions || preset.prompt || "";
  byId("prompt-name").value = preset.name || "";
  byId("prompt-instructions").value = preset.instructions || "";
  byId("prompt-id").value = preset.id || "";
  showToast(`Loaded prompt preset: ${preset.name || preset.id}`, "system-toast");
}

async function renderSavedPrompts() {
  try {
    const response = await api("/prompts");
    const prompts = (await response.json()).prompts || [];
    updatePromptPresetSelect(prompts);
    const target = byId("saved-prompts-list");
    if (!prompts.length) {
      target.innerHTML = '<div class="empty-library">No saved prompt presets yet.</div>';
      return;
    }
    target.innerHTML = prompts.map((prompt) => `<div class="cache-kv"><span>${escapeHtml(prompt.name || prompt.id)}</span><span>${escapeHtml(prompt.instructions || "")}</span><button class="text-button" type="button" data-prompt-id="${escapeHtml(prompt.id)}">Use</button></div>`).join("");
    target.querySelectorAll("[data-prompt-id]").forEach((button) => {
      button.addEventListener("click", async () => {
        const list = await loadPromptPresets();
        const preset = list.find((item) => item.id === button.dataset.promptId);
        if (preset) applyPromptPreset(preset);
      });
    });
  } catch (error) {
    byId("saved-prompts-list").innerHTML = `<div class="loading-state">${escapeHtml(error.message)}</div>`;
  }
}

async function saveCustomProvider(event) {
  event.preventDefault();
  try {
    const payload = {
      id: byId("provider-id").value.trim(),
      provider_type: byId("provider-type").value,
      model: byId("provider-model").value.trim(),
      base_url: byId("provider-base-url").value.trim(),
      api_key: byId("provider-api-key").value.trim(),
      timeout: Number(byId("provider-timeout").value) || 30,
      max_tokens: Number(byId("provider-max-tokens").value) || 4096,
      temperature: Number(byId("provider-temperature").value) || 0.7,
    };
    const response = await api("/providers/configured", { method: "POST", body: JSON.stringify(payload) });
    const result = await response.json();
    showToast(result.message || "Provider saved.", "system-toast");
    await loadProviders();
  } catch (error) { showToast(error.message, "system-toast"); }
}

async function saveCustomPrompt(event) {
  event.preventDefault();
  try {
    const payload = {
      id: byId("prompt-id").value.trim(),
      name: byId("prompt-name").value.trim(),
      instructions: byId("prompt-instructions").value.trim(),
    };
    const response = await api("/prompts", { method: "POST", body: JSON.stringify(payload) });
    const result = await response.json();
    showToast(result.message || "Prompt saved.", "system-toast");
    await renderSavedPrompts();
  } catch (error) { showToast(error.message, "system-toast"); }
}

async function loadStats() {
  const target = byId("generation-stats");
  try {
    const response = await api("/generation/stats");
    const stats = await response.json();
    const entries = Object.entries(stats).filter(([, value]) => value !== null && typeof value !== "object");
    target.innerHTML = entries.length ? entries.map(([key, value]) => `<div class="stat-item"><span>${escapeHtml(prettifyKey(key))}</span><strong>${escapeHtml(value)}</strong></div>`).join("") : '<div class="loading-state">No generation statistics yet.</div>';
  } catch (error) { target.innerHTML = `<div class="loading-state">${escapeHtml(error.message)}</div>`; }
}

async function loadCacheStats() {
  const target = byId("cache-stats");
  try {
    const response = await api("/generation/cache/stats");
    renderKeyValues(target, await response.json(), "No cache statistics available.");
  } catch (error) { target.textContent = error.message; }
}

async function refreshSystem() {
  await Promise.all([loadHealth(), loadProviders(), loadStats(), loadCacheStats()]);
}

async function changeProvider(event) {
  event.preventDefault();
  const provider = byId("system-provider").value;
  if (!provider) return;
  try {
    const response = await api(`/providers/change?provider=${encodeURIComponent(provider)}`, { method: "POST" });
    const result = await response.json();
    showToast(result.message || "Provider changed.", "system-toast");
    await loadProviders();
  } catch (error) { showToast(error.message, "system-toast"); }
}

async function clearCache() {
  if (!window.confirm("Clear all cached content for this engine?")) return;
  try {
    const response = await api("/generation/cache/clear", { method: "POST" });
    const result = await response.json();
    showToast(result.message || "Cache cleared.", "system-toast");
    await loadCacheStats();
  } catch (error) { showToast(error.message, "system-toast"); }
}

function debounce(callback, delay) {
  let timer;
  return (...args) => { clearTimeout(timer); timer = setTimeout(() => callback(...args), delay); };
}

document.querySelectorAll("[data-view]").forEach((button) => button.addEventListener("click", () => switchView(button.dataset.view)));
byId("compose-form").addEventListener("submit", generate);
byId("generation-mode").addEventListener("change", updateMode);
byId("temperature").addEventListener("input", (event) => { byId("temperature-value").value = event.target.value; });
byId("regenerate-button").addEventListener("click", regenerate);
byId("analyze-button").addEventListener("click", analyze);
byId("copy-button").addEventListener("click", () => copyText(byId("output-text").textContent, "Draft copied."));
byId("download-button").addEventListener("click", () => {
  const blob = new Blob([byId("output-text").textContent], { type: "text/plain;charset=utf-8" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "content-engine-draft.txt";
  link.click();
  URL.revokeObjectURL(link.href);
});
byId("templates-refresh").addEventListener("click", () => loadTemplates(byId("template-search").value));
byId("template-search").addEventListener("input", debounce((event) => loadTemplates(event.target.value), 250));
byId("template-category").addEventListener("change", () => loadTemplates(byId("template-search").value));
byId("template-type").addEventListener("change", () => loadTemplates(byId("template-search").value));
byId("template-form").addEventListener("submit", renderTemplate);
byId("use-template-button").addEventListener("click", useTemplate);
byId("copy-rendered").addEventListener("click", () => copyText(byId("rendered-content").textContent, "Rendered template copied."));
byId("provider-form").addEventListener("submit", changeProvider);
byId("custom-provider-form").addEventListener("submit", saveCustomProvider);
byId("custom-prompt-form").addEventListener("submit", saveCustomPrompt);
byId("load-prompt-button").addEventListener("click", async () => {
  const presetId = byId("prompt-preset").value;
  if (!presetId) return;
  const presets = await loadPromptPresets();
  const preset = presets.find((item) => item.id === presetId);
  if (preset) applyPromptPreset(preset);
});
byId("clear-cache").addEventListener("click", clearCache);
byId("stats-refresh").addEventListener("click", () => { loadStats(); loadCacheStats(); });
byId("refresh-button").addEventListener("click", refreshSystem);

updateMode();
refreshSystem();
renderSavedPrompts();
loadPromptPresets();
loadTemplates();