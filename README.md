# 🤖 Supply Chain Health Agent

> An agentic AI-powered supply chain diagnostic platform built on the **Anthropic Claude SDK** — assess the end-to-end health of any organisation's supply chain across 8 critical domains in under 60 seconds. Browser-based, no technical setup required.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Anthropic Claude](https://img.shields.io/badge/powered%20by-Anthropic%20Claude-purple.svg)](https://www.anthropic.com)
[![Streamlit](https://img.shields.io/badge/deployed%20on-Streamlit%20Cloud-FF4B4B.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🌐 Live App

**Try it now — no login, no setup, no installation required:**

👉 **[supply-chain-health-agent.streamlit.app](https://supply-chain-health-agent.streamlit.app)**

Open any browser, select your profile, and get a full supply chain assessment in under 60 seconds.

---

## 🆕 What's New — v4.1 (REWIRED + 2026 Update)

The latest release folds in McKinsey **REWIRED** principles and **2026** global supply chain trends ([PR #1](https://github.com/dwnjuguna/Supply-Chain-Health-Agent/pull/1)):

- **🌟 North Star intake** — a new opening question ("What does supply chain excellence look like for your organization in 2 years?") frames every recommendation against your stated vision.
- **🔍 Benchmark transparency** — every domain score is now reported with its world-class benchmark and source inline (e.g. *Demand: 64/100 — world-class 85, per Gartner*).
- **📈 2026 benchmarks** — all 8 domain benchmarks and trend notes refreshed to 2026, plus a cross-cutting **AI & Digital Adoption** standard (~70% of firms now report advanced/transformational AI adoption — *AI-as-operator*).
- **🌍 Geopolitical & sourcing footprint** — new intake questions on China-origin / rare-earth exposure and offshore vs nearshore vs reshore strategy, feeding the Risk and Procurement scores.
- **🛡️ Cyber resilience** — now scored and narrated as a named sub-dimension of the Risk domain, referencing 2026 AI-enabled attack vectors and digital supply chain vulnerabilities.
- **🐛 Wiring fixes** — the executive persona (strategic scenarios + 36-month roadmap) and cost-benefit analysis now correctly reach the assessment engine at runtime.

> Fully covered by a 17-test unit suite (see [Running Tests](#-running-tests)). No new runtime dependencies.

---

## ✨ What's New in v4.0

| Feature | v3.0 | v4.0 |
|---|---|---|
| Persona selection | Single experience | **5-persona landing screen** |
| User tracks | Analyst only | **Analyst, Executive, Consultant + 2 Coming Soon** |
| Phase 2 built | Not available | **SQLite memory, risk monitor, Slack, Jira, email** |
| Cross-session memory | Not available | **SQLite memory engine** |
| Proactive alerts | Not available | **Claude-powered risk monitor** |
| Slack integration | Not available | **Assessment push + risk alerts** |
| Jira integration | Not available | **Action plan to tickets** |
| Feature flags | Not available | **60+ features across 6 tiers** |

---

## 🎯 What It Does

The Supply Chain Health Agent uses Claude AI to evaluate your supply chain across **8 SCOR-aligned domains**, benchmark your performance against 2026 world-class standards, autonomously search for live market intelligence, and deliver a prioritised assessment — all in under 60 seconds.

#### 🆕 New in v4.1 (REWIRED + 2026)
- **North Star intake** — frames recommendations against your 2-year excellence vision
- **Benchmark transparency** — every score cites its world-class benchmark and source inline
- **Geopolitical & sourcing footprint** — China / rare-earth exposure and offshore vs nearshore vs reshore questions feed the Risk & Procurement scores
- **Cyber resilience** — scored as a named sub-dimension within the Risk domain

```
=======================================================
   SUPPLY CHAIN HEALTH AGENT  |  v4.1
   Powered by Anthropic Claude SDK
=======================================================

  Demand             [██████████████░░░░░░]  72/100  Good
  Procurement        [█████████████░░░░░░░]  65/100  Good
  Manufacturing      [███████████████░░░░░]  78/100  Good
  Inventory          [█████████████░░░░░░░]  68/100  Good
  Logistics          [██████████████░░░░░░]  71/100  Good
  Warehousing        [██████████████░░░░░░]  74/100  Good
  Risk               [███████████░░░░░░░░░]  58/100  Fair
  Sustainability     [████████████░░░░░░░░]  63/100  Good

  OVERALL SCORE                             69/100
=======================================================
```

---

## 👤 5 User Personas

Select your profile at the landing screen — the tool adapts the entire experience from that single choice.

| Persona | Track | What You Get |
|---|---|---|
| **📊 SC Manager / Analyst** | Practitioner | Deep KPI diagnostics, domain inputs, benchmarks, cost-benefit analysis |
| **🏢 CSCO / COO / VP SC** | Executive | Strategic scenarios, 36-month roadmap, board-ready summaries |
| **🎯 SC Consultant** | Consultant | Multi-client diagnostics, white-label reports, client intake forms |
| **⚙️ Enterprise Config** | Phase 2 | SSO, API access, custom branding, audit logs, on-premise |
| **🏛️ Government / Federal** | Phase 3 | FedRAMP, air-gap, GovCloud, classified deployment |

---

## 📋 4-Tab Results Structure

After every assessment, results are organised into four clean tabs:

| Tab | Contents |
|---|---|
| **📋 Diagnostic Report** | Executive Summary, Top Risks, Priority Recommendations |
| **🏷️ Domain Deep-Dive** | Domain Highlights + Visual Score Cards for all 8 domains |
| **📥 Export** | Download full assessment as a professional PDF report |
| **💬 Q&A** | Follow-up chat with context-aware responses referencing your scores |

---

## 📄 PDF Export

Every assessment can be downloaded as a professional multi-page PDF report including overall health score card, all domain scores with visual health bars, executive summary, top risks, domain highlights, and priority recommendations — ready to share with your team or board.

---

## 👤 Five User Tracks

Select your profile at the landing screen — the tool adapts everything from that single choice.

### 📊 SC Manager / Analyst Track ✅ Live
Built for practitioners who speak the KPI language.
- Deep domain diagnostics across all 8 SCOR domains
- Custom assessment mode — describe your org, get tailored scores
- Benchmark gaps vs 2026 Gartner Top 25 world-class thresholds
- Cost-benefit analysis with your real financial figures
- Follow-up Q&A with live web search access

### 🏢 CSCO / COO / VP Supply Chain Track ✅ Live
Built for leaders making investment and transformation decisions.
- Strategic scenario comparison — 3 named paths with trade-offs, investment ranges, and KPI targets
- 36-month phased maturity roadmap (Stabilise → Build → Lead)
- Board-ready language throughout — no jargon, impact-first framing
- Customisable orientation: growth-first vs cost-out vs balanced
- Financial context for dollar-sized scenario estimates

### 🎯 Supply Chain Consultant Track ✅ Live
Built for advisory professionals managing multiple client engagements.
- Multi-client diagnostic capability across all 11 verticals
- Client intake forms — shareable pre-assessment questionnaires
- White-label PDF reports with client branding
- Side-by-side client comparison and benchmarking
- Consultant-optimised output format for deliverables

### ⚙️ Enterprise Configuration *(Coming — Phase 2)*
Embed and configure the agent within your organisation's systems with custom branding, access controls, and compliance guardrails.
- SSO / SAML authentication and user management
- API access and webhook integrations
- Custom vertical definitions and branded outputs
- Audit logs, admin panel, and SLA guarantee
- On-premise deployment option

### 🏛️ Government / Federal Edition *(Coming — Phase 3)*
Purpose-built for federal agencies and defense contractors requiring the highest security standards.
- Air-gapped and GovCloud AWS deployment
- FedRAMP authorization pathway
- ITAR controls and FIPS 140-2 compliance
- Classified mode with dedicated infrastructure
- Federal SI partner model

---

## 🤖 Agentic Capabilities — Phase 1 (Live Now)

This is not just a chatbot. Claude takes autonomous multi-step actions during every assessment:

| Capability | What it does |
|---|---|
| **Live Web Search** | Autonomously searches for current benchmarks, freight rates, regulatory updates, and geopolitical risks during every assessment |
| **Auto Action Pack** | Generates a board summary, 90-day action plan, and risk watch list automatically — no prompt required |
| **Market Intelligence** | Dedicated parallel search surfaces the 5 most important supply chain signals for your vertical right now |
| **Agentic Q&A** | Follow-up questions can trigger live web searches for current data |

### Phase 2 — Built ✅
- 🧠 **Cross-session memory** — SQLite engine tracking org profiles, assessment history, KPI trends
- 🔔 **Proactive risk alerts** — Claude + web search scans for live risks, delivers via Slack and email
- 🔗 **Slack integration** — push full assessments, action plans, and risk watch lists to channels
- 🎫 **Jira integration** — parse 90-day action plan and create tracked tickets automatically
- 📧 **Email dispatcher** — branded HTML email reports with domain scores and risk alerts
- 🚦 **Feature flags** — 60+ features gated across 6 tiers without pricing in code

### Phase 3 Roadmap *(Coming)*
- 📋 **Intake forms** — 5-persona tailored client intake forms
- 🔌 **MCP server** — call assessments from Claude, ChatGPT, or any MCP-compatible agent
- 💳 **Stripe paywall** — hosted Pro and Team tier access
- 🏛️ **Government edition** — FedRAMP, air-gap, GovCloud infrastructure

---

## 📊 8 Health Domains Assessed

Each domain is scored 0–100 against explicit 2026 world-class thresholds.

| Domain | SCOR | Key KPIs | World-Class Target |
|---|---|---|---|
| Demand Planning & Forecasting | Plan | Forecast accuracy, bias, MAPE, S&OP maturity | FA ≥85–90%, MAPE <10% |
| Procurement & Sourcing | Source | Supplier OTD, spend under management, PPM | OTD ≥95%, <500 PPM |
| Manufacturing & Production | Make | OEE, first-pass yield, schedule adherence | OEE ≥85%, FPY ≥98% |
| Inventory Management | Plan/Deliver | Turns, stockout rate, E&O%, cash-to-cash | 8–12x turns, stockout <1% |
| Logistics & Transportation | Deliver | OTIF, freight cost %, perfect order rate | OTIF 95–98% |
| Warehousing & Fulfillment | Deliver | Order accuracy, utilisation, lines/hour | Accuracy ≥99.9% |
| Risk & Resilience | Enable | BCP coverage, TTR, supplier risk tiers, **cyber resilience** | BCP ≥95% of critical nodes |
| Sustainability & ESG | Enable | Scope 3 tracking, ESG audit coverage | Scope 3 ≥80% tracked |

**Score bands:**
| Score | Rating | What it means |
|---|---|---|
| 80–100 | 🟢 Excellent | World-class — at or above Gartner Top 25 |
| 60–79 | 🔵 Good | Above industry average — targeted improvements needed |
| 40–59 | 🟡 Fair | At or below industry average — structured plan required |
| 0–39 | 🔴 At Risk | Significantly below benchmarks — urgent action required |

---

## 🏭 11 Industry Verticals Supported

Each vertical applies sector-specific benchmarks, risk weighting, and reference organisations.

| Vertical | Focus Areas | Reference Orgs |
|---|---|---|
| 🏭 **General** | Standard SCOR + Gartner benchmarks across all domains | Gartner Top 25 |
| 💾 **Semiconductor** | Fab utilisation, die yield, export controls (CHIPS Act), rare earth risk | TSMC, Intel, NVIDIA, ASML |
| 🚗 **Automotive** | JIT/JIS delivery, zero line stoppages, EV transition readiness | Toyota (TPS), BMW, Tesla |
| 💊 **Pharmaceutical** | Cold chain integrity, GDP compliance, DSCSA serialisation | Pfizer, Roche, J&J |
| 🛒 **Retail & E-commerce** | OTIF, last-mile, omnichannel fulfillment, seasonal peaks | Amazon, Walmart, Zara |
| 📦 **Consumer Packaged Goods** | Case fill rate, trade promotion, retailer compliance, ESG | P&G, Unilever, Nestlé |
| ✈️ **Aerospace & Defense** | AS9100D compliance, long-lead parts, ITAR/EAR controls | Boeing, Airbus, Lockheed Martin |
| 🏥 **Healthcare** | UDI traceability, sterile supply chain, GPO compliance | Medtronic, Stryker, Becton Dickinson |
| 🍔 **Food & Beverage** | FSMA compliance, cold chain, shelf-life management, date codes | Nestlé, Coca-Cola, Tyson Foods |
| 💻 **Technology & Electronics** | Short product lifecycles, component obsolescence, NPI readiness | Apple, Samsung, Dell, Foxconn |
| 👗 **Apparel & Fashion** | Seasonal cycles, fast fashion speed-to-market, EPR compliance | Zara (Inditex), Nike, H&M |

---

## 💰 Cost-Benefit Analysis

Optionally enter financial context to size the dollar cost of every gap and estimate the ROI of closing it.

**Financial inputs (all optional):**
- Annual revenue range
- Supply chain cost as % of revenue
- Total inventory value
- Freight cost as % of revenue
- Current OTIF rate
- Gross margin

Claude uses your figures — or conservative benchmark assumptions where fields are left blank — to produce a priority matrix of Quick Wins, Strategic Bets, and items to deprioritise.

> ⚠️ **Illustrative & Directional Use Only.** All CBA figures are estimates for informational purposes only. Not certified financial projections or professional financial advice. Validate with your finance team before making investment decisions.

---

## 🔒 Privacy & Compliance

| Principle | Implementation |
|---|---|
| **Zero data storage** | Financial inputs exist only in your browser session — discarded on tab close or Reset |
| **Voluntary consent** | A clear consent checkbox must be actively checked before financial inputs appear |
| **API transparency** | Data passed to Anthropic Claude API is governed by [Anthropic's Privacy Policy](https://www.anthropic.com/legal/privacy) |
| **Regulatory compliance** | Operated under GDPR (EU) 2016/679 and CCPA — data subject rights satisfied by session expiry |
| **No third-party sharing** | Financial data is never sold or shared with third parties |

---

## 🚦 Open Source vs Hosted Tiers

Supply Chain Health Agent follows the **open source engine / hosted service** model.
The code is MIT — free forever. The hosted service is where advanced features live.

| Feature | Open Source | Hosted Free | Pro | Team | Enterprise | Gov |
|---|---|---|---|---|---|---|
| Core assessment (8 domains) | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| Basic PDF export | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| CLI interface | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| All 11 verticals | ✅ Self-hosted | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| Executive persona | ✅ Self-hosted | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| Consultant persona | ✅ Self-hosted | — | 🔒 Pro | 🔒 Pro | 🔒 Enterprise | 🔒 Gov |
| Assessments per month | Unlimited | 3/month | Unlimited | Unlimited | Unlimited | Unlimited |
| Cross-session memory | ✅ Self-hosted | — | 🔒 Pro | 🔒 Pro | 🔒 Enterprise | 🔒 Gov |
| KPI trend tracking | ✅ Self-hosted | — | 🔒 Pro | 🔒 Pro | 🔒 Enterprise | 🔒 Gov |
| Proactive risk alerts | ✅ Self-hosted | — | 🔒 Pro | 🔒 Pro | 🔒 Enterprise | 🔒 Gov |
| Slack integration | ✅ Self-hosted | — | 🔒 Pro | 🔒 Pro | 🔒 Enterprise | 🔒 Gov |
| Email delivery | ✅ Self-hosted | — | 🔒 Pro | 🔒 Pro | 🔒 Enterprise | 🔒 Gov |
| Client intake forms | ✅ Self-hosted | — | 🔒 Pro | 🔒 Pro | 🔒 Enterprise | 🔒 Gov |
| Jira integration | ✅ Self-hosted | — | — | 🔒 Team | 🔒 Enterprise | 🔒 Gov |
| Multi-client dashboard | ✅ Self-hosted | — | — | 🔒 Team | 🔒 Enterprise | 🔒 Gov |
| White-label reports | ✅ Self-hosted | — | — | 🔒 Team | 🔒 Enterprise | 🔒 Gov |
| API access + webhooks | ✅ Self-hosted | — | — | 🔒 Team | 🔒 Enterprise | 🔒 Gov |
| SSO / SAML | — | — | — | — | 🔒 Enterprise | 🔒 Gov |
| Custom verticals | — | — | — | — | 🔒 Enterprise | 🔒 Gov |
| On-premise deployment | — | — | — | — | 🔒 Enterprise | 🔒 Gov |
| Audit logs | — | — | — | — | 🔒 Enterprise | 🔒 Gov |
| FedRAMP / air-gap | — | — | — | — | — | 🔒 Gov |
| GovCloud deployment | — | — | — | — | — | 🔒 Gov |

**Self-hosters** get everything — bring your own Anthropic API key and run your own server.

> Pro, Team, Enterprise, and Government tiers are in development.
> **[Join the Waitlist](https://supply-chain-health-agent.streamlit.app)** to be first to know.

---

## 🚀 Quick Start — Local Development

### 1. Clone the repo
```bash
git clone https://github.com/dwnjuguna/supply-chain-health-agent.git
cd supply-chain-health-agent
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set your API key
```bash
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```
Get your key at [console.anthropic.com](https://console.anthropic.com)

### 4. Run the web UI (recommended)
```bash
streamlit run app.py
# Opens at http://localhost:8501
```

### 5. Or run the terminal CLI
```bash
python3 cli.py
```

---

## MCP Server (Claude Desktop & Claude Code)

The repo ships a Model Context Protocol (MCP) server that exposes the Supply Chain
Health Agent as a set of callable tools inside any MCP-compatible AI client — Claude
Desktop, Claude Code, or any other MCP host. Once registered, you can ask the
assistant to run a full supply chain assessment, pull KPI benchmarks, or review
assessment history directly in chat; it calls the SCHA engine on your behalf and
streams the structured results back — no browser or CLI required.

### Register with Claude Desktop

Add the following to your `claude_desktop_config.json` (macOS:
`~/Library/Application Support/Claude/claude_desktop_config.json`; Windows:
`%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "supply-chain-health-agent": {
      "command": "python3",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/absolute/path/to/supply-chain-health-agent",
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-..."
      }
    }
  }
}
```

> **Replace the `cwd` path with your own repo location** — set it to the absolute
> path of the folder where you cloned this repo (the directory that contains
> `mcp_server/`, `agent.py`, and `requirements.txt`). The `ANTHROPIC_API_KEY` is
> required for `run_assessment`; supply it here or via a `.env` file in that same
> directory. Restart Claude Desktop after editing the config.

For **Claude Code**, register the same server from that directory with:

```bash
claude mcp add supply-chain-health-agent -- python3 -m mcp_server.server
```

### Tools exposed

- `run_assessment` — Runs a full supply chain health assessment for an organization — 8-domain scores, overall score, narrative report, and a prioritized action pack — benchmarked against SCOR and Gartner standards.
- `get_assessment_history` — Lists previously persisted assessment runs (optionally filtered by organization). Persistence lands in a future release; for now it returns an empty list.
- `get_benchmarks` — Returns the 2026 world-class KPI benchmarks, optionally filtered by domain and/or industry vertical.

---

## 🧪 Running Tests

The prompt-assembly and scoring logic is covered by a fast unit suite — **no API key required** (no network calls, no Streamlit needed).

```bash
pip install -r dev-requirements.txt
pytest -q
```

**17 tests** validate:
- Conditional prompt blocks (CBA, executive sections, North Star, sourcing, cyber) include/exclude correctly
- The JSON scores contract stays exactly 8 domains (no key leakage)
- `parse_scores()` clamps to 0–100 and fails gracefully on malformed input
- A default analyst prompt contains no user-injected blocks (regression guard)

Test dependencies live in `dev-requirements.txt`, kept separate from runtime `requirements.txt`.

---

## ☁️ Deploy to Streamlit Community Cloud

1. Fork this repo to your GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **Create app** → select your fork → set main file to `app.py`
4. Go to **⋮ → Settings → Secrets** and add:
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```
5. Click **Deploy** — your app goes live in ~90 seconds

---

## 📁 Project Structure

```
supply-chain-health-agent/
├── agent.py          # Agentic core — web search, action pack, market intel
├── domains.py        # Domain definitions, 2026 KPI benchmarks, system prompt builder
├── personas.py                   # 5 persona configs and prompt extensions
├── phase2_config.py              # Feature flags — 6 tiers, 60+ features
├── verticals.py                  # 11 industry vertical presets with sector-specific benchmarks
├── scoring.py        # Score parsing and interpretation
├── cli.py            # Interactive terminal interface
├── app.py            # Streamlit web UI — premium SaaS design, tabbed results
├── requirements.txt              # anthropic, streamlit, python-dotenv, reportlab
├── memory/
│   └── memory_store.py           # SQLite cross-session memory
├── alerts/
│   ├── slack_dispatcher.py       # Slack webhook delivery
│   ├── email_dispatcher.py       # HTML email reports
│   └── risk_monitor.py           # Claude-powered risk scanning
├── integrations/
│   ├── slack_integration.py      # Push assessments to Slack
│   └── jira_integration.py       # Create Jira tickets from action plan
├── intake/                       # Persona intake forms (Phase 3)
└── .env                          # API key (gitignored)
```

---

## 🏗️ Architecture

```
User (Browser or Terminal)
         │
         ▼
  5-Persona Landing Screen
  Analyst · Executive · Consultant
  Enterprise (Phase 2) · Gov (Phase 3)
         │
         ▼
  Vertical Selection (11 presets)
         │
         ▼
  Prompt Builder
  (domains.py + personas.py + verticals.py)
         │
         ▼
  Anthropic Claude API
  (claude-sonnet-4-6, auto-fallback to Opus 4.8 / Haiku 4.5)
  + Web Search Tool (live market data)
         │
         ▼
  Assessment Engine (agent.py)
         │
    .----+--------------------.
    |                         |
    v                         v
4-Tab Results UI         Phase 2 Engine
 Diagnostic Report        Memory Store (SQLite)
 Domain Deep-Dive         Risk Monitor (Claude)
 Export (PDF)             Slack Dispatcher
 Q&A (context-aware)      Email Dispatcher
                          Jira Integration
                          Feature Flags (6 tiers)
```
---

## 📚 Frameworks & Standards Referenced

- [SCOR Model](https://www.ascm.org/learning-development/scor/) — Supply Chain Operations Reference
- [Gartner Supply Chain Top 25](https://www.gartner.com/en/supply-chain) — World-class benchmarks
- [Anthropic Claude SDK](https://docs.anthropic.com) — AI backbone
- [EU CSDDD](https://commission.europa.eu/business-economy-euro/doing-business-in-the-eu/sustainability-due-diligence-responsible-business/corporate-sustainability-due-diligence_en) — Corporate Sustainability Due Diligence Directive (effective 2026)
- [ISO 28000](https://www.iso.org/standard/79612.html) — Supply chain security management
- [GRI Standards](https://www.globalreporting.org) — ESG reporting

---

## 🤝 Contributing

Contributions are welcome. To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'feat: describe your change'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

**Ideas for contributions:**
- Additional industry verticals
- New KPI benchmarks as standards evolve
- Translations for non-English markets
- Integration with ERP or supply chain platforms

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details. Free to use, share, and adapt.

---

## 👤 Author

**David Njuguna**
- GitHub: [@dwnjuguna](https://github.com/dwnjuguna)
- Live app: [supply-chain-health-agent.streamlit.app](https://supply-chain-health-agent.streamlit.app)

---

## 📎 Resources

| Resource | Link |
|---|---|
| 🌐 Live app | [supply-chain-health-agent.streamlit.app](https://supply-chain-health-agent.streamlit.app) |
| 📄 Product overview PDF | `SC_Health_Agent_Overview_v4.1.pdf` (in this repo) |
| 📊 Commercial deck PDF | `SC_Health_Agent_Deck_v4.1.pdf` (in this repo) |
| 📖 Anthropic Claude SDK | [docs.anthropic.com](https://docs.anthropic.com) |
| 🔑 Get an API key | [console.anthropic.com](https://console.anthropic.com) |
| 📋 SCOR model | [ascm.org/learning-development/scor](https://www.ascm.org/learning-development/scor/) |
| 🔒 Anthropic Privacy Policy | [anthropic.com/legal/privacy](https://www.anthropic.com/legal/privacy) |

---

*Built with ❤️ using the Anthropic Claude SDK*
