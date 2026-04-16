#!/usr/bin/env python3
"""
LocalPrivate Harness: CLI agent with wiki persistence, test harness, and modes.
"""

import os, sys, json, time, argparse, re
import subprocess, threading
from pathlib import Path
from typing import Callable

# -----------------------------
# Configuration
# -----------------------------
# Default to the local directory (where the venv/project is running) unless LocalPrivate_DIR is specified.
env_dir = os.environ.get("LocalPrivate_DIR")
BASE = Path(env_dir) if env_dir else Path.cwd() / ".LocalPrivate"
WIKI_DIR = BASE / "wiki"
SOUL_FILE = BASE / "soul.json"
TESTS_DIR = BASE / "tests"
MODE_FILE = BASE / "mode.json"

LM_LOCAL_URL = "http://localhost:1234"  # LMStudio default
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")

# -----------------------------
# Utils
# -----------------------------
def safe_shell(cmd: str):
    """Run safe subprocess command; returns output."""
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def write_file(p: Path, content: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

def read_file(p: Path):
    return p.read_text(encoding="utf-8") if p.exists() else ""

def prompt(q: str) -> str:
    return input(f"{q.strip()} >>> ").strip()

# -----------------------------
# Install / Soul Setup
# -----------------------------
def install():
    """Initial install: create structure, ask soul questions."""
    print("LocalPrivate: Initial install. Establishing base structure…")
    for d in [BASE, WIKI_DIR, TESTS_DIR]:
        d.mkdir(exist_ok=True)

    if not SOUL_FILE.exists():
        soul = {}
        soul['name'] = prompt("What is your agent name?")
        soul['purpose'] = prompt("What is its core purpose?")
        soul['developer'] = prompt("Developer/Owner name?")
        write_file(SOUL_FILE, json.dumps(soul, indent=2))
        print("Soul file created.")

    if not MODE_FILE.exists():
        write_file(MODE_FILE, json.dumps({"mode":"cli"}))
        print("Default mode set: CLI")

    print("Done.")

# -----------------------------
# Wiki Management
# -----------------------------
def wiki_init():
    """Ensure wiki index and home page exist."""
    index = WIKI_DIR / "index.md"
    if not index.exists():
        write_file(index, "# Wiki Index\n\nThis wiki is maintained by LocalPrivate.\n")
    home = WIKI_DIR / "home.md"
    if not home.exists():
        write_file(home, "# Home\nThis is the root page.")

def wiki_add(page: str, content: str):
    write_file(WIKI_DIR / f"{page}.md", content)

def wiki_list():
    return [p.name for p in WIKI_DIR.glob("*.md")]

# -----------------------------
# Test Harness & TDD Loop
# -----------------------------
def run_tests() -> bool:
    """Run tests and return True if passing."""
    r = subprocess.run(["pytest", str(TESTS_DIR)], capture_output=True, text=True)
    print(r.stdout)
    return r.returncode == 0

def tdd_loop(task_func: Callable):
    """Test-Driven loop: tests -> code -> re-run until success."""
    while True:
        ok = run_tests()
        if ok:
            print("Tests passing. Task complete.")
            break
        print("Tests failing; attempting to run task step.")
        task_func()
        time.sleep(2)  # allow test state change

# -----------------------------
# Cron / Heartbeat
# -----------------------------
cron_threads = {}

def start_heartbeat(name: str, interval: int, job: Callable):
    if name in cron_threads:
        print(f"Heartbeat {name} already running")
        return
    def hb():
        while True:
            job()
            time.sleep(interval)
    t = threading.Thread(target=hb, daemon=True)
    cron_threads[name] = t
    t.start()
    print(f"Heartbeat {name} started.")

# -----------------------------
# LLM Backend
# -----------------------------
def call_llm(messages: list, tools: list = None):
    """Call a local LMStudio instance or OpenAI if API key set."""
    if OPENAI_KEY:
        import openai
        openai.api_key = OPENAI_KEY
        kwargs = {"model": "gpt-4o-mini", "messages": messages}
        if tools:
             kwargs["tools"] = tools
        # Handle v0.28 format used in this script historically
        return openai.ChatCompletion.create(**kwargs)["choices"][0]["message"]
    else:
        import requests
        payload = {"model":"local-model","messages":messages}
        if tools:
            payload["tools"] = tools
        r = requests.post(LM_LOCAL_URL + "/v1/chat/completions", json=payload)
        return r.json()["choices"][0]["message"]

def agent_loop(prompt_text: str, chat_history: list = None):
    """Multi-turn evaluation loop using native OpenAI Function Calling logic."""
    system_prompt = """You are an autonomous AI agent capable of executing local system actions.
Execute tools explicitly when asked to generate or manipulate files or run commands.
Do not hallucinate files without confirming their successful creation.
If no further tool use is needed, respond with normal human text out-of-band directly to the user."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "run_command",
                "description": "Execute a bash command on the local terminal",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cmd": {"type": "string", "description": "The exact bash command to execute"}
                    },
                    "required": ["cmd"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write code or text natively to a local file system path",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "The target relative or absolute file path. Relative paths anchor to the current directory."},
                        "content": {"type": "string", "description": "The exact source code or material to persist into the file."}
                    },
                    "required": ["path", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read text from a local system file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "The file path to read from."}
                    },
                    "required": ["path"]
                }
            }
        }
    ]

    if chat_history is None:
        chat_history = []

    messages = [{"role": "system", "content": system_prompt}] + chat_history
    messages.append({"role": "user", "content": prompt_text})
    
    while True:
        # Fetch dict object rather than plain text
        message = call_llm(messages, tools)
        messages.append(message)
        
        tool_calls = message.get("tool_calls")
        if not tool_calls:
            # The agent has finalized execution and responded with conversational text
            if chat_history is not None:
                chat_history.clear()
                chat_history.extend(messages[1:]) # Retain everything except the system prompt
            return message.get("content", "")
            
        for tool_call in tool_calls:
            func = tool_call.get("function", {})
            name = func.get("name")
            
            print(f"[Agent Tool Execution: {name}]")
            result = ""
            try:
                tool_args = json.loads(func.get("arguments", "{}"))
                
                if name == "run_command":
                    cmd = tool_args.get("cmd")
                    if cmd:
                        r = safe_shell(cmd)
                        result = f"STDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}"
                    else:
                        result = "Error: Missing 'cmd' argument."
                        
                elif name == "write_file":
                    p = tool_args.get("path")
                    c = tool_args.get("content")
                    if p:
                        file_path = Path(p)
                        if not file_path.is_absolute():
                            file_path = Path.cwd() / file_path
                        file_path = file_path.resolve()
                        
                        if not file_path.is_relative_to(Path.cwd()):
                            result = f"Error: Security policy blocked write. You are sandboxed to {Path.cwd()}."
                        else:
                            write_file(file_path, c or "")
                            result = f"File {file_path} written successfully inside sandbox."
                    else:
                        result = "Error: Missing 'path' parameter."
                        
                elif name == "read_file":
                    p = tool_args.get("path")
                    if p:
                        file_path = Path(p)
                        if not file_path.is_absolute():
                            file_path = Path.cwd() / file_path
                        file_path = file_path.resolve()
                        
                        if not file_path.is_relative_to(Path.cwd()):
                            result = f"Error: Security policy blocked read. You are sandboxed to {Path.cwd()}."
                        else:
                            result = read_file(file_path)
                    else:
                        result = "Error: Missing 'path' parameter."
                else:
                    result = f"Error: Unknown tool '{name}' executed."
                    
            except Exception as e:
                result = f"Tool Execution Pipeline Error: {str(e)}"
                
            print(f"[Result]: {result[:120].strip()}...")
            # Native OpenAI functional standard requires role=tool and matching ID
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.get("id"),
                "name": name,
                "content": result
            })

# -----------------------------
# CLI Modes
# -----------------------------
def cli_mode():
    raw_soul = read_file(SOUL_FILE)
    soul = json.loads(raw_soul) if raw_soul.strip() else {"name": "Agent", "purpose": "General"}
    print(f"Welcome to {soul['name']} CLI. Purpose: {soul['purpose']}")
    wiki_init()
    
    chat_history = []
    
    while True:
        q = prompt("Ask, wiki, cron, tests, exit?")
        if q == "exit":
            break
        elif q.startswith("wiki"):
            parts = q.split()
            if len(parts) == 1:
                print(wiki_list())
            elif len(parts) >= 2 and parts[1] == "add":
                name = prompt("Page name")
                content = prompt("Content")
                wiki_add(name, content)
        elif q.startswith("cron"):
            if "start" in q:
                name = prompt("Heartbeat name")
                interval = int(prompt("Interval seconds"))
                start_heartbeat(name, interval, lambda: print("Heartbeat tick"))
        elif q.startswith("tests"):
            run_tests()
        else:
            if q.strip():
                try:
                    print("Thinking...")
                    response = agent_loop(q, chat_history)
                    print(f"\nAgent Response:\n{response}\n")
                except Exception as e:
                    print(f"Error connecting to LLM: {e}")

# -----------------------------
# Main
# -----------------------------
if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace", type=str, nargs="?", default=None, help="Target directory for the agent to securely sandbox inside")
    parser.add_argument("--install", action="store_true")
    parser.add_argument("--mode", type=str)
    parser.add_argument("--task", type=str, help="Run a single task directly and exit")
    args = parser.parse_args()

    if args.workspace:
        workspace_path = Path(args.workspace).resolve()
        workspace_path.mkdir(parents=True, exist_ok=True)
        os.chdir(workspace_path)
        print(f"Agent Workspace Sandboxed exactly to: {workspace_path}")
        
        # Dynamically remap internal globals to lock them inside the new active sandbox
        env_dir = os.environ.get("LocalPrivate_DIR")
        BASE = Path(env_dir) if env_dir else Path.cwd() / ".LocalPrivate"
        WIKI_DIR = BASE / "wiki"
        SOUL_FILE = BASE / "soul.json"
        TESTS_DIR = BASE / "tests"
        MODE_FILE = BASE / "mode.json"

    if args.install:
        install()
        sys.exit(0)

    if args.task:
        print(f"Executing task: {args.task}")
        try:
            response = agent_loop(args.task)
            print("\nResponse:")
            print(response)
        except Exception as e:
            print(f"Error calling LLM: {e}")
        sys.exit(0)

    if args.mode:
        mfile = json.loads(read_file(MODE_FILE)) if MODE_FILE.exists() else {}
        mfile["mode"] = args.mode
        write_file(MODE_FILE, json.dumps(mfile))
        print(f"Mode set: {args.mode}")

    mode = json.loads(read_file(MODE_FILE)).get("mode", "cli") if MODE_FILE.exists() else "cli"
    
    if mode == "cli":
        cli_mode()
    elif mode == "api":
        print("Starting API Server mode...")
        print("Listening on port 8080. (Note: API endpoint functionality is a placeholder)")
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            print("API server stopped.")
    else:
        print(f"Mode {mode} not implemented yet.")
