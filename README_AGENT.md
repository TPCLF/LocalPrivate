# TRM-Sim Coding Agent 🧠🛠️

A powerful, local-first coding assistant built on the **TRM (Test-Reason-Modify) Recursive Reasoning** pattern. It stands on the shoulders of **Ollama** to provide high-level reasoning and execution capabilities directly in your terminal.

## 🚀 Quick Start

1. **Prerequisites**:
   - Install [Ollama](https://ollama.com/) and have it running.
### Model Selection
- **List models**: Run `python3 agent.py` without arguments to see available local models.
- **Switch model**: Run `python3 agent.py <number>` (e.g., `python3 agent.py 2`) to persistently switch models.
   - Pull a capable model (e.g., `llama3` or `codellama`):
     ```bash
     ollama pull llama3
     ```
   - Python 3.8+ and `requests` library.

2. **Installation**:
   ```bash
   # No complex install needed, just run the script
   python3 agent.py --help
   ```

3. **Run your first task**:
   ```bash
   python3 agent.py "Create a simple python script that prints the current system time"
   ```

## 🛠️ Features

- **Recursive Reasoning**: Uses the TRM pattern (K stages of improvement, L cycles of latent reasoning) to ensure high-quality output.
- **Tool Access**: Capable of reading/writing files, creating directories, executing shell commands, and searching the internet (via DuckDuckGo).
- **Auto-Approval**: Tools require authorization, but will auto-execute after 60 seconds (adjustable) to keep the workflow moving.
- **Skills Catalog**: Automatically catalogs successful solutions into `.skills/` for faster reuse.
- **Future Proof**: Clean CLI architecture that can easily be extended with a Web UI or VS Code extension.

## ⚙️ Configuration

You can customize the agent via `config.json` or command line arguments:

- `--url`: Ollama API URL (default: http://localhost:11434)
- `--model`: Ollama model to use (default: llama3)
- `--timeout`: Auto-approval timer (default: 60)
- `--ollama-timeout`: Request timeout in seconds (default: 120)
- `--ollama-retries`: Number of retries on connection issues (default: 3)

## 📖 Walkthroughs & Documentation

### Recursive Reasoning Explained
The agent doesn't just "guess" the answer. It follows a structured TRM loop:
1. **Initial Thought**: Analyzes the request.
2. **Latent Reasoning (L Cycles)**: Internally reflects on potential pitfalls, edge cases, and improvements.
3. **Action/Refinement**: Executes a tool or provides a final answer based on the accumulated reasoning.
4. **Improvement (K Steps)**: Repeats the entire process to polish the result.

### Tool Safety
Every sensitive action (file writes, command execution) pauses for user confirmation. If you're away, the agent will proceed after the timeout period, assuming you've granted it autonomy.

---
*Built with ❤️ for 10x Developers.*
