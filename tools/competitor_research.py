"""
Tool: Competitor Research
=========================
Fetches and summarizes competitor data for Instagram growth services.
Can be called standalone or imported into agent.py as a tool extension.

Usage:
    python tools/competitor_research.py "competitor name or URL"
"""

import sys
import os
import anthropic
import httpx
from urllib.parse import urlparse


def fetch_page_text(url: str) -> str:
    """Fetch raw text from a URL (simple, no JS rendering)."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; ConstellationAgent/1.0)"}
        resp = httpx.get(url, headers=headers, timeout=15, follow_redirects=True)
        resp.raise_for_status()
        # Very basic HTML stripping — enough for pricing pages
        text = resp.text
        # Remove scripts and styles
        import re
        text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text[:12000]  # Cap to avoid token overflow
    except Exception as e:
        return f"Failed to fetch {url}: {e}"


def analyze_competitor(query: str) -> str:
    """
    Given a competitor name or URL, research and return a structured analysis.
    Uses Claude to interpret findings.
    """
    client = anthropic.Anthropic()

    # If it looks like a URL, fetch it
    page_content = ""
    if query.startswith("http"):
        page_content = fetch_page_text(query)
        context = f"Here is the content from {query}:\n\n{page_content}"
    else:
        context = f"Competitor to research: {query}"

    prompt = f"""You are researching a competitor in the Instagram growth services space for a SaaS company.

{context}

Please provide a structured competitor analysis covering:
1. **What they offer** — core service, features
2. **Pricing** — plans, price points, free trial
3. **Target audience** — who they're selling to
4. **Positioning** — how they differentiate
5. **Strengths** — what they do well
6. **Weaknesses / gaps** — what they're missing
7. **Key takeaways** — 2-3 actionable insights for SocialGrowth

Be concise and specific. Focus on what's actionable."""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/competitor_research.py <competitor name or URL>")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    print(f"Researching: {query}\n")
    print(analyze_competitor(query))
