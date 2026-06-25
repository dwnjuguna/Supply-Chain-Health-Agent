// SC Health Agent — Technical Architecture Deck v4.2
// 35 slides · Junior Engineer → Principal Engineer / CTO audience
// v4.2 additions: MCP server architecture section (3 new slides), updated stack, 2026 benchmarks
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout  = "LAYOUT_16x9";
pres.title   = "Supply Chain Health Agent — Technical Architecture v4.2";
pres.author  = "David Njuguna";

// ── Palette ────────────────────────────────────────────────────────────────
const C = {
  navy:   "1E1A4E", purple: "534AB7", teal:   "0F6E56",
  amber:  "E8A020", red:    "E24B4A", mgray:  "6B7280",
  dgray:  "374151", lgray:  "F7F6F3", white:  "FFFFFF",
  code:   "1A1F2E", codehi: "A5D6A7", codedim:"7986CB",
  codefn: "80CBC4", codekw: "CE93D8", codestr:"FFD54F",
  mintbg: "E1F5EE", amberbg:"FFF8E7", offwht: "F0EFF9",
  blue:   "2563EB", bluebg: "EFF6FF",
};

const shadow = () => ({type:"outer",color:"000000",opacity:0.10,blur:6,offset:2,angle:135});
const makeSh  = () => ({type:"outer",color:"000000",opacity:0.07,blur:4,offset:1,angle:135});

// ── Layout helpers ─────────────────────────────────────────────────────────
function sectionSlide(label, sub="") {
  const s = pres.addSlide();
  s.background = { color: C.navy };
  s.addShape(pres.shapes.RECTANGLE,{x:0,y:0,w:0.12,h:5.625,fill:{color:C.purple},line:{color:C.purple}});
  s.addText(label,{x:0.4,y:1.9,w:9.2,h:0.9,fontSize:34,bold:true,color:C.white,fontFace:"Calibri",align:"left",valign:"middle"});
  if(sub) s.addText(sub,{x:0.4,y:2.95,w:9.2,h:0.5,fontSize:14,color:"AFA9EC",fontFace:"Calibri"});
  return s;
}

function slide(title) {
  const s = pres.addSlide();
  s.background = { color: C.white };
  s.addText(title,{x:0.5,y:0.1,w:9.0,h:0.95,fontSize:20,bold:true,color:C.navy,fontFace:"Calibri",align:"left",valign:"top"});
  return s;
}

// Box + label for diagrams
function box(s,x,y,w,h,label,sublabel,fill,text=C.white,fontSize=10.5) {
  s.addShape(pres.shapes.RECTANGLE,{x,y,w,h,fill:{color:fill},line:{color:fill},shadow:shadow()});
  if(sublabel) {
    s.addText(label,{x,y:y+0.04,w,h:h*0.52,fontSize,bold:true,color:text,fontFace:"Calibri",align:"center",valign:"middle"});
    s.addText(sublabel,{x,y:y+h*0.52,w,h:h*0.42,fontSize:8.5,color:text,fontFace:"Calibri",align:"center",valign:"middle"});
  } else {
    s.addText(label,{x,y,w,h,fontSize,bold:true,color:text,fontFace:"Calibri",align:"center",valign:"middle"});
  }
}

function smallBox(s,x,y,w,h,label,fill,textColor=C.white,fs=9) {
  s.addShape(pres.shapes.RECTANGLE,{x,y,w,h,fill:{color:fill},line:{color:fill},shadow:makeSh()});
  s.addText(label,{x,y,w,h,fontSize:fs,bold:true,color:textColor,fontFace:"Calibri",align:"center",valign:"middle"});
}

// Horizontal arrow (left → right only, for clean diagram rendering)
function arrowH(s,x1,y,x2,color=C.mgray,lw=1.5) {
  const dx = x2 - x1;
  s.addShape(pres.shapes.LINE,{
    x:x1, y, w:dx, h:0,
    line:{color,width:lw,endArrowType:"arrow"}
  });
}

// Vertical arrow (top → bottom only)
function arrowV(s,x,y1,y2,color=C.mgray,lw=1.5) {
  const dy = y2 - y1;
  s.addShape(pres.shapes.LINE,{
    x, y:y1, w:0, h:dy,
    line:{color,width:lw,endArrowType:"arrow"}
  });
}

// Diagonal arrow (used sparingly, explicit dx/dy)
function arrowD(s,x1,y1,dx,dy,color=C.mgray,lw=1.0) {
  s.addShape(pres.shapes.LINE,{
    x:x1, y:y1, w:dx, h:dy,
    line:{color,width:lw,endArrowType:"arrow"}
  });
}

function dashedBox(s,x,y,w,h,label,color) {
  s.addShape(pres.shapes.RECTANGLE,{x,y,w,h,fill:{color:"FFFFFF",transparency:100},line:{color,width:1.2,dashType:"dash"}});
  s.addText(label,{x:x+0.1,y:y+0.05,w:w-0.2,h:0.3,fontSize:8,bold:true,color,fontFace:"Calibri"});
}

// Code block
function codeBlock(s,x,y,w,h,lines) {
  s.addShape(pres.shapes.RECTANGLE,{x,y,w,h,fill:{color:C.code},line:{color:"2D3748",width:0.5},shadow:shadow()});
  s.addText(lines,{x:x+0.18,y:y+0.1,w:w-0.3,h:h-0.2,fontFace:"Courier New",fontSize:8.5,color:C.white,valign:"top",lineSpacing:13});
}

// Info card
function infoCard(s,x,y,w,h,title,body,accent,bg) {
  s.addShape(pres.shapes.RECTANGLE,{x,y,w,h,fill:{color:bg},line:{color:"E5E7EB",width:0.5},shadow:makeSh()});
  s.addShape(pres.shapes.RECTANGLE,{x,y,w,h:0.05,fill:{color:accent},line:{color:accent}});
  s.addText(title,{x:x+0.14,y:y+0.1,w:w-0.28,h:0.36,fontSize:11,bold:true,color:accent,fontFace:"Calibri"});
  s.addText(body, {x:x+0.14,y:y+0.48,w:w-0.28,h:h-0.55,fontSize:9.5,color:C.dgray,fontFace:"Calibri",valign:"top"});
}

// Pill badge
function badge(s,x,y,label,color) {
  s.addShape(pres.shapes.RECTANGLE,{x,y,w:0.9,h:0.28,fill:{color:color},line:{color:color}});
  s.addText(label,{x,y,w:0.9,h:0.28,fontSize:7.5,bold:true,color:C.white,fontFace:"Calibri",align:"center",valign:"middle"});
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 1 — COVER
// ═══════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.navy };
  s.addShape(pres.shapes.RECTANGLE,{x:0,y:0,w:0.18,h:5.625,fill:{color:C.purple},line:{color:C.purple}});
  s.addShape(pres.shapes.RECTANGLE,{x:0,y:4.75,w:10,h:0.875,fill:{color:"16123C"},line:{color:"16123C"}});

  s.addText("SUPPLY CHAIN HEALTH AGENT",{x:0.4,y:0.45,w:9.2,h:0.7,fontSize:26,bold:true,color:C.white,fontFace:"Calibri",charSpacing:2});
  s.addText("Technical Architecture & Engineering Reference — v4.2",{x:0.4,y:1.25,w:9.2,h:0.55,fontSize:20,color:"AFA9EC",fontFace:"Calibri"});
  s.addText("Agentic AI · Anthropic Claude SDK · Python · Streamlit · MCP Server · MIT License",{x:0.4,y:1.88,w:9.2,h:0.32,fontSize:12,color:"7C78C0",fontFace:"Calibri"});

  // Stats boxes — 6 items at narrower width to fit cleanly
  const stats=[
    ["Python 3.10+","Runtime"],["Streamlit","Web Framework"],
    ["Claude Sonnet","AI Engine"],["MCP 1.28","MCP Server"],["MIT","License"],
  ];
  stats.forEach(([v,l],i)=>{
    const x=0.4+i*1.84, col=i===2?C.teal:i===3?C.blue:i===4?C.amber:C.purple;
    s.addShape(pres.shapes.RECTANGLE,{x,y:2.55,w:1.65,h:1.42,fill:{color:col},line:{color:col},shadow:shadow()});
    s.addText(v,{x,y:2.65,w:1.65,h:0.7,fontSize:16,bold:true,color:C.white,fontFace:"Calibri",align:"center",valign:"middle"});
    s.addText(l,{x,y:3.28,w:1.65,h:0.55,fontSize:10,color:C.white,fontFace:"Calibri",align:"center"});
  });

  s.addText("github.com/dwnjuguna/Supply-Chain-Health-Agent  ·  supply-chain-health-agent.streamlit.app  ·  June 2026",{
    x:0.4,y:4.83,w:9.2,h:0.32,fontSize:8.5,color:"7C78C0",fontFace:"Calibri",align:"center"
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 2 — SECTION: SYSTEM OVERVIEW
// ═══════════════════════════════════════════════════════════════════════
sectionSlide("01 — System Overview","Tech stack, dependencies, architecture and module structure");

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 3 — TECH STACK & DEPENDENCIES
// ═══════════════════════════════════════════════════════════════════════
{
  const s = slide("Tech stack & core dependencies");
  const cols = [
    {title:"Language & Runtime", items:["Python 3.10+","pip / requirements.txt","python-dotenv for config",".env for local secrets (gitignored)"], accent:C.purple, bg:C.offwht},
    {title:"Web Framework", items:["Streamlit — UI and session state","Multi-tab result layout","Sidebar configuration panel","No custom frontend code needed"], accent:C.teal, bg:C.mintbg},
    {title:"AI & Inference", items:["anthropic SDK (official Python client)","Model: claude-sonnet-4-6","Server-side web_search_20250305 tool","Max 5 web searches per assessment call"], accent:C.amber, bg:C.amberbg},
    {title:"MCP Server (v4.2)", items:["mcp>=1.28.0 (Anthropic MCP SDK)","stdio transport — Claude Desktop / Code","3 tools: run_assessment · get_benchmarks","· get_assessment_history"], accent:C.blue, bg:C.bluebg},
    {title:"Storage & Infra", items:["Session state only (Phase 1)","SQLite → Supabase (Phase 2)","Streamlit Cloud (hosted)","GitHub Actions (CI/CD path)"], accent:C.navy, bg:C.lgray},
  ];
  // 5 columns, each 1.72" wide in 8.6" total
  const cw = 1.72;
  cols.forEach((c,i)=>{
    const x=0.5+i*cw;
    s.addShape(pres.shapes.RECTANGLE,{x,y:1.12,w:cw-0.08,h:4.25,fill:{color:c.bg},line:{color:"E5E7EB",width:0.5},shadow:makeSh()});
    s.addShape(pres.shapes.RECTANGLE,{x,y:1.12,w:cw-0.08,h:0.05,fill:{color:c.accent},line:{color:c.accent}});
    s.addText(c.title,{x:x+0.1,y:1.17,w:cw-0.28,h:0.42,fontSize:9.5,bold:true,color:c.accent,fontFace:"Calibri"});
    s.addText(c.items.map(t=>({text:t,options:{bullet:true,breakLine:true,paraSpaceAfter:5}})),{
      x:x+0.1,y:1.62,w:cw-0.28,h:3.6,fontSize:8.5,color:C.dgray,fontFace:"Calibri",valign:"top"
    });
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 4 — DIAGRAM: SYSTEM ARCHITECTURE
// ═══════════════════════════════════════════════════════════════════════
{
  const s = slide("System architecture — component overview");

  // Tier labels (rotated, left margin)
  const tierLabel=(label,y)=>s.addText(label,{x:0.08,y,w:0.72,h:0.38,fontSize:7,bold:true,color:C.mgray,fontFace:"Calibri",align:"center",valign:"middle",rotate:90});
  tierLabel("CLIENT",  1.18);
  tierLabel("APP",     1.95);
  tierLabel("MCP",     2.72);
  tierLabel("CORE",    3.49);
  tierLabel("AI/API",  4.26);
  tierLabel("MODULES", 5.0);

  // Layer backgrounds — 6 rows, y-step 0.75"
  const layerBgs=[["F8F9FF",1.1],["F0EFF9",1.87],["EFF6FF",2.64],["E1F5EE",3.41],["FFF8E7",4.18],["F7F6F3",4.95]];
  layerBgs.forEach(([c,y])=>s.addShape(pres.shapes.RECTANGLE,{x:0.82,y,w:8.75,h:0.72,fill:{color:c},line:{color:"E5E7EB",width:0.3}}));

  // CLIENT layer
  smallBox(s,1.0,1.16,1.7,0.58,"Browser / Desktop",C.purple,"FFFFFF",8.5);
  // Arrow from Browser right edge → to APP layer (horizontal then vertical)
  arrowH(s,2.7,1.45,4.9,C.purple,1.5);
  s.addText("HTTPS",{x:3.5,y:1.28,w:0.8,h:0.18,fontSize:7,color:C.purple,fontFace:"Calibri",align:"center"});

  // APP layer
  smallBox(s,3.55,1.93,2.7,0.58,"app.py — Streamlit UI",C.purple,"FFFFFF",9);
  s.addText("Session state · Sidebar · Tab rendering",{x:3.55,y:2.22,w:2.7,h:0.26,fontSize:7.5,color:"D4C8FF",fontFace:"Calibri",align:"center"});
  arrowV(s,4.9,1.74,1.93,C.purple,1.5);

  // MCP layer (NEW v4.2)
  smallBox(s,1.0,2.70,1.7,0.58,"Claude Desktop\n/ Claude Code",C.blue,"FFFFFF",8.5);
  smallBox(s,3.55,2.70,2.7,0.58,"mcp_server/server.py",C.blue,"FFFFFF",9);
  s.addText("stdio · 3 tools · stateless bridge",{x:3.55,y:2.99,w:2.7,h:0.24,fontSize:7.5,color:"BFDBFE",fontFace:"Calibri",align:"center"});
  arrowH(s,2.7,2.99,3.55,C.blue,1.5);
  s.addText("MCP stdio",{x:2.72,y:2.82,w:0.75,h:0.18,fontSize:7,color:C.blue,fontFace:"Calibri",align:"center"});
  arrowV(s,4.9,2.51,2.70,C.blue,1.0);

  // CORE layer
  smallBox(s,3.55,3.47,2.7,0.58,"agent.py — Agentic Core",C.teal,"FFFFFF",9);
  s.addText("Tool orchestration · Prompt assembly · Parsing",{x:3.55,y:3.76,w:2.7,h:0.24,fontSize:7.5,color:"A7F3D0",fontFace:"Calibri",align:"center"});
  arrowV(s,4.9,3.28,3.47,C.teal,1.5);

  // AI layer
  smallBox(s,3.55,4.24,2.7,0.58,"Anthropic API",C.amber,"FFFFFF",9);
  s.addText("Claude Sonnet · web_search tool",{x:3.55,y:4.53,w:2.7,h:0.24,fontSize:7.5,color:"FDE68A",fontFace:"Calibri",align:"center"});
  arrowV(s,4.9,4.05,4.24,C.amber,1.5);
  // Web search
  smallBox(s,6.6,4.24,1.55,0.58,"Live Web\nData",C.amber,"FFFFFF",8.5);
  arrowH(s,6.25,4.53,6.6,C.amber,1.0);

  // MODULES layer — 4 modules evenly spaced
  const mods=[["domains.py","KPI Benchmarks"],["personas.py","Prompt Configs"],["verticals.py","11 Presets"],["scoring.py","Score Parser"]];
  mods.forEach(([name,role],i)=>{
    const x=0.9+i*2.12;
    s.addShape(pres.shapes.RECTANGLE,{x,y:5.01,w:1.92,h:0.54,fill:{color:C.lgray},line:{color:"D1D5DB",width:0.5}});
    s.addShape(pres.shapes.RECTANGLE,{x,y:5.01,w:1.92,h:0.04,fill:{color:C.purple},line:{color:C.purple}});
    s.addText(name,{x,y:5.05,w:1.92,h:0.24,fontSize:8,bold:true,color:C.purple,fontFace:"Calibri",align:"center"});
    s.addText(role,{x,y:5.28,w:1.92,h:0.22,fontSize:7.5,color:C.mgray,fontFace:"Calibri",align:"center"});
    // Thin arrow up from module to CORE
    arrowD(s,x+0.96,5.01,4.9-(x+0.96),-0.54,C.lgray.replace("F7F6F3","D1D5DB"),0.6);
  });

  // cli.py — CORE layer, right side, clearly separate from agent.py
  smallBox(s,6.65,3.47,1.5,0.58,"cli.py\nTerminal UI",C.mgray,"FFFFFF",8.5);
  arrowH(s,6.25,3.76,6.65,C.mgray,0.8);
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 5 — PROJECT MODULE MAP
// ═══════════════════════════════════════════════════════════════════════
{
  const s = slide("Project structure — every file's role");

  // Left: file tree
  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:1.12,w:4.15,h:4.3,fill:{color:C.code},line:{color:"2D3748",width:0.5},shadow:shadow()});
  s.addText("supply-chain-health-agent/",{x:0.7,y:1.18,w:3.8,h:0.3,fontSize:9,bold:true,color:C.codehi,fontFace:"Courier New"});
  const tree=[
    ["├── app.py",          "# Streamlit web UI · main entry point"],
    ["├── agent.py",        "# Agentic core · web search · action pack"],
    ["├── domains.py",      "# 8 SCOR domains · 2026 KPI benchmarks"],
    ["├── personas.py",     "# 5 persona configs · prompt extensions"],
    ["├── verticals.py",    "# 11 industry vertical presets"],
    ["├── scoring.py",      "# Score parser · interpretation engine"],
    ["├── cli.py",          "# Interactive terminal interface"],
    ["├── mcp_server/",     "# MCP server — stdio, 3 tools (v4.2)"],
    ["│   ├── server.py",  "#   stdio bridge · tool dispatch"],
    ["│   └── schemas.py", "#   JSON Schema tool contracts"],
    ["├── requirements.txt","# Python dependencies (incl. mcp>=1.28)"],
    ["├── memory/",         "# Phase 2 — cross-session SQLite engine"],
    ["└── integrations/",   "# Phase 2 — Slack · Email · Jira"],
  ];
  tree.forEach(([file,comment],i)=>{
    s.addText([
      {text:file,   options:{color:C.codehi}},
      {text:"  "+comment, options:{color:"64748B"}},
    ],{x:0.72,y:1.52+i*0.215,w:3.7,h:0.21,fontSize:7.8,fontFace:"Courier New"});
  });

  // Right: role descriptions
  const roles=[
    {file:"app.py",role:"Streamlit UI + session orchestrator",detail:"Renders the persona picker, sidebar config, tabbed results. Owns all st.session_state. Calls agent.py for assessments and market intelligence.",accent:C.purple},
    {file:"agent.py",role:"Agentic core — the brain",detail:"Builds system prompts per persona, assembles the tools list, fires the Anthropic API call, handles tool_use blocks, triggers auto action pack and market intel in parallel.",accent:C.teal},
    {file:"mcp_server/",role:"MCP server — AI-native access layer (v4.2)",detail:"Thin stateless stdio bridge exposing 3 tools: run_assessment, get_benchmarks, get_assessment_history. Schemas in schemas.py. Launched by Claude Desktop or Claude Code.",accent:C.blue},
    {file:"domains.py",role:"Knowledge base + prompt builder",detail:"Contains the 8 SCOR domain definitions, 2026 world-class KPI thresholds, scoring rubrics, and the dynamic system prompt constructor.",accent:C.amber},
  ];
  roles.forEach((r,i)=>{
    const y=1.12+i*1.08;
    s.addShape(pres.shapes.RECTANGLE,{x:4.85,y,w:4.65,h:1.0,fill:{color:C.lgray},line:{color:"E5E7EB",width:0.5},shadow:makeSh()});
    s.addShape(pres.shapes.RECTANGLE,{x:4.85,y,w:4.65,h:0.04,fill:{color:r.accent},line:{color:r.accent}});
    s.addText([{text:r.file,options:{bold:true,color:r.accent}},{text:"  —  "+r.role,options:{color:C.dgray}}],{
      x:5.0,y:y+0.08,w:4.35,h:0.3,fontSize:9.5,fontFace:"Calibri"
    });
    s.addText(r.detail,{x:5.0,y:y+0.4,w:4.35,h:0.55,fontSize:8.5,color:C.mgray,fontFace:"Calibri",valign:"top"});
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 6 — SECTION: AGENTIC AI ENGINE
// ═══════════════════════════════════════════════════════════════════════
sectionSlide("02 — The Agentic AI Engine","SDK integration, request lifecycle, tool use, token budgets, graceful degradation");

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 7 — ANTHROPIC SDK INTEGRATION
// ═══════════════════════════════════════════════════════════════════════
{
  const s = slide("Anthropic SDK integration pattern");

  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:1.12,w:5.0,h:4.3,fill:{color:C.code},line:{color:"2D3748",width:0.5},shadow:shadow()});
  s.addText("# agent.py — core assessment call",{x:0.7,y:1.18,w:4.7,h:0.25,fontSize:8.5,color:"64748B",fontFace:"Courier New"});

  const codeLines=[
    {text:"client",options:{color:C.codehi}},{text:" = ",options:{color:C.white}},{text:"anthropic",options:{color:C.codedim}},{text:".Anthropic()\n",options:{color:C.white}},
    {text:"\nresponse",options:{color:C.codehi}},{text:" = client.",options:{color:C.white}},{text:"messages",options:{color:C.codefn}},{text:".create(\n",options:{color:C.white}},
    {text:"    model",options:{color:C.codehi}},{text:'="claude-sonnet-4-6",\n',options:{color:C.codestr}},
    {text:"    max_tokens",options:{color:C.codehi}},{text:"=token_budget,",options:{color:C.white}},{text:"  # per persona\n",options:{color:"64748B"}},
    {text:"    system",options:{color:C.codehi}},{text:"=system_prompt,",options:{color:C.white}},{text:"   # built by domains.py\n",options:{color:"64748B"}},
    {text:"    messages",options:{color:C.codehi}},{text:"=[{",options:{color:C.white}},{text:'"role"',options:{color:C.codestr}},{text:":",options:{color:C.white}},{text:'"user"',options:{color:C.codestr}},{text:",\n",options:{color:C.white}},
    {text:'               ',options:{color:C.white}},{text:'"content"',options:{color:C.codestr}},{text:":user_input}],\n",options:{color:C.white}},
    {text:"    tools",options:{color:C.codehi}},{text:"=[{\n",options:{color:C.white}},
    {text:'        "type"',options:{color:C.codestr}},{text:':',options:{color:C.white}},{text:'"web_search_20250305"',options:{color:C.codestr}},{text:",\n",options:{color:C.white}},
    {text:'        "name"',options:{color:C.codestr}},{text:':',options:{color:C.white}},{text:'"web_search"',options:{color:C.codestr}},{text:",\n",options:{color:C.white}},
    {text:'        "max_uses"',options:{color:C.codestr}},{text:":5",options:{color:C.amber}},{text:"\n    }]\n",options:{color:C.white}},
    {text:")\n",options:{color:C.white}},
    {text:"\n# Response is mixed content blocks:\n",options:{color:"64748B"}},
    {text:"# text | tool_use | tool_result\n",options:{color:"64748B"}},
    {text:"text = _extract_text(response.content)",options:{color:C.codefn}},
  ];
  s.addText(codeLines,{x:0.7,y:1.48,w:4.6,h:3.8,fontSize:8.5,fontFace:"Courier New",valign:"top",lineSpacing:12});

  const notes=[
    {title:"Server-side tool execution",body:"web_search_20250305 runs on Anthropic's infrastructure — you don't proxy or cache search results. Claude autonomously decides when and what to search.",accent:C.teal},
    {title:"max_uses: 5",body:"Caps web searches per assessment call. Balances insight freshness against API cost (~$0.05–$0.15 per search). Configurable per tier.",accent:C.amber},
    {title:"Mixed content response",body:"The API returns content blocks of type: text, tool_use, and tool_result. _extract_text() joins all text blocks from the mixed response into the final narrative.",accent:C.purple},
    {title:"Async parallelism",body:"Action pack and market intelligence are separate API calls triggered immediately after the assessment returns — not sequential. Keeps total latency under 60s.",accent:C.navy},
  ];
  notes.forEach((n,i)=>{
    infoCard(s,5.75,1.12+i*1.08,3.75,1.0,n.title,n.body,n.accent,C.lgray);
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 8 — DIAGRAM: ASSESSMENT REQUEST LIFECYCLE
// ═══════════════════════════════════════════════════════════════════════
{
  const s = slide("Assessment request lifecycle — end to end");

  // Row 1: left-to-right flow
  const r1y=1.55, bw=1.55, bh=0.62, gap=0.16;

  // Boxes row 1
  smallBox(s,0.5,      r1y,bw,bh,"1. User Input\n& Config",   C.purple);
  smallBox(s,0.5+bw+gap,r1y,bw,bh,"2. Build\nSystem Prompt",  C.purple);
  smallBox(s,0.5+(bw+gap)*2,r1y,bw,bh,"3. API Call\n(with tools)", C.teal);

  // Horizontal arrows row 1
  arrowH(s,0.5+bw,       r1y+bh/2, 0.5+bw+gap,       C.purple,1.5);
  arrowH(s,0.5+(bw+gap)+bw, r1y+bh/2, 0.5+(bw+gap)*2, C.purple,1.5);
  arrowH(s,0.5+(bw+gap)*2+bw, r1y+bh/2, 0.5+(bw+gap)*3, C.teal,1.5);

  // Decision box
  const dx = 0.5+(bw+gap)*3;
  s.addShape(pres.shapes.RECTANGLE,{x:dx,y:r1y+0.1,w:1.55,h:0.42,fill:{color:C.amber},line:{color:C.amber},shadow:shadow()});
  s.addText("Claude decides\nto search?",{x:dx,y:r1y+0.1,w:1.55,h:0.42,fontSize:8,bold:true,color:C.white,fontFace:"Calibri",align:"center",valign:"middle"});

  // YES branch — down
  const decCx = dx + 0.775;
  arrowV(s,decCx, r1y+0.52, r1y+1.3, C.amber, 1.2);
  s.addText("YES (×0–5)",{x:decCx+0.06,y:r1y+0.6,w:1.1,h:0.22,fontSize:7.5,color:C.amber,fontFace:"Calibri"});
  smallBox(s,dx,r1y+1.3,1.55,0.62,"web_search\ntool call",C.amber);
  // Loop back — arrow goes left then label sits above
  arrowH(s,dx, r1y+1.61, dx-0.8, C.amber, 1.0);
  arrowV(s,dx-0.8, r1y+1.61, r1y+0.52, C.amber, 1.0);
  s.addText("Result fed\nback to Claude",{x:dx-1.6,y:r1y+0.9,w:1.4,h:0.4,fontSize:7.5,color:C.amber,fontFace:"Calibri",align:"center"});

  // NO branch — right
  arrowH(s,dx+1.55, r1y+0.31, dx+1.85, C.teal, 1.2);
  s.addText("NO",{x:dx+1.57,y:r1y+0.12,w:0.5,h:0.2,fontSize:7.5,color:C.teal,fontFace:"Calibri"});
  smallBox(s,dx+1.85,r1y,1.55,bh,"4. Synthesise\n& Return",C.teal);

  // Row 2: parse → render diagnostic
  const r2y=3.35;
  smallBox(s,0.5,  r2y,1.55,bh,"5. Parse\nScores",  C.purple);
  arrowH(s,0.5+1.55,r2y+bh/2, 0.5+1.55+gap, C.purple,1.2);
  smallBox(s,0.5+1.55+gap,r2y,1.55,bh,"6. Render\nDiagnostic Tab",C.purple);

  // Arrow from Synthesise&Return box down to row 2 split point
  const synthRx = dx+1.85+1.55; // right edge of Synthesise box
  const synthMx = dx+1.85+0.775; // centre x of Synthesise box
  arrowV(s,synthMx, r1y+bh, r2y, C.teal, 1.2);

  // Action Pack and Market Intel — parallel outputs, clearly spaced
  const apx = 6.5, mix = 7.8;
  smallBox(s,apx,r2y,1.5,bh,"7A. Action\nPack call",C.teal);
  smallBox(s,mix,r2y,1.6,bh,"7B. Market\nIntel call",C.navy);
  // Arrow from split point left to Action Pack
  arrowH(s,synthMx,r2y+bh/2, apx, C.teal,1.0);
  // Arrow from split point right to Market Intel
  arrowH(s,synthMx,r2y+bh/2+0.08, mix, C.navy,1.0);

  // Arrow from Assessment (centre) to Diagnostic Report (row 1 output)
  arrowH(s,4.9, r2y+bh/2, 0.5, C.purple, 0.8);

  // Final combined output
  arrowV(s,apx+0.75, r2y+bh, r2y+bh+0.22, C.teal,1.0);
  arrowV(s,mix+0.8, r2y+bh, r2y+bh+0.22, C.navy,1.0);
  smallBox(s,5.5,r2y+bh+0.22,3.5,0.62,"8. All 4 Tabs: Diagnostic · Action Pack · Mkt Intel · Q&A",C.teal,"FFFFFF",8.5);

  // Timing note
  s.addText("Total: < 60 seconds  ·  Assessment ~30–45s  ·  Action Pack ~10–15s  ·  Market Intel ~10–15s (parallel)",{
    x:0.5,y:5.3,w:9.0,h:0.25,fontSize:8.5,bold:false,color:C.mgray,fontFace:"Calibri"
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 9 — WEB SEARCH TOOL
// ═══════════════════════════════════════════════════════════════════════
{
  const s = slide("Server-side web search — web_search_20250305");

  const leftCards=[
    {t:"What it is",b:"A server-side tool executed by Anthropic's infrastructure. You pass the tool definition in the API call. Claude decides autonomously when to call it, what to query, and how many times (up to the max_uses cap).",a:C.teal},
    {t:"Why server-side matters",b:"You never see raw search results or handle HTTP. Anthropic fetches, parses, and summarises web content. Your app receives a text block containing Claude's synthesis of the search results.",a:C.purple},
    {t:"Graceful fallback",b:"If web search isn't enabled on the API key, Anthropic returns a BadRequestError. agent.py catches this and retries without the tools list — assessment still runs from training data.",a:C.amber},
  ];
  leftCards.forEach((c,i)=>infoCard(s,0.5,1.12+i*1.45,4.5,1.36,c.t,c.b,c.a,C.lgray));

  s.addShape(pres.shapes.RECTANGLE,{x:5.2,y:1.12,w:4.3,h:4.3,fill:{color:C.offwht},line:{color:"E5E7EB",width:0.5},shadow:makeSh()});
  s.addShape(pres.shapes.RECTANGLE,{x:5.2,y:1.12,w:4.3,h:0.05,fill:{color:C.purple},line:{color:C.purple}});
  s.addText("What Claude searches for — autonomously",{x:5.35,y:1.2,w:4.0,h:0.35,fontSize:11,bold:true,color:C.purple,fontFace:"Calibri"});

  const searches=[
    ["Freight & Logistics","Spot freight rates · carrier capacity · port congestion · fuel surcharges"],
    ["Regulatory","CHIPS Act updates · FDA guidance · EU CSDDD · trade sanctions"],
    ["Commodity Markets","Steel · rare earths · semiconductor materials · energy prices"],
    ["Geopolitical Risk","Supply chain disruptions · trade route changes · conflict impact"],
    ["Benchmarks","Current Gartner Top 25 · SCOR updates · industry performance data"],
  ];
  searches.forEach(([cat,detail],i)=>{
    s.addText([{text:cat,options:{bold:true,color:C.purple}},{text:"  "+detail,options:{color:C.dgray}}],{
      x:5.35,y:1.65+i*0.5,w:4.0,h:0.42,fontSize:9.5,fontFace:"Calibri"
    });
    if(i<searches.length-1) s.addShape(pres.shapes.LINE,{x:5.35,y:2.06+i*0.5,w:3.8,h:0,line:{color:"E5E7EB",width:0.5}});
  });

  s.addShape(pres.shapes.RECTANGLE,{x:5.2,y:4.18,w:4.3,h:1.24,fill:{color:C.mintbg},line:{color:"D1FAE5",width:0.5}});
  s.addText("Cost note",{x:5.35,y:4.23,w:4.0,h:0.28,fontSize:9.5,bold:true,color:C.teal,fontFace:"Calibri"});
  s.addText("Web search incurs per-search cost on the Anthropic account (~$0.05–$0.15/search). The max_uses:5 cap limits cost per assessment. Phase 2 alert scans use a separate lower-token call.",{
    x:5.35,y:4.5,w:4.0,h:0.85,fontSize:9,color:C.dgray,fontFace:"Calibri",valign:"top"
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 10 — TOKEN BUDGET ARCHITECTURE
// ═══════════════════════════════════════════════════════════════════════
{
  const s = slide("Token budget architecture — why it's per-persona, not global");

  const budgets=[
    {persona:"Standard Analyst",tokens:1500,pct:37.5,note:"KPI diagnostics only · no CBA · faster response",color:C.purple},
    {persona:"Analyst + CBA",  tokens:2500,pct:62.5,note:"Includes cost-benefit sizing — longer output needed",color:C.teal},
    {persona:"Executive Track",tokens:4000,pct:100, note:"Scenarios + maturity roadmap — highest output volume",color:C.amber},
    {persona:"Action Pack",    tokens:2000,pct:50,  note:"Separate call: board summary + 90-day plan + risk list",color:C.navy},
    {persona:"Market Intel",   tokens:1000,pct:25,  note:"Parallel call: 5 live supply chain signals",color:C.mgray},
  ];

  budgets.forEach((b,i)=>{
    const y=1.2+i*0.82;
    s.addText(b.persona,{x:0.5,y,w:2.3,h:0.36,fontSize:10.5,bold:true,color:b.color,fontFace:"Calibri",valign:"middle"});
    s.addShape(pres.shapes.RECTANGLE,{x:2.9,y:y+0.04,w:5.0,h:0.3,fill:{color:C.lgray},line:{color:"E5E7EB",width:0.3}});
    s.addShape(pres.shapes.RECTANGLE,{x:2.9,y:y+0.04,w:5.0*(b.pct/100),h:0.3,fill:{color:b.color},line:{color:b.color}});
    s.addText(`${b.tokens.toLocaleString()} tokens`,{x:8.05,y,w:1.2,h:0.36,fontSize:10,bold:true,color:b.color,fontFace:"Calibri",align:"right",valign:"middle"});
    s.addText(b.note,{x:2.9,y:y+0.38,w:6.3,h:0.28,fontSize:8.5,color:C.mgray,fontFace:"Calibri"});
  });

  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:5.1,w:9.0,h:0.38,fill:{color:C.offwht},line:{color:"E5E7EB",width:0.5}});
  s.addText([
    {text:"Why per-persona?  ",options:{bold:true,color:C.purple}},
    {text:"Over-allocating tokens inflates cost unnecessarily. Under-allocating truncates output — a junior analyst doesn't need a 36-month roadmap. personas.py is the single source of truth for these values.",options:{color:C.dgray}}
  ],{x:0.65,y:5.12,w:8.7,h:0.34,fontSize:9,fontFace:"Calibri",valign:"middle"});
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 11 — GRACEFUL DEGRADATION
// ═══════════════════════════════════════════════════════════════════════
{
  const s = slide("Graceful degradation — the app never breaks");

  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:1.12,w:5.0,h:3.5,fill:{color:C.code},line:{color:"2D3748",width:0.5},shadow:shadow()});
  s.addText("# agent.py — graceful web search fallback",{x:0.7,y:1.18,w:4.7,h:0.25,fontSize:8.5,color:"64748B",fontFace:"Courier New"});
  const degradLines=[
    {text:"try",options:{color:C.codekw}},{text:":\n",options:{color:C.white}},
    {text:"    response = client.messages.create(\n",options:{color:C.white}},
    {text:"        ...\n",options:{color:"64748B"}},
    {text:"        tools=[web_search_tool],",options:{color:C.white}},{text:"  # with search\n",options:{color:"64748B"}},
    {text:"    )\n\n",options:{color:C.white}},
    {text:"except",options:{color:C.codekw}},{text:" anthropic.",options:{color:C.white}},
    {text:"BadRequestError",options:{color:C.codehi}},
    {text:":\n",options:{color:C.white}},
    {text:"    ",options:{color:C.white}},{text:"# Web search not enabled — retry without\n",options:{color:"64748B"}},
    {text:"    response = client.messages.create(\n",options:{color:C.white}},
    {text:"        ...\n",options:{color:"64748B"}},
    {text:"        tools=[],",options:{color:C.white}},{text:"           # static knowledge only\n",options:{color:"64748B"}},
    {text:"    )\n\n",options:{color:C.white}},
    {text:"# Either path → valid assessment output\n",options:{color:"64748B"}},
    {text:"text = _extract_text(response.content)",options:{color:C.codefn}},
  ];
  s.addText(degradLines,{x:0.7,y:1.48,w:4.6,h:3.0,fontSize:8.5,fontFace:"Courier New",valign:"top",lineSpacing:12});

  const cards=[
    {t:"Why this matters",b:"A user with a paid API key gets live web search. A developer with a basic key gets a full assessment from training data. Zero code change, zero error shown to the user.",a:C.teal},
    {t:"What changes between paths",b:"Path 1 (with search): Claude autonomously searches up to 5 times during assessment. Path 2 (without): Claude uses training data knowledge. Output format and structure identical.",a:C.purple},
    {t:"_extract_text() helper",b:"Joins all text-type content blocks from the mixed API response (text + tool_use + tool_result). Both paths return the same text extraction contract — rest of the app is unaware.",a:C.amber},
  ];
  cards.forEach((c,i)=>infoCard(s,5.75,1.12+i*1.3,3.75,1.22,c.t,c.b,c.a,C.lgray));

  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:4.72,w:9.0,h:0.74,fill:{color:C.mintbg},line:{color:"D1FAE5",width:0.5}});
  s.addText("Design principle — the tool is the product, not the API key tier. Any valid Anthropic key can run the full assessment. Web search is an enhancement, not a requirement.",{
    x:0.65,y:4.76,w:8.7,h:0.66,fontSize:9.5,color:C.teal,fontFace:"Calibri",valign:"middle",italic:true
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 12 — MULTI-OUTPUT ARCHITECTURE
// ═══════════════════════════════════════════════════════════════════════
{
  const s = slide("Multi-output architecture — three API calls, not one");

  // Input box
  smallBox(s,0.5,2.35,1.8,0.9,"User runs\nassessment",C.purple);
  arrowH(s,2.3,2.8,3.1,C.purple,1.5);

  // Fan-out box
  s.addShape(pres.shapes.RECTANGLE,{x:3.1,y:2.35,w:1.8,h:0.9,fill:{color:C.teal},line:{color:C.teal},shadow:shadow()});
  s.addText("Assessment\nAPI Call",{x:3.1,y:2.35,w:1.8,h:0.9,fontSize:10,bold:true,color:C.white,fontFace:"Calibri",align:"center",valign:"middle"});
  arrowH(s,4.9,2.8,5.55,C.teal,1.5);

  // Three output boxes - Diagnostic Report is ABOVE, needs upward arrow from split
  const outputs=[
    {y:1.35,label:"Diagnostic Report",sub:"full domain scores\n+ narrative + CBA",c:C.purple},
    {y:2.35,label:"Auto Action Pack",sub:"board summary\n90-day plan + risks",c:C.teal},
    {y:3.35,label:"Market Intelligence",sub:"5 live signals\nfor chosen vertical",c:C.amber},
  ];

  // Split point is right edge of Assessment box (x=4.9, y=2.8)
  // Draw fan arrows from split to each output
  outputs.forEach((o,idx)=>{
    smallBox(s,5.55,o.y,2.0,0.9,o.label+"\n"+o.sub,o.c);
    arrowH(s,7.55,o.y+0.45,8.1,o.c,1.0);
    smallBox(s,8.1,o.y,1.4,0.9,"Tab "+(idx+1),o.c);
  });
  // Vertical connector from Assessment right edge down/up to outputs
  arrowV(s,5.55+1.0, 2.8, 1.35+0.45, C.purple, 0.8); // up to Diagnostic Report
  arrowV(s,5.55+1.0, 2.8, 2.35+0.45, C.teal, 0.8);   // same level for Action Pack
  arrowV(s,5.55+1.0, 2.8, 3.35+0.45, C.amber, 0.8);  // down to Market Intel
  // Horizontal from Assessment to split
  arrowH(s,4.9,2.8,5.55,C.teal,1.5);

  // Q&A — user-initiated
  s.addShape(pres.shapes.RECTANGLE,{x:8.1,y:4.35,w:1.4,h:0.9,fill:{color:C.navy},line:{color:C.navy},shadow:shadow()});
  s.addText("Tab 4\nQ&A",{x:8.1,y:4.35,w:1.4,h:0.9,fontSize:10,bold:true,color:C.white,fontFace:"Calibri",align:"center",valign:"middle"});
  s.addText("(user-initiated,\nper question)",{x:8.1,y:4.92,w:1.4,h:0.3,fontSize:7.5,color:C.mgray,fontFace:"Calibri",align:"center"});
  arrowD(s,3.1,3.25,-0.8,1.55,C.mgray,0.8);
  smallBox(s,0.5,4.55,1.8,0.7,"Q&A\nAPI Call",C.navy);
  arrowH(s,2.3,4.9,8.1,C.navy,0.8);

  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:5.22,w:9.0,h:0.3,fill:{color:C.lgray},line:{color:"E5E7EB",width:0.3}});
  s.addText([{text:"Key: ",options:{bold:true,color:C.navy}},{text:"Action Pack and Market Intel are triggered immediately after assessment — not on-demand. They run in parallel, keeping total time under 60s. Q&A fires per user question.",options:{color:C.dgray}}],
    {x:0.65,y:5.24,w:8.7,h:0.26,fontSize:8.5,fontFace:"Calibri",valign:"middle"});
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 13 — SECTION: DATA ARCHITECTURE & PRIVACY
// ═══════════════════════════════════════════════════════════════════════
sectionSlide("03 — Data Architecture & Privacy","Session-only model · GDPR/CCPA by design · zero persistent storage in Phase 1");

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 14 — SESSION-ONLY DATA MODEL
// ═══════════════════════════════════════════════════════════════════════
{
  const s = slide("Session-only data model — what's stored and where");

  const rows=[
    {label:"Domain inputs (KPI descriptions)",where:"Browser session (st.session_state)",persist:"Tab close → gone",icon:C.teal},
    {label:"Financial data (CBA optional)",where:"Browser session only — never logged",persist:"Tab close → gone",icon:C.teal},
    {label:"Assessment results / scores",where:"Browser session (st.session_state)",persist:"Tab close → gone",icon:C.teal},
    {label:"Consent checkbox state",where:"Browser session",persist:"Tab close → gone",icon:C.teal},
    {label:"API call payloads",where:"Anthropic API (per their Privacy Policy)",persist:"Per Anthropic retention",icon:C.amber},
    {label:"Web search queries",where:"Anthropic infrastructure only",persist:"Not accessible to us",icon:C.amber},
    {label:"Org profile / KPI history",where:"SQLite (Phase 2, opt-in only)",persist:"User-controlled, deletable",icon:C.purple},
  ];

  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:1.12,w:9.0,h:0.42,fill:{color:C.navy},line:{color:C.navy}});
  ["Data type","Where it lives","Persistence"].forEach((h,i)=>{
    s.addText(h,{x:0.65+i*3.0,y:1.14,w:2.8,h:0.38,fontSize:10,bold:true,color:C.white,fontFace:"Calibri",valign:"middle"});
  });

  rows.forEach((r,i)=>{
    const y=1.54+i*0.48, bg=i%2===0?C.white:C.lgray;
    s.addShape(pres.shapes.RECTANGLE,{x:0.5,y,w:9.0,h:0.46,fill:{color:bg},line:{color:"E5E7EB",width:0.3}});
    s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:y+0.09,w:0.06,h:0.28,fill:{color:r.icon},line:{color:r.icon}});
    s.addText(r.label,  {x:0.7, y:y+0.05,w:2.9,h:0.38,fontSize:9.5,color:C.dgray, fontFace:"Calibri",valign:"middle"});
    s.addText(r.where,  {x:3.65,y:y+0.05,w:2.9,h:0.38,fontSize:9.5,color:C.dgray, fontFace:"Calibri",valign:"middle"});
    s.addText(r.persist,{x:6.6, y:y+0.05,w:2.8,h:0.38,fontSize:9.5,color:r.icon===C.teal?C.teal:r.icon===C.amber?C.amber:C.purple,bold:true,fontFace:"Calibri",valign:"middle"});
  });

  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:4.95,w:9.0,h:0.52,fill:{color:C.mintbg},line:{color:"D1FAE5",width:0.5}});
  s.addText([{text:"GDPR / CCPA: ",options:{bold:true,color:C.teal}},{text:"No data subject rights requests possible — because no personal data is retained. Session expiry satisfies access, correction, and deletion rights automatically.",options:{color:C.dgray}}],
    {x:0.65,y:4.97,w:8.7,h:0.48,fontSize:9,fontFace:"Calibri",valign:"middle"});
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 15 — DIAGRAM: DATA FLOW
// ═══════════════════════════════════════════════════════════════════════
{
  const s = slide("Data flow — what enters, what leaves, what's stored");

  // Three zones
  s.addShape(pres.shapes.RECTANGLE,{x:0.4,y:1.1,w:2.8,h:4.3,fill:{color:"F0EFF9"},line:{color:"C4B5FD",width:0.8}});
  s.addText("BROWSER",{x:0.4,y:1.12,w:2.8,h:0.28,fontSize:8,bold:true,color:C.purple,fontFace:"Calibri",align:"center"});

  s.addShape(pres.shapes.RECTANGLE,{x:3.4,y:1.1,w:3.2,h:4.3,fill:{color:"F0FDF4"},line:{color:"86EFAC",width:0.8}});
  s.addText("NETWORK / API",{x:3.4,y:1.12,w:3.2,h:0.28,fontSize:8,bold:true,color:C.teal,fontFace:"Calibri",align:"center"});

  s.addShape(pres.shapes.RECTANGLE,{x:6.8,y:1.1,w:2.7,h:4.3,fill:{color:"FFFBEB"},line:{color:"FDE68A",width:0.8}});
  s.addText("ANTHROPIC INFRA",{x:6.8,y:1.12,w:2.7,h:0.28,fontSize:8,bold:true,color:C.amber,fontFace:"Calibri",align:"center"});

  const browserItems=[
    ["User inputs","KPI descriptions\nVertical · Persona"],
    ["Financial data","Optional · consent\ngated · never logged"],
    ["Session state","st.session_state\nExpires on tab close"],
    ["Results display","Scores · charts\nPDF export"],
  ];
  browserItems.forEach(([title,detail],i)=>{
    s.addShape(pres.shapes.RECTANGLE,{x:0.55,y:1.52+i*0.88,w:2.5,h:0.78,fill:{color:C.white},line:{color:"C4B5FD",width:0.5}});
    s.addText(title, {x:0.65,y:1.55+i*0.88,w:2.3,h:0.28,fontSize:9,bold:true,color:C.purple,fontFace:"Calibri"});
    s.addText(detail,{x:0.65,y:1.8+i*0.88,w:2.3,h:0.46,fontSize:8,color:C.dgray,fontFace:"Calibri",valign:"top"});
  });

  // Horizontal arrows: browser → network → anthropic
  [1.85,2.73,3.61].forEach(y=>{
    arrowH(s,3.05,y,3.4,C.teal,1.0);
    arrowH(s,6.6,y,6.8,C.amber,1.0);
  });

  s.addShape(pres.shapes.RECTANGLE,{x:3.55,y:1.52,w:2.9,h:0.78,fill:{color:C.white},line:{color:"86EFAC",width:0.5}});
  s.addText("HTTPS encrypted\nAPI payload",{x:3.65,y:1.56,w:2.7,h:0.32,fontSize:9,bold:true,color:C.teal,fontFace:"Calibri"});
  s.addText("Prompt + inputs →\n← Response text",{x:3.65,y:1.86,w:2.7,h:0.38,fontSize:8,color:C.dgray,fontFace:"Calibri",valign:"top"});

  s.addShape(pres.shapes.RECTANGLE,{x:3.55,y:2.42,w:2.9,h:0.78,fill:{color:C.white},line:{color:"86EFAC",width:0.5}});
  s.addText("Search queries",{x:3.65,y:2.46,w:2.7,h:0.28,fontSize:9,bold:true,color:C.teal,fontFace:"Calibri"});
  s.addText("Sent to Anthropic\nnot to search engine",{x:3.65,y:2.72,w:2.7,h:0.44,fontSize:8,color:C.dgray,fontFace:"Calibri",valign:"top"});

  const anthItems=[["Claude Sonnet","Model inference"],["web_search","Tool execution"],["Response","Returned to app"]];
  anthItems.forEach(([t,d],i)=>{
    s.addShape(pres.shapes.RECTANGLE,{x:6.95,y:1.52+i*0.88,w:2.4,h:0.78,fill:{color:C.white},line:{color:"FDE68A",width:0.5}});
    s.addText(t,{x:7.05,y:1.55+i*0.88,w:2.2,h:0.28,fontSize:9,bold:true,color:C.amber,fontFace:"Calibri"});
    s.addText(d,{x:7.05,y:1.82+i*0.88,w:2.2,h:0.44,fontSize:8,color:C.dgray,fontFace:"Calibri",valign:"top"});
  });

  s.addShape(pres.shapes.RECTANGLE,{x:0.55,y:4.95,w:2.5,h:0.36,fill:{color:C.teal},line:{color:C.teal}});
  s.addText("NOTHING STORED",{x:0.55,y:4.95,w:2.5,h:0.36,fontSize:9.5,bold:true,color:C.white,fontFace:"Calibri",align:"center",valign:"middle"});
  s.addText("Phase 1 — no database, no logs, no analytics",{x:3.4,y:4.98,w:6.1,h:0.3,fontSize:9,color:C.mgray,fontFace:"Calibri",valign:"middle"});
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 16 — GDPR / CCPA COMPLIANCE
// ═══════════════════════════════════════════════════════════════════════
{
  const s = slide("GDPR & CCPA compliance — by design, not by policy");

  const principles=[
    {t:"Data minimisation",b:"No persistent storage in Phase 1. Session state is the only memory. Everything discarded on tab close or session expiry. No analytics, no tracking, no cookies beyond what Streamlit requires.",a:C.teal,bg:C.mintbg},
    {t:"Purpose limitation",b:"Financial data entered in the CBA section is used solely to generate cost-benefit estimates during the active session. It is never transmitted for any other purpose.",a:C.purple,bg:C.offwht},
    {t:"Explicit consent",b:"A consent checkbox must be actively checked before financial input fields appear. The full assessment runs without any financial data. Consent is not pre-ticked.",a:C.amber,bg:C.amberbg},
    {t:"Data subject rights",b:"Satisfied automatically. No stored data means no access, correction, or deletion request is possible — or necessary. There is nothing to retrieve, correct, or delete.",a:C.teal,bg:C.mintbg},
    {t:"Third-party processing",b:"Anthropic processes API payloads under their own Privacy Policy and DPA. The app does not send data to any other third party. No marketing tools or analytics SDKs integrated.",a:C.navy,bg:C.lgray},
    {t:"Regulatory basis",b:"Operated under GDPR (EU) 2016/679 and the California Consumer Privacy Act (CCPA). No personal data is stored beyond the active session — compliance surface is minimal by design.",a:C.purple,bg:C.offwht},
  ];
  principles.forEach((p,i)=>{
    const col=i%3, row=Math.floor(i/3);
    infoCard(s,0.5+col*3.07,1.12+row*2.15,2.88,2.0,p.t,p.b,p.a,p.bg);
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 17 — SECTION: PHASE 2 INFRASTRUCTURE
// ═══════════════════════════════════════════════════════════════════════
sectionSlide("04 — Phase 2 Infrastructure","Built & ready · gated by feature flags · available to self-hosters today");

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 18 — PHASE 2 ARCHITECTURE DIAGRAM
// ═══════════════════════════════════════════════════════════════════════
{
  const s = slide("Phase 2 architecture — what's built vs. what's gated");

  // Central: app.py
  smallBox(s,4.1,2.35,1.8,0.9,"app.py\nStreamlit",C.purple);

  // Feature flags gate
  s.addShape(pres.shapes.RECTANGLE,{x:3.85,y:1.5,w:2.3,h:0.6,fill:{color:C.lgray},line:{color:"D1D5DB",width:0.8,dashType:"dash"}});
  s.addText("Feature Flag Check",{x:3.85,y:1.5,w:2.3,h:0.6,fontSize:8.5,bold:true,color:C.mgray,fontFace:"Calibri",align:"center",valign:"middle"});
  arrowV(s,5.0,2.1,2.35,C.mgray,1.0);

  // Left side modules — horizontal arrows from each module right edge to app.py left edge
  smallBox(s,1.0,1.55,1.85,0.78,"Cross-Session\nMemory (SQLite)",C.teal);
  arrowH(s,2.85,1.55+0.39, 4.1, C.teal,1.2);

  smallBox(s,1.0,2.65,1.85,0.78,"Proactive\nAlert Engine",C.purple);
  arrowH(s,2.85,2.65+0.39, 4.1, C.purple,1.2);

  smallBox(s,1.0,3.75,1.85,0.78,"Supabase\n(at scale)",C.mgray);
  // Arrow FROM app.py TO Supabase — from app.py left edge (x=4.1) to Supabase right edge (x=2.85)
  arrowH(s,4.1,3.75+0.39, 2.85, C.mgray, 0.8);

  // Right side modules
  smallBox(s,7.15,1.55,1.85,0.78,"Slack\nIntegration",C.teal);
  arrowH(s,5.9,2.6+0.1, 7.15, C.teal,1.2);

  smallBox(s,7.15,2.65,1.85,0.78,"Email\nDispatcher",C.purple);
  arrowH(s,5.9,2.8+0.05, 7.15, C.purple,1.2);

  smallBox(s,7.15,3.75,1.85,0.78,"Jira\nIntegration",C.amber);
  arrowH(s,5.9,3.0+0.35, 7.15, C.amber,1.2);

  s.addText("PHASE 2 MODULES (built, gated by tier)",{x:0.5,y:4.95,w:9.0,h:0.28,fontSize:9,bold:true,color:C.mgray,fontFace:"Calibri",align:"center"});

  const badgeItems=[["SQLite Memory","Pro+",C.teal],["Alert Engine","Pro+",C.teal],["Slack/Email","Pro+",C.teal],["Jira","Team+",C.amber],["Supabase","Scale",C.mgray]];
  badgeItems.forEach(([l,t,c],i)=>{
    badge(s,0.5+i*1.8,5.1,`${l} · ${t}`,c);
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 19 — CROSS-SESSION MEMORY
// ═══════════════════════════════════════════════════════════════════════
{
  const s = slide("Cross-session memory — SQLite engine (Phase 2)");

  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:1.12,w:4.8,h:4.3,fill:{color:C.code},line:{color:"2D3748",width:0.5},shadow:shadow()});
  s.addText("-- memory/schema.sql",{x:0.7,y:1.18,w:4.5,h:0.25,fontSize:8.5,color:"64748B",fontFace:"Courier New"});
  const sqlLines=[
    {text:"CREATE TABLE ",options:{color:C.codekw}},{text:"organisations",options:{color:C.codehi}},{text:" (\n",options:{color:C.white}},
    {text:"    id          ",options:{color:C.codehi}},{text:"INTEGER ",options:{color:C.codekw}},{text:"PRIMARY KEY",options:{color:C.codekw}},{text:",\n",options:{color:C.white}},
    {text:"    org_name    ",options:{color:C.codehi}},{text:"TEXT",options:{color:C.codekw}},{text:",\n",options:{color:C.white}},
    {text:"    vertical    ",options:{color:C.codehi}},{text:"TEXT",options:{color:C.codekw}},{text:",\n",options:{color:C.white}},
    {text:"    created_at  ",options:{color:C.codehi}},{text:"TIMESTAMP\n",options:{color:C.codekw}},
    {text:");\n\n",options:{color:C.white}},
    {text:"CREATE TABLE ",options:{color:C.codekw}},{text:"assessments",options:{color:C.codehi}},{text:" (\n",options:{color:C.white}},
    {text:"    id          ",options:{color:C.codehi}},{text:"INTEGER ",options:{color:C.codekw}},{text:"PRIMARY KEY",options:{color:C.codekw}},{text:",\n",options:{color:C.white}},
    {text:"    org_id      ",options:{color:C.codehi}},{text:"INTEGER ",options:{color:C.codekw}},{text:"REFERENCES",options:{color:C.codekw}},{text:" orgs,\n",options:{color:C.white}},
    {text:"    run_at      ",options:{color:C.codehi}},{text:"TIMESTAMP",options:{color:C.codekw}},{text:",\n",options:{color:C.white}},
    {text:"    scores_json ",options:{color:C.codehi}},{text:"TEXT",options:{color:C.codekw}},{text:",\n",options:{color:C.white}},
    {text:"    overall     ",options:{color:C.codehi}},{text:"REAL",options:{color:C.codekw}},{text:",\n",options:{color:C.white}},
    {text:"    inputs_hash ",options:{color:C.codehi}},{text:"TEXT",options:{color:C.codekw}},{text:"\n);\n\n",options:{color:C.white}},
    {text:"-- KPI trend tracking\n",options:{color:"64748B"}},
    {text:"CREATE TABLE ",options:{color:C.codekw}},{text:"kpi_snapshots",options:{color:C.codehi}},{text:" (\n",options:{color:C.white}},
    {text:"    ...\n",options:{color:"64748B"}},
    {text:"    domain, score, recorded_at\n",options:{color:C.codehi}},
    {text:");",options:{color:C.white}},
  ];
  s.addText(sqlLines,{x:0.7,y:1.48,w:4.4,h:3.8,fontSize:8.2,fontFace:"Courier New",valign:"top",lineSpacing:12});

  const cards=[
    {t:"What it enables",b:"Persistent org profiles across sessions. KPI trend lines over time — 'your OTIF was 82% in March, 88% now'. Claude remembers your vertical, context, and previous scores to give richer follow-up assessments.",a:C.teal},
    {t:"Phase 1 → Phase 2 migration",b:"The schema is designed so Phase 1 (session-only) needs no schema changes to enable. Flip the feature flag, add the SQLite file path to secrets, and memory activates. Zero app code change.",a:C.purple},
    {t:"Scale path",b:"SQLite handles thousands of org profiles with no performance concerns. At enterprise scale, the engine transparently migrates to Supabase — same queries, same models, connection string swap only.",a:C.amber},
  ];
  cards.forEach((c,i)=>infoCard(s,5.55,1.12+i*1.48,3.95,1.36,c.t,c.b,c.a,C.lgray));
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 20 — PROACTIVE ALERT ENGINE
// ═══════════════════════════════════════════════════════════════════════
{
  const s = slide("Proactive alert engine — risk monitoring before you ask (Phase 2)");

  // Linear flow diagram — all horizontal, clearly spaced
  const bw=1.72, bh=0.8, y=1.55, gap=0.22;
  smallBox(s,0.5,       y,bw,bh,"Scheduled\nTrigger",  C.purple);
  arrowH(s,0.5+bw,      y+bh/2, 0.5+bw+gap,          C.purple,1.5);
  smallBox(s,0.5+bw+gap,y,bw,bh,"Load Org\nProfiles",  C.teal);
  arrowH(s,0.5+(bw+gap)+bw, y+bh/2, 0.5+(bw+gap)*2,  C.teal,1.5);
  smallBox(s,0.5+(bw+gap)*2,y,bw,bh,"Claude + Search\nRisk Scan",C.amber);
  arrowH(s,0.5+(bw+gap)*2+bw, y+bh/2, 0.5+(bw+gap)*3,C.amber,1.5);
  smallBox(s,0.5+(bw+gap)*3,y,bw,bh,"Score\nChange?",  C.navy);

  // YES branch — down then fan out to channels
  const decCx = 0.5+(bw+gap)*3 + bw/2;
  arrowV(s,decCx, y+bh, y+bh+0.35, C.teal, 1.2);
  s.addText("YES",{x:decCx+0.06,y:y+bh+0.04,w:0.5,h:0.2,fontSize:7.5,color:C.teal,fontFace:"Calibri"});
  smallBox(s,0.5+(bw+gap)*3,y+bh+0.35,bw,bh,"Dispatch\nAlerts",C.teal);

  // Three alert channels — placed below Dispatch Alerts, evenly spread
  const channels=[["Slack","Push to channel",C.teal],["Email","Branded HTML",C.purple],["In-app","Next session",C.amber]];
  const dispatchBox_y = y+bh+0.35;
  const dispatchBox_cx = 0.5+(bw+gap)*3 + bw/2;
  channels.forEach(([ch,sub,c],i)=>{
    const cx = 1.5 + i*3.0;
    arrowV(s,dispatchBox_cx, dispatchBox_y+bh, dispatchBox_y+bh+0.3, c, 0.8);
    smallBox(s,cx-0.85,dispatchBox_y+bh+0.3,1.7,0.72,`${ch}\n${sub}`,c);
  });

  // What triggers it — below the flow, full width
  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:3.95,w:9.0,h:1.6,fill:{color:C.lgray},line:{color:"E5E7EB",width:0.5},shadow:makeSh()});
  s.addText("What triggers an alert",{x:0.65,y:4.0,w:8.7,h:0.3,fontSize:11,bold:true,color:C.navy,fontFace:"Calibri"});
  const triggers=["Domain score drops >10 points vs last assessment","Live web search finds new regulation affecting your vertical","Commodity price move exceeds threshold for your supply chain","Geopolitical risk event in your supplier geography","Competitor or benchmark shift changes your relative position"];
  s.addText(triggers.map(t=>({text:t,options:{bullet:true,breakLine:true,paraSpaceAfter:3}})),{
    x:0.7,y:4.32,w:8.6,h:1.18,fontSize:9,color:C.dgray,fontFace:"Calibri",valign:"top"
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 21 — INTEGRATION SURFACE
// ═══════════════════════════════════════════════════════════════════════
{
  const s = slide("Integration surface — Slack, Email, Jira (Phase 2)");

  const integrations=[
    {name:"Slack",file:"integrations/slack.py",what:"Push assessment summaries, action plans and risk alerts to configured channels.",config:"SLACK_BOT_TOKEN + SLACK_CHANNEL_ID via Streamlit secrets.",sample:"Bot posts: '⚠️ Risk score dropped to 52 in Semiconductor vertical. 3 alerts flagged.'",accent:C.teal,bg:C.mintbg},
    {name:"Email Dispatcher",file:"integrations/email.py",what:"Branded HTML email reports with domain scores, top risks and action plan. Sent via SendGrid.",config:"SENDGRID_API_KEY + FROM_EMAIL + recipient list.",sample:"Subject: 'SC Health Alert — Risk & Resilience score dropped to 52/100'",accent:C.purple,bg:C.offwht},
    {name:"Jira Integration",file:"integrations/jira.py",what:"Creates Jira issues from 90-day action plan items. One issue per action with owner, due date and description auto-populated.",config:"JIRA_URL + JIRA_API_TOKEN + JIRA_PROJECT_KEY.",sample:"Creates: '[SC-ACTION] Map all Tier-1 suppliers'  ·  Assignee: Procurement  ·  Due: +28 days",accent:C.amber,bg:C.amberbg},
  ];
  integrations.forEach((integ,i)=>{
    const y=1.12+i*1.42;
    s.addShape(pres.shapes.RECTANGLE,{x:0.5,y,w:9.0,h:1.34,fill:{color:integ.bg},line:{color:"E5E7EB",width:0.5},shadow:makeSh()});
    s.addShape(pres.shapes.RECTANGLE,{x:0.5,y,w:0.06,h:1.34,fill:{color:integ.accent},line:{color:integ.accent}});
    s.addText([{text:integ.name,options:{bold:true,color:integ.accent}},{text:"  —  ",options:{color:C.mgray}},{text:integ.file,options:{color:C.mgray,italic:true}}],{x:0.72,y:y+0.07,w:8.6,h:0.28,fontSize:10.5,fontFace:"Calibri"});
    s.addText(integ.what,  {x:0.72,y:y+0.36,w:8.5,h:0.26,fontSize:9,color:C.dgray,fontFace:"Calibri"});
    s.addText([{text:"Config: ",options:{bold:true,color:C.dgray}},{text:integ.config,options:{color:C.mgray}}],{x:0.72,y:y+0.63,w:8.5,h:0.22,fontSize:8.5,fontFace:"Calibri"});
    s.addText([{text:"Example: ",options:{bold:true,color:integ.accent}},{text:integ.sample,options:{color:C.dgray,italic:true}}],{x:0.72,y:y+0.88,w:8.5,h:0.38,fontSize:8,fontFace:"Calibri",valign:"top"});
  });

  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:5.42,w:9.0,h:0.26,fill:{color:C.lgray},line:{color:"E5E7EB"}});
  s.addText("All integrations activate via feature flag + secrets only — no code changes required.",{x:0.65,y:5.44,w:8.7,h:0.22,fontSize:8.5,color:C.mgray,fontFace:"Calibri",valign:"middle"});
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 22 — FEATURE FLAG SYSTEM
// ═══════════════════════════════════════════════════════════════════════
{
  const s = slide("Feature flag system — 60+ flags, 6 tiers, no pricing in application code");

  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:1.12,w:4.85,h:3.0,fill:{color:C.code},line:{color:"2D3748",width:0.5},shadow:shadow()});
  s.addText("# phase2_config.py — feature flag pattern",{x:0.7,y:1.18,w:4.5,h:0.25,fontSize:8.5,color:"64748B",fontFace:"Courier New"});
  const ffLines=[
    {text:"TIER_FEATURES",options:{color:C.codehi}},{text:" = {\n",options:{color:C.white}},
    {text:'    "free"',options:{color:C.codestr}},{text:": [",options:{color:C.white}},{text:'"core"',options:{color:C.codestr}},{text:", ",options:{color:C.white}},{text:'"verticals"',options:{color:C.codestr}},{text:", ...],\n",options:{color:C.white}},
    {text:'    "pro"',options:{color:C.codestr}},{text:": [",options:{color:C.white}},{text:'"alerts"',options:{color:C.codestr}},{text:", ",options:{color:C.white}},{text:'"slack"',options:{color:C.codestr}},{text:", ",options:{color:C.white}},{text:'"memory"',options:{color:C.codestr}},{text:", ...],\n",options:{color:C.white}},
    {text:'    "team"',options:{color:C.codestr}},{text:": [",options:{color:C.white}},{text:'...pro + "jira"',options:{color:C.codestr}},{text:", ...],\n",options:{color:C.white}},
    {text:'    "enterprise"',options:{color:C.codestr}},{text:": [...team + ",options:{color:C.white}},{text:'"sso"',options:{color:C.codestr}},{text:"],\n",options:{color:C.white}},
    {text:"}\n\n",options:{color:C.white}},
    {text:"def ",options:{color:C.codekw}},{text:"is_enabled",options:{color:C.codefn}},{text:"(feature, user_tier):\n",options:{color:C.white}},
    {text:"    tier_features = TIER_FEATURES.get(\n",options:{color:C.white}},
    {text:"        user_tier, []\n",options:{color:C.white}},
    {text:"    )\n",options:{color:C.white}},
    {text:"    ",options:{color:C.white}},{text:"return",options:{color:C.codekw}},{text:" feature ",options:{color:C.white}},{text:"in",options:{color:C.codekw}},{text:" tier_features\n\n",options:{color:C.white}},
    {text:"# Usage — gating in app.py:\n",options:{color:"64748B"}},
    {text:"if",options:{color:C.codekw}},{text:" is_enabled(",options:{color:C.white}},{text:'"slack"',options:{color:C.codestr}},{text:", user.tier):\n",options:{color:C.white}},
    {text:"    slack.push(assessment_summary)",options:{color:C.codefn}},
  ];
  s.addText(ffLines,{x:0.7,y:1.48,w:4.5,h:2.5,fontSize:8.5,fontFace:"Courier New",valign:"top",lineSpacing:12});

  const tiers=[
    {name:"Open Source",count:"Core",color:C.mgray},
    {name:"Hosted Free",count:"Core + Hosted",color:"3B8BD4"},
    {name:"Pro",count:"+ Alerts · Slack · Email · Memory",color:C.purple},
    {name:"Team",count:"+ Jira · White-label · Multi-client",color:C.teal},
    {name:"Enterprise",count:"+ SSO · API · Webhooks · Custom",color:C.amber},
    {name:"Gov",count:"+ FedRAMP · Air-gap · FIPS",color:C.red},
  ];
  tiers.forEach((t,i)=>{
    const y=1.12+i*0.68;
    s.addShape(pres.shapes.RECTANGLE,{x:5.55,y,w:3.95,h:0.6,fill:{color:C.lgray},line:{color:"E5E7EB",width:0.4}});
    s.addShape(pres.shapes.RECTANGLE,{x:5.55,y,w:0.06,h:0.6,fill:{color:t.color},line:{color:t.color}});
    s.addText(t.name,{x:5.72,y:y+0.06,w:1.4,h:0.26,fontSize:10,bold:true,color:t.color,fontFace:"Calibri"});
    s.addText(t.count,{x:5.72,y:y+0.32,w:3.6,h:0.22,fontSize:8.5,color:C.mgray,fontFace:"Calibri"});
  });

  s.addShape(pres.shapes.RECTANGLE,{x:5.55,y:5.2,w:3.95,h:0.28,fill:{color:C.mintbg},line:{color:"D1FAE5",width:0.5}});
  s.addText("Pricing never touches application code — feature flags only.",{x:5.65,y:5.21,w:3.75,h:0.26,fontSize:9,bold:true,color:C.teal,fontFace:"Calibri",valign:"middle"});

  infoCard(s,0.5,4.28,4.85,1.18,"Why this design",
    "Tier upgrades are a config change, not a deployment. Pricing is in the business layer, not the application layer. Engineering can build all features without knowing the price — pricing decisions happen after build.",
    C.purple,C.offwht);
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 23 — SECTION: DEPLOYMENT & SCALING
// ═══════════════════════════════════════════════════════════════════════
sectionSlide("05 — Deployment & Scaling","Current infrastructure · scaling path · environment configuration");

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 24 — DEPLOYMENT ARCHITECTURE DIAGRAM
// ═══════════════════════════════════════════════════════════════════════
{
  const s = slide("Deployment architecture — current and future paths");

  // Current path
  s.addText("CURRENT (Phase 1)",{x:0.5,y:1.12,w:9.0,h:0.3,fontSize:10,bold:true,color:C.purple,fontFace:"Calibri"});
  s.addShape(pres.shapes.LINE,{x:0.5,y:1.42,w:9.0,h:0,line:{color:C.purple,width:0.8}});

  const cur=[["Developer\nMachine",C.mgray],["GitHub\ngithub.com/...",C.navy],["Streamlit Cloud\nAuto-deploy",C.purple],["Users\n(Browser)",C.teal]];
  cur.forEach(([label,c],i)=>{
    smallBox(s,0.5+i*2.25,1.5,1.8,0.75,label,c);
    if(i<cur.length-1) arrowH(s,0.5+i*2.25+1.8, 1.875, 0.5+(i+1)*2.25, c, 1.5);
  });

  // Secrets note
  s.addShape(pres.shapes.RECTANGLE,{x:5.3,y:2.35,w:1.9,h:0.6,fill:{color:C.amberbg},line:{color:"FDE68A",width:0.6,dashType:"dash"}});
  s.addText("secrets.toml\nANTHROPIC_API_KEY",{x:5.3,y:2.35,w:1.9,h:0.6,fontSize:7.5,color:C.amber,fontFace:"Calibri",align:"center",valign:"middle"});
  arrowV(s,6.25,2.35,2.25,C.amber,0.8);

  // Future path
  s.addText("SCALING PATH (Phase 2+)",{x:0.5,y:3.15,w:9.0,h:0.3,fontSize:10,bold:true,color:C.teal,fontFace:"Calibri"});
  s.addShape(pres.shapes.LINE,{x:0.5,y:3.45,w:9.0,h:0,line:{color:C.teal,width:0.8}});

  const futurePaths=[
    {label:"Railway / Render\nFull backend",color:C.teal},
    {label:"FastAPI\nWebhook receiver",color:C.purple},
    {label:"Supabase\nPersistent storage",color:C.amber},
    {label:"Stripe\nPaywall / billing",color:C.navy},
    {label:"Enterprise\nCustom deploy",color:C.red},
  ];
  futurePaths.forEach((p,i)=>{
    const x=0.5+i*1.82;
    smallBox(s,x,3.52,1.7,0.75,p.label,p.color);
    if(i<futurePaths.length-1) arrowH(s,x+1.7,3.895,x+1.82,p.color,0.8);
  });

  // Self-host note
  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:4.42,w:9.0,h:0.85,fill:{color:C.lgray},line:{color:"E5E7EB",width:0.5}});
  s.addText("Self-hosting (available today — MIT License)",{x:0.65,y:4.47,w:8.7,h:0.28,fontSize:10.5,bold:true,color:C.navy,fontFace:"Calibri"});
  s.addText("Clone the repo → pip install -r requirements.txt → add .env with ANTHROPIC_API_KEY → streamlit run app.py. All Phase 2 infrastructure (memory, alerts, integrations) is available immediately to self-hosters by enabling the relevant feature flags and providing the config secrets.",{
    x:0.65,y:4.76,w:8.7,h:0.45,fontSize:8.5,color:C.dgray,fontFace:"Calibri",valign:"top"
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 25 — API COST MODEL & SCALING
// ═══════════════════════════════════════════════════════════════════════
{
  const s = slide("API cost model & scaling path — unit economics for engineers");

  const costRows=[
    {op:"Standard assessment (no web search)",input:"~2,000",output:"~1,500",cost:"$0.04–$0.06"},
    {op:"Assessment + web search (5 searches)",input:"~3,500",output:"~1,500",cost:"$0.12–$0.22"},
    {op:"Executive assessment (scenario + roadmap)",input:"~4,500",output:"~4,000",cost:"$0.20–$0.35"},
    {op:"Auto Action Pack (parallel call)",input:"~3,000",output:"~2,000",cost:"$0.08–$0.15"},
    {op:"Market Intelligence (parallel call)",input:"~1,500",output:"~1,000",cost:"$0.04–$0.08"},
    {op:"Proactive alert scan (Phase 2)",input:"~2,000",output:"~800",cost:"$0.05–$0.12"},
  ];

  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:1.12,w:9.0,h:0.4,fill:{color:C.navy},line:{color:C.navy}});
  [["Operation",3.5],["Input tokens",1.2],["Output tokens",1.3],["Est. cost",1.5]].reduce((x,[h,w])=>{
    s.addText(h,{x,y:1.12,w,h:0.4,fontSize:9.5,bold:true,color:C.white,fontFace:"Calibri",valign:"middle",margin:5});
    return x+w+0.35;
  },0.6);

  costRows.forEach((r,i)=>{
    const y=1.52+i*0.42, bg=i%2===0?C.white:C.lgray;
    s.addShape(pres.shapes.RECTANGLE,{x:0.5,y,w:9.0,h:0.4,fill:{color:bg},line:{color:"E5E7EB",width:0.3}});
    s.addText(r.op,     {x:0.6,y:y+0.03,w:3.45,h:0.34,fontSize:9,color:C.dgray,fontFace:"Calibri",valign:"middle"});
    s.addText(r.input,  {x:4.1,y:y+0.03,w:1.15,h:0.34,fontSize:9,color:C.dgray,fontFace:"Calibri",valign:"middle",align:"center"});
    s.addText(r.output, {x:5.3,y:y+0.03,w:1.25,h:0.34,fontSize:9,color:C.dgray,fontFace:"Calibri",valign:"middle",align:"center"});
    s.addText(r.cost,   {x:6.65,y:y+0.03,w:1.45,h:0.34,fontSize:9,bold:true,color:C.teal,fontFace:"Calibri",valign:"middle",align:"center"});
  });

  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:4.15,w:9.0,h:1.3,fill:{color:C.mintbg},line:{color:"D1FAE5",width:0.5}});
  s.addText("Unit economics at 50 Pro customers",{x:0.65,y:4.2,w:8.7,h:0.3,fontSize:11,bold:true,color:C.teal,fontFace:"Calibri"});
  const econ=[
    ["Revenue","~$20,000/mo","(50 × $399)"],
    ["API cost","~$800–$2,000/mo","(varies by usage intensity)"],
    ["Gross margin","~90%+","primary cost is Anthropic API"],
  ];
  econ.forEach(([l,v,n],i)=>{
    s.addText([{text:l+": ",options:{bold:true,color:C.teal}},{text:v,options:{bold:true,color:C.navy}},{text:"  "+n,options:{color:C.mgray}}],{
      x:0.65,y:4.52+i*0.26,w:8.7,h:0.24,fontSize:9.5,fontFace:"Calibri"
    });
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 26 — ENVIRONMENT & SECRETS
// ═══════════════════════════════════════════════════════════════════════
{
  const s = slide("Environment configuration & secrets management");

  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:1.12,w:4.5,h:2.4,fill:{color:C.code},line:{color:"2D3748",width:0.5},shadow:shadow()});
  s.addText("# .env  (local — gitignored)",{x:0.7,y:1.18,w:4.2,h:0.25,fontSize:8.5,color:"64748B",fontFace:"Courier New"});
  const envLines=[
    {text:"ANTHROPIC_API_KEY",options:{color:C.codehi}},{text:'=',options:{color:C.white}},{text:'"sk-ant-..."',options:{color:C.codestr}},{text:"\n",options:{color:C.white}},
    {text:"\n# Phase 2 — add as needed\n",options:{color:"64748B"}},
    {text:"SLACK_BOT_TOKEN",options:{color:C.codehi}},{text:'=',options:{color:C.white}},{text:'"xoxb-..."',options:{color:C.codestr}},{text:"\n",options:{color:C.white}},
    {text:"SLACK_CHANNEL_ID",options:{color:C.codehi}},{text:'=',options:{color:C.white}},{text:'"C0..."',options:{color:C.codestr}},{text:"\n",options:{color:C.white}},
    {text:"SENDGRID_API_KEY",options:{color:C.codehi}},{text:'=',options:{color:C.white}},{text:'"SG...."',options:{color:C.codestr}},{text:"\n",options:{color:C.white}},
    {text:"JIRA_URL",options:{color:C.codehi}},{text:'=',options:{color:C.white}},{text:'"https://..."',options:{color:C.codestr}},{text:"\n",options:{color:C.white}},
    {text:"JIRA_API_TOKEN",options:{color:C.codehi}},{text:'=',options:{color:C.white}},{text:'"..."',options:{color:C.codestr}},{text:"\n",options:{color:C.white}},
    {text:"DATABASE_URL",options:{color:C.codehi}},{text:'=',options:{color:C.white}},{text:'"./memory/sc_health.db"',options:{color:C.codestr}},
  ];
  s.addText(envLines,{x:0.7,y:1.48,w:4.1,h:1.9,fontSize:8.5,fontFace:"Courier New",valign:"top",lineSpacing:12});

  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:3.65,w:4.5,h:1.7,fill:{color:C.code},line:{color:"2D3748",width:0.5},shadow:shadow()});
  s.addText("# Streamlit Cloud: App Settings → Secrets",{x:0.7,y:3.71,w:4.2,h:0.25,fontSize:8.5,color:"64748B",fontFace:"Courier New"});
  const secretLines=[
    {text:"# Paste the .env content directly\n",options:{color:"64748B"}},
    {text:"# into the Secrets text field.\n",options:{color:"64748B"}},
    {text:"# Streamlit exposes as st.secrets[]\n\n",options:{color:"64748B"}},
    {text:"api_key = st.secrets[",options:{color:C.white}},{text:'"ANTHROPIC_API_KEY"',options:{color:C.codestr}},{text:"]\n",options:{color:C.white}},
    {text:"client = anthropic.Anthropic(",options:{color:C.white}},
    {text:"api_key=api_key)",options:{color:C.codefn}},
  ];
  s.addText(secretLines,{x:0.7,y:4.0,w:4.1,h:1.28,fontSize:8.5,fontFace:"Courier New",valign:"top",lineSpacing:12});

  const secNotes=[
    {t:"Never commit .env",b:"The .env file is in .gitignore by default. The API key must never appear in any committed file, commit message, or GitHub issue. Rotate if accidentally exposed.",a:C.red},
    {t:"Streamlit Cloud secrets",b:"Inject secrets via the App Settings panel. They're encrypted at rest and injected as environment variables at runtime. Never use st.write() to display secret values.",a:C.amber},
    {t:"Self-host config",b:"python-dotenv loads .env automatically on startup. No secret should be hardcoded in any .py file. All config is externalised — the app is environment-driven.",a:C.teal},
    {t:"API key scoping",b:"Create a separate Anthropic API key for production vs. development. Allows rotation and spend tracking per environment without touching code.",a:C.purple},
  ];
  secNotes.forEach((n,i)=>infoCard(s,5.2,1.12+i*1.12,4.3,1.02,n.t,n.b,n.a,C.lgray));
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 27 — SECTION: SECURITY & COMPLIANCE
// ═══════════════════════════════════════════════════════════════════════
sectionSlide("06 — Security & Compliance","Threat surface · API key management · what's in scope and what's not");

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 28 — SECURITY MODEL
// ═══════════════════════════════════════════════════════════════════════
{
  const s = slide("Security model — threat surface and mitigations");

  const threats=[
    {threat:"API key exposure",risk:"HIGH",mitigation:"Stored in environment variables only. Never in code, logs, or version control. .gitignore covers .env. Rotate via Anthropic console if suspect compromise.",color:C.red},
    {threat:"Injection via user inputs",risk:"MED",mitigation:"User inputs are passed as message content to Claude, not as system prompt components. Claude is not a code executor — no SQL, shell, or eval path exists in the app.",color:C.amber},
    {threat:"Session data leakage",risk:"LOW",mitigation:"Session state is per-browser tab, per-connection. Streamlit's session model provides natural isolation. No shared state between users on the hosted service.",color:C.teal},
    {threat:"Anthropic API availability",risk:"MED",mitigation:"Graceful degradation to static knowledge if API is unavailable. The BadRequestError fallback covers partial unavailability. No single-point-of-failure in assessment logic.",color:C.amber},
    {threat:"Dependency vulnerabilities",risk:"MED",mitigation:"requirements.txt pins major versions. Dependabot or pip-audit can be enabled on the GitHub repo for automated CVE scanning. Streamlit and anthropic SDK are actively maintained.",color:C.amber},
    {threat:"Data exfiltration via prompt",risk:"LOW",mitigation:"Users input supply chain data voluntarily for their own assessment. No multi-tenancy in Phase 1 — each session is isolated. Phase 2 SQLite is local to the deployment.",color:C.teal},
  ];

  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:1.12,w:9.0,h:0.38,fill:{color:C.navy},line:{color:C.navy}});
  [["Threat vector",2.8],["Risk",0.65],["Mitigation",5.2]].reduce((x,[h,w])=>{
    s.addText(h,{x,y:1.12,w,h:0.38,fontSize:9.5,bold:true,color:C.white,fontFace:"Calibri",valign:"middle",margin:5});
    return x+w+0.2;
  },0.6);

  threats.forEach((t,i)=>{
    const y=1.5+i*0.64, bg=i%2===0?C.white:C.lgray;
    s.addShape(pres.shapes.RECTANGLE,{x:0.5,y,w:9.0,h:0.62,fill:{color:bg},line:{color:"E5E7EB",width:0.3}});
    s.addText(t.threat,    {x:0.6,y:y+0.04,w:2.65,h:0.54,fontSize:9.5,color:C.dgray,fontFace:"Calibri",valign:"middle"});
    s.addShape(pres.shapes.RECTANGLE,{x:3.4,y:y+0.14,w:0.62,h:0.34,fill:{color:t.color},line:{color:t.color}});
    s.addText(t.risk,      {x:3.4,y:y+0.14,w:0.62,h:0.34,fontSize:8,bold:true,color:C.white,fontFace:"Calibri",align:"center",valign:"middle"});
    s.addText(t.mitigation,{x:4.15,y:y+0.04,w:5.2,h:0.54,fontSize:8.5,color:C.dgray,fontFace:"Calibri",valign:"middle"});
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 29 — SECTION: MCP SERVER (NEW — v4.2)
// ═══════════════════════════════════════════════════════════════════════
sectionSlide("07 — MCP Server (v4.2)","AI-native access · stdio transport · 3 free tools · Claude Desktop & Claude Code");

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 30 — MCP ARCHITECTURE OVERVIEW
// ═══════════════════════════════════════════════════════════════════════
{
  const s = slide("MCP server architecture — how it fits into the stack");

  // Left: architecture diagram
  // Three layers: MCP Client → server.py → engine
  const lx=0.5, lw=4.4;

  // MCP Client layer
  s.addShape(pres.shapes.RECTANGLE,{x:lx,y:1.12,w:lw,h:0.78,fill:{color:C.bluebg},line:{color:"BFDBFE",width:0.8}});
  s.addText("MCP CLIENT",{x:lx+0.1,y:1.14,w:1.0,h:0.22,fontSize:7.5,bold:true,color:C.blue,fontFace:"Calibri"});
  const clients=[["Claude Desktop","claude_desktop_config.json"],["Claude Code","claude mcp add ..."]];
  clients.forEach(([c,sub],i)=>{
    smallBox(s,lx+0.2+i*2.0,1.22,1.8,0.56,c+"\n"+sub,C.blue,"FFFFFF",8);
  });

  // stdio transport arrow
  arrowV(s,lx+lw/2, 1.9,2.1,C.blue,1.5);
  s.addText("stdio transport",{x:lx+lw/2+0.08,y:1.92,w:1.4,h:0.2,fontSize:7.5,color:C.blue,fontFace:"Calibri"});

  // server.py layer
  s.addShape(pres.shapes.RECTANGLE,{x:lx,y:2.1,w:lw,h:0.78,fill:{color:"EFF6FF"},line:{color:C.blue,width:0.8}});
  s.addText("mcp_server/server.py",{x:lx+0.12,y:2.14,w:lw-0.24,h:0.28,fontSize:10,bold:true,color:C.blue,fontFace:"Calibri"});
  s.addText("Thin stateless bridge  ·  list_tools()  ·  call_tool()  ·  asyncio.to_thread()",{x:lx+0.12,y:2.42,w:lw-0.24,h:0.38,fontSize:8.5,color:C.dgray,fontFace:"Calibri"});

  // Arrow from server.py down to schemas.py
  arrowV(s,lx+lw/2,2.88,3.05,C.blue,1.0);

  // schemas.py reference
  s.addShape(pres.shapes.RECTANGLE,{x:lx,y:3.05,w:lw,h:0.58,fill:{color:C.lgray},line:{color:"D1D5DB",width:0.5}});
  s.addText("mcp_server/schemas.py  —  single source of truth for all tool contracts",{x:lx+0.12,y:3.08,w:lw-0.24,h:0.52,fontSize:8.5,color:C.dgray,fontFace:"Calibri",valign:"middle"});

  // Arrow to engine
  arrowV(s,lx+lw/2,3.63,3.83,C.teal,1.5);
  s.addText("asyncio.to_thread()",{x:lx+lw/2+0.08,y:3.65,w:1.5,h:0.2,fontSize:7.5,color:C.teal,fontFace:"Calibri"});

  // Engine layer
  s.addShape(pres.shapes.RECTANGLE,{x:lx,y:3.83,w:lw,h:0.78,fill:{color:C.mintbg},line:{color:"86EFAC",width:0.8}});
  s.addText("SCHA Engine",{x:lx+0.12,y:3.87,w:lw-0.24,h:0.28,fontSize:10,bold:true,color:C.teal,fontFace:"Calibri"});
  s.addText("agent.py  ·  domains.py  ·  scoring.py  ·  verticals.py",{x:lx+0.12,y:4.15,w:lw-0.24,h:0.38,fontSize:8.5,color:C.dgray,fontFace:"Calibri"});

  // Right: design principles
  const principles=[
    {t:"Stateless by design",b:"Each MCP tool call is fully self-contained. No session state is held between calls. Inputs carry everything the tool needs — org_name, vertical, persona, domain_responses.",a:C.blue},
    {t:"Free tier only",b:"This MCP server exposes the 3 free-tier tools. Pro-tier tools (financial impact, 3-horizon roadmap, ERP connectors) live in the private stratos-pro repo under Streamable HTTP transport.",a:C.purple},
    {t:"JSON Schema (draft 2020-12)",b:"Every tool has a strictly typed inputSchema and outputSchema. additionalProperties: False on every object. FREE_TOOLS / PRO_TOOLS / ALL_TOOLS registries in schemas.py.",a:C.teal},
    {t:"ToolError clean failures",b:"Validation errors and engine failures surface as ToolError — never raw Python tracebacks. MCP clients receive structured error text the AI can interpret and explain to the user.",a:C.amber},
  ];
  principles.forEach((p,i)=>{
    infoCard(s,5.1,1.12+i*1.12,4.4,1.02,p.t,p.b,p.a,C.lgray);
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 31 — MCP TOOL SCHEMAS
// ═══════════════════════════════════════════════════════════════════════
{
  const s = slide("MCP tool schemas — the 3 free-tier tools (schemas.py)");

  // Left: schemas.py code showing the pattern
  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:1.12,w:4.8,h:4.3,fill:{color:C.code},line:{color:"2D3748",width:0.5},shadow:shadow()});
  s.addText("# mcp_server/schemas.py — tool contract pattern",{x:0.7,y:1.18,w:4.5,h:0.25,fontSize:8.5,color:"64748B",fontFace:"Courier New"});

  const schemaLines=[
    {text:"RUN_ASSESSMENT",options:{color:C.codehi}},{text:" = {\n",options:{color:C.white}},
    {text:'    "name"',options:{color:C.codestr}},{text:':',options:{color:C.white}},{text:'"run_assessment"',options:{color:C.codestr}},{text:",\n",options:{color:C.white}},
    {text:'    "tier"',options:{color:C.codestr}},{text:':',options:{color:C.white}},{text:'"free"',options:{color:C.codestr}},{text:",\n",options:{color:C.white}},
    {text:'    "inputSchema"',options:{color:C.codestr}},{text:": _object(\n",options:{color:C.white}},
    {text:'        properties={\n',options:{color:C.white}},
    {text:'            "org_name"',options:{color:C.codestr}},{text:': {"type":"string"},\n',options:{color:C.white}},
    {text:'            "vertical"',options:{color:C.codestr}},{text:': {"type":"string",\n',options:{color:C.white}},
    {text:'                        "enum":[...11 verticals]},\n',options:{color:"64748B"}},
    {text:'            "persona"',options:{color:C.codestr}},{text:': {"type":"string",\n',options:{color:C.white}},
    {text:'                       "enum":["analyst","executive"]},\n',options:{color:"64748B"}},
    {text:'            "domain_responses"',options:{color:C.codestr}},{text:': {...},\n',options:{color:C.white}},
    {text:'        },\n',options:{color:C.white}},
    {text:'        required=["org_name","vertical","persona"]\n',options:{color:C.codefn}},
    {text:"    ),\n",options:{color:C.white}},
    {text:'    "outputSchema"',options:{color:C.codestr}},{text:": _object(\n",options:{color:C.white}},
    {text:'        properties={"overall_score","domain_scores",\n',options:{color:"64748B"}},
    {text:'                    "narrative","action_pack","findings"},\n',options:{color:"64748B"}},
    {text:"        required=[...]\n    )\n}",options:{color:C.white}},
  ];
  s.addText(schemaLines,{x:0.7,y:1.48,w:4.45,h:3.85,fontSize:8,fontFace:"Courier New",valign:"top",lineSpacing:11.5});

  // Right: 3 tool summary cards
  const tools=[
    {name:"run_assessment",tier:"free",inputs:"org_name · vertical · persona · north_star (opt) · domain_responses (opt)",outputs:"assessment_id · overall_score · domain_scores · narrative · action_pack · benchmarks_used · findings",color:C.teal},
    {name:"get_benchmarks",tier:"free",inputs:"domain (opt, enum 8 keys) · vertical (opt, enum 11) · limit · cursor",outputs:"benchmarks[] — id · domain · metric · unit · world_class · industry_average · description",color:C.purple},
    {name:"get_assessment_history",tier:"free",inputs:"org_name (opt) · limit (default 25, max 200) · cursor",outputs:"assessments[] (summaries) · page_info { has_more · next_cursor }",color:C.amber},
  ];

  tools.forEach((t,i)=>{
    const y=1.12+i*1.45;
    s.addShape(pres.shapes.RECTANGLE,{x:5.5,y,w:4.0,h:1.36,fill:{color:C.lgray},line:{color:"E5E7EB",width:0.5},shadow:makeSh()});
    s.addShape(pres.shapes.RECTANGLE,{x:5.5,y,w:4.0,h:0.05,fill:{color:t.color},line:{color:t.color}});
    s.addText([{text:t.name,options:{bold:true,color:t.color,fontSize:11}},{text:"  ·  free tier",options:{color:C.mgray,fontSize:8.5}}],{x:5.64,y:y+0.1,w:3.72,h:0.3,fontSize:11,fontFace:"Calibri"});
    s.addText([{text:"In:  ",options:{bold:true,color:C.dgray}},{text:t.inputs,options:{color:C.mgray}}],{x:5.64,y:y+0.44,w:3.72,h:0.38,fontSize:8.5,fontFace:"Calibri",valign:"top"});
    s.addText([{text:"Out: ",options:{bold:true,color:C.dgray}},{text:t.outputs,options:{color:C.mgray}}],{x:5.64,y:y+0.82,w:3.72,h:0.45,fontSize:8.5,fontFace:"Calibri",valign:"top"});
  });

  // Registry note at bottom — compact to fit within slide
  s.addShape(pres.shapes.RECTANGLE,{x:5.5,y:4.48,w:4.0,h:0.95,fill:{color:C.bluebg},line:{color:"BFDBFE",width:0.5}});
  s.addText("Registries in schemas.py",{x:5.64,y:4.52,w:3.72,h:0.24,fontSize:9,bold:true,color:C.blue,fontFace:"Calibri"});
  s.addText("FREE_TOOLS = [run_assessment, get_benchmarks, get_assessment_history]\nPRO_TOOLS = []  # stratos-pro repo\nTOOLS_BY_NAME = {tool['name']: tool for tool in ALL_TOOLS}",{
    x:5.64,y:4.76,w:3.72,h:0.62,fontSize:7.5,color:C.blue,fontFace:"Courier New",valign:"top"
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 32 — MCP CLAUDE DESKTOP CONFIG
// ═══════════════════════════════════════════════════════════════════════
{
  const s = slide("MCP server — Claude Desktop config & testing");

  // Left: config snippet
  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:1.12,w:5.0,h:2.9,fill:{color:C.code},line:{color:"2D3748",width:0.5},shadow:shadow()});
  s.addText("# claude_desktop_config.json",{x:0.7,y:1.18,w:4.7,h:0.25,fontSize:8.5,color:"64748B",fontFace:"Courier New"});
  const configLines=[
    {text:'{\n',options:{color:C.white}},
    {text:'  "mcpServers"',options:{color:C.codestr}},{text:': {\n',options:{color:C.white}},
    {text:'    "supply-chain-health-agent"',options:{color:C.codestr}},{text:': {\n',options:{color:C.white}},
    {text:'      "command"',options:{color:C.codestr}},{text:': ',options:{color:C.white}},{text:'"python3"',options:{color:C.codestr}},{text:',\n',options:{color:C.white}},
    {text:'      "args"',options:{color:C.codestr}},{text:': [',options:{color:C.white}},{text:'"-m","mcp_server.server"',options:{color:C.codestr}},{text:'],\n',options:{color:C.white}},
    {text:'      "cwd"',options:{color:C.codestr}},{text:': ',options:{color:C.white}},{text:'"/path/to/supply-chain-health-agent"',options:{color:C.codestr}},{text:',\n',options:{color:C.white}},
    {text:'      "env"',options:{color:C.codestr}},{text:': { ',options:{color:C.white}},
    {text:'"ANTHROPIC_API_KEY"',options:{color:C.codestr}},{text:': ',options:{color:C.white}},{text:'"sk-ant-..."',options:{color:C.codestr}},{text:' }\n',options:{color:C.white}},
    {text:'    }\n  }\n}',options:{color:C.white}},
  ];
  s.addText(configLines,{x:0.7,y:1.48,w:4.6,h:2.5,fontSize:8.5,fontFace:"Courier New",valign:"top",lineSpacing:12});

  // Claude Code CLI alternative
  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:4.12,w:5.0,h:1.3,fill:{color:C.code},line:{color:"2D3748",width:0.5},shadow:shadow()});
  s.addText("# Claude Code — register from repo directory",{x:0.7,y:4.18,w:4.7,h:0.25,fontSize:8.5,color:"64748B",fontFace:"Courier New"});
  const cliLines=[
    {text:"cd supply-chain-health-agent\n",options:{color:C.codehi}},
    {text:"claude mcp add supply-chain-health-agent \\\n",options:{color:C.white}},
    {text:"  -- python3 -m mcp_server.server",options:{color:C.codehi}},
  ];
  s.addText(cliLines,{x:0.7,y:4.44,w:4.6,h:0.9,fontSize:8.5,fontFace:"Courier New",valign:"top",lineSpacing:12});

  // Right: smoke test + usage
  const rightCards=[
    {t:"Smoke test sequence",b:"1. python3 -c 'import mcp_server.server as srv'  — confirms engine imports resolve.\n2. asyncio.run(srv.list_tools())  — confirms 3 tools advertised.\n3. call_tool('get_benchmarks', {})  — no API key needed, returns benchmark data.",a:C.teal},
    {t:"What the user says in Claude",b:"'Run a supply chain health assessment for Acme Corp, automotive vertical, analyst persona.' — Claude calls run_assessment with the correct parameters automatically.",a:C.blue},
    {t:"Pro tier MCP (stratos-pro)",b:"Streamable HTTP transport, 8 tools, tenant isolation. Lives in the private stratos-pro repo. Adds: financial_impact, three_horizon_roadmap, erp_data_pull, proactive_risk_alerts, tenant_memory.",a:C.purple},
  ];
  rightCards.forEach((c,i)=>infoCard(s,5.7,1.12+i*1.52,3.8,1.4,c.t,c.b,c.a,C.lgray));
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 33 — SECTION: GET THE CODE
// ═══════════════════════════════════════════════════════════════════════
sectionSlide("08 — Get the Code","5-minute setup · MCP server · extending the system · contributing to the repo");

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 34 — 5-MINUTE SETUP
// ═══════════════════════════════════════════════════════════════════════
{
  const s = slide("5-minute setup — from zero to running assessment");

  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:1.12,w:9.0,h:4.3,fill:{color:C.code},line:{color:"2D3748",width:0.5},shadow:shadow()});
  s.addText("# Terminal — 6 steps (Step 5 = MCP server, new in v4.2)",{x:0.7,y:1.18,w:8.6,h:0.26,fontSize:9,color:"64748B",fontFace:"Courier New"});

  const setupSteps=[
    {step:"1. Clone",cmd:"git clone https://github.com/dwnjuguna/Supply-Chain-Health-Agent.git",sub:"cd Supply-Chain-Health-Agent"},
    {step:"2. Install",cmd:"pip install -r requirements.txt",sub:"# Python 3.10+ required. Includes mcp>=1.28.0 for MCP server."},
    {step:"3. Configure",cmd:"echo 'ANTHROPIC_API_KEY=sk-ant-...' > .env",sub:"# Get your key at console.anthropic.com"},
    {step:"4A. Web UI",cmd:"streamlit run app.py",sub:"# Opens at http://localhost:8501"},
    {step:"4B. CLI",cmd:"python3 cli.py",sub:"# Interactive terminal assessment"},
    {step:"5. MCP Server",cmd:"python3 -m mcp_server.server",sub:"# Stdio MCP server — register in claude_desktop_config.json or via 'claude mcp add'"},
  ];
  setupSteps.forEach((step,i)=>{
    const y=1.5+i*0.62;
    s.addText([
      {text:`# ${step.step}\n`,options:{color:"64748B"}},
      {text:step.cmd+"\n",options:{color:C.codehi}},
      {text:step.sub,options:{color:"64748B"}},
    ],{x:0.7,y,w:8.5,h:0.56,fontSize:8.8,fontFace:"Courier New",valign:"top",lineSpacing:12});
    if(i<setupSteps.length-1) s.addShape(pres.shapes.LINE,{x:0.7,y:y+0.58,w:8.3,h:0,line:{color:"2D3748",width:0.4}});
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 35 — EXTENDING THE SYSTEM
// ═══════════════════════════════════════════════════════════════════════
{
  const s = slide("Extending the system — where to make changes");

  const extensions=[
    {what:"Add a new industry vertical",file:"verticals.py",how:"Add a dict entry with the vertical name, focus_areas, benchmarks, and reference_orgs. The UI, prompts, and scoring update automatically. The MCP get_benchmarks tool also picks it up.",accent:C.teal},
    {what:"Add a new user persona",file:"personas.py",how:"Define track name, UI label, context questions, token budget, and optional system prompt extension. personas.py is the single source of truth — no other file changes needed.",accent:C.purple},
    {what:"Update KPI benchmarks",file:"domains.py",how:"Edit the world_class_target and scoring_rubric for any domain. New thresholds flow immediately into all assessments and into the MCP get_benchmarks response.",accent:C.amber},
    {what:"Add a Pro-tier MCP tool",file:"stratos-pro/mcp_server/schemas.py",how:"Add tool dict to PRO_TOOLS list in the private repo schemas.py. Implement handler in pro_server.py. The FREE/PRO/ALL_TOOLS registry pattern keeps tiers cleanly separated.",accent:C.blue},
  ];
  extensions.forEach((e,i)=>{
    const y=1.12+i*1.1;
    s.addShape(pres.shapes.RECTANGLE,{x:0.5,y,w:9.0,h:1.02,fill:{color:C.lgray},line:{color:"E5E7EB",width:0.5},shadow:makeSh()});
    s.addShape(pres.shapes.RECTANGLE,{x:0.5,y,w:0.06,h:1.02,fill:{color:e.accent},line:{color:e.accent}});
    s.addText([{text:e.what,options:{bold:true,color:e.accent}},{text:"  →  edit ",options:{color:C.mgray}},{text:e.file,options:{bold:true,color:e.accent,italic:true}}],{
      x:0.7,y:y+0.08,w:8.6,h:0.28,fontSize:10.5,fontFace:"Calibri"
    });
    s.addText(e.how,{x:0.7,y:y+0.4,w:8.5,h:0.54,fontSize:9.5,color:C.dgray,fontFace:"Calibri",valign:"top"});
  });
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 36 — CLOSING / GITHUB CTA
// ═══════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.navy };
  s.addShape(pres.shapes.RECTANGLE,{x:0,y:0,w:0.18,h:5.625,fill:{color:C.teal},line:{color:C.teal}});
  s.addShape(pres.shapes.RECTANGLE,{x:0,y:4.6,w:10,h:1.025,fill:{color:"16123C"},line:{color:"16123C"}});

  s.addText("Get the code.",{x:0.5,y:0.45,w:9.0,h:0.7,fontSize:34,bold:true,color:C.white,fontFace:"Calibri"});
  s.addText("Read it. Fork it. Build on it. The architecture is open.",{x:0.5,y:1.22,w:9.0,h:0.48,fontSize:17,color:"AFA9EC",fontFace:"Calibri",italic:true});

  const links=[
    {label:"GitHub Repository",sub:"Full source · MIT License\ngithub.com/dwnjuguna/Supply-Chain-Health-Agent",c:C.purple},
    {label:"Live Application",sub:"Try a real assessment\nsupply-chain-health-agent.streamlit.app",c:C.teal},
    {label:"Anthropic SDK Docs",sub:"Claude API reference\ndocs.anthropic.com",c:C.amber},
  ];
  links.forEach((l,i)=>{
    const x=0.5+i*3.07;
    s.addShape(pres.shapes.RECTANGLE,{x,y:2.05,w:2.88,h:2.08,fill:{color:l.c},line:{color:l.c},shadow:shadow()});
    s.addText(l.label,{x,y:2.2,w:2.88,h:0.45,fontSize:14,bold:true,color:C.white,fontFace:"Calibri",align:"center"});
    s.addText(l.sub,{x:x+0.1,y:2.72,w:2.68,h:1.2,fontSize:10,color:C.white,fontFace:"Calibri",align:"center",valign:"top"});
  });

  s.addText([
    {text:"⚙  The diagrams in this deck map directly to file names in the repo.\n",options:{color:"7C78C0"}},
    {text:"The MCP server (v4.2) and Phase 2 infrastructure are built and available to self-hosters today.",options:{color:"7C78C0"}},
  ],{x:0.5,y:4.32,w:9.0,h:0.42,fontSize:9,fontFace:"Calibri",valign:"middle"});

  s.addText("Supply Chain Health Agent · Technical Architecture v4.2 · June 2026 · MIT License · github.com/dwnjuguna/Supply-Chain-Health-Agent",{
    x:0.4,y:4.67,w:9.2,h:0.28,fontSize:8,color:"7C78C0",fontFace:"Calibri",align:"center"
  });
}

// ═══════════════════════════════════════════════════════════════════════
// WRITE
// ═══════════════════════════════════════════════════════════════════════
pres.writeFile({fileName:"SC_Health_Agent_Tech_Deck_v4_2.pptx"})
  .then(()=>console.log("✅ SC_Health_Agent_Tech_Deck_v4_2.pptx — 36 slides"))
  .catch(e=>{console.error("❌",e);process.exit(1);});
