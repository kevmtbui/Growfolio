// Dashboard logic: read stored profile, compute stats, fetch explanations
const API_BASE = "https://growfolio-production.up.railway.app";

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

  console.log("Dashboard loaded data:", { userData, recommendedRisk, investable, userProfile, traderType, analysisData });

  // Derive stats FIRST and render them immediately - summary should never be hidden
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

  // Render stat chips IMMEDIATELY - summary should always be visible
  const statsGrid = $("statsGrid");
  statsGrid.innerHTML = "";
  stats.forEach(s => {
    const div = document.createElement("div");
    div.className = "chip";
    div.innerHTML = `<div class="label">${s.label}</div><div class="value">${s.value}</div>`;
    statsGrid.appendChild(div);
  });

  // Now handle recommendations - clear recommendations list for loading
  const recsList = $("recsList");
  const insight = $("insight");
  recsList.innerHTML = "";

  // If no analysis data, try to generate it
  if (!analysisData && userProfile && traderType && userData) {
    try {
      const response = await fetch(`${API_BASE}/analyze_trader_type`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_data: userData,
          user_profile: userProfile,
          trader_type: traderType
        })
      });

      if (response.ok) {
        const newAnalysisData = await response.json();
        await chrome.storage.local.set({ analysisData: newAnalysisData });
        await renderTraderSpecificContent(traderType, newAnalysisData, userProfile);
        return;
      }
    } catch (error) {
      console.error('Failed to generate analysis:', error);
      insight.textContent = "Failed to generate recommendations. Please try refreshing.";
      return;
    }
  }

  // We have analysis data, render the content
  if (analysisData) {
    await renderTraderSpecificContent(traderType, analysisData, userProfile);
  }

  // Footer actions
  $("btnExport").addEventListener("click", async () => {
    await exportToPDF();
  });

  // Refresh button
  $("btnRefresh").addEventListener("click", async () => {
    await refreshRecommendations();
  });

  // Update profile button
  $("btnUpdateProfile").addEventListener("click", () => {
    window.location.href = "popup.html?from=dashboard";
  });
})();

async function refreshRecommendations() {
  try {
    // Get stored user data
    const { userData, userProfile, traderType } = await chrome.storage.local.get([
      "userData", "userProfile", "traderType"
    ]);

    if (!userData || !userProfile || !traderType) {
      alert("No profile data found. Please complete the onboarding first.");
      return;
    }

    // Show loading state
    const insight = $("insight");
    const recsList = $("recsList");
    const btnRefresh = $("btnRefresh");
    
    btnRefresh.disabled = true;
    btnRefresh.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
        <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>
        <path d="M21 3v5h-5"/>
        <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>
        <path d="M3 21v-5h5"/>
      </svg>
      Refreshing...
    `;
    
    // Clear recommendations list for refresh
    recsList.innerHTML = "";

    // Call backend to get fresh analysis
    const response = await fetch(`${API_BASE}/analyze_trader_type`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_data: userData,
        user_profile: userProfile,
        trader_type: traderType
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const analysisData = await response.json();
    
    // Store updated analysis
    await chrome.storage.local.set({ analysisData });
    
    // Re-render content
    await renderTraderSpecificContent(traderType, analysisData, userProfile);
    
    // Reset button
    btnRefresh.disabled = false;
    btnRefresh.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
        <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>
        <path d="M21 3v5h-5"/>
        <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>
        <path d="M3 21v-5h5"/>
      </svg>
      Refresh
    `;
    
  } catch (error) {
    console.error('Refresh failed:', error);
    alert(`Failed to refresh recommendations: ${error.message}`);
    
    // Reset button on error
    const btnRefresh = $("btnRefresh");
    btnRefresh.disabled = false;
    btnRefresh.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
        <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>
        <path d="M21 3v5h-5"/>
        <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>
        <path d="M3 21v-5h5"/>
      </svg>
      Refresh
    `;
  }
}

async function exportToPDF() {
  try {
    const { userData, recommendedRisk, userProfile, traderType, analysisData } = await chrome.storage.local.get([
      "userData", "recommendedRisk", "userProfile", "traderType", "analysisData"
    ]);

    // Create formatted text content for PDF
    let content = "GROWFOLIO INVESTMENT REPORT\n";
    content += "=".repeat(50) + "\n\n";
    
    content += "PROFILE SUMMARY\n";
    content += "-".repeat(50) + "\n";
    content += `Income: $${fmt(userData?.income || 0)}/mo\n`;
    content += `Expenses: $${fmt(userData?.total_expenses || 0)}/mo\n`;
    content += `Savings: $${fmt(userData?.savings || 0)}\n`;
    content += `Risk Profile: ${riskName(recommendedRisk || 5)}\n`;
    content += `Trader Type: ${traderType ? traderType.replace('_', ' ').toUpperCase() : 'N/A'}\n\n`;
    
    content += "RECOMMENDATIONS\n";
    content += "-".repeat(50) + "\n";
    
    if (traderType === "day_trader" && analysisData?.analysis?.predictions) {
      // Day trader with ML predictions
      for (let i = 0; i < analysisData.analysis.predictions.length; i++) {
        const pred = analysisData.analysis.predictions[i];
        const explanation = await explain(pred.ticker, userProfile, pred);
        const rationale = explanation || `${pred.action.toUpperCase()} signal based on ML analysis`;
        
        content += `\n${i + 1}. ${pred.ticker} - ${pred.action.toUpperCase()}\n`;
        content += `   Confidence: ${pred.confidence}%\n`;
        if (pred.current_price) content += `   Current Price: $${pred.current_price.toFixed(2)}\n`;
        if (pred.target_buy) content += `   Buy Target: $${pred.target_buy.toFixed(2)}\n`;
        if (pred.target_sell) content += `   Sell Target: $${pred.target_sell.toFixed(2)}\n`;
        content += `   AI Feedback: ${rationale}\n`;
      }
      
      // Add market insights
      if (analysisData.analysis.market_sentiment) {
        content += `\n\nMARKET INSIGHTS\n`;
        content += `-`.repeat(50) + "\n";
        content += `Market Sentiment: ${analysisData.analysis.market_sentiment}\n`;
        content += `Volatility Level: ${analysisData.analysis.volatility_level}\n`;
        content += `Recommended Position Size: ${analysisData.analysis.recommended_position_size}\n`;
      }
    } else if (analysisData?.analysis?.portfolio) {
      // Advanced portfolio format
      for (let i = 0; i < analysisData.analysis.portfolio.length; i++) {
        const item = analysisData.analysis.portfolio[i];
        content += `\n${i + 1}. ${item.asset} - ${(item.weight * 100).toFixed(1)}%\n`;
        content += `   ${item.name}\n`;
        content += `   ${item.notes}\n`;
        if (item.reasons && item.reasons.length > 0) {
          content += `   Reasons: ${item.reasons.join(", ")}\n`;
        }
      }
      
      // Add comprehensive explanation
      if (analysisData.analysis.explanation) {
        content += `\n\nPORTFOLIO STRATEGY\n`;
        content += `-`.repeat(50) + "\n";
        content += `Risk Profile: ${analysisData.analysis.risk?.title || "Moderate"} (${analysisData.analysis.risk?.score || 5}/10)\n`;
        content += `Jurisdiction: ${analysisData.analysis.jurisdiction || "CA"}\n\n`;
        content += analysisData.analysis.explanation + "\n";
      }
    } else if (analysisData?.analysis?.asset_allocation) {
      // Basic allocation format - fetch AI feedback for each ETF
      const allocation = analysisData.analysis.asset_allocation;
      let itemNum = 1;
      
      for (const [assetClass, data] of Object.entries(allocation)) {
        if (data.recommendations && Array.isArray(data.recommendations)) {
          const percentPerETF = data.percentage / data.recommendations.length;
          
          for (const rec of data.recommendations) {
            const ticker = rec.split(' ')[0].replace(/[()]/g, '');
            const explanation = await explain(ticker, userProfile);
            const rationale = explanation || `${assetClass} allocation for diversification and ${assetClass === 'stocks' ? 'growth' : 'stability'}.`;
            
            content += `\n${itemNum}. ${ticker} - ${percentPerETF.toFixed(1)}%\n`;
            content += `   ${rec}\n`;
            content += `   Asset Class: ${assetClass.toUpperCase()}\n`;
            content += `   AI Feedback: ${rationale}\n`;
            itemNum++;
          }
        }
      }
      
      // Add rationale
      if (analysisData.analysis.rationale) {
        content += `\n\nPORTFOLIO STRATEGY\n`;
        content += `-`.repeat(50) + "\n";
        // Clean up rationale text
        let cleanRationale = analysisData.analysis.rationale;
        cleanRationale = cleanRationale.replace(/```json[\s\S]*?```/g, '');
        cleanRationale = cleanRationale.replace(/```[\s\S]*?```/g, '');
        const sentences = cleanRationale.split(/[.!?]+/).filter(s => s.trim().length > 20);
        const summary = sentences.slice(0, 3).join('. ').trim() + (sentences.length > 0 ? '.' : '');
        content += summary + "\n";
      }
    }
    
    content += "\n" + "=".repeat(50) + "\n";
    content += `Generated: ${new Date().toLocaleString()}\n`;
    
    // Create blob and download
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `growfolio-report-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    
    alert("Report exported successfully! ✓");
  } catch (error) {
    console.error("Export error:", error);
    alert(`Failed to export: ${error.message}`);
  }
}

async function renderTraderSpecificContent(traderType, analysisData, userProfile) {
  const recsList = $("recsList");
  const insight = $("insight");

  // Clear recommendations list
  recsList.innerHTML = "";

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
  const insightCard = insight.closest('.card'); // Get the parent card

  // Hide the "Why these picks?" section for day traders
  if (insightCard) {
    insightCard.style.display = 'none';
  }

  recsList.innerHTML = "";

  if (analysisData?.analysis?.predictions) {
    const predictions = analysisData.analysis.predictions;

    // Generate all explanations first, then display all at once
    const explanations = await Promise.all(
      predictions.map(async (pred) => {
        const explanation = await explain(pred.ticker, userProfile, pred);
        
        // Add explanation of what BUY/SELL/HOLD means
        let actionExplanation = "";
        if (pred.action === "buy") {
          actionExplanation = "Consider opening a new position or adding to an existing one.";
        } else if (pred.action === "sell") {
          actionExplanation = "Consider taking profits or reducing your position.";
        } else if (pred.action === "hold") {
          actionExplanation = "Maintain your current position - no immediate action needed.";
        }
        
        const rationale = (explanation || `${pred.action.toUpperCase()} signal based on ML analysis`) + " " + actionExplanation;
        
        return { pred, rationale };
      })
    );

    // Now display all recommendations at once
    explanations.forEach(({ pred, rationale }) => {
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
    });

    // Show disclaimer after all recommendations
    const disclaimerCard = document.createElement("div");
    disclaimerCard.className = "rec";
    disclaimerCard.style.cssText = "background-color: #FFF3E0; border-left: 3px solid #F57C00;";
    disclaimerCard.innerHTML = `<p style="margin: 0;"><em>⚠️ These are ML-generated predictions for short-term trading. Always do your own research before making investment decisions.</em></p>`;
    recsList.appendChild(disclaimerCard);
  } else {
    // Fallback if no analysis data
    recsList.innerHTML = "<p class='muted'>No trading signals available. Please refresh or check your connection.</p>";
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
    
    // Get explanations for each ETF - generate all at once, then display all at once
    const explanations = await Promise.all(
      allRecommendations.map(async (rec) => {
        const explanation = await explain(rec.ticker, userProfile);
        const rationale = explanation || `${rec.assetClass} allocation for diversification and ${rec.assetClass === 'stocks' ? 'growth' : 'stability'}.`;
        return { rec, rationale };
      })
    );
    
    // Now display all recommendations at once
    explanations.forEach(({ rec, rationale }) => {
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
        <p class="muted"><strong>${rec.name.replace(rec.ticker, '').trim()}</strong></p>
        <p class="muted">${rationale}</p>
      `;
      recsList.appendChild(card);
    });

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

// Initialize the dashboard
init();

