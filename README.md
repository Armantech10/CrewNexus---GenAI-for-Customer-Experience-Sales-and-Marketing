# Unified GenAI Platform

A comprehensive AI-powered platform for Customer Experience, Sales Automation, and Marketing - built with FastAPI, Next.js, and multiple LLM integrations.

## 🚀 Features

### AI-Powered Agents
- **Sales Agent** - Lead qualification, product recommendations, payment processing
- **Marketing Agent** - Campaign management, cross-platform posting, content generation
- **Support Agent** - Customer service, ticket management, knowledge base

### Integrations
- **LLM Providers** - OpenAI GPT-4, Anthropic Claude (with mock fallback)
- **Payments** - Stripe payment intents, checkout sessions, webhooks
- **Web Search** - Exa AI semantic search with content extraction
- **Social Media** - Instagram, LinkedIn, Facebook posting and analytics
- **Calendar** - Event scheduling, availability finder, smart meeting booking
- **CRM** - Customer lookup, lead management, payment links

## 📁 Project Structure

```
unified-genai-platform/
├── backend/
│   ├── api/
│   │   ├── main.py              # FastAPI app entry
│   │   └── routers/             # API endpoints
│   │       ├── chat.py          # Chat endpoint
│   │       ├── marketing.py     # Campaign CRUD
│   │       ├── payments.py      # Stripe payments
│   │       ├── search.py        # Web search
│   │       ├── social.py        # Social media
│   │       └── calendar.py      # Scheduling
│   ├── agents/                  # AI agents
│   ├── services/                # Core services
│   │   ├── llm_service.py       # Multi-provider LLM
│   │   └── intent_detector.py   # Intent analysis
│   ├── tools/                   # External integrations
│   │   ├── stripe_payments.py
│   │   ├── web_search.py
│   │   ├── social_media.py
│   │   ├── calendar.py
│   │   ├── crm.py
│   │   └── knowledge_base.py
│   └── tests/                   # Pytest tests
├── frontend/
│   ├── app/dashboard/           # Next.js pages
│   ├── components/              # React components
│   ├── lib/api-client.ts        # API client
│   └── stores/                  # Zustand stores
└── specs.json                   # Project specification
```

## 🛠️ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
# Navigate to project
cd unified-genai-platform

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Start backend
python -m uvicorn backend.api.main:app --reload
```

Backend will be available at http://localhost:8000

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at http://localhost:3000

## ⚙️ Environment Variables

Create a `.env` file in the root directory:

```env
# LLM Providers (optional - mocks work without keys)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Payments (optional)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Search (optional)
EXA_API_KEY=...

# Database (optional)
REDIS_URL=redis://localhost:6379
POSTGRES_URL=postgresql://...
```

> **Note:** All integrations work in mock mode without API keys for testing.

## 📖 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/chat` | POST | Send message to AI agents |
| `/api/v1/marketing/campaigns` | GET/POST | Campaign CRUD |
| `/api/v1/payments/create-intent` | POST | Create payment |
| `/api/v1/search` | GET | Web search |
| `/api/v1/social/posts` | GET/POST | Social media posts |
| `/api/v1/calendar/events` | GET/POST | Calendar events |

## 🧪 Testing

```bash
# Run all tests
pytest backend/tests/ -v

# Run specific test file
pytest backend/tests/test_tools.py -v

# Run with coverage
pytest backend/tests/ --cov=backend
```

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   FastAPI       │
│   (Next.js)     │     │   Backend       │
└─────────────────┘     └────────┬────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
              ┌──────────┐ ┌──────────┐ ┌──────────┐
              │  Sales   │ │Marketing │ │ Support  │
              │  Agent   │ │  Agent   │ │  Agent   │
              └────┬─────┘ └────┬─────┘ └────┬─────┘
                   │            │            │
         ┌─────────┴────────────┴────────────┴─────────┐
         │                   Tools                      │
         ├──────────┬──────────┬──────────┬────────────┤
         │ Stripe   │   Exa    │  Social  │  Calendar  │
         │ Payments │  Search  │  Media   │ Scheduling │
         └──────────┴──────────┴──────────┴────────────┘
```

## 📝 License

MIT License - see LICENSE file for details.
