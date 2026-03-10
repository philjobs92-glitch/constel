"""
Tool: Copy Generator
====================
Generate on-brand copy for any SocialGrowth brand.
Reads brand context from context/brands.md automatically.

Usage:
    python tools/copy_generator.py --brand "Brand Name" --type email --goal "re-engage churned users"
    python tools/copy_generator.py --brand "Brand Name" --type landing-page --goal "convert trial users"
    python tools/copy_generator.py --brand "Brand Name" --type ad --goal "cold audience, Instagram"
"""

import sys
import os
import argparse
from pathlib import Path

import anthropic

CONTEXT_DIR = Path(__file__).parent.parent / "context"

COPY_TYPES = {
    "email": "a marketing email",
    "landing-page": "landing page hero section (headline, subheadline, CTA, 3 benefit bullets)",
    "ad": "a paid ad (headline + 2-3 lines body copy + CTA)",
    "onboarding": "an onboarding email sequence (3 emails: welcome, day 3, day 7)",
    "sms": "an SMS message (max 160 chars)",
    "push": "a push notification (max 100 chars)",
    "social": "3 social media posts (Instagram captions with hashtags)",
    "cancellation": "a cancellation win-back email",
    "upsell": "an upsell email to upgrade to a higher plan",
}


def load_brand_context(brand_name: str) -> str:
    brands_file = CONTEXT_DIR / "brands.md"
    if not brands_file.exists():
        return "No brand context available."

    content = brands_file.read_text()

    # Try to extract the relevant brand section
    lines = content.split("\n")
    brand_section = []
    in_section = False
    for line in lines:
        if brand_name.lower() in line.lower() and line.startswith("##"):
            in_section = True
        elif in_section and line.startswith("## ") and brand_name.lower() not in line.lower():
            break
        if in_section:
            brand_section.append(line)

    if brand_section:
        return "\n".join(brand_section)
    return f"Brand '{brand_name}' not found in context/brands.md. Using general brand context."


def generate_copy(brand: str, copy_type: str, goal: str, tone: str = "professional") -> str:
    client = anthropic.Anthropic()

    brand_context = load_brand_context(brand)
    copy_description = COPY_TYPES.get(copy_type, f"marketing copy of type '{copy_type}'")

    prompt = f"""You are a conversion copywriter for {brand}, an Instagram growth service.

Brand context:
{brand_context}

Task: Write {copy_description}
Goal: {goal}
Tone: {tone}

Requirements:
- Write in the brand's voice (infer from brand context, default to confident + results-focused)
- Focus on outcomes (more followers, engagement, growth) not features
- Include urgency where appropriate
- Make the CTA clear and strong
- Avoid generic phrases like "take your Instagram to the next level"

Output the copy directly, no preamble."""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate copy for SocialGrowth brands")
    parser.add_argument("--brand", "-b", required=True, help="Brand name")
    parser.add_argument(
        "--type", "-t", required=True,
        choices=list(COPY_TYPES.keys()),
        help="Type of copy to generate",
    )
    parser.add_argument("--goal", "-g", required=True, help="Goal of the copy")
    parser.add_argument("--tone", default="professional", help="Tone (default: professional)")
    args = parser.parse_args()

    print(f"Generating {args.type} copy for {args.brand}...\n")
    print(generate_copy(args.brand, args.type, args.goal, args.tone))
