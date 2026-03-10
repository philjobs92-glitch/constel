"""
Tool: Metrics Analyzer
======================
Paste or pipe in CSV/JSON data and get an instant analysis.
Useful for: MRR reports, churn data, conversion data, ad performance.

Usage:
    python tools/metrics_analyzer.py data.csv "analyze MRR trend and flag issues"
    cat data.json | python tools/metrics_analyzer.py - "which brand has highest churn?"
"""

import sys
import os
import json
import csv
import io
import anthropic


def read_data(source: str) -> str:
    """Read data from file path or stdin (-)."""
    if source == "-":
        return sys.stdin.read()
    try:
        with open(source) as f:
            return f.read()
    except FileNotFoundError:
        return f"File not found: {source}"
    except Exception as e:
        return f"Error reading file: {e}"


def analyze_metrics(data: str, question: str) -> str:
    """Send data + question to Claude for analysis."""
    client = anthropic.Anthropic()

    prompt = f"""You are a data analyst for SocialGrowth, a portfolio of Instagram growth service brands.

The user has provided the following data:

```
{data[:10000]}
```

Their question / task:
{question}

Instructions:
- Identify patterns, trends, and anomalies
- Flag any numbers that look problematic (high churn, low conversion, declining revenue)
- Give concrete, actionable recommendations
- If comparing brands, rank them
- Use tables or bullet points for clarity
- Be specific with numbers"""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    )

    # Extract text (skip thinking blocks)
    for block in response.content:
        if block.type == "text":
            return block.text
    return "No response generated."


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python tools/metrics_analyzer.py <file.csv or -> <question>")
        print("  Use - to read from stdin")
        sys.exit(1)

    source = sys.argv[1]
    question = " ".join(sys.argv[2:])

    data = read_data(source)
    if data.startswith("File not found") or data.startswith("Error"):
        print(data)
        sys.exit(1)

    print(f"Analyzing data ({len(data)} chars)...\n")
    print(analyze_metrics(data, question))
