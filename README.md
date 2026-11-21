# Iron Claw 🦾

**Mobile-First Autonomous Agent Architecture**

A comprehensive monorepo system that orchestrates Android device automation, voice AI calls, job hunting, and personal productivity tasks through an intuitive web interface and Telegram bot.

---

## 🌟 Features

### Core Capabilities

| Feature | Description | Status |
|---------|-------------|--------|
| **🤖 AI Chat** | Natural language control of your Android device via chat interface | ✅ Active |
| **💼 Job Hunter** | Auto-parse resume and apply to jobs via mobile Chrome | ✅ Active |
| **⏰ Temporal Guardian** | Set alarms and calendar events via Android intents | ✅ Active |
| **📞 Active Interrupter** | Voice AI wake-up calls with cognitive verification | ✅ Active |
| **🗂️ Tab Manager** | Organize, merge, and manage Chrome tabs automatically | ✅ Active |
| **📱 Device Mirror** | Real-time screen streaming (WebRTC/MobileRun) | ✅ Active |
| **🤝 Human-in-the-Loop** | Smart intervention for CAPTCHAs and logins | ✅ Active |
| **💬 Telegram Bot** | Control everything via Telegram | ✅ Active |
| **🌍 i18n Support** | Multi-language interface (10+ languages) | ✅ Active |
| **🎨 Personalization** | AI-powered wallpaper extraction and setting | ✅ Active |
| **📅 Schedule Extractor** | OCR-based schedule extraction to calendar | ✅ Active |

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              WEB INTERFACE (Port 5173)                       │
│  React + TypeScript • Tailwind CSS • shadcn/ui • TanStack Query             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │   Sidebar    │  │  ChatArea    │  │ DeviceMirror │  │ CategoryPills    │ │
│  │  (Threads)   │  │  (Messages)  │  │(WebRTC/Cloud)│  │ (Action Groups)  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │ HTTP / WebSocket
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              GATEWAY (Port 8000)                             │
│                         FastAPI • DroidRun • MobileRun                       │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                         API ROUTERS                                     │ │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │ │
│  │  │  chat   │ │  jobs   │ │  alarms │ │   tabs  │ │  wake   │          │ │
│  │  │/api/chat│ │/api/v1/ │ │/api/v1/ │ │/api/v1/ │ │/api/v1/ │          │ │
│  │  │         │ │  jobs   │ │ alarms  │ │  tabs   │ │  wake   │          │ │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘          │ │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐                                  │ │
│  │  │  speech │ │mobilerun│ │  hitl   │                                  │ │
│  │  │/api/v1/ │ │/api/v1/ │ │/api/v1/ │                                  │ │
│  │  │  speech │ │mobilerun│ │  hitl   │                                  │ │
│  │  └─────────┘ └─────────┘ └─────────┘                                  │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                         SERVICE MODULES                                 │ │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │ │
│  │  │  JobHunterService│  │TemporalGuardian  │  │ VapiInterrupter  │      │ │
│  │  │  (Resume Parser) │  │ (Alarm/Calendar) │  │ (Voice Wake-up)  │      │ │
│  │  └──────────────────┘  └──────────────────┘  └──────────────────┘      │ │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │ │
│  │  │  TabManagerService│  │TelegramBotService│  │Personalization   │      │ │
│  │  │  (Chrome Tabs)   │  │  (HITL Notifier) │  │ (Wallpaper/Theme) │      │ │
│  │  └──────────────────┘  └──────────────────┘  └──────────────────┘      │ │
│  │  ┌──────────────────┐  ┌──────────────────┐                            │ │
│  │  │ ScheduleExtractor│  │   NanoBananaPro  │                            │ │
│  │  │ (OCR → Calendar) │  │ (AI Wallpaper)   │                            │ │
│  │  └──────────────────┘  └──────────────────┘                            │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                         CORE SERVICES                                   │ │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │ │
│  │  │ ExecutionService │  │   HITLService    │  │TabExecutionService│      │ │
│  │  │ (MobileRun/Droid)│  │ (Human-in-Loop)  │  │ (Chrome Control)  │      │ │
│  │  └──────────────────┘  └──────────────────┘  └──────────────────┘      │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                     ┌──────────────────┼──────────────────┐
                     ▼                  ▼                  ▼
┌───────────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  JOB HUNTER SERVICE   │ │  MIRROR SERVICE  │ │  ANDROID DEVICE  │
│    (Port 5123)        │ │ (Port 8080-8082) │ │  (ADB/MobileRun) │
│  Flask • MongoDB      │ │ WebRTC • MJPEG   │ │  Chrome • Apps   │
│  ┌──────────────────┐ │ │                  │ │                  │
│  │ ResumeParser     │ │ │  ┌──────────────┐│ │  ┌──────────────┐│
│  │ (PDF → Struct)   │ │ │  │ server.js    ││ │  │ Local ADB    ││
│  └──────────────────┘ │ │  │ (MJPEG 8080) ││ │  │   Device     ││
│  ┌──────────────────┐ │ │  └──────────────┘│ │  └──────────────┘│
│  │ JobApplicationOrchestrator              │ │  ┌──────────────┐│
│  │ (Apply Flow)     │ │ │  ┌──────────────┐│ │  │ MobileRun    ││
│  └──────────────────┘ │ │  │server-webrtc.││ │  │   Cloud      ││
│  ┌──────────────────┐ │ │  │js (WS 8082)  ││ │  │   API        ││
│  │ MongoDBManager   │ │ │  └──────────────┘│ │  └──────────────┘│
│  │ (Applications DB)│ │ └──────────────────┘ └──────────────────┘
│  └──────────────────┘ │
│  ┌──────────────────┐ │
│  │GoogleSheetsManager│
│  │ (Tracking Sheet) │ │
│  └──────────────────┘ │
└───────────────────────┘
```

---

## 📁 Project Structure

```
monorepo/
├── apps/
│   ├── gateway/                    # Main FastAPI gateway (Port 8000)
│   │   ├── src/ironclaw/
│   │   │   ├── main.py            # FastAPI entry point
│   │   │   ├── api/               # API route handlers
│   │   │   │   ├── chat.py        # Web chat interface
│   │   │   │   ├── jobs.py        # Job hunter endpoints
│   │   │   │   ├── alarms.py      # Alarm/calendar endpoints
│   │   │   │   ├── tabs.py        # Tab manager endpoints
│   │   │   │   ├── wake.py        # Voice wake-up endpoints
│   │   │   │   ├── hitl.py        # Human-in-the-loop endpoints
│   │   │   │   ├── speech.py      # Speech-to-text endpoints
│   │   │   │   ├── mobilerun.py   # MobileRun cloud integration
│   │   │   │   └── mobilerun_ws.py# MobileRun WebSocket
│   │   │   ├── agents/            # Agent implementations
│   │   │   │   ├── ironclaw_agent.py    # Main DroidRun wrapper
│   │   │   │   └── adb_connection.py    # ADB wrapper
│   │   │   ├── modules/           # Feature modules
│   │   │   │   ├── job_hunter.py        # Resume parsing & job search
│   │   │   │   ├── temporal_guardian.py # Alarm/calendar management
│   │   │   │   ├── tab_manager.py       # Chrome tab organization
│   │   │   │   ├── vapi_interrupter.py  # Voice AI wake-up calls
│   │   │   │   ├── telegram_bot.py      # Telegram bot integration
│   │   │   │   ├── personalization.py   # Wallpaper personalization
│   │   │   │   ├── schedule_extractor.py# OCR schedule extraction
│   │   │   │   └── nanobanana.py        # AI wallpaper extraction
│   │   │   ├── services/          # Core services
│   │   │   │   ├── execution_service.py     # MobileRun/DroidRun execution
│   │   │   │   ├── hitl_service.py          # Human-in-the-loop
│   │   │   │   └── tab_execution_service.py # Chrome tab execution
│   │   │   └── utils/             # Utilities
│   │   │       ├── config.py      # Configuration management
│   │   │       └── step_parser.py # Step parsing utilities
│   │   ├── config.yaml            # Gateway configuration
│   │   └── pyproject.toml         # Python dependencies
│   │
│   ├── job-hunter/                 # Standalone job hunter service (Port 5123)
│   │   ├── src/job_hunter/
│   │   │   ├── main.py            # CLI entry point
│   │   │   ├── app.py             # Flask web app
│   │   │   ├── orchestrator.py    # Job application orchestration
│   │   │   ├── resume_parser.py   # PDF resume parsing
│   │   │   ├── agent_factory.py   # MobileRun/DroidRun agent factory
│   │   │   ├── mobilerun_agent.py # MobileRun API client
│   │   │   ├── droidrun_backup.py # DroidRun fallback
│   │   │   ├── database.py        # MongoDB manager
│   │   │   ├── google_sheets.py   # Google Sheets integration
│   │   │   └── config.py          # Configuration
│   │   └── templates/index.html   # Web dashboard
│   │
│   ├── mirror-service/             # Screen streaming service (Port 8080-8082)
│   │   ├── server.js              # MJPEG streaming server
│   │   ├── server-webrtc.js       # WebRTC signaling server
│   │   └── server-h264-fmp4.js    # H264 streaming server
│   │
│   └── web/                        # React web interface (Port 5173)
│       ├── src/
│       │   ├── App.tsx            # Main app component
│       │   ├── pages/
│       │   │   ├── Index.tsx      # Main chat interface
│       │   │   └── NotFound.tsx   # 404 page
│       │   ├── components/
│       │   │   ├── ChatArea.tsx           # Chat message display
│       │   │   ├── ChatInput.tsx          # Message input with attachments
│       │   │   ├── Sidebar.tsx            # Thread sidebar
│       │   │   ├── CategoryPills.tsx      # Action category buttons
│       │   │   ├── EndpointActions.tsx    # Quick action buttons
│       │   │   ├── DeviceMirrorWebRTC.tsx # WebRTC device mirror
│       │   │   ├── DeviceMirrorCloud.tsx  # MobileRun cloud mirror
│       │   │   ├── DeviceMirrorMSE.tsx    # MSE-based streaming (unused)
│       │   │   ├── DeviceMirror.tsx       # Legacy MJPEG mirror (unused)
│       │   │   ├── LanguageSwitcher.tsx   # i18n language switcher
│       │   │   ├── SnowAnimation.tsx      # Visual effect
│       │   │   └── ui/                    # shadcn/ui components
│       │   ├── hooks/
│       │   │   ├── useLocalThreads.ts     # Thread state management
│       │   │   └── useAttachments.ts      # File attachment handling
│       │   ├── lib/
│       │   │   ├── api.ts         # API client
│       │   │   └── storage.ts     # LocalStorage utils
│       │   ├── types/
│       │   │   └── chat.ts        # TypeScript types
│       │   └── public/translations/       # i18n translation files
│       └── package.json
│
├── packages/                       # Shared packages
│   ├── shared/                     # Shared types & utilities
│   ├── adb-client/                 # ADB client library
│   ├── mobilerun-client/           # MobileRun API client
│   └── vapi-client/                # Vapi voice API client
│
├── config.yaml                     # Root configuration (Duolingo settings)
├── pyproject.toml                  # Root Python workspace config
├── start.sh                        # PM2 startup script
└── .env.example                    # Environment template
```

---

## 🔌 Services & Ports

| Service | Port | Description |
|---------|------|-------------|
| Gateway API | 8000 | Main FastAPI backend |
| Web Interface | 5173 | React development server |
| Job Hunter | 5123 | Flask job hunter service |
| Mirror Service (MJPEG) | 8080 | ADB screen streaming |
| Mirror Service (HTTP) | 8081 | Mirror HTTP endpoints |
| Mirror Service (WebRTC) | 8082 | WebRTC signaling |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- ADB (Android Debug Bridge) - optional for local mode
- Android device or [MobileRun](https://mobilerun.ai) cloud account

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd monorepo

# Install Python dependencies (using uv)
uv sync

# Install Node dependencies for web app
cd apps/web && pnpm install && cd ../..

# Install Node dependencies for mirror service
cd apps/mirror-service && npm install && cd ../..
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# Required:
# - GEMINI_API_KEY (for AI agent)
# - MOBILERUN_API_KEY (for cloud devices)
# Optional:
# - VAPI_API_KEY (for voice calls)
# - TELEGRAM_BOT_TOKEN (for Telegram bot)
# - MONGODB_URI (for job hunter persistence)
```

### Running Services

**Option 1: Using PM2 (Recommended)**
```bash
./start.sh
```

**Option 2: Manual Start**
```bash
# Terminal 1: Gateway
cd apps/gateway && uv run uvicorn ironclaw.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2: Job Hunter
cd apps/job-hunter && uv run python -m job_hunter.main web

# Terminal 3: Web Interface
cd apps/web && pnpm run dev

# Terminal 4: Mirror Service
cd apps/mirror-service && npm run start:webrtc
```

---

## 📊 Data Flow

### Chat Command Flow

```
User Input (Web)
       │
       ▼
┌──────────────┐
│  ChatArea    │
│  Component   │
└──────────────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│  api.chat()  │────▶│  /api/chat   │
│  (lib/api.ts)│     │  (chat.py)   │
└──────────────┘     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │IronClawAgent │
                     │create_agent() │
                     └──────────────┘
                            │
               ┌────────────┴────────────┐
               ▼                         ▼
        ┌──────────────┐          ┌──────────────┐
        │ MobileRun    │          │ DroidRun     │
        │ Cloud API    │          │ Local ADB    │
        └──────────────┘          └──────────────┘
               │                         │
               └─────────────┬───────────┘
                             ▼
                      ┌──────────────┐
                      │Android Device│
                      │  (Actions)   │
                      └──────────────┘
```

### Job Hunter Flow

```
Resume PDF
    │
    ▼
┌──────────────┐
│ResumeParser  │
│  (PyPDF2)    │
└──────────────┘
    │
    ▼
┌──────────────┐
│JobApplication│
│Orchestrator  │
└──────────────┘
    │
    ▼
┌──────────────┐     ┌──────────────┐
│ MobileRun    │────▶│ Chrome on    │
│ Agent        │     │ Android      │
└──────────────┘     └──────────────┘
    │                         │
    ▼                         ▼
┌──────────────┐     ┌──────────────┐
│ MongoDB      │     │ Job Portals  │
│ (Tracking)   │     │ (LinkedIn,   │
└──────────────┘     │ Indeed, etc) │
                     └──────────────┘
```

---

## 🔍 Dead/Unused Code Analysis

### Unused Components (Frontend)

| File | Status | Notes |
|------|--------|-------|
| [`DeviceMirror.tsx`](apps/web/src/components/DeviceMirror.tsx) | 🟡 Unused | Legacy MJPEG mirror, replaced by WebRTC/Cloud versions |
| [`DeviceMirrorMSE.tsx`](apps/web/src/components/DeviceMirrorMSE.tsx) | 🟡 Unused | MSE-based streaming, not actively used |
| [`DeviceMirrorSimple.tsx`](apps/web/src/components/DeviceMirrorSimple.tsx) | 🔴 Not Found | Referenced but doesn't exist |

### Unused Backend Code

| File/Module | Status | Notes |
|-------------|--------|-------|
| `config.yaml` (root) | 🟡 Stale | Contains only Duolingo settings, likely outdated |
| Debug logging in agents | 🟡 Excessive | Multiple DEBUG statements in production code |

### TODOs in Codebase

- **Resume parsing trigger** ([`chat.py:258`](apps/gateway/src/ironclaw/api/chat.py)) - TODO for resume upload handling
- **CAPTCHA handling** ([`orchestrator.py:307`](apps/job-hunter/src/job_hunter/orchestrator.py)) - TODO for CAPTCHA automation

---

## 🔧 Configuration

### Gateway Config (`apps/gateway/config.yaml`)

```yaml
# Agent Settings
agent:
  max_steps: 30
  reasoning: true
  after_sleep_action: 1.5

# Security - Allowed packages
safe_packages:
  - com.android.chrome
  - com.google.android.calendar
  - com.google.android.deskclock
  - com.google.android.apps.nexuslauncher
  - com.google.android.gm
  - com.android.documentsui

# Module Settings
alarm:
  default_label: "Iron Claw Reminder"
  skip_ui: true

vapi:
  voice_provider: "11labs"
  voice_id: "rachel"
  transcriber_provider: "deepgram"
  transcriber_model: "nova-2"
  max_call_duration: 300

job_hunter:
  max_applications_per_session: 5
  screenshot_interval: 2

tab_manager:
  max_tabs_to_close: 10
  default_days_old: 7
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ Yes | Google Gemini API key for AI agent |
| `MOBILERUN_API_KEY` | ✅ Yes | MobileRun cloud API key |
| `MOBILERUN_DEVICE_ID` | ⚠️ Conditional | Required for cloud mode |
| `VAPI_API_KEY` | ❌ No | Vapi API for voice calls |
| `VAPI_PHONE_NUMBER_ID` | ❌ No | Vapi phone number ID |
| `TELEGRAM_BOT_TOKEN` | ❌ No | Telegram bot token |
| `MONGODB_URI` | ❌ No | MongoDB connection string |
| `DEVICE_SERIAL` | ❌ No | ADB device serial (for local mode) |
| `USE_TCP` | ❌ No | Use TCP for ADB (default: true) |
| `USER_PHONE_NUMBER` | ❌ No | User's phone for wake-up calls |

---

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest apps/gateway/tests/test_hitl_service.py

# Run web tests
cd apps/web && pnpm test
```

---

## 📦 Technology Stack

### Backend
- **FastAPI** - Web framework
- **DroidRun** - Local Android automation
- **MobileRun** - Cloud Android automation
- **Google GenAI** - LLM integration
- **APScheduler** - Job scheduling
- **python-telegram-bot** - Telegram integration

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components
- **TanStack Query** - Data fetching
- **Lingo.dev** - i18n internationalization

### Services
- **Flask** - Job hunter web service
- **MongoDB** - Application tracking database
- **WebSocket** - Real-time communication
- **WebRTC** - Low-latency streaming

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is proprietary and confidential.

---

## 🆘 Troubleshooting

### Common Issues

**Gateway won't start:**
- Check if port 8000 is available
- Verify `.env` file exists with required API keys
- Run `uv sync` to ensure dependencies are installed

**Web interface can't connect to gateway:**
- Ensure gateway is running on port 8000
- Check CORS settings in [`main.py`](apps/gateway/src/ironclaw/main.py)
- Verify `VITE_API_URL` in web `.env`

**MobileRun connection fails:**
- Verify `MOBILERUN_API_KEY` is set correctly
- Check device ID is valid
- Review MobileRun dashboard for device status

**ADB device not found:**
- Run `adb devices` to check connection
- Enable USB debugging on Android device
- Try `adb tcpip 5555` for wireless debugging

---

## 🔗 External Services

| Service | Purpose | Documentation |
|---------|---------|---------------|
| Google Gemini | LLM for agent reasoning | [Gemini API](https://ai.google.dev/) |
| MobileRun | Cloud Android devices | [MobileRun](https://mobilerun.ai) |
| Vapi | Voice AI calls | [Vapi Docs](https://docs.vapi.ai/) |
| MongoDB | Database | [MongoDB](https://www.mongodb.com/) |
| Google Sheets | Application tracking | [Sheets API](https://developers.google.com/sheets) |

---

*Built with 🦾 by the Iron Claw team*
