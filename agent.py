#!/usr/bin/env python3
"""
Constellation AI Agent
======================
Main agent runner for philjobs92 / SocialGrowth.

Usage:
    python agent.py                        # Interactive chat mode
    python agent.py "your task here"       # Single task mode
    python agent.py --task "your task"     # Explicit flag

Setup:
    pip install anthropic
    export ANTHROPIC_API_KEY=your_key_here
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime

import anthropic

# ── Config ─────────────────────────────────────────────────────────────────
MODEL = "claude-opus-4-6"
MAX_TOKENS = 8096
CONTEXT_DIR = Path(__file__).parent / "context"
CLAUDE_MD = Path(__file__).parent / "CLAUDE.md"

# ── Load context ────────────────────────────────────────────────────────────

def load_context_files() -> str:
    """Load all context files and CLAUDE.md into the system prompt."""
    parts = []

    if CLAUDE_MD.exists():
        parts.append(f"# MASTER INSTRUCTIONS\n{CLAUDE_MD.read_text()}")

    if CONTEXT_DIR.exists():
        for md_file in sorted(CONTEXT_DIR.glob("*.md")):
            content = md_file.read_text().strip()
            if content:
                parts.append(f"# {md_file.stem.upper()} CONTEXT\n{content}")

    return "\n\n---\n\n".join(parts)


def build_system_prompt() -> str:
    context = load_context_files()
    today = datetime.now().strftime("%A, %B %d, %Y")
    return f"""You are the Constellation AI agent for philjobs92, working on the SocialGrowth project.

Today's date: {today}

{context}

---

Always read the context above before responding. If context files have unfilled placeholders,
ask the user to fill them in so you can give more precise help.
"""

# ── Tools ──────────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "read_context_file",
        "description": (
            "Read a specific context file from the context/ directory. "
            "Use this to get up-to-date details about brands, operations, goals, etc."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The filename to read (e.g. 'brands.md', 'goals.md'). "
                                   "Files are in the context/ directory.",
                }
            },
            "required": ["filename"],
        },
    },
    {
        "name": "write_context_file",
        "description": (
            "Write or update a context file. Use this to save new information "
            "about brands, goals, operations, or any business knowledge that should persist."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Filename to write in context/ (e.g. 'brands.md')",
                },
                "content": {
                    "type": "string",
                    "description": "Full content to write to the file",
                },
            },
            "required": ["filename", "content"],
        },
    },
    {
        "name": "save_output",
        "description": (
            "Save a generated document (SOP, email template, copy draft, report, etc.) "
            "to the outputs/ directory so the user can use it."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Filename for the output (e.g. 'onboarding-sop.md', 'email-campaign-brand2.md')",
                },
                "content": {
                    "type": "string",
                    "description": "Content to save",
                },
            },
            "required": ["filename", "content"],
        },
    },
    {
        "name": "list_context_files",
        "description": "List all available context files and output files.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
]


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a tool call and return the result as a string."""

    if tool_name == "read_context_file":
        filename = tool_input["filename"]
        filepath = CONTEXT_DIR / filename
        if filepath.exists():
            return filepath.read_text()
        return f"File not found: context/{filename}"

    elif tool_name == "write_context_file":
        filename = tool_input["filename"]
        content = tool_input["content"]
        CONTEXT_DIR.mkdir(exist_ok=True)
        filepath = CONTEXT_DIR / filename
        filepath.write_text(content)
        return f"Saved: context/{filename}"

    elif tool_name == "save_output":
        filename = tool_input["filename"]
        content = tool_input["content"]
        output_dir = Path(__file__).parent / "outputs"
        output_dir.mkdir(exist_ok=True)
        filepath = output_dir / filename
        filepath.write_text(content)
        return f"Saved to outputs/{filename}"

    elif tool_name == "list_context_files":
        lines = []
        if CONTEXT_DIR.exists():
            lines.append("Context files:")
            for f in sorted(CONTEXT_DIR.glob("*.md")):
                lines.append(f"  context/{f.name}")
        output_dir = Path(__file__).parent / "outputs"
        if output_dir.exists():
            lines.append("Output files:")
            for f in sorted(output_dir.glob("*")):
                lines.append(f"  outputs/{f.name}")
        return "\n".join(lines) if lines else "No files found."

    return f"Unknown tool: {tool_name}"


# ── Agent loop ──────────────────────────────────────────────────────────────

def run_agent(user_message: str, conversation_history: list) -> tuple[str, list]:
    """
    Run one turn of the agent loop.
    Returns (assistant_text, updated_history).
    """
    client = anthropic.Anthropic()
    system_prompt = build_system_prompt()

    conversation_history.append({"role": "user", "content": user_message})
    messages = list(conversation_history)

    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            thinking={"type": "adaptive"},
            tools=TOOLS,
            messages=messages,
        )

        # Collect all text from this response
        text_parts = []
        tool_uses = []

        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_uses.append(block)

        # Append assistant turn to message history
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            final_text = "\n".join(text_parts)
            # Update conversation history with assistant response
            conversation_history.append(
                {"role": "assistant", "content": response.content}
            )
            return final_text, conversation_history

        if response.stop_reason == "tool_use" and tool_uses:
            # Execute all tool calls
            tool_results = []
            for tool_use in tool_uses:
                print(f"  [tool: {tool_use.name}({json.dumps(tool_use.input, ensure_ascii=False)[:80]})]")
                result = execute_tool(tool_use.name, tool_use.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": result,
                })

            messages.append({"role": "user", "content": tool_results})
            # continue loop

        else:
            # Unexpected stop — return what we have
            final_text = "\n".join(text_parts)
            conversation_history.append(
                {"role": "assistant", "content": response.content}
            )
            return final_text, conversation_history


# ── CLI ─────────────────────────────────────────────────────────────────────

BANNER = """
╔══════════════════════════════════════════════════════╗
║         Constellation AI Agent — SocialGrowth        ║
║  Type your task. 'quit' to exit. 'clear' to reset.  ║
╚══════════════════════════════════════════════════════╝
"""


def interactive_mode():
    print(BANNER)
    conversation_history = []

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "bye"):
            print("Bye.")
            break
        if user_input.lower() == "clear":
            conversation_history = []
            print("[Conversation cleared]")
            continue

        print("\nAgent: ", end="", flush=True)
        try:
            response, conversation_history = run_agent(user_input, conversation_history)
            print(response)
        except anthropic.AuthenticationError:
            print("ERROR: Invalid API key. Set ANTHROPIC_API_KEY environment variable.")
            break
        except anthropic.RateLimitError:
            print("ERROR: Rate limited. Wait a moment and try again.")
        except Exception as e:
            print(f"ERROR: {e}")


def single_task_mode(task: str):
    print(f"Task: {task}\n")
    try:
        response, _ = run_agent(task, [])
        print(response)
    except anthropic.AuthenticationError:
        print("ERROR: Invalid API key. Set ANTHROPIC_API_KEY environment variable.")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Constellation AI Agent for SocialGrowth"
    )
    parser.add_argument(
        "task",
        nargs="?",
        help="Task to run (omit for interactive mode)",
    )
    parser.add_argument(
        "--task",
        "-t",
        dest="task_flag",
        help="Task to run (alternative to positional arg)",
    )
    args = parser.parse_args()

    task = args.task or args.task_flag

    if task:
        single_task_mode(task)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
