// ====== GrowFolio Popup (MV3) ======
// Backend base
const API_BASE = "http://localhost:8000";

// Intake questions (extended to match backend risk/goal signals)
const questions = [
  { key: "age", text: "Hey there! How old are you?", type: "number", min: 0, max: 120 },
  { key: "total_expenses", text: "Let’s get a sense of your spending.", subtext: "Total monthly expenses including rent, food, bills, subscriptions, and other stuff.", type: "number", min: 0 },
  { key: "income", text: "How much do you bring home each month?", subtext: "Take-home income after taxes.", type: "number", min: 0 },
  { key: "savings", text: "How much do you already have saved?", subtext: "Include bank accounts or investments.", type: "number", min: 0 },
  { key: "dependents", text: "Any dependents relying on you financially?", subtext: "Family members, kids, or others you support.", type: "number", min: 0 },

  // Goal & horizon
  { key: "primary_goal", text: "What's your primary investment goal?", type: "select",
    options: ["Retirement", "Short-term trading", "Supplemental Income"] },
  { key: "horizon", text: "How long do you plan to keep this money invested?", type: "select",
    options: ["<1 year", "1-3 years", "3-7 years", "7-15 years", "15+ years"] },

  // Risk temperament
  { key: "risk_scale", text: "Prefer steady growth or higher potential returns?", subtext: "1 = safety, 5 = more ups/downs", type: "number", min: 1, max: 5 },
  { key: "drawdown_resp", text: "If your investment dropped 20% in a month, what would you do?", type: "select",
    options: ["Sell everything", "Sell some", "Do nothing", "Buy more"] },

  // Experience
  { key: "experience", text: "How experienced are you with investing?", type: "select",
    options: ["Beginner", "Intermediate", "Advanced"] }
];

let currentQuestion = 0;
let answers = {};
let userProfile = null;

// DOM
const container = document.getElementById("question-container");
const nextBtn = document.getElementById("nextBtn");
const output = document.getElementById("output");
const divider = document.getElementById("postIntakeDivider");
const postIntake = document.getElementById("post-intake");
const tickerInput = document.getElementById("tickerInput");
const explainBtn = document.getElementById("explainBtn");
const explainResult = document.getElementById("explainResult");

// inline helpers
const errorEl = document.createElement("div");
errorEl.id = "inlineError";
errorEl.className = "muted";

// Back button
const buttonContainer = document.getElementById("button-container");
const backBtn = document.createElement("button");
backBtn.textContent = "Back";
backBtn.type = "button";
backBtn.style.background = "transparent";
backBtn.style.border = "1px solid #c7c7c7";
backBtn.style.borderRadius = "8px";
backBtn.style.color = "inherit";
backBtn.style.padding = "10px 12px";
backBtn.style.cursor = "pointer";
buttonContainer.insertBefore(backBtn, nextBtn);

backBtn.addEventListener("click", () => {
  if (currentQuestion > 0) {
    currentQuestion--;
    saveProgress();
    showQuestion(currentQuestion, true);
  }
});

// Restore saved answers + progress + profile
chrome.storage.local.get(["userData", "currentQuestion", "userProfile"], (result) => {
  if (result.userData) answers = result.userData;
  if (Number.isInteger(result.currentQuestion)) currentQuestion = Math.min(result.currentQuestion, questions.length);
  if (result.userProfile) userProfile = result.userProfile;
  showQuestion(currentQuestion, true);

  // If already completed earlier, show post-intake
  if (currentQuestion >= questions.length) {
    nextBtn.style.display = "none";
    backBtn.style.display = "inline-block";
    divider.classList.remove("hidden");
    postIntake.classList.remove("hidden");
  }
});

function sanitizeNumber(x) {
  const n = Number(x);
  return Number.isFinite(n) ? n : 0;
}
function saveProgress() {
  chrome.storage.local.set({ userData: answers, currentQuestion });
}

function progressMarkup(i) {
  return `<div class="muted" style="margin-bottom:6px;">Question ${i + 1} / ${questions.length}</div>`;
}

function showQuestion(index, prefill = false) {
  errorEl.textContent = "";

  if (index >= questions.length) {
    container.innerHTML = `<p>All questions completed!</p>`;
    nextBtn.style.display = "none";
    backBtn.style.display = "inline-block";
    calculateRisk();     // compute + show guardrails
    createProfile();     // call backend to build Gemini profile
    divider.classList.remove("hidden");
    postIntake.classList.remove("hidden");
    return;
  }

  const q = questions[index];
  let html = "";
  html += progressMarkup(index);
  html += `<label>${q.text}</label>`;
  if (q.subtext) html += `<small>${q.subtext}</small>`;

  if (q.type === "select") {
    const opts = q.options.map(opt => `<option value="${opt}">${opt}</option>`).join("");
    html += `
      <select id="answerInput" required>
        <option value="" disabled selected>Select an option</option>
        ${opts}
      </select>
    `;
  } else {
    html += `
      <input type="${q.type}" id="answerInput" required
        ${q.min !== undefined ? `min="${q.min}"` : ""}
        ${q.max !== undefined ? `max="${q.max}"` : ""}
        inputmode="decimal" autocomplete="off">
    `;
  }

  container.innerHTML = html;
  container.appendChild(errorEl);

  const inputEl = document.getElementById("answerInput");
  if (prefill && answers[q.key] !== undefined && inputEl) inputEl.value = String(answers[q.key]);
  if (inputEl) {
    inputEl.focus();
    inputEl.addEventListener("keydown", (e) => {
      if (e.key === "Enter") { e.preventDefault(); nextBtn.click(); }
    });
  }

  backBtn.style.display = index > 0 ? "inline-block" : "none";
  nextBtn.style.display = "inline-block";
}

function validateAnswer(q, valRaw) {
  if (q.type === "select") return valRaw ? null : "Please select an option.";
  if (valRaw === "" || valRaw === null || valRaw === undefined) return "This field is required.";
  const n = sanitizeNumber(valRaw);
  if (!Number.isFinite(n)) return "Please enter a valid number.";
  if (q.min !== undefined && n < q.min) return `Value must be ≥ ${q.min}.`;
  if (q.max !== undefined && n > q.max) return `Value must be ≤ ${q.max}.`;
  return null;
}

function calculateRisk() {
  const income = sanitizeNumber(answers["income"]);
  const expenses = sanitizeNumber(answers["total_expenses"]);
  const savings = sanitizeNumber(answers["savings"]);
  const age = sanitizeNumber(answers["age"]);
  const dependents = sanitizeNumber(answers["dependents"]);

  const investable = Math.max(0, income - expenses);
  const runwayMonths = savings / Math.max(1, expenses || 1);
  let risk = 5;

  if (income > expenses * 1.25) risk += 1;
  if (income > expenses * 1.5) risk += 1;
  if (expenses > income * 0.7) risk -= 1;
  if (expenses > income * 0.9) risk -= 1;
  if (dependents >= 1) risk -= Math.min(2, dependents);
  if (age <= 25) risk += 1;
  if (age >= 55) risk -= 1;
  if (runwayMonths >= 6) risk += 1; else if (runwayMonths < 3) risk -= 2;

  // temperament signals
  const riskScale = sanitizeNumber(answers["risk_scale"]);
  if (riskScale >= 4) risk += 1;
  if (riskScale <= 2) risk -= 1;

  risk = Math.max(1, Math.min(10, Math.round(risk)));

  const caps = { 1:0.1, 2:0.15, 3:0.2, 4:0.25, 5:0.35, 6:0.45, 7:0.55, 8:0.65, 9:0.75, 10:0.85 };
  const cap = caps[risk] ?? 0.35;
  const suggested = investable * cap;

  const warnings = [];
  if (investable <= 0) warnings.push("Your expenses are equal to or higher than income — consider pausing investing until cash flow is positive.");
  if (runwayMonths < 3) warnings.push(`Emergency fund is low (~${runwayMonths.toFixed(1)} months). Aim for 3–6 months before taking higher risk.`);

  let msg = `<strong>Risk level:</strong> ${risk}/10<br>`;
  msg += `<strong>Investable (monthly):</strong> $${investable.toLocaleString(undefined,{maximumFractionDigits:2})}<br>`;
  msg += `<strong>Suggested allocation cap:</strong> $${suggested.toLocaleString(undefined,{maximumFractionDigits:2})} (${Math.round(cap*100)}%)<br>`;
  if (warnings.length) { msg += `<br><em>${warnings.join(" ")}</em>`; output.classList.add("error"); }
  else { output.classList.remove("error"); }

  output.innerHTML = msg;
  output.classList.remove("hidden");

  chrome.storage.local.set({ userData: answers, recommendedRisk: risk, investable, suggested });
}

async function createProfile() {
  try {
    const resp = await fetch(`${API_BASE}/create_profile`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(answers)
    });
    const data = await resp.json();
    userProfile = data.user_profile || null;
    chrome.storage.local.set({ userProfile });

    // Show a brief status line in the output box
    const note = userProfile ? "Profile created via Gemini ✓" : "Profile creation returned no data.";
    output.innerHTML += `<br><span class="muted">${note}</span>`;
  } catch (e) {
    output.innerHTML += `<br><span class="muted">Profile error: ${String(e)}</span>`;
  }
}

function renderExplanation(res) {
  const { stock, ml_output, gemini_explanation } = res || {};
  return `
    <strong>${stock || "(no ticker)"}:</strong>
    <div class="muted">ML: ${ml_output ? JSON.stringify(ml_output) : "n/a"}</div>
    <p>${gemini_explanation || "No explanation returned."}</p>
  `;
}

explainBtn.addEventListener("click", async () => {
  explainResult.innerHTML = "Thinking…";
  const ticker = (tickerInput.value || "").toUpperCase().trim();
  if (!ticker) { explainResult.innerHTML = "Please enter a ticker (e.g., AAPL)."; return; }
  if (!userProfile) {
    // attempt lazy fetch from storage if popup reloaded
    const s = await chrome.storage.local.get(["userProfile"]);
    userProfile = s.userProfile || null;
  }
  if (!userProfile) {
    explainResult.innerHTML = "User profile not ready yet. Complete intake first.";
    return;
  }

  try {
    const resp = await fetch(`${API_BASE}/recommend_stock`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        stock_name: ticker,
        user_profile: userProfile,
        ml_output: { confidence: 80, action: "buy" } // placeholder for now
      })
    });
    const data = await resp.json();
    if (data.error) {
      explainResult.innerHTML = `Error: ${data.error}`;
    } else {
      explainResult.innerHTML = renderExplanation(data);
    }
  } catch (e) {
    explainResult.innerHTML = `Request failed: ${String(e)}`;
  }
});

// Next (save & advance)
nextBtn.addEventListener("click", () => {
  const q = questions[currentQuestion];
  const inputElement = document.getElementById("answerInput");
  if (!q || !inputElement) return;

  const raw = (q.type === "select") ? inputElement.value : inputElement.value.trim();
  const err = validateAnswer(q, raw);
  if (err) { errorEl.textContent = err; inputElement.after(errorEl); inputElement.focus(); return; }

  answers[q.key] = (q.type === "number") ? sanitizeNumber(raw) : raw;
  currentQuestion++;
  saveProgress();
  showQuestion(currentQuestion);
});

// Keyboard quick nav
window.addEventListener("keydown", (e) => {
  if (e.altKey && e.key === "ArrowLeft" && currentQuestion > 0) {
    e.preventDefault(); currentQuestion--; saveProgress(); showQuestion(currentQuestion, true);
  }
  if (e.altKey && e.key === "ArrowRight" && currentQuestion < questions.length) {
    e.preventDefault(); nextBtn.click();
  }
});
