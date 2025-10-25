// Dashboard logic: read stored profile, compute stats, fetch explanations
const API_BASE = "http://localhost:8000";

const $ = (id) => document.getElementById(id);

// Simple helpers
const fmt = (n) => {
  if (typeof n !== "number" || !isFinite(n)) return String(n);
  return n.toLocaleString(undefined, { maximumFractionDigits: 2 });
};
const riskName = (r) => {
  if (r <= 3) return "Conservative";
  if (r <= 6) return "Moderate";
  return "Aggressive";
};

(async function init(){
  // Load everything we might need from storage
  const { userData, recommendedRisk, investable, userProfile } = await chrome.storage.local.get([
    "userData", "recommendedRisk", "investable", "userProfile"
  ]);

  // Derive stats
  const income = Number(userData?.income || 0);
  const expenses = Number(userData?.total_expenses || 0);
  const savingsRate = income > 0 ? ((Math.max(0, income - expenses) / income) * 100) : 0;

  const stats = [
    { label: "Income", value: `$${fmt(income)}/mo` },
    { label: "Expenses", value: `$${fmt(expenses)}/mo` },
    { label: "Savings Rate", value: `${Math.round(savingsRate)}%` },
    { label: "Risk Profile", value: riskName(Number(recommendedRisk || 5)) },
  ];

  // Render stat chips
  const statsGrid = $("statsGrid");
  statsGrid.innerHTML = "";
  stats.forEach(s => {
    const div = document.createElement("div");
    div.className = "chip";
    div.innerHTML = `<div class="label">${s.label}</div><div class="value">${s.value}</div>`;
    statsGrid.appendChild(div);
  });

  // Default rec list
  const recSeed = [
    { ticker:"AAPL", company:"Apple Inc.", confidence:78 },
    { ticker:"MSFT", company:"Microsoft Corp.", confidence:82 },
    { ticker:"VTI",  company:"Total Market ETF", confidence:85 }
  ];

  // Try to fetch Gemini explanations for each
  const recsList = $("recsList");
  recsList.innerHTML = "";
  const insight = $("insight");
  let combinedWhy = [];

  for (const rec of recSeed) {
    const explanation = await explain(rec.ticker, userProfile);
    const rationale = explanation || "Stable profile match; diversified and aligned with your horizon.";
    combinedWhy.push(`${rec.ticker}: ${rationale}`);

    const card = document.createElement("div");
    card.className = "rec";
    card.innerHTML = `
      <div class="top">
        <div>
          <div class="ticker">${rec.ticker}</div>
          <div class="company">${rec.company}</div>
        </div>
        <div class="conf">${rec.confidence}% confidence</div>
      </div>
      <p class="muted">${rationale}</p>
    `;
    recsList.appendChild(card);
  }

  // High-level Gemini summary (fallback if none)
  insight.textContent = combinedWhy.length
    ? `Based on your income, spending, and ${riskName(Number(recommendedRisk || 5)).toLowerCase()} risk tolerance, we prioritized resilient cash-flow leaders and broad-market exposure. ${combinedWhy.join("  ·  ")}`
    : "Based on your profile, we prioritized resilient cash-flow companies with lower volatility and diversified exposure.";

  // Footer actions
  $("btnSave").addEventListener("click", async () => {
    // simple toast replacement
    alert("Saved ✓ (You can persist starred tickers or preferences here.)");
  });

  $("btnExport").addEventListener("click", async () => {
    const all = await chrome.storage.local.get(null);
    const blob = new Blob([JSON.stringify(all, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);

    // trigger download within extension context
    const a = document.createElement("a");
    a.href = url;
    a.download = "growfolio-export.json";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  });

  $("btnConnect").addEventListener("click", () => {
    alert("Connect flow not implemented in MVP (hook Wealthsimple/Auth here).");
  });
})();

async function explain(ticker, userProfile) {
  try {
    if (!userProfile) return ""; // will fall back on generic text
    const resp = await fetch(`${API_BASE}/recommend_stock`, {
      method: "POST",
      headers: { "Content-Type":"application/json" },
      body: JSON.stringify({
        stock_name: ticker,
        user_profile: userProfile,
        ml_output: { confidence: 80, action: "buy" } // placeholder
      })
    });
    const data = await resp.json();
    return data?.gemini_explanation || "";
  } catch (_) {
    return "";
  }
}
