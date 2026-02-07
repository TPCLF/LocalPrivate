import os
import subprocess
import json
import time
import sys
import select

class ToolEngine:
    def __init__(self, timeout=60):
        self.timeout = timeout
        self.tools = {
            "read_file": self.read_file,
            "write_file": self.write_file,
            "list_dir": self.list_dir,
            "make_directory": self.make_directory,
            "execute_command": self.execute_command,
            "search_internet": self.search_internet
        }

    def get_tool_schema(self):
        """Returns a string description of available tools for the LLM prompt."""
        return """
- read_file(path: str): Reads the content of a file.
- write_file(path: str, content: str): Writes content to a file. Creates parent directories if needed.
- list_dir(path: str = "."): Lists files in a directory.
- make_directory(path: str): Creates a new directory (including parents).
- execute_command(command: str): Runs a shell command and returns stdout/stderr.
- search_internet(query: str): Searches the web for information.
"""

    def ask_permission(self, tool_name, args):
        print(f"\n⚠️  [ACTION] Tool: {tool_name}")
        print(f"   Arguments: {json.dumps(args, indent=2)}")
        print(f"   Auto-approving in {self.timeout} seconds... (Press ENTER to approve, 'n' to deny)")
        
        # Simple cross-platform timeout input
        if sys.stdin in select.select([sys.stdin], [], [], self.timeout)[0]:
            line = sys.stdin.readline().strip().lower()
            if line == 'n':
                return False
        return True

    def read_file(self, path):
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    def write_file(self, path, content):
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(content)
            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Error writing file: {e}"

    def list_dir(self, path="."):
        try:
            return "\n".join(os.listdir(path))
        except Exception as e:
            return f"Error listing directory: {e}"

    def make_directory(self, path):
        try:
            os.makedirs(path, exist_ok=True)
            return f"Successfully created directory {path}"
        except Exception as e:
            return f"Error creating directory: {e}"

    def execute_command(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
            return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        except Exception as e:
            return f"Error executing command: {e}"

    def search_internet(self, query):
        # Placeholder for duckduckgo-search if missing
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(query, max_results=5)]
                return json.dumps(results, indent=2)
        except ImportError:
            return "Error: duckduckgo-search package not installed. Search unavailable."
        except Exception as e:
            return f"Error during search: {e}"

    def run_tool(self, tool_name, args):
        if tool_name not in self.tools:
            return f"Error: Tool {tool_name} not found."
        
        if self.ask_permission(tool_name, args):
            return self.tools[tool_name](**args)
        else:
            return "Permission denied by user."
