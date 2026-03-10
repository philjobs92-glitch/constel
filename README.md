# Constellation AI Agent

Your personal AI agent for running **SocialGrowth** — the white-labeled Instagram growth SaaS portfolio.

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your API key
```bash
export ANTHROPIC_API_KEY=your_key_here
```
Get your key at: https://console.anthropic.com

### 3. Fill in your company context (one-time setup)
Edit these files before first use:

| File | What to fill in |
|------|----------------|
| `context/brands.md` | Name, domain, pricing, and positioning for each brand |
| `context/operations.md` | Tech stack, support channels, team, processes |
| `context/goals.md` | Current quarter goals and success metrics |

The more you fill in, the better the agent performs. Start with `brands.md` — it's the most important.

### 4. Run the agent
```bash
# Interactive chat (recommended for most use)
python agent.py

# Single task
python agent.py "What should I focus on this week?"
python agent.py "Write a churn win-back email for Brand 2"
python agent.py "Research our top 3 competitors"
```

---

## Project Structure

```
constel/
├── agent.py                  ← Main agent (run this)
├── requirements.txt
├── CLAUDE.md                 ← Agent instructions & master context
│
├── context/                  ← YOUR BUSINESS KNOWLEDGE (fill these in)
│   ├── company.md            ← Company overview (pre-filled)
│   ├── brands.md             ← Brand registry (fill in)
│   ├── operations.md         ← Tech stack, processes (fill in)
│   └── goals.md              ← Quarterly goals (fill in)
│
├── tools/                    ← Standalone tools
│   ├── competitor_research.py
│   ├── metrics_analyzer.py
│   └── copy_generator.py
│
└── outputs/                  ← Agent-generated files saved here
    └── (created automatically)
```

---

## What the Agent Can Do

### In chat mode (`python agent.py`)
Ask it anything related to SocialGrowth:

```
You: What should I prioritize this week?
You: Write a win-back email for churned users on Brand 3
You: Analyze why Brand 2 has higher churn than Brand 1
You: Create an SOP for customer onboarding
You: Research [competitor name]
You: Draft a pricing page for Brand 4
You: Suggest 5 ways to reduce support tickets
```

The agent **remembers context within a session** (multi-turn conversation).
To start fresh, type `clear`.

### Standalone tools (for specific tasks)

**Research a competitor:**
```bash
python tools/competitor_research.py "Kicksta"
python tools/competitor_research.py "https://kicksta.co/pricing"
```

**Analyze metrics from a CSV:**
```bash
python tools/metrics_analyzer.py monthly_report.csv "which brand has the highest churn?"
cat data.json | python tools/metrics_analyzer.py - "summarize MRR by brand"
```

**Generate copy for a brand:**
```bash
python tools/copy_generator.py --brand "Brand Name" --type email --goal "re-engage inactive users"
python tools/copy_generator.py --brand "Brand Name" --type landing-page --goal "increase free trial signups"
# Types: email, landing-page, ad, onboarding, sms, push, social, cancellation, upsell
```

---

## How to Get the Best Results

### 1. Fill in context files completely
The agent uses `context/brands.md` etc. as its memory. The more detail you add, the more precise its answers will be. Think of it as onboarding a new employee.

### 2. Be specific about which brand
Instead of: *"Help me improve conversion"*
Say: *"Help me improve conversion on Brand 2's pricing page"*

### 3. Let it write things for you
The agent will save outputs to `outputs/` automatically. Just ask:
- "Write an SOP for handling refund requests"
- "Create a 3-email onboarding sequence for new subscribers"
- "Draft a case study template"

### 4. Tell it when something changes
New brand acquired? Update `context/brands.md`.
New goal? Update `context/goals.md`.
The agent can do this for you — just tell it.

### 5. Use it for recurring tasks
Ask the agent to build you templates for tasks you do repeatedly:
- Weekly reporting prompts
- Customer win-back sequences
- Brand launch checklists
- A/B test planning templates

---

## Adding More Context

You can drop any document into the `context/` folder as a `.md` file and the agent will automatically read it. For example:

- `context/pricing.md` — detailed pricing for all brands
- `context/competitors.md` — competitor analysis notes
- `context/roadmap.md` — product roadmap
- `context/team.md` — team roles and contacts

---

## Upgrading the Agent

### Adding new tools to the agent loop
Edit `agent.py` and add to the `TOOLS` list (JSON schema definition) and `execute_tool()` function.

### Giving the agent web access
The agent's `TOOLS` list can be extended with web search. For now, use `tools/competitor_research.py` for web research tasks.

### Multiple specialized agents
As your needs grow, you can create separate agents for specific tasks:
- `agent_support.py` — handles support ticket drafting
- `agent_growth.py` — focused on acquisition/conversion
- `agent_ops.py` — handles operational tasks

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `AuthenticationError` | Set `ANTHROPIC_API_KEY` environment variable |
| Agent gives generic answers | Fill in `context/brands.md` with real brand details |
| Agent doesn't know about a brand | Add the brand to `context/brands.md` |
| Output file not created | The `outputs/` directory is created automatically on first save |
