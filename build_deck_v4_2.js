// SC Health Agent Deck v4.2 — Jobs/Ive/Fadell standard
// Key changes: MCP server access added, 2026 benchmarks, new MCP slide, June 2026
const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "Supply Chain Health Agent v4.2";
pres.author = "David Njuguna";

const C = {
  navy:   "1E1A4E", purple: "534AB7", teal:   "0F6E56",
  amber:  "E8A020", red:    "E24B4A", lgray:  "F7F6F3",
  dgray:  "374151", mgray:  "6B7280", white:  "FFFFFF",
  offwht: "F0EFF9", mintbg: "E1F5EE", amberbg:"FFF8E7",
  blue:   "2563EB",
};

const shadow = () => ({ type:"outer", color:"000000", opacity:0.09, blur:5, offset:2, angle:135 });

// ── Section divider slide (dark, no content needed) ──────────────────
function sectionSlide(pres, label, subtitle="") {
  const s = pres.addSlide();
  s.background = { color: C.navy };
  s.addShape(pres.shapes.RECTANGLE, { x:0, y:0, w:0.12, h:5.625, fill:{color:C.purple}, line:{color:C.purple} });
  s.addText(label, { x:0.4, y:1.85, w:9.2, h:0.9, fontSize:36, bold:true, color:C.white, fontFace:"Calibri", align:"left", valign:"middle" });
  if (subtitle) s.addText(subtitle, { x:0.4, y:2.9, w:9.2, h:0.5, fontSize:15, color:"AFA9EC", fontFace:"Calibri" });
  return s;
}

// ── Content slide: title only, no decorative line ─────────────────────
function contentSlide(pres, title) {
  const s = pres.addSlide();
  s.background = { color: C.white };
  s.addText(title, {
    x:0.5, y:0.1, w:9.0, h:0.95,
    fontSize:20, bold:true, color:C.navy, fontFace:"Calibri",
    align:"left", valign:"top"
  });
  return s;
}

// ── Stat box ─────────────────────────────────────────────────────────
function statBox(s, x, y, w, h, stat, label, color) {
  s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill:{color}, line:{color}, shadow:shadow() });
  s.addText(stat,  { x, y:y+0.1,      w, h:h*0.5,  fontSize:30, bold:true, color:C.white, fontFace:"Calibri", align:"center", valign:"middle" });
  s.addText(label, { x, y:y+h*0.56,   w, h:h*0.38, fontSize:10, color:C.white, fontFace:"Calibri", align:"center", valign:"top" });
}

// ── Card (colored top bar, title, body) ───────────────────────────────
function card(s, x, y, w, h, title, body, accent, bg) {
  s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill:{color:bg||C.white}, line:{color:"E5E7EB",width:0.5}, shadow:shadow() });
  s.addShape(pres.shapes.RECTANGLE, { x, y, w, h:0.06, fill:{color:accent}, line:{color:accent} });
  s.addText(title, { x:x+0.15, y:y+0.12, w:w-0.3, h:0.38, fontSize:11.5, bold:true, color:accent, fontFace:"Calibri" });
  s.addText(body,  { x:x+0.15, y:y+0.52, w:w-0.3, h:h-0.6, fontSize:10, color:C.dgray, fontFace:"Calibri", valign:"top" });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 1 — COVER
// ═══════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.navy };
  s.addShape(pres.shapes.RECTANGLE, { x:0, y:0, w:0.18, h:5.625, fill:{color:C.purple}, line:{color:C.purple} });
  s.addShape(pres.shapes.RECTANGLE, { x:0, y:4.8, w:10, h:0.825, fill:{color:"16123C"}, line:{color:"16123C"} });

  s.addText("SUPPLY CHAIN HEALTH AGENT", { x:0.4, y:0.55, w:9.2, h:0.75, fontSize:30, bold:true, color:C.white, fontFace:"Calibri", charSpacing:3 });
  s.addText("AI-powered end-to-end supply chain diagnostics", { x:0.4, y:1.38, w:9.2, h:0.48, fontSize:18, color:"AFA9EC", fontFace:"Calibri" });
  // CHANGE 1: Added MCP Server to capability line
  s.addText("Powered by Anthropic Claude SDK  ·  MCP Server  ·  Browser-based  ·  No login required", { x:0.4, y:1.9, w:9.2, h:0.32, fontSize:11.5, color:"7C78C0", fontFace:"Calibri" });

  // CHANGE 2: Replaced 100%/Browser-Based with MCP/AI-Native Access in blue
  const stats = [["60s","Time to\nAssessment"],["8","SCOR\nDomains"],["11","Industry\nVerticals"],["5","User\nPersonas"],["MCP","AI-Native\nAccess"]];
  const colors5 = [C.purple, C.purple, C.teal, C.amber, C.blue];
  stats.forEach(([v,l],i) => statBox(s, 0.4+i*1.84, 2.55, 1.65, 1.52, v, l, colors5[i]));

  // CHANGE 7: Updated date to June 2026
  s.addText("supply-chain-health-agent.streamlit.app  ·  github.com/dwnjuguna/Supply-Chain-Health-Agent  ·  June 2026", {
    x:0.4, y:4.88, w:9.2, h:0.32, fontSize:9, color:"7C78C0", fontFace:"Calibri", align:"center"
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 2 — SECTION: THE CHALLENGE
// ═══════════════════════════════════════════════════════════════════════
sectionSlide(pres, "01 — The Challenge", "Supply chain failures are costing enterprises more than ever");

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 3 — COST STATS
// ═══════════════════════════════════════════════════════════════════════
{
  const s = contentSlide(pres, "Supply chain underperformance costs enterprises $100M–$300M annually");
  const bigStats = [
    ["$182M","avg. annual loss per\nFortune 500 from disruptions\n(McKinsey, 2024)", C.red],
    ["12 wks","avg. time for a\nconsulting-led supply\nchain diagnostic",    C.amber],
    ["$300K","avg. consulting cost\nfor a full-scope\nhealth assessment",    C.purple],
    ["94%","of executives say\nvisibility is their\n#1 concern (Gartner)",  C.teal],
  ];
  bigStats.forEach(([v,l,col],i) => statBox(s, 0.5+i*2.28, 1.15, 2.08, 1.95, v, l, col));

  const rows = [
    [{ text:"Domain",options:{bold:true,color:C.white} }, {text:"World-class",options:{bold:true,color:C.white}}, {text:"Industry Avg",options:{bold:true,color:C.white}}, {text:"Annual Gap",options:{bold:true,color:C.white}}],
    ["OTIF","95–98%","85–88%","~$12M/yr in penalties & premium freight"],
    ["Inventory Turns","8–12x","4–5x","~$40M trapped per $200M inventory"],
    ["Forecast Accuracy","85–90%","60–70%","25–35% excess safety stock cost"],
    ["OEE",">85%","60–65%","~$18M lost output per $100M capacity"],
  ];
  s.addTable(rows, { x:0.5, y:3.28, w:9.0, colW:[1.8,1.45,1.45,4.3], border:{pt:0.5,color:"E5E7EB"}, fontFace:"Calibri", fontSize:10.5, color:C.dgray, rowH:0.44 });
  s.addShape(pres.shapes.RECTANGLE, { x:0.5, y:3.28, w:9.0, h:0.44, fill:{color:C.navy}, line:{color:C.navy} });
  s.addTable([[{text:"Domain",options:{bold:true,color:C.white}},{text:"World-class",options:{bold:true,color:C.white}},{text:"Industry Avg",options:{bold:true,color:C.white}},{text:"Annual Gap",options:{bold:true,color:C.white}}]], {
    x:0.5, y:3.28, w:9.0, colW:[1.8,1.45,1.45,4.3], border:{pt:0.5,color:C.navy}, fontFace:"Calibri", fontSize:10.5, rowH:0.44,
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 4 — COMPETITIVE COMPARISON
// ═══════════════════════════════════════════════════════════════════════
{
  const s = contentSlide(pres, "60 seconds vs 12 weeks — the same insight at a fraction of the cost");
  const hd = { bold:true, color:C.white };
  const yc = { bold:true, color:C.teal };
  const rows = [
    [{text:"Alternative",options:hd},{text:"Cost",options:hd},{text:"Time to Insight",options:hd},{text:"Live Data",options:hd},{text:"Always On",options:hd}],
    ["McKinsey / Big 4","$150K–$500K","8–12 weeks","No","No"],
    ["Gartner Membership","$25K–$60K/yr","Weeks","No","No"],
    ["Internal Team","$30K–$80K","4–8 weeks","No","No"],
    ["ASCM Free Tool","$0","1 hour","No","No"],
    [{text:"SC Health Agent",options:yc},{text:"Contact for pricing",options:yc},{text:"60 seconds",options:yc},{text:"Yes ✓",options:yc},{text:"Yes ✓",options:yc}],
  ];
  s.addTable(rows, { x:0.5, y:1.15, w:9.0, colW:[2.5,1.8,1.8,1.3,1.6], border:{pt:0.5,color:"E5E7EB"}, fontFace:"Calibri", fontSize:11.5, color:C.dgray, rowH:0.72 });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 5 — SECTION: THE PLATFORM
// ═══════════════════════════════════════════════════════════════════════
sectionSlide(pres, "02 — The Platform", "What it does, how it works, and what makes it agentic");

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 6 — SIX CAPABILITIES
// ═══════════════════════════════════════════════════════════════════════
{
  const s = contentSlide(pres, "Six core capabilities — diagnostics, intelligence, and autonomous action");
  const caps = [
    ["Instant Diagnostics","Scores 8 domains 0–100 vs 2026 Gartner and SCOR benchmarks",C.purple],
    ["Live Market Intelligence","Autonomously searches freight rates, regulatory updates, geopolitical risks",C.teal],
    ["Auto Action Pack","Generates board summary, 90-day plan and risk watch list — automatically",C.amber],
    ["Context-Aware Q&A","Follow-up answers reference your specific scores — not generic advice",C.purple],
    ["Professional PDF Export","Multi-page report with scores, narrative, recommendations — board-ready",C.teal],
    ["Phase 2 Risk Alerts","Proactive monitoring via Claude + web search, delivered to Slack and email",C.red],
  ];
  caps.forEach(([title,body,accent],i) => {
    const col=i%3, row=Math.floor(i/3);
    card(s, 0.5+col*3.07, 1.15+row*2.15, 2.88, 2.0, title, body, accent, C.lgray);
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 7 — AGENTIC AI
// ═══════════════════════════════════════════════════════════════════════
{
  const s = contentSlide(pres, "Agentic AI — Claude works autonomously, without waiting to be asked");
  s.addShape(pres.shapes.RECTANGLE, { x:0.5, y:1.15, w:4.3, h:4.2, fill:{color:C.mintbg}, line:{color:"D1FAE5",width:0.5} });
  s.addText("LIVE NOW", { x:0.65, y:1.25, w:4.0, h:0.35, fontSize:12, bold:true, color:C.teal, fontFace:"Calibri" });
  s.addText([
    {text:"Live Web Search",options:{bold:true,breakLine:true}},{text:" — fetches freight rates, regulations, geopolitical risks during every assessment",options:{breakLine:true,paraSpaceAfter:8}},
    {text:"Auto Action Pack",options:{bold:true,breakLine:true}},{text:" — board summary, 90-day plan and risk watch list, generated without any prompt",options:{breakLine:true,paraSpaceAfter:8}},
    {text:"Market Intelligence",options:{bold:true,breakLine:true}},{text:" — parallel search surfaces the 5 most critical developments for your vertical",options:{breakLine:true,paraSpaceAfter:8}},
    {text:"Agentic Q&A",options:{bold:true,breakLine:true}},{text:" — follow-up questions trigger web searches for current data",options:{}},
  ], { x:0.65, y:1.65, w:4.0, h:3.5, fontSize:11, color:C.dgray, fontFace:"Calibri", valign:"top" });

  s.addShape(pres.shapes.RECTANGLE, { x:5.2, y:1.15, w:4.3, h:4.2, fill:{color:C.amberbg}, line:{color:"FDE68A",width:0.5} });
  s.addText("PHASE 2 — BUILT & READY", { x:5.35, y:1.25, w:4.0, h:0.35, fontSize:12, bold:true, color:C.amber, fontFace:"Calibri" });
  s.addText([
    {text:"Cross-Session Memory",options:{bold:true,breakLine:true}},{text:" — SQLite engine tracks org profiles, scores and KPI trends over time",options:{breakLine:true,paraSpaceAfter:8}},
    {text:"Proactive Risk Alerts",options:{bold:true,breakLine:true}},{text:" — Claude monitors supply chain news and flags risks before you ask",options:{breakLine:true,paraSpaceAfter:8}},
    {text:"Slack + Email",options:{bold:true,breakLine:true}},{text:" — push assessments, action plans and alerts to channels",options:{breakLine:true,paraSpaceAfter:8}},
    {text:"Jira Integration",options:{bold:true,breakLine:true}},{text:" — create tickets from the 90-day action plan automatically",options:{}},
  ], { x:5.35, y:1.65, w:4.0, h:3.5, fontSize:11, color:C.dgray, fontFace:"Calibri", valign:"top" });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 8 — 8 DOMAINS
// CHANGE 3: 2025 → 2026 in slide title
// ═══════════════════════════════════════════════════════════════════════
{
  const s = contentSlide(pres, "Eight SCOR-aligned domains — scored 0–100 against 2026 world-class benchmarks");
  const domains = [
    ["Demand Planning & Forecasting","FA >85–90%, MAPE <10%",C.purple],
    ["Procurement & Sourcing","OTD >95%, <500 PPM",C.teal],
    ["Manufacturing & Production","OEE >85%, FPY >98%",C.amber],
    ["Inventory Management","8–12x turns, <1% stockout",C.purple],
    ["Logistics & Transportation","OTIF 95–98%",C.teal],
    ["Warehousing & Fulfillment","Accuracy >99.9%",C.amber],
    ["Risk & Resilience","BCP >95% critical nodes",C.red],
    ["Sustainability & ESG","Scope 3 >80% tracked",C.teal],
  ];
  domains.forEach(([name,target,accent],i) => {
    const col=i%4, row=Math.floor(i/4);
    card(s, 0.5+col*2.28, 1.15+row*2.15, 2.1, 2.0, name, `World-class:\n${target}`, accent, C.white);
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 9 — SECTION: WHO IT'S FOR
// ═══════════════════════════════════════════════════════════════════════
sectionSlide(pres, "03 — Who It's For", "Five user personas — three live now, two on the roadmap");

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 10 — 5 PERSONAS
// ═══════════════════════════════════════════════════════════════════════
{
  const s = contentSlide(pres, "Five personas — each with a distinct track, from practitioner to federal");
  const personas = [
    ["SC Manager / Analyst","Practitioner Track","Live Now","Deep KPI diagnostics, benchmark gaps vs Gartner Top 25, CBA, Q&A with live web search.",C.purple,C.offwht],
    ["CSCO / COO / VP SC","Executive Track","Live Now","Strategic scenario comparison, 36-month maturity roadmap, board-ready language throughout.",C.teal,C.mintbg],
    ["SC Consultant","Consultant Track","Live Now","Multi-client diagnostics across 11 verticals, white-label PDF reports, client intake forms.",C.amber,C.amberbg],
    ["Enterprise IT / Config","Enterprise Track","Phase 2","SSO/SAML, API access, webhook integrations, custom verticals, audit logs, SLA guarantee.",C.mgray,C.lgray],
    ["Government / Federal","Federal Track","Phase 3","Air-gapped & GovCloud deployment, FedRAMP pathway, ITAR controls, FIPS 140-2 compliance.",C.red,"FEF2F2"],
  ];
  personas.forEach(([name,track,status,desc,accent,bg],i) => {
    const y = 1.15+i*0.86;
    s.addShape(pres.shapes.RECTANGLE, { x:0.5, y, w:9.0, h:0.8, fill:{color:bg}, line:{color:"E5E7EB",width:0.3} });
    s.addShape(pres.shapes.RECTANGLE, { x:0.5, y, w:0.07, h:0.8, fill:{color:accent}, line:{color:accent} });
    s.addText(name,  { x:0.72, y:y+0.05, w:2.7, h:0.32, fontSize:12, bold:true, color:accent, fontFace:"Calibri" });
    s.addText(track, { x:0.72, y:y+0.45, w:2.4, h:0.26, fontSize:9, color:C.mgray, fontFace:"Calibri" });
    s.addText(desc,  { x:3.4,  y:y+0.08, w:5.1, h:0.62, fontSize:10.5, color:C.dgray, fontFace:"Calibri", valign:"top" });
    const bc = status==="Live Now"?C.teal:status==="Phase 2"?C.amber:C.mgray;
    s.addShape(pres.shapes.RECTANGLE, { x:8.62, y:y+0.24, w:0.82, h:0.3, fill:{color:bc}, line:{color:bc} });
    s.addText(status, { x:8.62, y:y+0.24, w:0.82, h:0.3, fontSize:7.5, bold:true, color:C.white, fontFace:"Calibri", align:"center", valign:"middle" });
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 11 — SECTION: INDUSTRY COVERAGE
// ═══════════════════════════════════════════════════════════════════════
sectionSlide(pres, "04 — Industry Coverage", "11 vertical presets — sector-specific benchmarks and reference organisations");

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 12 — 11 VERTICALS
// ═══════════════════════════════════════════════════════════════════════
{
  const s = contentSlide(pres, "11 industry verticals — tailored benchmarks, risk weighting and reference orgs");
  const verticals = [
    ["General Manufacturing","Gartner Top 25"],["Semiconductor","TSMC, Intel, NVIDIA"],
    ["Automotive","Toyota, BMW, Tesla"],["Pharmaceutical","Pfizer, Roche, J&J"],
    ["Retail & E-commerce","Amazon, Walmart, Zara"],["Consumer Packaged Goods","P&G, Unilever, Nestlé"],
    ["Aerospace & Defense","Boeing, Airbus, Lockheed"],["Healthcare","Medtronic, Stryker, BD"],
    ["Food & Beverage","Nestlé, Coca-Cola, Tyson"],["Technology & Electronics","Apple, Samsung, Dell"],
    ["Apparel & Fashion","Zara, Nike, H&M"],
  ];
  const accents=[C.purple,C.teal,C.amber,C.teal,C.purple,C.teal,C.red,C.teal,C.amber,C.purple,C.teal];
  verticals.forEach(([name,refs],i) => {
    const col=i%4, row=Math.floor(i/4);
    const x=0.5+col*2.28, y=1.15+row*1.45, accent=accents[i];
    s.addShape(pres.shapes.RECTANGLE, { x, y, w:2.1, h:1.32, fill:{color:C.white}, line:{color:"E5E7EB",width:0.5}, shadow:shadow() });
    s.addShape(pres.shapes.RECTANGLE, { x, y, w:2.1, h:0.06, fill:{color:accent}, line:{color:accent} });
    s.addText(name, { x:x+0.12, y:y+0.1, w:1.86, h:0.6, fontSize:10.5, bold:true, color:C.navy, fontFace:"Calibri", valign:"top" });
    s.addText(refs, { x:x+0.12, y:y+0.78, w:1.86, h:0.42, fontSize:8.5, color:C.mgray, fontFace:"Calibri", valign:"top" });
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 13 — SECTION: HOW IT WORKS
// ═══════════════════════════════════════════════════════════════════════
sectionSlide(pres, "05 — How It Works", "Three steps from opening a browser to board-ready results");

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 14 — THREE STEPS
// ═══════════════════════════════════════════════════════════════════════
{
  const s = contentSlide(pres, "Select · Configure · Assess — under 60 seconds, zero technical setup");
  const steps = [
    ["1","Select","Choose your persona — Analyst, Executive, Consultant, Enterprise or Federal. Everything adapts from this single choice.",C.purple],
    ["2","Configure","Pick your industry vertical from 11 presets. Run an instant benchmark or a tailored custom assessment.",C.teal],
    ["3","Assess","Click Run Assessment. Claude searches the web and delivers scores, action pack and market intelligence in under 60 seconds.",C.amber],
  ];
  steps.forEach(([num,title,body,accent],i) => {
    const x=0.5+i*3.07;
    s.addShape(pres.shapes.RECTANGLE, { x, y:1.15, w:2.88, h:4.3, fill:{color:C.lgray}, line:{color:"E5E7EB"} });
    s.addShape(pres.shapes.RECTANGLE, { x, y:1.15, w:2.88, h:0.06, fill:{color:accent}, line:{color:accent} });
    s.addShape(pres.shapes.OVAL, { x:x+1.1, y:1.4, w:0.65, h:0.65, fill:{color:accent}, line:{color:accent} });
    s.addText(num,   { x:x+1.1, y:1.4, w:0.65, h:0.65, fontSize:22, bold:true, color:C.white, fontFace:"Calibri", align:"center", valign:"middle" });
    s.addText(title, { x:x+0.15, y:2.2, w:2.55, h:0.48, fontSize:17, bold:true, color:accent, fontFace:"Calibri", align:"center" });
    s.addText(body,  { x:x+0.2,  y:2.75, w:2.45, h:2.55, fontSize:11, color:C.dgray, fontFace:"Calibri", valign:"top" });
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 14b — MCP SERVER (NEW — CHANGE 6)
// Two access modes side by side: Web App (purple) and MCP Server (blue)
// ═══════════════════════════════════════════════════════════════════════
{
  const s = contentSlide(pres, "MCP Server — run assessments directly from your AI assistant");

  // Left card — Web App (purple)
  const wx = 0.5, wy = 1.15, ww = 4.42, wh = 4.3;
  s.addShape(pres.shapes.RECTANGLE, { x:wx, y:wy, w:ww, h:wh, fill:{color:C.offwht}, line:{color:"E5E7EB",width:0.5}, shadow:shadow() });
  s.addShape(pres.shapes.RECTANGLE, { x:wx, y:wy, w:ww, h:0.06, fill:{color:C.purple}, line:{color:C.purple} });
  s.addText("Web App", { x:wx+0.2, y:wy+0.18, w:ww-0.4, h:0.45, fontSize:18, bold:true, color:C.purple, fontFace:"Calibri" });
  s.addText("Visit supply-chain-health-agent.streamlit.app\n\nNo login. No download. No IT ticket.\n\nResults in under 60 seconds — browser-based, works anywhere.", {
    x:wx+0.2, y:wy+0.75, w:ww-0.4, h:3.3, fontSize:12, color:C.dgray, fontFace:"Calibri", valign:"top"
  });

  // Right card — MCP Server (blue)
  const mx = 5.08, my = 1.15, mw = 4.42, mh = 4.3;
  s.addShape(pres.shapes.RECTANGLE, { x:mx, y:my, w:mw, h:mh, fill:{color:"EFF6FF"}, line:{color:"E5E7EB",width:0.5}, shadow:shadow() });
  s.addShape(pres.shapes.RECTANGLE, { x:mx, y:my, w:mw, h:0.06, fill:{color:C.blue}, line:{color:C.blue} });
  s.addText("MCP Server", { x:mx+0.2, y:my+0.18, w:mw-0.4, h:0.45, fontSize:18, bold:true, color:C.blue, fontFace:"Calibri" });
  s.addText("Add one config block to Claude Desktop or Claude Code.\n\nAsk your AI assistant to run a supply chain assessment — no browser needed.\n\nThree tools exposed:\n• run_assessment\n• get_benchmarks\n• get_assessment_history", {
    x:mx+0.2, y:my+0.75, w:mw-0.4, h:3.3, fontSize:12, color:C.dgray, fontFace:"Calibri", valign:"top"
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 15 — FOUR OUTPUT TABS
// ═══════════════════════════════════════════════════════════════════════
{
  const s = contentSlide(pres, "Four output tabs — results delivered automatically, no extra prompting required");
  const tabs = [
    ["Diagnostic Report","Domain scores 0–100 with benchmark gaps, priority recommendations, executive summary and cost-benefit analysis.",C.purple],
    ["Auto Action Pack","Board summary (5 bullets for CFO/CEO), prioritised 90-day action plan with named owners, and a top-5 risk watch list.",C.teal],
    ["Market Intelligence","5 real-time supply chain signals searched live — freight conditions, commodity moves, regulatory changes, geopolitical risks.",C.amber],
    ["Q&A","Ask Claude anything. Suggested questions provided. Claude searches the web for current data when answering follow-ups.",C.red],
  ];
  tabs.forEach(([title,body,accent],i) => {
    const col=i%2, row=Math.floor(i/2);
    card(s, 0.5+col*4.6, 1.15+row*2.18, 4.42, 2.05, title, body, accent, C.white);
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 16 — ACTION PACK DETAIL
// ═══════════════════════════════════════════════════════════════════════
{
  const s = contentSlide(pres, "The Auto Action Pack — three board-ready outputs, generated without prompting");
  const packs = [
    ["Board Summary","5 bullets written for CFO/CEO — impact-first, no jargon, ready to paste into a board presentation.",[
      "Overall score and rating vs world-class","Top 2 domain gaps with dollar cost estimates",
      "Priority recommendation with payback timeline","Recommended strategic scenario","Single next action"
    ],C.purple],
    ["90-Day Action Plan","8–10 specific actions with named owners, success metrics and week-by-week timing.",[
      "Weeks 1–4: foundational quick wins","Weeks 5–8: process and tool improvements",
      "Weeks 9–12: capability build and tracking","Named owner for each action","Measurable success metric per action"
    ],C.teal],
    ["Risk Watch List","Top 5 supply chain risks by severity and likelihood, each with an immediate mitigation action.",[
      "HIGH / MEDIUM / LOW severity rating","Likelihood assessment",
      "Immediate mitigation action","Vertical-specific risks (e.g. export controls)","Links to live market intelligence"
    ],C.amber],
  ];
  packs.forEach(([title,sub,items,accent],i) => {
    const x=0.5+i*3.07;
    s.addShape(pres.shapes.RECTANGLE, { x, y:1.15, w:2.88, h:4.28, fill:{color:C.white}, line:{color:"E5E7EB"}, shadow:shadow() });
    s.addShape(pres.shapes.RECTANGLE, { x, y:1.15, w:2.88, h:0.06, fill:{color:accent}, line:{color:accent} });
    s.addText(title, { x:x+0.15, y:1.26, w:2.55, h:0.42, fontSize:13, bold:true, color:accent, fontFace:"Calibri" });
    s.addText(sub,   { x:x+0.15, y:1.72, w:2.55, h:0.7, fontSize:9.5, color:C.dgray, fontFace:"Calibri", valign:"top" });
    s.addText(items.map(t=>({text:t,options:{bullet:true,breakLine:true,paraSpaceAfter:5}})), {
      x:x+0.15, y:2.5, w:2.55, h:2.7, fontSize:10, color:C.dgray, fontFace:"Calibri", valign:"top"
    });
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 17 — SECTION: OPEN SOURCE vs HOSTED
// ═══════════════════════════════════════════════════════════════════════
sectionSlide(pres, "06 — Open Source vs Hosted", "MIT — free forever at the core. Advanced features on the hosted service.");

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 18 — TIER COMPARISON TABLE
// CHANGE 4: Added MCP server access row — Yes across all tiers
// ═══════════════════════════════════════════════════════════════════════
{
  const s = contentSlide(pres, "MIT — free forever at the core. Advanced features on the hosted service.");
  const hd={bold:true,color:C.white};
  const yc={bold:true,color:C.teal};
  const no={color:C.mgray};
  const p2={bold:true,color:C.amber};
  const tm={bold:true,color:C.teal};
  const en={bold:true,color:C.amber};
  const gv={bold:true,color:C.red};
  const ct={bold:true,color:C.purple};
  const rows=[
    [{text:"Feature",options:hd},{text:"Open Source",options:hd},{text:"Hosted Free",options:hd},{text:"Pro",options:hd},{text:"Team",options:hd},{text:"Enterprise",options:hd},{text:"Gov",options:hd}],
    ["Core assessment (8 domains)",{text:"Yes",options:yc},{text:"Yes",options:yc},{text:"Yes",options:yc},{text:"Yes",options:yc},{text:"Yes",options:yc},{text:"Yes",options:yc}],
    ["All 11 verticals",{text:"Yes",options:yc},{text:"Yes",options:yc},{text:"Yes",options:yc},{text:"Yes",options:yc},{text:"Yes",options:yc},{text:"Yes",options:yc}],
    ["PDF export",{text:"Yes",options:yc},{text:"Yes",options:yc},{text:"Yes",options:yc},{text:"Yes",options:yc},{text:"Yes",options:yc},{text:"Yes",options:yc}],
    ["Assessments / month","Unlimited","3/mo","Unlimited","Unlimited","Unlimited","Unlimited"],
    ["Cross-session memory","Self-host",{text:"—",options:no},{text:"Pro+",options:p2},{text:"Pro+",options:p2},{text:"Pro+",options:p2},{text:"Pro+",options:p2}],
    ["Proactive risk alerts","Self-host",{text:"—",options:no},{text:"Pro+",options:p2},{text:"Pro+",options:p2},{text:"Pro+",options:p2},{text:"Pro+",options:p2}],
    ["Slack + Email delivery","Self-host",{text:"—",options:no},{text:"Pro+",options:p2},{text:"Pro+",options:p2},{text:"Pro+",options:p2},{text:"Pro+",options:p2}],
    // CHANGE 4: New MCP server access row
    ["MCP server access",{text:"Yes",options:yc},{text:"Yes",options:yc},{text:"Yes",options:yc},{text:"Yes",options:yc},{text:"Yes",options:yc},{text:"Yes",options:yc}],
    ["White-label reports","Self-host",{text:"—",options:no},{text:"—",options:no},{text:"Team+",options:tm},{text:"Team+",options:tm},{text:"Team+",options:tm}],
    ["SSO / SAML + API access",{text:"—",options:no},{text:"—",options:no},{text:"—",options:no},{text:"—",options:no},{text:"Ent+",options:en},{text:"Ent+",options:en}],
    ["FedRAMP / GovCloud",{text:"—",options:no},{text:"—",options:no},{text:"—",options:no},{text:"—",options:no},{text:"—",options:no},{text:"Gov",options:gv}],
    [{text:"Pricing",options:{bold:true}},{text:"Free",options:yc},{text:"Free",options:yc},{text:"Contact us",options:ct},{text:"Contact us",options:ct},{text:"Contact us",options:ct},{text:"Contact us",options:ct}],
  ];
  s.addTable(rows,{
    x:0.3, y:1.1, w:9.4, colW:[2.2,1.1,1.0,0.9,0.9,1.2,1.1],
    border:{pt:0.4,color:"E5E7EB"}, fontFace:"Calibri", fontSize:9.5, color:C.dgray, rowH:0.32,
  });
  s.addShape(pres.shapes.RECTANGLE,{x:0.3,y:1.1,w:9.4,h:0.38,fill:{color:C.navy},line:{color:C.navy}});
  s.addTable([[{text:"Feature",options:hd},{text:"Open Source",options:hd},{text:"Hosted Free",options:hd},{text:"Pro",options:hd},{text:"Team",options:hd},{text:"Enterprise",options:hd},{text:"Gov",options:hd}]],{
    x:0.3,y:1.1,w:9.4,colW:[2.2,1.1,1.0,0.9,0.9,1.2,1.1],border:{pt:0.4,color:C.navy},fontFace:"Calibri",fontSize:9.5,rowH:0.38,
  });
  s.addText("Contact us to discuss Pro, Team, Enterprise and Gov pricing — supply-chain-health-agent.streamlit.app",{
    x:0.3,y:5.35,w:9.4,h:0.22,fontSize:8.5,color:C.mgray,fontFace:"Calibri",align:"center",italic:true,
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 19 — SECTION: EXPECTED OUTCOMES
// ═══════════════════════════════════════════════════════════════════════
sectionSlide(pres, "07 — Expected Outcomes", "From diagnostic to decision-ready in a single session");

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 20 — SIX OUTPUTS
// CHANGE 5: 2025 → 2026 in first card body text
// ═══════════════════════════════════════════════════════════════════════
{
  const s = contentSlide(pres, "Six decision-enabling outputs — everything needed to brief leadership and act");
  const outputs=[
    ["A scored, benchmarked health check","Domain scores 0–100 against 2026 world-class. You know exactly where you stand vs Gartner Top 25.",C.purple],
    ["The dollar cost of every gap","Each domain gap sized in financial terms — working capital trapped, penalty exposure, lost revenue.",C.amber],
    ["A board-ready executive summary","5 bullets for CFO or CEO. Impact-first, no jargon. Ready to paste into a board presentation.",C.teal],
    ["A prioritised 90-day action plan","Named initiatives, suggested owners, success metrics and week-by-week timing.",C.purple],
    ["A risk watch list","Top 5 supply chain risks by severity and likelihood, each with an immediate mitigation action.",C.red],
    ["Strategic scenarios (C-Suite track)","Three named transformation paths with investment ranges, KPI targets, trade-offs and a recommendation.",C.teal],
  ];
  outputs.forEach(([title,body,accent],i) => {
    const col=i%3, row=Math.floor(i/3);
    card(s, 0.5+col*3.07, 1.15+row*2.14, 2.88, 2.0, title, body, accent, C.lgray);
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 21 — SECTION: GET STARTED
// ═══════════════════════════════════════════════════════════════════════
sectionSlide(pres, "08 — Get Started", "No installation, no IT ticket — open any browser and go");

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 22 — CLOSING CTA
// CHANGE 7: May 2026 → June 2026
// ═══════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.navy };
  s.addShape(pres.shapes.RECTANGLE, { x:0, y:0, w:0.18, h:5.625, fill:{color:C.teal}, line:{color:C.teal} });
  s.addShape(pres.shapes.RECTANGLE, { x:0, y:4.62, w:10, h:1.005, fill:{color:"16123C"}, line:{color:"16123C"} });
  s.addText("The supply chain leaders who win", { x:0.5, y:0.4, w:9.0, h:0.68, fontSize:30, bold:true, color:C.white, fontFace:"Calibri" });
  s.addText("are the ones who know their numbers.", { x:0.5, y:1.05, w:9.0, h:0.68, fontSize:30, bold:true, color:"AFA9EC", fontFace:"Calibri" });
  s.addText("Now you can know yours — in 60 seconds. Grounded in 2026 reality.", { x:0.5, y:1.85, w:9.0, h:0.45, fontSize:18, color:C.white, fontFace:"Calibri", italic:true });
  const links=[["Try it now","supply-chain-health-agent.streamlit.app",C.purple],["GitHub","github.com/dwnjuguna/Supply-Chain-Health-Agent",C.teal],["Contact for pricing","Open Pro, Team, Enterprise & Gov tiers",C.amber]];
  links.forEach(([label,url,accent],i) => {
    const x=0.5+i*3.07;
    s.addShape(pres.shapes.RECTANGLE, { x, y:2.65, w:2.85, h:1.65, fill:{color:accent}, line:{color:accent}, shadow:shadow() });
    s.addText(label, { x, y:2.78, w:2.85, h:0.45, fontSize:14, bold:true, color:C.white, fontFace:"Calibri", align:"center" });
    s.addText(url,   { x:x+0.1, y:3.3, w:2.65, h:0.85, fontSize:9.5, color:C.white, fontFace:"Calibri", align:"center", valign:"top" });
  });
  s.addText("MIT License · Open Source · Author: David Njuguna · June 2026\nAll assessments are illustrative and directional only. Not professional financial or consulting advice.", {
    x:0.5, y:4.68, w:9.0, h:0.5, fontSize:8, color:"7C78C0", fontFace:"Calibri", align:"center"
  });
}

// CHANGE 8: Updated output filename to v4_2
pres.writeFile({ fileName:"SC_Health_Agent_Deck_v4_2.pptx" })
  .then(() => console.log("✅ SC_Health_Agent_Deck_v4_2.pptx written — v4.2 complete (23 slides)"))
  .catch(e => { console.error("❌", e); process.exit(1); });
