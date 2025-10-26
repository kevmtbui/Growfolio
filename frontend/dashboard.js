// Dashboard logic: read stored profile, compute stats, fetch explanations
const API_BASE = "http://localhost:8000";

const $ = (id) => document.getElementById(id);

// Simple helpers
const fmt = (n) => {
  if (typeof n !== "number" || !isFinite(n)) return String(n);
  return n.toLocaleString(undefined, { maximumFractionDigits: 2 });
};

const num = (x) => {
  const n = Number(x);
  return Number.isFinite(n) ? n : 0;
};

const riskName = (r) => {
  if (r <= 3) return "Conservative";
  if (r <= 6) return "Moderate";
  return "Aggressive";
};

(async function init() {
  // Load everything we might need from storage
  const { userData, recommendedRisk, investable, userProfile, traderType, analysisData } = await chrome.storage.local.get([
    "userData", "recommendedRisk", "investable", "userProfile", "traderType", "analysisData"
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
    { label: "Trader Type", value: traderType ? traderType.replace('_', ' ').toUpperCase() : "UNKNOWN" },
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

  // Render content based on trader type
  await renderTraderSpecificContent(traderType, analysisData, userProfile);

  // Footer actions
  $("btnRefresh").addEventListener("click", async () => {
    await refreshAnalysis();
  });

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
})();

async function renderTraderSpecificContent(traderType, analysisData, userProfile) {
  const recsList = $("recsList");
  const insight = $("insight");

  if (traderType === "day_trader") {
    await renderDayTraderContent(analysisData, userProfile);
  } else if (traderType === "retirement_investor") {
    await renderRetirementInvestorContent(analysisData, userProfile);
  } else {
    // Default/fallback content
    await renderDefaultContent(userProfile);
  }
}

async function renderDayTraderContent(analysisData, userProfile) {
  const recsList = $("recsList");
  const insight = $("insight");

  recsList.innerHTML = "";

  if (analysisData?.analysis?.predictions) {
    const predictions = analysisData.analysis.predictions;

    for (const pred of predictions) {
      const explanation = await explain(pred.ticker, userProfile, pred);
      const rationale = explanation || `${pred.action.toUpperCase()} signal based on ML analysis`;

      const card = document.createElement("div");
      card.className = "rec";
      
      // Build price info
      let priceInfo = "";
      if (pred.current_price) {
        priceInfo = `<p class="muted"><strong>Current:</strong> $${pred.current_price.toFixed(2)}`;
        if (pred.target_buy) priceInfo += ` | <strong>Buy:</strong> $${pred.target_buy.toFixed(2)}`;
        if (pred.target_sell) priceInfo += ` | <strong>Sell:</strong> $${pred.target_sell.toFixed(2)}`;
        priceInfo += `</p>`;
      }
      
      card.innerHTML = `
        <div class="top">
          <div>
            <div class="ticker">${pred.ticker}</div>
            <div class="action ${pred.action}">${pred.action.toUpperCase()}</div>
          </div>
          <div class="conf">${pred.confidence}% confidence</div>
        </div>
        ${priceInfo}
        <p class="muted">${rationale}</p>
      `;
      recsList.appendChild(card);
    }

    insight.innerHTML = `
      <strong>Market Sentiment:</strong> ${analysisData.analysis.market_sentiment}<br>
      <strong>Volatility:</strong> ${analysisData.analysis.volatility_level}<br>
      <strong>Position Size:</strong> ${analysisData.analysis.recommended_position_size}<br>
      <em>These are ML-generated predictions for short-term trading. Always do your own research.</em>
    `;
  } else {
    // Fallback if no analysis data
    recsList.innerHTML = "<p class='muted'>No trading signals available. Please refresh or check your connection.</p>";
    insight.textContent = "Day trading analysis not available. Please try again.";
  }
}

async function renderRetirementInvestorContent(analysisData, userProfile) {
  const recsList = $("recsList");
  const insight = $("insight");

  recsList.innerHTML = "";

  // Check if we have advanced portfolio data
  if (analysisData?.analysis?.portfolio) {
    const portfolio = analysisData.analysis.portfolio;

    // Create portfolio cards with live data
    portfolio.forEach(item => {
      const card = document.createElement("div");
      card.className = "rec";

      let quoteInfo = "";
      if (item.asset !== "CASH" && analysisData.analysis.quotes?.[item.asset]) {
        const quote = analysisData.analysis.quotes[item.asset];
        quoteInfo = `<p class="muted">Price: $${quote.c?.toFixed(2) || 'N/A'} (${quote.dp?.toFixed(2) || 'N/A'}%)</p>`;
      }

      card.innerHTML = `
        <div class="top">
          <div>
            <div class="ticker">${item.asset}</div>
            <div class="percentage">${(item.weight * 100).toFixed(1)}%</div>
          </div>
          <div class="conf">${item.name}</div>
        </div>
        <p class="muted">${item.notes}</p>
        ${quoteInfo}
        ${item.reasons ? `<p class="muted">Reasons: ${item.reasons.join(", ")}</p>` : ""}
      `;
      recsList.appendChild(card);
    });

    // Show comprehensive explanation
    insight.innerHTML = `
      <strong>Risk Profile:</strong> ${analysisData.analysis.risk?.title || "Moderate"} (${analysisData.analysis.risk?.score || 5}/10)<br>
      <strong>Jurisdiction:</strong> ${analysisData.analysis.jurisdiction || "CA"}<br><br>
      ${analysisData.analysis.explanation || "Balanced allocation based on your risk profile and investment horizon."}
    `;

  } else if (analysisData?.analysis?.asset_allocation) {
    // Fallback to basic allocation format - show individual ETF recommendations
    const allocation = analysisData.analysis.asset_allocation;
    
    // Extract all ETF recommendations from the allocation
    const allRecommendations = [];
    Object.entries(allocation).forEach(([assetClass, data]) => {
      if (data.recommendations && Array.isArray(data.recommendations)) {
        // Split the percentage equally among recommendations in this asset class
        const percentPerETF = data.percentage / data.recommendations.length;
        
        data.recommendations.forEach(rec => {
          // Extract ticker from recommendation (e.g., "VTI (Vanguard...)" -> "VTI")
          const ticker = rec.split(' ')[0].replace(/[()]/g, '');
          allRecommendations.push({
            ticker: ticker,
            name: rec,
            assetClass: assetClass,
            percentage: percentPerETF
          });
        });
      }
    });
    
    // Get explanations for each ETF
    for (const rec of allRecommendations) {
      const explanation = await explain(rec.ticker, userProfile);
      const rationale = explanation || `${rec.assetClass} allocation for diversification and ${rec.assetClass === 'stocks' ? 'growth' : 'stability'}.`;
      
      const card = document.createElement("div");
      card.className = "rec";
      card.innerHTML = `
        <div class="top">
          <div>
            <div class="ticker">${rec.ticker}</div>
            <div class="percentage">${rec.assetClass.toUpperCase()}</div>
          </div>
          <div class="conf">${rec.percentage}% allocation</div>
        </div>
        <p class="muted"><strong>${rec.name.split('(')[0].trim()}</strong></p>
        <p class="muted">${rationale}</p>
      `;
      recsList.appendChild(card);
    }

    // Clean up rationale text - remove JSON formatting and extract key points
    let cleanRationale = analysisData.analysis.rationale || "Balanced allocation based on your risk profile and investment horizon.";
    
    // Remove JSON blocks
    cleanRationale = cleanRationale.replace(/```json[\s\S]*?```/g, '');
    cleanRationale = cleanRationale.replace(/```[\s\S]*?```/g, '');
    
    // Extract first 3 sentences or key points
    const sentences = cleanRationale.split(/[.!?]+/).filter(s => s.trim().length > 20);
    const summary = sentences.slice(0, 3).join('. ').trim() + (sentences.length > 0 ? '.' : '');

    insight.innerHTML = `
      <strong>Portfolio Strategy:</strong><br>
      ${summary || "Diversified allocation designed for long-term growth while managing risk through balanced exposure across asset classes."}
    `;
  } else {
    // No analysis data available
    recsList.innerHTML = "<p class='muted'>No portfolio allocation available. Please refresh or check your connection.</p>";
    insight.textContent = "Retirement portfolio analysis not available. Please try again.";
  }
}

async function renderDefaultContent(userProfile) {
  const recsList = $("recsList");
  const insight = $("insight");

  // Default rec list
  const recSeed = [
    { ticker: "AAPL", company: "Apple Inc.", confidence: 78 },
    { ticker: "MSFT", company: "Microsoft Corp.", confidence: 82 },
    { ticker: "VTI", company: "Total Market ETF", confidence: 85 }
  ];

  recsList.innerHTML = "";
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
    ? `Based on your income, spending, and moderate risk tolerance, we prioritized resilient cash-flow leaders and broad-market exposure. ${combinedWhy.join("  ·  ")}`
    : "Based on your profile, we prioritized resilient cash-flow companies with lower volatility and diversified exposure.";
}

async function refreshAnalysis() {
  try {
    const { userProfile, traderType } = await chrome.storage.local.get(["userProfile", "traderType"]);

    if (!userProfile || !traderType) {
      alert("No profile data found. Please complete the onboarding first.");
      return;
    }

    // Show loading state
    const insight = $("insight");
    insight.textContent = "Refreshing analysis...";

    // Get fresh analysis from backend
    const resp = await fetch(`${API_BASE}/analyze_trader_type`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_profile: userProfile,
        trader_type: traderType
      })
    });

    if (!resp.ok) {
      throw new Error(`HTTP ${resp.status}: ${resp.statusText}`);
    }

    const analysisData = await resp.json();

    // Update storage with new analysis
    await chrome.storage.local.set({ analysisData });

    // Re-render content with fresh data
    await renderTraderSpecificContent(traderType, analysisData, userProfile);

    alert("Analysis refreshed successfully! ✓");
  } catch (error) {
    console.error("Refresh error:", error);
    alert(`Failed to refresh analysis: ${error.message}`);

    // Reset insight to show error
    const insight = $("insight");
    insight.textContent = "Failed to refresh analysis. Please try again.";
  }
}
async function explain(ticker, userProfile, predictionData = null) {
  try {
    if (!userProfile) return ""; // will fall back on generic text
    
    const ml_output = predictionData ? {
      confidence: predictionData.confidence,
      action: predictionData.action,
      current_price: predictionData.current_price,
      target_buy: predictionData.target_buy,
      target_sell: predictionData.target_sell,
      timeframe: predictionData.timeframe
    } : { confidence: 80, action: "buy" };
    
    const resp = await fetch(`${API_BASE}/recommend_stock`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        stock_name: ticker,
        user_profile: userProfile,
        ml_output: ml_output
      })
    });
    const data = await resp.json();
    return data?.gemini_explanation || "";
  } catch (_) {
    return "";
  }
}

