# ZEULE — Zero-Effort Ultimate Launch Engine
## Project Status & Context Document

**Client:** Daniel Mendoza
**Developer:** Mehroz Muneer
**Budget:** $825 USD
**Deadline:** March 3, 2026
**Repo:** https://github.com/MuhammadMehroz786/Zelu.git
**Deployment Target:** Railway
**Meetings:** Every 2 days with Daniel

---

## What Is ZEULE?

ZEULE is an AI-powered system that automates the entire digital product creation pipeline — from finding trending niches to launching Meta Ads campaigns. It takes a niche/topic and runs it through 8 phases to produce a complete sellable digital product (ebook/guide/course) with a live funnel and ad creatives.

**Target output:** 15 complete digital products per day.

---

## The 8-Phase Pipeline

| Phase | Agent | What It Does |
|-------|-------|-------------|
| 1 | Trend Discovery | Finds trending topics using Google Trends (SerpAPI), Reddit, Hotmart marketplace signals. AI scores each trend for digital product potential. |
| 2 | Niche Validation | Validates demand using Meta Ad Library (competitor ads), Hotmart (existing products), and keyword data. Returns green/red light with confidence score. |
| 3 | Audience & Pain Points | Builds buyer persona using People Also Ask, Reddit discussions, Perplexity research. Extracts top pain points ranked by intensity. |
| 4 | Product Structure | Creates master blueprint: main product (8-12 chapters) + Bonus 1 + Bonus 2 + Order Bump + Upsell. Each product is independent but complementary. |
| 5 | Content Writing | Claude writes chapter-by-chapter with custom author style. AI Review Agent checks for AI artifacts, quality, and actionability. Each bonus/upsell = separate file. |
| 6 | Visual Design | Ideogram generates book covers with text. Gamma formats content into professional PDFs. |
| 7 | Funnel & Copy | Claude generates landing page copy (13 sections), 7-email sequence, 4 ad copy variations (pain/curiosity/authority/contrarian hooks). Stripe product created. GHL workflow set up. |
| 8 | Campaign Launch | Ideogram generates ad creative images (4 variations x 3 formats = 12 images). Bannerbear applies branded templates. Meta Ads campaign created in PAUSED state. |

---

## Tech Stack

- **Backend:** Flask (Python), Celery + Redis (task queue), PostgreSQL
- **AI:** OpenAI GPT-4o (analysis/structuring), Claude (content writing), Perplexity (research)
- **Research APIs:** SerpAPI (Google Trends, autocomplete, People Also Ask), Reddit API, Meta Ad Library API, Hotmart API
- **Design:** Ideogram (covers + ad images), Bannerbear (branded templates), Gamma (PDF formatting)
- **Platforms:** GoHighLevel (CRM, email automation, funnels), Meta Ads API (campaigns), Stripe (payments)
- **Hosting:** Railway (Docker deployment)

---

## Key Architecture Decisions

### No SEMrush / No Exploding Topics
Both are too expensive for API access ($549/mo and $1000+/mo respectively). Instead, we built a custom Trend Discovery Engine combining:
- **Google Trends via SerpAPI** (same data source Exploding Topics scrapes from) — already paying $75/mo
- **Google Autocomplete & People Also Ask via SerpAPI** (same data as Answer The Public) — included
- **Reddit API** (real discussions, emerging communities) — free
- **Meta Ad Library API** (what competitors are spending money on) — free
- **Hotmart Marketplace** (validated demand, existing products) — already have access
- **LLM scoring** — GPT-4o analyzes all signals and scores trends specifically for digital info-product potential

This saves ~$1,500/month and is actually better tuned for Daniel's use case.

### No AdCreative.ai
Download cap (100/month) doesn't work for 15 products/day volume. Replaced with:
- **Ideogram API** (~$0.03/image) for ad creative images — no download cap, scales with volume
- **Bannerbear** ($149/mo, 10,000 credits) for branded template overlays

### Funnel Creation
- **GHL (GoHighLevel)** replaced Systeme.io for scalability
- GHL API is limited for programmatic funnel page creation
- Current approach: system generates ALL copy and assets, GHL handles CRM + email workflows via API
- **Funnel page automation options discussed but deferred:**
  - Option 1: GHL Snapshots + Custom Values (clone template funnels, inject content via API)
  - Option 2: Custom HTML funnels deployed to Railway (fully automated)
  - Option 3: Hybrid — custom HTML pages + GHL for CRM/emails
  - Daniel wants to explore full automation — revisit after MVP

### Human-in-the-Loop
- Toggle-based system per phase (ON = pause for review, OFF = auto-advance)
- All toggles start ON while testing
- Phase 7 (funnel) and Phase 8 (campaign launch) always require human review
- Admin panel lets Daniel approve, reject, or edit outputs at each gate

### Learning Layer
- Every pipeline run logs: niche, prompts used, outputs, human feedback (approve/reject/edit)
- When starting a new product in a similar niche, system queries past successes and injects them into prompts
- Meta Ads performance syncs hourly → back-fills performance scores on learning logs
- Over time: system learns which trend signals, headlines, hooks, and structures convert best per niche

### Prompt Management
- All prompts stored in database with versioning
- Admin panel allows editing prompts directly
- Each edit creates a new version (history preserved)
- "Test Prompt" feature sends prompt with sample variables and shows AI response
- Default prompts loaded from YAML config files on seed

---

## What's DONE (Completed)

### Infrastructure
- [x] `Dockerfile` — Python 3.12 slim image
- [x] `docker-compose.yml` — Flask web, Celery worker, Celery beat, PostgreSQL 16, Redis 7
- [x] `requirements.txt` — all dependencies pinned
- [x] `.env.example` — all environment variables documented
- [x] `.gitignore` — Python, env, assets excluded
- [x] `config/settings.py` — centralized settings from env vars

### Database Models (8 tables)
- [x] `pipeline_runs` — pipeline lifecycle tracking
- [x] `products` — product records (main, bonus, upsell, order_bump)
- [x] `phase_results` — output per phase with status, duration, trace_id
- [x] `prompt_templates` — versioned editable prompts
- [x] `approvals` — human review records (pending/approved/rejected/edited)
- [x] `phase_toggles` — per-phase approval toggle settings
- [x] `learning_logs` — feedback + performance tracking
- [x] `ad_performance` — Meta Ads metrics per campaign/ad

### Orchestrator
- [x] `engine.py` — pipeline coordinator, phase execution, auto-advance logic
- [x] `state.py` — state machine with valid transitions for pipeline and phase statuses
- [x] `gates.py` — approval gate creation, resolution, learning log integration

### AI Agents (9 agents)
- [x] `base.py` — shared logic: prompt loading, LLM calls, JSON parsing, learning context retrieval
- [x] `trend_discovery.py` — Phase 1: gathers signals from SerpAPI + Reddit + Hotmart, LLM analysis
- [x] `niche_validator.py` — Phase 2: Meta Ad Library + Hotmart + keyword validation
- [x] `audience_profiler.py` — Phase 3: search questions + Reddit + Perplexity research, builds buyer persona
- [x] `product_architect.py` — Phase 4: creates blueprint, saves Product records to DB
- [x] `content_writer.py` — Phase 5: chapter-by-chapter with Claude, AI review agent, updates Product records
- [x] `designer.py` — Phase 6: Ideogram covers + Gamma PDFs, updates Product assets
- [x] `funnel_builder.py` — Phase 7: landing page copy + email sequence + ad copy + Stripe + GHL
- [x] `campaign_launcher.py` — Phase 8: Ideogram creatives + Bannerbear templates + Meta Ads campaign
- [x] `qa_reviewer.py` — cross-phase quality checker (content, copy, brand consistency)

### API Integration Clients (13 clients)
- [x] `openai_client.py` — GPT-4o with JSON mode support
- [x] `anthropic_client.py` — Claude Sonnet for content writing
- [x] `perplexity_client.py` — AI-powered research
- [x] `serpapi_client.py` — Google Trends, autocomplete, People Also Ask, keyword data
- [x] `reddit_client.py` — trending posts, comments, subreddit search
- [x] `meta_adlibrary.py` — competitor ad search
- [x] `meta_ads.py` — campaign + ad set + ad creation, performance insights
- [x] `hotmart_client.py` — marketplace search with OAuth
- [x] `sparktoro_client.py` — audience intelligence (placeholder, needs API access from sales)
- [x] `ideogram_client.py` — image generation with aspect ratio + style control
- [x] `bannerbear_client.py` — template-based image generation with polling
- [x] `gamma_client.py` — document/PDF generation
- [x] `ghl_client.py` — contacts, tags, pipeline creation, workflow setup
- [x] `stripe_client.py` — product + price creation, checkout sessions

### REST API Routes
- [x] `pipeline.py` — CRUD pipelines, start/stop, stats dashboard
- [x] `prompts.py` — list/create/update/test prompts, version history
- [x] `approvals.py` — list pending, get details, approve/reject/edit (triggers pipeline resume)
- [x] `analytics.py` — learning logs, ad performance, dashboard stats, toggle management

### Celery Workers
- [x] `celery_app.py` — broker config, beat schedule (hourly ad sync)
- [x] `tasks.py` — run_pipeline, run_phase, resume_after_approval, sync_ad_performance

### Prompt Templates (7 YAML files)
- [x] `trend_discovery.yaml` — analyze_trends, score_trend
- [x] `niche_validation.yaml` — validate_niche, analyze_competitors
- [x] `audience_profiling.yaml` — build_audience_profile, extract_pain_points
- [x] `product_structure.yaml` — create_blueprint, improve_from_competitors
- [x] `content_writing.yaml` — write_chapter, write_bonus, review_content
- [x] `marketing_copy.yaml` — generate_landing_page, generate_email_sequence, generate_ad_copy
- [x] `ad_creative.yaml` — ideogram_prompt, bannerbear_template_config

### Services
- [x] `learning_service.py` — niche insights, ad performance sync, score back-filling
- [x] `trend_service.py` — trend signal scoring and ranking
- [x] `content_service.py` — content chunking and assembly
- [x] `creative_service.py` — creative brief building, cost estimation

### Utilities
- [x] `logger.py` — structured logging with structlog (JSON output)
- [x] `retry.py` — exponential backoff retry decorator using tenacity
- [x] `file_manager.py` — asset directory management, JSON/text file I/O

### Other
- [x] `seed.py` — populates database with default phase toggles + prompt templates from YAML

---

## What's LEFT (TODO)

### High Priority
- [ ] **Frontend Admin Panel** — React + Tailwind + shadcn/ui dashboard (Gemini prompt is ready, see below)
- [ ] **Connect real API keys** — get credentials from Daniel, fill .env, test each integration
- [ ] **End-to-end testing** — run a complete pipeline with a real niche, fix any integration issues
- [ ] **Deploy to Railway** — set up services (web, worker, beat, PostgreSQL, Redis)
- [ ] **Fine-tune prompts** — work with Daniel to optimize prompts for his methodology and writing style

### Medium Priority
- [ ] **GHL funnel automation** — deep-dive into GHL API for programmatic funnel creation. Daniel wants maximum automation here. Explore Snapshots + Custom Values approach or custom HTML funnels.
- [ ] **Translation pipeline** — Daniel may need Spanish translations. Add a translation step after content writing.
- [ ] **Google Drive integration** — save outputs to Google Drive (mentioned in proposal)
- [ ] **Alembic migrations setup** — proper database migration management (currently using db.create_all())

### Lower Priority
- [ ] **Parallel pipeline execution** — currently sequential, scale to run multiple products concurrently
- [ ] **A/B testing integration** — track which ad variations win and feed back to learning layer
- [ ] **Webhook endpoints** — Stripe webhooks for purchase tracking, GHL webhooks for contact events
- [ ] **Rate limit management** — implement per-API rate limiting to avoid bans
- [ ] **Asset download/packaging** — bundle all product assets into a downloadable "Launch Package" ZIP

---

## Frontend — Gemini Prompt

Use this prompt in Gemini to generate the admin panel:

> Build me a complete React + Tailwind CSS + shadcn/ui admin dashboard for an AI automation system called ZEULE. It connects to a Flask REST API backend. Here's exactly what I need:
>
> **Pages:**
>
> **1. Dashboard (home)** — Summary cards: total products created, active pipelines, products awaiting approval, today's output count. Recent pipeline runs list showing: topic/niche, current phase, status (running/paused/completed/failed), timestamp. Quick action button: "Start New Product Pipeline"
>
> **2. Pipeline View (single pipeline run)** — Visual stepper/progress bar showing all 8 phases: Trend Discovery → Niche Validation → Audience Profiling → Product Structure → Content Writing → Visual Design → Funnel & Copy → Campaign Launch. Each phase shows: status, duration, expandable output preview. If "waiting approval": show output with Approve / Reject / Edit buttons. Edit opens modal to modify output before approving.
>
> **3. Products List** — Table with columns: name, niche, type (main/bonus/upsell), status, created date, actions. Filter by status, niche, date. Click product to see all assets with download links.
>
> **4. Prompt Editor** — List of prompt templates grouped by phase. Each shows: name, agent, version, last updated. Click to edit: full-screen editor with syntax highlighting for {{variables}}. Save creates new version (history visible). "Test Prompt" button.
>
> **5. Phase Toggles / Settings** — Toggle switches per phase: "Require human approval" and "Enable/disable phase". Save button.
>
> **6. Learning & Analytics** — Learning logs table with filters. Charts: products over time, approval rate by phase, top niches. Meta Ads performance table: campaigns, CTR, ROAS, spend.
>
> **7. Activity Log** — Real-time log stream with filters by pipeline, phase, severity.
>
> **API Endpoints:** Base URL configurable. GET/POST /api/pipelines, GET /api/pipelines/:id, POST /api/pipelines/:id/phases/:phase/approve, GET/PUT /api/prompts, GET/PUT /api/settings/toggles, GET /api/products, GET /api/analytics/learning, GET /api/analytics/ads, GET /api/logs
>
> **Design:** Dark theme default with light toggle. Sidebar nav. Fully responsive. Loading states. Toast notifications. Tech: React 18, React Router, Tailwind CSS, shadcn/ui, axios, recharts, lucide-react.

---

## API Endpoints Reference

### Pipelines
- `GET /api/pipelines/` — list all pipelines (filter by status, paginated)
- `POST /api/pipelines/` — create new pipeline `{"niche": "...", "auto_start": true}`
- `GET /api/pipelines/<id>` — get pipeline with all phases and products
- `POST /api/pipelines/<id>/start` — start/resume pipeline (Celery task)
- `POST /api/pipelines/<id>/stop` — stop pipeline
- `GET /api/pipelines/stats` — dashboard summary stats

### Prompts
- `GET /api/prompts/` — list all active prompts grouped by phase
- `GET /api/prompts/<id>` — get single prompt
- `PUT /api/prompts/<id>` — update prompt (creates new version)
- `POST /api/prompts/` — create new prompt
- `POST /api/prompts/<id>/test` — test prompt with sample variables
- `GET /api/prompts/<id>/history` — version history

### Approvals
- `GET /api/approvals/pending` — list pending approvals
- `GET /api/approvals/<id>` — get approval with full phase output
- `POST /api/approvals/<id>/resolve` — approve/reject/edit `{"decision": "approved"}`

### Analytics
- `GET /api/analytics/learning` — learning logs (filter by niche, phase, feedback)
- `GET /api/analytics/ads` — ad performance data
- `GET /api/analytics/dashboard` — full dashboard stats
- `GET /api/analytics/toggles` — get phase toggle settings
- `PUT /api/analytics/toggles` — update toggle settings

---

## What Daniel Needs to Provide

1. **API keys** for: OpenAI, Claude/Anthropic, Perplexity, SerpAPI, Ideogram, Bannerbear, Gamma, GoHighLevel, Meta Ads, Hotmart, Stripe
2. **Author style guide** — tone, writing style examples for content generation
3. **Brand config** — colors, fonts, visual guidelines
4. **Sample niche** — first niche to test end-to-end
5. **GHL access** — so we can explore funnel automation capabilities

---

## Key Files to Know

| File | Purpose |
|------|---------|
| `app/orchestrator/engine.py` | Main pipeline coordinator — this is the brain |
| `app/agents/base.py` | Shared agent logic — prompt loading, LLM calls, learning context |
| `app/orchestrator/gates.py` | Approval system — create/resolve gates, log to learning |
| `config/prompts/*.yaml` | Default prompt templates — these get seeded to DB |
| `app/api/pipeline.py` | REST API for starting/managing pipelines |
| `worker/tasks.py` | Celery tasks that run pipeline phases async |
| `seed.py` | Run this to populate DB with defaults |
| `docker-compose.yml` | Full stack: Flask + Celery + PostgreSQL + Redis |

---

## How to Run

```bash
# 1. Copy env and fill in API keys
cp .env.example .env

# 2. Start all services
docker-compose up --build

# 3. Seed the database
docker-compose exec web python seed.py

# 4. Create your first pipeline
curl -X POST http://localhost:5000/api/pipelines/ \
  -H "Content-Type: application/json" \
  -d '{"niche": "keto diet for beginners", "auto_start": true}'

# 5. Check status
curl http://localhost:5000/api/pipelines/stats
```

---

*Last updated: February 14, 2026*
