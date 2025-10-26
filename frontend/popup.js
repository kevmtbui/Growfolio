// ====== GrowFolio Intake (3 slides, compact UI) ======
const API_BASE = "http://localhost:8001";

/**
 * 3 slides mirroring your backend sections.
 * Each question has a stable 'key' for storage. Types supported:
 *  - int, float, dropdown, multiple_choice, slider, scale, categories
 */
const SLIDES = [
  {
    id: 1, title: "Financial Snapshot",
    questions: [
      { key: "income", text: "Net monthly take-home (after taxes)", type: "float", min: 0, sub: "e.g., 3200" },
      {
        key: "expenses_breakdown", text: "Monthly expenses by category", type: "categories",
        categories: ["Housing", "Groceries", "Utilities", "Transportation", "Miscellaneous"]
      },
      { key: "savings", text: "Current savings / investments", type: "float", min: 0, sub: "bank + investments" },
      {
        key: "debt_type", text: "Any debt / ongoing loan payments?", type: "multiple_choice",
        options: ["None", "Credit cards", "Student loans", "Car loans", "Other"]
      },
      { key: "dependents", text: "How many dependents rely on you?", type: "int", min: 0 },
      { key: "age", text: "Your age", type: "int", min: 0, max: 120 }
    ]
  },
  {
    id: 2, title: "Investment Goals",
    questions: [
      {
        key: "primary_goal", text: "Primary investment goal", type: "multiple_choice",
        options: ["Retirement", "Short-term trading", "Supplemental Income"]
      },
      {
        key: "trader_type", text: "What type of trader are you?", type: "multiple_choice",
        options: ["Day Trader", "Retirement Investor", "Both"],
        sub: "This determines the type of analysis you'll receive"
      },
      {
        key: "horizon", text: "Planned investment horizon", type: "dropdown",
        options: ["<1 year", "1-3 years", "3-7 years", "7-15 years", "15+ years"]
      },
      {
        key: "retire_age", text: "If retirement, at what age would you like to retire?", type: "int", min: 18, max: 120,
        conditional: { key: "primary_goal", equals: "Retirement" }
      },
      { key: "invest_pct", text: "How much of your net savings are you willing to invest?", type: "slider", min: 1, max: 100 },
      { key: "risk_scale", text: "Preference: steady vs. higher returns (1–5)", type: "scale", min: 1, max: 5 },
      {
        key: "drawdown_resp", text: "If your investment dropped 20% in a month, what would you do?", type: "multiple_choice",
        options: ["Sell everything", "Sell some", "Do nothing", "Buy more"]
      }
    ]
  },
  {
    id: 3, title: "Personal Profile",
    questions: [
      {
        key: "experience", text: "Investing experience", type: "multiple_choice",
        options: ["Beginner", "Intermediate", "Advanced"]
      },
      {
        key: "news_freq", text: "How often do you check portfolio/news?", type: "multiple_choice",
        options: ["Daily", "Weekly", "Monthly", "Rarely"]
      },
      {
        key: "risk_statement", text: "Which best describes you?", type: "multiple_choice",
        options: [
          "I'd rather miss some gains than lose money.",
          "I'm okay with short-term losses if I can earn more long-term.",
          "I enjoy taking calculated risks."
        ]
      },
      {
        key: "portfolio_pref", text: "Portfolio should prioritize…", type: "multiple_choice",
        options: ["Safety & Stability", "Balanced Growth", "Aggressive Growth"]
      }
    ]
  }
];

let slideIndex = 0;
let answers = {};
let userProfile = null;

// DOM
const stepper = document.getElementById("stepper");
const form = document.getElementById("slideForm");
const container = document.getElementById("question-container");
const backBtn = document.getElementById("backBtn");
const nextBtn = document.getElementById("nextBtn");
const output = document.getElementById("output");
const goDashRow = document.getElementById("goDashRow");
const goDashboardBtn = document.getElementById("goDashboardBtn");

// Restore stored progress
chrome.storage.local.get(["userData", "currentSlide", "userProfile"], (st) => {
  if (st.userData) answers = st.userData;
  if (Number.isInteger(st.currentSlide)) slideIndex = Math.min(st.currentSlide, SLIDES.length - 1);
  if (st.userProfile) userProfile = st.userProfile;
  renderSlide();
  updateStepper();
});

const fmt = (n) => Number(n).toLocaleString(undefined, { maximumFractionDigits: 2 });
const num = (x) => { const n = Number(x); return Number.isFinite(n) ? n : 0; };
function saveProgress() { chrome.storage.local.set({ userData: answers, currentSlide: slideIndex }); }
function updateStepper() { stepper.textContent = `Step ${slideIndex + 1} of ${SLIDES.length} — ${SLIDES[slideIndex].title}`; }

// Render current slide
function renderSlide() {
  output.classList.add("hidden");
  output.textContent = "";
  goDashRow.classList.add("hidden");
  container.innerHTML = "";

  const s = SLIDES[slideIndex];

  for (const q of s.questions) {
    // conditional question (retire_age)
    if (q.conditional) {
      const dep = answers[q.conditional.key];
      if (dep !== q.conditional.equals) continue;
    }

    const wrap = document.createElement("div");
    wrap.className = "field";
    wrap.dataset.key = q.key;

    // label
    const label = document.createElement("label");
    label.textContent = q.text;
    wrap.appendChild(label);
    if (q.sub) {
      const sm = document.createElement("small");
      sm.textContent = q.sub;
      wrap.appendChild(sm);
    }

    // control by type
    if (q.type === "multiple_choice" || q.type === "dropdown") {
      const sel = document.createElement("select");
      sel.className = "q-input";
      sel.name = q.key;
      const def = document.createElement("option");
      def.value = ""; def.textContent = "Select an option"; def.disabled = true; def.selected = true;
      sel.appendChild(def);
      for (const opt of q.options) {
        const o = document.createElement("option");
        o.value = opt; o.textContent = opt;
        sel.appendChild(o);
      }
      if (answers[q.key]) sel.value = String(answers[q.key]);
      wrap.appendChild(sel);

    } else if (q.type === "int" || q.type === "float") {
      const inp = document.createElement("input");
      inp.type = "number";
      inp.className = "q-input";
      inp.name = q.key;
      if (q.min !== undefined) inp.min = String(q.min);
      if (q.max !== undefined) inp.max = String(q.max);
      inp.step = (q.type === "int") ? "1" : "0.01";
      inp.inputMode = "decimal";
      if (answers[q.key] !== undefined) inp.value = String(answers[q.key]);
      wrap.appendChild(inp);

    } else if (q.type === "slider" || q.type === "scale") {
      const min = q.min ?? 1, max = q.max ?? 5;
      const rw = document.createElement("div");
      rw.className = "range-wrap";
      const rng = document.createElement("input");
      rng.type = "range"; rng.min = String(min); rng.max = String(max); rng.step = "1";
      rng.className = "q-input"; rng.name = q.key; rng.value = String(answers[q.key] ?? min);
      const val = document.createElement("div");
      val.className = "range-value";
      const span = document.createElement("span");
      span.id = `range-${q.key}`; span.textContent = String(rng.value);
      val.appendChild(span);
      if (q.type === "slider") { val.innerHTML += "%"; val.insertBefore(span, val.firstChild); }
      rng.addEventListener("input", () => { span.textContent = String(rng.value); });
      rw.appendChild(rng); rw.appendChild(val);
      wrap.appendChild(rw);

    } else if (q.type === "categories") {
      const cats = q.categories || [];
      const grid = document.createElement("div");
      grid.className = "categories"; grid.id = `categories-${q.key}`;
      const saved = answers[q.key] || {};
      for (const c of cats) {
        const rowLabel = document.createElement("label");
        rowLabel.textContent = c; rowLabel.className = "cat-label";
        const rowInput = document.createElement("input");
        rowInput.type = "number"; rowInput.className = "cat-input";
        rowInput.name = `${q.key}:${c}`; rowInput.min = "0"; rowInput.step = "0.01"; rowInput.inputMode = "decimal";
        if (saved && saved[c] !== undefined) rowInput.value = String(saved[c]);
        grid.appendChild(rowLabel);
        grid.appendChild(rowInput);
      }
      const total = document.createElement("div");
      total.className = "cat-total";
      total.innerHTML = `<strong>Total:</strong> $<span id="cat-total-${q.key}">0.00</span>/mo`;
      grid.addEventListener("input", () => updateCategoriesTotal(q.key));
      wrap.appendChild(grid);
      wrap.appendChild(total);
      // initialize
      updateCategoriesTotal(q.key);
    }

    container.appendChild(wrap);
  }

  // buttons state
  backBtn.style.visibility = (slideIndex === 0) ? "hidden" : "visible";
  nextBtn.textContent = (slideIndex === SLIDES.length - 1) ? "Finish" : "Next";
  updateStepper();

  // Enter to submit
  form.onkeydown = (e) => {
    if (e.key === "Enter") { e.preventDefault(); nextBtn.click(); }
  };
}

// categories total helper
function updateCategoriesTotal(key) {
  const grid = document.getElementById(`categories-${key}`);
  if (!grid) return;
  let sum = 0;
  grid.querySelectorAll(".cat-input").forEach(inp => sum += num(inp.value));
  const span = document.getElementById(`cat-total-${key}`);
  if (span) span.textContent = fmt(sum);
}

// validation & collect
function validateAndCollect() {
  const s = SLIDES[slideIndex];
  const fields = container.querySelectorAll(".field");

  for (const field of fields) {
    const key = field.dataset.key;
    const def = s.questions.find(q => q.key === key) || SLIDES.flatMap(x => x.questions).find(q => q.key === key);
    if (!def) continue;

    if (def.type === "categories") {
      const grid = field.querySelector(".categories");
      const inputs = grid.querySelectorAll(".cat-input");
      const obj = {}; let hasValue = false;
      for (const inp of inputs) {
        const name = inp.name.split(":")[1];
        const v = num(inp.value);
        if (v < 0) return { ok: false, msg: "Values can’t be negative." };
        obj[name] = v;
        if (v) hasValue = true;
      }
      if (!hasValue) return { ok: false, msg: "Enter at least one category amount." };
      answers[def.key] = obj;
      // update total_expenses for risk math
      const total = Object.values(obj).reduce((a, b) => a + Number(b || 0), 0);
      answers["total_expenses"] = total;
      continue;
    }

    const el = field.querySelector(".q-input, select, input[type='number']");
    if (!el) continue;

    if (def.type === "multiple_choice" || def.type === "dropdown") {
      if (!el.value) return { ok: false, msg: "Please select an option." };
      answers[def.key] = el.value;

    } else if (def.type === "int" || def.type === "float") {
      if (el.value === "") return { ok: false, msg: "This field is required." };
      const v = num(el.value);
      if (!Number.isFinite(v)) return { ok: false, msg: "Please enter a valid number." };
      if (def.min !== undefined && v < def.min) return { ok: false, msg: `Value must be ≥ ${def.min}.` };
      if (def.max !== undefined && v > def.max) return { ok: false, msg: `Value must be ≤ ${def.max}.` };
      if (def.type === "int" && !Number.isInteger(v)) return { ok: false, msg: "Please enter a whole number." };
      answers[def.key] = v;

    } else if (def.type === "slider" || def.type === "scale") {
      const min = def.min ?? 1, max = def.max ?? 5;
      const v = num(el.value);
      if (v < min || v > max) return { ok: false, msg: `Value must be between ${min} and ${max}.` };
      answers[def.key] = v;
    }
  }

  return { ok: true };
}

function showError(msg) {
  output.textContent = msg;
  output.classList.add("error");
  output.classList.remove("hidden");
}
function clearError() {
  output.textContent = "";
  output.classList.add("hidden");
  output.classList.remove("error");
}

// Risk summary
function computeRisk() {
  const income = num(answers["income"]);
  const expenses = num(answers["total_expenses"]);
  const savings = num(answers["savings"]);
  const age = num(answers["age"]);
  const dependents = num(answers["dependents"]);
  const riskScale = num(answers["risk_scale"]);

  const investable = Math.max(0, income - expenses);
  const runway = savings / Math.max(1, expenses || 1);

  let risk = 5;
  if (income > expenses * 1.25) risk += 1;
  if (income > expenses * 1.5) risk += 1;
  if (expenses > income * 0.7) risk -= 1;
  if (expenses > income * 0.9) risk -= 1;
  if (dependents >= 1) risk -= Math.min(2, dependents);
  if (age <= 25) risk += 1;
  if (age >= 55) risk -= 1;
  if (riskScale >= 4) risk += 1;
  if (riskScale <= 2) risk -= 1;
  if (runway >= 6) risk += 1; else if (runway < 3) risk -= 2;

  risk = Math.max(1, Math.min(10, Math.round(risk)));
  const caps = { 1: 0.1, 2: 0.15, 3: 0.2, 4: 0.25, 5: 0.35, 6: 0.45, 7: 0.55, 8: 0.65, 9: 0.75, 10: 0.85 };
  const cap = caps[risk] ?? 0.35;
  const suggested = investable * cap;

  const warnings = [];
  if (investable <= 0) warnings.push("Your expenses are equal to or higher than income — consider pausing investing until cash flow is positive.");
  if (runway < 3) warnings.push(`Emergency fund is low (~${runway.toFixed(1)} months). Aim for 3–6 months before taking higher risk.`);

  let msg = `<strong>Risk level:</strong> ${risk}/10<br>`;
  msg += `<strong>Investable (monthly):</strong> $${fmt(investable)}<br>`;
  msg += `<strong>Suggested allocation cap:</strong> $${fmt(suggested)} (${Math.round(cap * 100)}%)<br>`;
  if (warnings.length) {
    msg += `<br><em>${warnings.join(" ")}</em>`;
    output.classList.add("error");
  } else {
    output.classList.remove("error");
  }
  output.innerHTML = msg;
  output.classList.remove("hidden");

  chrome.storage.local.set({ userData: answers, recommendedRisk: risk, investable, suggested });
}

// Create profile (Gemini)
async function createProfile() {
  try {
    // Try advanced profile first, fallback to basic if it fails
    let resp = await fetch(`${API_BASE}/create_advanced_profile`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(answers)
    });

    let data = await resp.json();
    let userProfile = data.user_profile || null;

    // If advanced profile fails, try basic profile
    if (!userProfile && data.error) {
      console.log("Advanced profile failed, trying basic profile:", data.error);
      resp = await fetch(`${API_BASE}/create_profile`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(answers)
      });
      data = await resp.json();
      userProfile = data.user_profile || null;
    }

    // Determine trader type and get appropriate analysis
    const traderType = determineTraderType(answers);
    const analysisData = await getTraderAnalysis(userProfile, traderType);

    chrome.storage.local.set({
      userProfile,
      traderType,
      analysisData,
      isAdvancedProfile: !!userProfile && !data.error
    });

    output.innerHTML += `<br><span class="muted">Profile created via Gemini ✓</span>`;
    output.innerHTML += `<br><span class="muted">Analysis: ${traderType} ✓</span>`;
    if (userProfile && !data.error) {
      output.innerHTML += `<br><span class="muted">Advanced portfolio system enabled ✓</span>`;
    }
  } catch (e) {
    output.innerHTML += `<br><span class="muted">Profile error: ${String(e)}</span>`;
  }
}

function determineTraderType(answers) {
  const traderTypeAnswer = answers.trader_type;
  const primaryGoal = answers.primary_goal;

  if (traderTypeAnswer === "Day Trader") return "day_trader";
  if (traderTypeAnswer === "Retirement Investor") return "retirement_investor";
  if (traderTypeAnswer === "Both") return "both";

  // Fallback based on primary goal
  if (primaryGoal === "Short-term trading") return "day_trader";
  if (primaryGoal === "Retirement") return "retirement_investor";

  return "retirement_investor"; // Default
}

async function getTraderAnalysis(userProfile, traderType) {
  try {
    const resp = await fetch(`${API_BASE}/analyze_trader_type`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_profile: userProfile,
        trader_type: traderType
      })
    });
    const data = await resp.json();
    return data;
  } catch (e) {
    console.error("Analysis error:", e);
    return null;
  }
}

/* Buttons */
backBtn.addEventListener("click", () => {
  if (slideIndex === 0) return;
  clearError();
  slideIndex -= 1;
  saveProgress();
  renderSlide();
});

nextBtn.addEventListener("click", async () => {
  clearError();
  const res = validateAndCollect();
  if (!res.ok) { showError(res.msg); return; }

  saveProgress();

  // Last slide -> finish
  if (slideIndex === SLIDES.length - 1) {
    computeRisk();
    await createProfile();
    goDashRow.classList.remove("hidden");
    nextBtn.textContent = "Done";
    nextBtn.disabled = true;
    return;
  }

  // Move to next
  slideIndex += 1;
  renderSlide();
});

goDashboardBtn.addEventListener("click", () => {
  window.location.href = "dashboard.html";
});
