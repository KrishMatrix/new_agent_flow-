# Agnes — AI Supply Chain Manager 🏭

> **Spherecast Hackathon Project**
> A multi-agent AI system for e-commerce supply chain management, featuring demand forecasting, anomaly detection, and inventory optimization — all through a Mario-style animated chat interface.

---

## 🎮 Demo Preview

Agnes features three specialized pixel-art AI agents:

| Agent | Name | Role | Color |
|-------|------|------|-------|
| 📊 | **Forecaster** | "The Strategist" — Predicts demand using historical sales data | Blue `#3b82f6` |
| 🔍 | **Scout** | "The Lookout" — Detects anomalies in sales, returns, and channels | Red `#ef4444` |
| ⚙️ | **Optimizer** | "The Builder" — Calculates reorder points, safety stock, EOQ | Green `#10b981` |

---

## 🏗️ Architecture

```
User (E-commerce Manager)
        │
        ▼
┌─────────────────────┐
│   Chat Interface     │  ← Mario-style animated UI (React + Vite)
│   (React Frontend)   │
└────────┬────────────┘
         │ REST API (POST /api/chat)
         ▼
┌─────────────────────┐
│   Agnes Router       │  ← Central orchestrator (intent classification)
│   (FastAPI Backend)  │     Routes queries to the right agent
└────┬───┬───┬────────┘
     │   │   │
     ▼   ▼   ▼
┌─────────┐ ┌──────┐ ┌──────────┐
│Forecaster│ │Scout │ │Optimizer │
│  Agent   │ │Agent │ │  Agent   │
└────┬─────┘ └──┬───┘ └────┬─────┘
     │          │           │
     ▼          ▼           ▼
┌─────────┐ ┌────────┐ ┌─────────┐
│ Demand  │ │Anomaly │ │Reorder  │
│Forecast │ │Detector│ │Calculator│
│  Tool   │ │  Tool  │ │  Tool   │
└─────────┘ └────────┘ └─────────┘
```

---

## 📁 Project Structure

```
agnes/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variable template
│
├── backend/                           # Python FastAPI Backend
│   ├── main.py                        # FastAPI app entry point (endpoints: /api/chat, /api/dashboard, /api/inventory, /api/health)
│   ├── config.py                      # Environment variables & settings (pydantic-settings)
│   ├── router.py                      # Agnes Router — central orchestrator (intent classification → agent routing)
│   ├── generate_data.py               # Script to generate realistic 90-day sales history
│   │
│   ├── agents/                        # AI Agents
│   │   ├── __init__.py
│   │   ├── base_agent.py              # Abstract base class (shared interface & response builder)
│   │   ├── forecaster.py              # Demand prediction agent (exponential smoothing + Claude LLM)
│   │   ├── scout.py                   # Anomaly detection agent (Z-score + IQR analysis)
│   │   └── optimizer.py               # Stock optimization agent (EOQ + safety stock formulas)
│   │
│   ├── tools/                         # Analytical Tools (called by agents)
│   │   ├── __init__.py
│   │   ├── data_loader.py             # CSV data ingestion + pandas DataFrames + SKU lookup
│   │   ├── demand_forecast.py         # Exponential smoothing, moving averages, trend detection
│   │   ├── anomaly_detector.py        # Z-score spike/drop detection, return rate monitoring, channel mismatches
│   │   └── reorder_calculator.py      # EOQ formula, safety stock (95% service level), days-of-stock
│   │
│   ├── models/                        # Pydantic Data Models
│   │   ├── __init__.py
│   │   ├── product.py                 # Product/SKU schema
│   │   ├── inventory.py               # Inventory level schema
│   │   ├── forecast.py                # Forecast output schema
│   │   └── alert.py                   # Anomaly alert schema
│   │
│   └── data/                          # Mock CSV Data (20 SKUs, 90 days, 3 channels)
│       ├── products.csv               # 20 SKUs with name, category, price, supplier, lead time
│       ├── sales_history.csv          # 1,800 rows — daily sales per SKU with seasonality & trends
│       ├── inventory_levels.csv       # Current stock levels (includes deliberately low-stock items)
│       └── channels.csv              # Multi-channel data (Amazon, Shopify, DTC) with anomalies
│
├── frontend/                          # React + Vite Frontend
│   ├── index.html                     # Entry HTML with SEO meta tags
│   ├── package.json                   # Node dependencies (react, recharts, axios)
│   ├── vite.config.js                 # Vite configuration
│   │
│   ├── public/
│   │   └── assets/                    # Game Assets
│   │       ├── forecaster.png         # Pixel-art Forecaster character sprite
│   │       ├── scout.png              # Pixel-art Scout character sprite
│   │       ├── optimizer.png          # Pixel-art Optimizer character sprite
│   │       └── background.png         # Pixel-art warehouse scene background
│   │
│   └── src/
│       ├── main.jsx                   # React entry point
│       ├── App.jsx                    # Root component (layout: AgentScene + Chat + Dashboard)
│       │
│       ├── components/
│       │   ├── ChatWindow.jsx         # Main chat interface (welcome screen, messages, input bar, quick actions)
│       │   ├── MessageBubble.jsx      # Individual message with markdown formatting, inline charts/tables
│       │   ├── AgentAvatar.jsx        # Agent avatar with pixel-art sprite or emoji fallback
│       │   ├── AgentScene.jsx         # Mario-style scene with walking agents & speech bubbles
│       │   ├── DashboardPanel.jsx     # Side panel: KPI cards, sales trend chart, top products, low stock alerts
│       │   ├── ForecastChart.jsx      # Recharts area chart for demand forecasts with confidence intervals
│       │   └── InventoryTable.jsx     # Flexible table for metrics and tabular data with severity badges
│       │
│       ├── hooks/
│       │   ├── useChat.js             # Chat state management + API calls to backend
│       │   └── useAgentAnimation.js   # Agent sprite animation state machine
│       │
│       └── styles/
│           ├── global.css             # Design system: dark theme, CSS variables, animations, glassmorphism
│           ├── chat.css               # Chat UI: message bubbles, typing indicator, input bar, welcome screen
│           └── agents.css             # Agent scene: sprite animations, dashboard panel, KPI cards, tables
│
└── docs/
    ├── agent_prompts.md               # System prompts for all agents
    └── pitch_script.md                # Hackathon presentation script & demo flow
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (for backend)
- **Node.js 18+** (for frontend)
- **Anthropic API Key** (optional — app works without it in fallback mode)

### 1. Clone & Setup Environment Variables

```bash
cd agnes
cp .env.example backend/.env
```

Edit `backend/.env` and add your Anthropic API key (optional):
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

> **Note:** The app works without an API key! Agents will use template-based responses instead of Claude LLM responses.

### 2. Start the Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install -r ../requirements.txt

# Generate the 90-day sales history data
python generate_data.py

# Start the FastAPI server
uvicorn main:app --reload --port 8000
```

The backend will be running at **http://localhost:8000**

### 3. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will be running at **http://localhost:5173**

### 4. Open the App

Navigate to **http://localhost:5173** in your browser. You'll see the Agnes chat interface with:
- 🎮 Mario-style agent scene at the top
- 💬 Chat window in the center
- 📊 Dashboard panel on the right

---

## 💬 Example Queries

### Forecaster (📊 Demand Predictions)
```
"What's the demand forecast for blue sneakers next week?"
"Forecast my top selling products for the next 30 days"
"Predict sales for SKU001 next month"
```

### Scout (🔍 Anomaly Detection)
```
"Are there any anomalies in our sales data?"
"Check for issues with red t-shirts"
"Scan for return rate problems"
```

### Optimizer (⚙️ Stock Optimization)
```
"When should I reorder red t-shirts?"
"Give me a full stock optimization report"
"How many days of stock do we have for SKU006?"
```

### General
```
"Hello" / "Help" / "What can you do?"
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/chat` | Send a message to Agnes (body: `{"message": "..."}`) |
| `GET` | `/api/dashboard` | Get KPI summary data (total SKUs, stock, daily sales, trends) |
| `GET` | `/api/inventory` | Get full inventory table with stock status |

### Chat API Example

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "forecast for blue sneakers next week"}'
```

**Response:**
```json
{
  "agent": "Forecaster",
  "agent_color": "#3b82f6",
  "agent_icon": "📊",
  "message": "📊 **Forecast for Blue Running Sneakers** (SKU001)...",
  "data": { ... },
  "chart_type": "forecast",
  "chart_data": [ ... ]
}
```

---

## 🧠 How the Agents Work

### Intent Classification (Agnes Router)

The router classifies every message using either:
1. **Claude LLM** (if API key is set) — sends the message to Claude with a classification prompt
2. **Keyword matching** (fallback) — scores the message against keyword lists for each category

Categories: `FORECAST` → Forecaster | `ANOMALY` → Scout | `OPTIMIZE` → Optimizer | `GENERAL` → Agnes

### Forecaster — Demand Prediction

1. Extracts SKU from user message (by SKU ID, product name, or category)
2. Loads 90 days of sales history from CSV
3. Runs **exponential smoothing** (α=0.3) + **linear trend** detection
4. Generates forecast with **95% confidence intervals**
5. Detects seasonal patterns (7-day MA vs 30-day MA)
6. Returns forecast data + chart data for inline visualization

### Scout — Anomaly Detection

1. Runs 4 types of anomaly checks across all SKUs:
   - **Sales spikes/drops** — Z-score analysis (threshold: ±2.5σ)
   - **Return rate anomalies** — Flags when recent rate > 2.5× average
   - **Slow-moving inventory** — Stock > 90 days at current sell rate
   - **Channel mismatches** — One channel > 2.5× others
2. Ranks alerts by severity: `critical` > `high` > `medium` > `low`
3. Returns alerts table for inline display

### Optimizer — Stock Optimization

1. Calculates for each SKU:
   - **Days of stock remaining** = on_hand ÷ avg_daily_demand
   - **Safety stock** = 1.65 × σ × √(lead_time) (95% service level)
   - **Reorder point** = avg_demand × lead_time + safety_stock
   - **EOQ** = √(2 × annual_demand × order_cost ÷ holding_cost)
2. Assesses risk: `critical` (stock < lead time) > `high` > `medium` > `low`
3. Returns specific reorder quantities and deadlines

---

## 🎨 Frontend Features

- **Dark Theme** — Premium dark UI with glassmorphism effects
- **Mario-style Agent Scene** — Pixel-art characters walk in when responding
- **Inline Charts** — Recharts area charts with gradient fills for forecasts
- **Inline Tables** — Severity-badged data tables for anomaly alerts
- **KPI Dashboard** — Real-time metrics panel (total SKUs, stock levels, trends)
- **Quick Actions** — One-click prompt chips for common queries
- **Typing Indicator** — Animated dots while agents process
- **Responsive Messages** — Markdown-formatted responses with bold, italic, lists

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React 19 + Vite 8 | UI framework & dev server |
| Styling | Vanilla CSS | Dark theme, animations, glassmorphism |
| Charts | Recharts | Inline forecast charts & dashboard trends |
| HTTP Client | Axios | Frontend → Backend API calls |
| Backend | Python FastAPI | REST API server |
| LLM | Claude (Anthropic) | Natural language responses (optional) |
| Forecasting | statsmodels + pandas + numpy | Exponential smoothing, moving averages |
| Data Models | Pydantic | Request/response validation |
| Data | CSV mock data | 20 SKUs × 90 days × 3 channels |

---

## 📋 Mock Data Summary

| File | Records | Description |
|------|---------|-------------|
| `products.csv` | 20 SKUs | Name, category, price ($12.99–$129.99), supplier, lead time (3–8 days) |
| `sales_history.csv` | 1,800 rows | 90 days of daily sales per SKU with weekday/weekend patterns, monthly trends, and March seasonality |
| `inventory_levels.csv` | 20 rows | Current stock with deliberately low items (SKU002: 18 units, SKU006: 5 units, SKU012: 8 units) |
| `channels.csv` | 40 rows | Amazon, Shopify, DTC channel splits with return anomalies for SKU002 |

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend won't start | Make sure you're in the venv: `source venv/bin/activate` |
| "Module not found" errors | Run `pip install -r ../requirements.txt` from `/backend` |
| Frontend shows connection error | Make sure backend is running on port 8000 |
| No LLM responses | App works without API key — uses template responses. Add key to `.env` for Claude responses |
| Sales data missing | Run `python generate_data.py` from `/backend` |

---

## 📜 License

Built for the Spherecast Hackathon. MIT License.
