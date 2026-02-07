import argparse
import json
import os
import sys
from ollama_client import OllamaClient
from tool_engine import ToolEngine
from skills_manager import SkillsManager

class TRMCodingAgent:
    def __init__(self, config):
        self.config = config
        self.ollama = OllamaClient(
            base_url=config['ollama_url'], 
            model=config['model'],
            timeout=config.get('ollama_timeout', 120),
            retries=config.get('ollama_retries', 3)
        )
        self.tools = ToolEngine(timeout=config['timeout'])
        self.skills = SkillsManager()
        self.history = []

    def recursive_reasoning(self, task, max_steps=50, L_cycles=3):
        """The TRM reasoning loop: think, refine, act. Continues until completion."""
        print(f"\n🚀 Starting Task: {task}")
        current_state = f"Task: {task}"
        
        for k in range(max_steps):
            print(f"\n--- 🧠 Step {k+1} ---")
            
            # Determine if this step needs deep reasoning
            is_complex = self._is_complex_task(task, current_state)
            
            reflections = []
            if is_complex:
                # Reasoning Cycles (L)
                for l in range(L_cycles):
                    print(f"  💭 Reasoning Cycle {l+1}/{L_cycles}... ", end="", flush=True)
                    prompt = self._build_reasoning_prompt(task, current_state, reflections)
                    thought = self.ollama.generate(prompt, temperature=0.5)
                    
                    if thought:
                        reflections.append(thought)
                        print("✅")
            else:
                print("  ⚡ Processing Action...", end="", flush=True)
            
            if is_complex:
                print(f"  ✨ Reasoning complete. Processing action...")
            else:
                print(" ✅")
            
            # Action Phase
            action_prompt = self._build_action_prompt(task, current_state, reflections)
            action_json = self.ollama.generate(action_prompt, temperature=0.2, stop=["```"])
            
            # Try to parse and run tool
            try:
                if not action_json:
                    raise ValueError("Ollama returned an empty response.")

                # Advanced cleaning of LLM output for JSON
                clean_json = action_json.strip()
                if "{" in clean_json:
                    clean_json = clean_json[clean_json.find("{"):clean_json.rfind("}")+1]
                
                action = json.loads(clean_json)
                if action.get("tool"):
                    result = self.tools.run_tool(action["tool"], action.get("args", {}))
                    if "not found" in result.lower():
                        result += f"\n💡 Hint: Choose from available tools: {list(self.tools.tools.keys())}"
                    
                    current_state += f"\nAction: {action['tool']}\nResult: {result}"
                    print(f"  🛠️  Tool Result: {result[:100]}...")
                elif action.get("final_answer"):
                    print(f"\n✅ Task Completed: {action['final_answer']}")
                    return action['final_answer']
                else:
                    print(f"  ⚠️  No tool or final_answer found. Re-evaluating next step.")
                    current_state += "\nAction: No valid tool provided. Reasoning must be more specific."
            except Exception as e:
                current_state += f"\nError parsing action: {e}. Thought: {action_json[:200]}..."
                print(f"  ❌ Failed to parse action: {e}")
                # Optional: self-correction step could go here

        print("\n⚠️  Maximum reasoning attempts reached.")
        return "Max steps reached."

    def _is_complex_task(self, task, state):
        """Quickly assess if the current step requires deep reasoning."""
        prompt = f"""Task: {task}
Current State: {state}

Does the NEXT step require complex planning or code generation?
Respond with ONLY 'YES' or 'NO'.
Complex:"""
        decision = self.ollama.generate(prompt, temperature=0.1)
        return "YES" in decision.upper()

    def _build_reasoning_prompt(self, task, state, reflections):
        return f"""You are a 10x Senior Developer AI using TRM Reasoning.
Context: {state}
Reflections so far: {json.dumps(reflections)}

Analyze the task and progress. What is the next logical step to complete the task? 
Focus on identifying errors, missing information, or complex logic needs.
Keep your reasoning deep but concise."""

    def _build_action_prompt(self, task, state, reflections):
        skills_context = json.dumps([s['name'] for s in self.skills.list_skills()])
        tools_schema = self.tools.get_tool_schema()
        return f"""You are a 10x Senior Developer. You MUST complete the task using the provided tools.
Available Tools:
{tools_schema}

Available Skills: {skills_context}

Based on these reflections: {json.dumps(reflections)}
And current state: {state}

Choose exactly ONE action from the tools above. Use `execute_command` for system operations not covered by other tools.
Output ONLY a valid JSON object.
Format for tool usage:
{{
  "tool": "tool_name",
  "args": {{ "arg1": "value" }}
}}

If the task is fully completed, verify everything and output:
{{
  "final_answer": "Summary of what was done and verification results."
}}

JSON only:"""

def main():
    parser = argparse.ArgumentParser(description="TRM-Sim Coding Agent")
    parser.add_argument("task", nargs="?", help="The task for the agent to perform")
    parser.add_argument("--url", default="http://localhost:11434", help="Ollama URL")
    parser.add_argument("--model", default="llama3", help="Ollama model name")
    parser.add_argument("--timeout", type=int, default=60, help="Auto-approval timeout in seconds")
    parser.add_argument("--ollama-timeout", type=int, default=2000, help="Ollama request timeout in seconds")
    parser.add_argument("--ollama-retries", type=int, default=3, help="Ollama request retries")
    parser.add_argument("--config", help="Path to custom config.json")
    
    args = parser.parse_args()
    
    # Load or create config
    config = {
        "ollama_url": args.url,
        "model": args.model,
        "timeout": args.timeout,
        "ollama_timeout": getattr(args, 'ollama_timeout', 2000),
        "ollama_retries": getattr(args, 'ollama_retries', 3)
    }
    
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config.update(json.load(f))

    if not args.task:
        agent = TRMCodingAgent(config)
        models = agent.ollama.list_models()
        if models:
            print("\n🤖 Available Ollama Models:")
            for i, model in enumerate(models, 1):
                star = "⭐ " if model == config['model'] else "   "
                print(f"{star}{i}. {model}")
            print("\n💡 Tip: Run `python3 agent.py <number>` to switch models.")
        else:
            print("\n❌ No models found. Is Ollama running?")
        sys.exit(0)

    # Handle numeric model selection
    if args.task.isdigit():
        agent = TRMCodingAgent(config)
        models = agent.ollama.list_models()
        idx = int(args.task) - 1
        if 0 <= idx < len(models):
            new_model = models[idx]
            config['model'] = new_model
            with open(args.config or "config.json", 'w') as f:
                json.dump(config, f, indent=2)
            print(f"\n✅ Model switched to: {new_model}")
            sys.exit(0)
        else:
            print(f"\n❌ Invalid model number: {args.task}")
            sys.exit(1)

    agent = TRMCodingAgent(config)
    agent.recursive_reasoning(args.task)

if __name__ == "__main__":
    main()
