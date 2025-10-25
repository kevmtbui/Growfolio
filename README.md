# Growfolio

### Chrome Extension · AI-Powered Financial Advisor

Growfolio helps young investors make smarter, stress-free financial decisions using AI insights, machine learning predictions, and the Gemini API — all within a simple Chrome extension.

---

## Overview

**Problem**  
Financial literacy and investing confidence are low among young adults. Most robo-advisors are complex or paywalled.

**Solution**  
Growfolio bridges that gap by providing personalized stock recommendations, explanations, and trend insights powered by AI and ML. It enables users to grow wealth safely and confidently through an accessible Chrome extension.

---

## Goals and Objectives

- Simplify portfolio decision-making for new investors  
- Use the Gemini API to interpret user intent and explain recommendations  
- Integrate ML models to detect short-term stock trends and risk patterns  
- Encourage long-term, sustainable investing habits

---

## Target Users

- Primary: Students and young professionals new to investing  
- Secondary: Budget-conscious individuals seeking AI-assisted financial planning

---

## Core Features (MVP)

| Feature | Description | Priority |
|----------|--------------|----------|
| Smart Financial Intake | Collects income, rent, and spending data | High |
| Risk and Literacy Quiz | Determines user confidence and tolerance | High |
| AI Stock Recommender | Suggests stocks matched to user risk and goals | High |
| Decision Support Summaries | Explains why each stock was chosen | High |
| Manual Ticker Analysis | Lets users query any stock for AI insights | Medium |
| Chrome Extension UI | Dashboard for financial tools | High |
| Auto-Trading (Stretch) | Wealthsimple API integration | Low |

---

## AI and ML Integration

**Gemini API (LLM Layer)**  
- Understands user intent  
- Summarizes patterns and reasoning  
- Generates natural-language explanations  

**ML Model (Analytical Layer)**  
- Predicts short-term stock trends  
- Uses Random Forest or LSTM on open data (Yahoo Finance or Alpha Vantage)  
- Outputs confidence and volatility metrics  

**Example Output**  
“Given your moderate risk tolerance, AAPL shows stable growth with 78% confidence.  
Gemini explains: Apple’s cash flow resilience aligns with your goal to save safely over time.”

---

## Decision Support Logic

1. Collect user context (income, expenses, goals)  
2. Predict stock performance using the ML model  
3. Generate reasoning with the Gemini API  
4. Rank 3–5 stocks by confidence and risk match  
5. Allow the user to simulate or trade manually  

---

## Tech Stack

| Layer | Tools |
|--------|-------|
| Frontend | Chrome Extension (HTML/CSS/JS, optional React) |
| Backend | Python (FastAPI) or Node.js |
| ML Model | scikit-learn / TensorFlow Lite |
| AI Assistant | Google Gemini API |
| Data | Yahoo Finance / Alpha Vantage |
| Storage | LocalStorage / IndexedDB |
| Integration (Stretch) | Wealthsimple API |

---

## Hackathon Prize Fit

| Category | Qualification |
|-----------|----------------|
| Finance & Fintech | Personalized AI robo-trader |
| Personal Wellness | Promotes financial wellbeing |
| Best Use of Gemini API | Uses Gemini for reasoning and insights |
| DigitalOcean Gradient | Host ML model inference |
| Snowflake API | Store anonymized financial data |
| ElevenLabs Voice (Stretch) | Voice summaries of portfolio |

---

## User Flow

1. Install Growfolio Chrome extension  
2. Complete financial intake and quiz  
3. Receive stock recommendations (ML + Gemini)  
4. View explanation summaries  
5. Simulate or trade manually  
6. (Stretch) Enable voice insights  

---

## Success Metrics

- Chrome extension collects financial data and predicts locally  
- Gemini generates reasoning for at least three stock recommendations  
- Explanations improve user confidence  
- Works offline with mock data  
- Stretch: Wealthsimple or voice integration  

---

## 24-Hour Development Plan

| Time | Task | Owner |
|------|------|--------|
| 0–2 hrs | Wireframe and UI design | Frontend |
| 2–6 hrs | Chrome extension setup and local data | Frontend |
| 6–10 hrs | ML model training and stock API integration | Backend/ML |
| 10–16 hrs | Gemini API integration | AI Lead |
| 16–20 hrs | Connect layers and polish UI | Full stack |
| 20–24 hrs | Demo video and final documentation | All |

---

## Run Locally

```bash
# Clone the repository
git clone https://github.com/<your-org>/growfolio.git
cd growfolio

# Frontend
cd frontend
npm install
npm start

# Backend
cd backend
python main.py
