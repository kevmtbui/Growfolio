# 🌱 Growfolio

### Chrome Extension · AI-Powered Financial Advisor · Hackathon Project

> **Growfolio** helps young investors make smarter, stress-free financial decisions using **AI insights, ML predictions, and the Gemini API** — all inside a simple Chrome extension.

---

## 🧩 Overview

**Problem:**  
Financial literacy and investing confidence are low among young adults. Most robo-advisors are either complex or paywalled.

**Solution:**  
Growfolio bridges the gap — a **Gemini-powered Chrome extension** that gives personalized stock recommendations, explanations, and trend insights, helping users grow wealth safely and confidently.

---

## 🎯 Goals & Objectives

- Simplify portfolio decision-making for new investors.  
- Use **Gemini API** to interpret user intent and explain recommendations in plain English.  
- Integrate an **ML model** to detect short-term stock trends and risk patterns.  
- Encourage long-term, stress-free investing habits (Financial Wellness theme).  

---

## 👤 Target Users

- **Primary:** Students & young professionals new to investing.  
- **Secondary:** Budget-conscious individuals seeking AI-assisted financial planning.  

---

## ⚙️ Core Features (MVP)

| Feature | Description | Priority |
|----------|--------------|----------|
| Smart Financial Intake | Collects income, rent, and spending data. | High |
| Risk & Literacy Quiz | Determines user confidence and tolerance. | High |
| **AI Stock Recommender (Gemini-Enhanced)** | Suggests stocks matched to risk and goals. | High |
| Decision Support Summaries | Explains *why* a stock was chosen (Gemini). | High |
| Manual Ticker Analysis | Lets users query any stock for AI insights. | Medium |
| Chrome Extension UI | One-click dashboard for all tools. | High |
| Auto-Trading *(Stretch)* | Wealthsimple API integration. | Low |

---

## 🤖 AI & ML Integration

**Dual-Layer Intelligence:**

- **Gemini API (LLM Layer)**  
  - Understands user intent  
  - Summarizes patterns and reasoning  
  - Generates human-readable explanations  

- **ML Model (Analytical Layer)**  
  - Predicts short-term stock trends  
  - Uses Random Forest or LSTM on open data (Yahoo Finance / Alpha Vantage)  
  - Outputs confidence & volatility metrics  

**Example Output:**  
> “Given your moderate risk tolerance, AAPL shows stable growth with 78% confidence.  
> Gemini explains: *‘Apple’s cash flow resilience aligns with your goal to save safely over time.’*”

---

## 🧠 Decision Support Logic

1. Collect user context (income, expenses, goals)  
2. Predict stock performance (ML model)  
3. Generate reasoning (Gemini API)  
4. Rank 3–5 stocks by risk and confidence  
5. Let user simulate or trade manually  

---

## 🧰 Tech Stack

| Layer | Tools |
|--------|-------|
| Frontend | Chrome Extension (HTML/CSS/JS, optional React) |
| Backend | Python (FastAPI) or Node.js |
| ML Model | scikit-learn / TensorFlow Lite |
| AI Assistant | Google Gemini API |
| Data | Yahoo Finance / Alpha Vantage |
| Storage | LocalStorage / IndexedDB |
| Integration *(Stretch)* | Wealthsimple API |

---

## 🏆 Hackathon Prize Fit

| Category | Why Growfolio Qualifies |
|-----------|------------------------|
| 🏦 Finance & Fintech | Personalized AI robo-trader |
| 🧘 Personal Wellness | Promotes financial wellbeing |
| 🤖 Best Use of Gemini API | Uses Gemini for reasoning & insights |
| ☁️ DigitalOcean Gradient | Host ML model inference |
| ❄️ Snowflake API | Store anonymized financial data |
| 🗣️ ElevenLabs Voice | (Stretch) Voice summaries of portfolio |

---

## 🧭 User Flow

1. Install Growfolio Chrome extension  
2. Complete financial intake & quiz  
3. Receive stock recommendations (ML + Gemini)  
4. View explanation summaries  
5. Simulate or trade manually  
6. *(Stretch)* Enable Gemini voice insights  

---

## 📊 Success Metrics

✅ Chrome extension collects financial data and predicts locally  
✅ Gemini generates reasoning for ≥3 stock recommendations  
✅ Clear explanations improve user confidence  
✅ Offline mock data supported  
⭐ Stretch: Wealthsimple or voice integration  

---

## 🧩 24-Hour Development Plan

| Time | Task | Owner |
|------|
