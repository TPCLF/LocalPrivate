# LocalPrivate Quick Start Guide

LocalPrivate is a CLI agent with wiki persistence, a test harness, and multiple operational modes. This guide will walk you through the setup and show you how to link the harness to a local LLM through LM Studio.

## Dependency Setup

Ensure you have Python 3 installed. It is highly recommended (and safest) to run this project inside a Python virtual environment to keep dependencies isolated and avoid system-wide package conflicts.

Navigate to the `LocalPrivate` project directory and create a virtual environment:

```bash
python3 -m venv venv
```
*(Note for Ubuntu/Debian users: If the above command fails stating that `ensurepip is not available`, you may need to run `sudo apt install python3-venv` before creating the virtual environment).*

Activate the virtual environment. You will need to do this every time you open a new terminal to work on or run this project:

- **On Linux and macOS:**
  ```bash
  source venv/bin/activate
  ```
- **On Windows:**
  ```bash
  venv\Scripts\activate
  ```

Once the virtual environment is activated (you should see `(venv)` at the beginning of your terminal prompt), install the necessary dependencies via pip:

```bash
pip install -r requirements.txt
```
This will install `requests`, `openai`, and `pytest`. Ensure that all `python3` commands listed later in this guide are executed while your virtual environment is active.

## LM Studio Setup

This harness is designed pointing directly to **LM Studio**'s Local Inference Server default port. 
1. Open **LM Studio**.
2. Go to the **Local Server** option menu (usually the "<->" icon in the left rail).
3. Load your preferred model on the top panel.
4. Ensure the server port is set to `1234` (the default).
5. Click **Start Server**.

## Installation Questionnaire

The first time you run `LocalPrivate.py`, you need to properly initialize your agent profile (the "soul") and its working directory. 

Run the installation questionnaire by using the `--install` argument:
```bash
python3 LocalPrivate.py --install
```

The application will prompt you for the following inputs:
- `What is your agent name?`: The system's identity name.
- `What is its core purpose?`: The goal or function of your new agent.
- `Developer/Owner name?`: The primary maintainer of this system.

This creates an initialization folder containing configurations at `~/.LocalPrivate/`. 

## Running the Application

Once successfully installed, you have three primary ways to interact with the agent:

### 1. Interactive CLI (Conversational Mode)
Run the agent in a continuous, Claude-like conversational loop. This is the default mode where you can chat, access the wiki, and trigger tests dynamically.

```bash
python3 LocalPrivate.py --mode cli
```
*(Or simply `python3 LocalPrivate.py` since CLI is the default)*

### 2. Single Task Command
If you want the agent to execute a one-off objective without entering the interactive shell, use the `--task` flag.

```bash
python3 LocalPrivate.py --task "Write a python script that prints hello world"
```

### 3. API Server Mode
To run the agent as a local service that other applications can send requests to, launch it in API mode.

### 4. Sandboxed Directory Target
For maximum security and directory control, you can launch the agent explicitly inside a target folder. The system will sandbox the agent natively to that directory, locking `read_file` and `write_file` tool permissions so the LLM mathematically cannot traverse outside that active project root. 

```bash
# General CLI mode locked to the snake_game sandbox folder:
python3 LocalPrivate.py /home/user/snake_game --mode cli
```
