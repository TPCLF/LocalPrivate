```Special Note: I've been struggling with an aspect of github copilot and something that I think degrades the code ouput. This repo will serve as a testing ground. Next update will be posted here.```

# TRM Simulation with Ollama

A Python implementation that simulates the Tiny Recursion Model (TRM) recursive reasoning process using your local Ollama instance. This allows you to experiment with TRM-style reasoning without training models from scratch.

## Overview

This script recreates the core TRM recursive reasoning approach:
1. **Initial Answer**: Generate first response to the question
2. **Recursive Reasoning**: Multiple cycles of self-reflection and analysis
3. **Progressive Improvement**: Iteratively refine the answer based on insights
4. **Parameter Efficiency**: Uses prompting instead of training new model weights

## Requirements

- Python 3.7+
- [Ollama](https://ollama.ai/) installed and running
- A compatible language model (tested with GPT-OSS 20B)

```bash
pip install requests
```

## Installation

1. **Install Ollama** (if not already installed):
   ```bash
   # On macOS/Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # On Windows - download from https://ollama.ai/
   ```

2. **Download a model**:
   ```bash
   ollama pull gpt-oss-20b
   # or any other model you prefer: llama2, mistral, codellama, etc.
   ```

3. **Clone/download the script**:
   ```bash
   wget https://raw.githubusercontent.com/your-repo/trm_simulation.py
   # or copy the code from above
   ```

## Usage

### Basic Usage

1. **Start Ollama** (if not running):
   ```bash
   ollama serve
   ```

2. **Run the simulation**:
   ```bash
   python trm_simulation.py
   ```

### Custom Questions

Edit the `test_questions` list in the script or create your own:

```python
custom_questions = [
    "Your math problem here",
    "Your logic puzzle here", 
    "Your pattern recognition task here"
]

trm = TRMSimulator()
for question in custom_questions:
    result = trm.recursive_reasoning(question, K_steps=3, L_cycles=4)
```

### Configuration Options

#### Model Settings
```python
# Use different model
trm = TRMSimulator(model="llama2")

# Different Ollama endpoint
trm = TRMSimulator(ollama_url="http://remote-server:11434")
```

#### Reasoning Parameters
```python
# More intensive reasoning
result = trm.recursive_reasoning(
    question="Your question",
    K_steps=5,      # More improvement steps
    L_cycles=6      # More reasoning cycles per step
)

# Faster reasoning
result = trm.recursive_reasoning(
    question="Your question", 
    K_steps=2,      # Fewer improvement steps
    L_cycles=2      # Fewer reasoning cycles per step
)
```

## Example Output

```
🧠 TRM Simulation: 2 improvement steps, 3 reasoning cycles each

❓ Question: A farmer has chickens and cows. There are 30 heads and 74 legs total. How many chickens and how many cows?

🎯 Initial Answer: Let me set up equations. Each animal has 1 head. Chickens have 2 legs, cows have 4 legs...

🔄 Improvement Step 1/2
  💭 Reasoning Cycle 1: Need to check if the algebra is correct...
  💭 Reasoning Cycle 2: Should verify the solution makes sense...
  💭 Reasoning Cycle 3: Could double-check by substitution...
  ✨ Improved Answer: Let me solve this systematically. Let c = chickens, w = cows...

🔄 Improvement Step 2/2
  💭 Reasoning Cycle 1: The equations look correct now...
  💭 Reasoning Cycle 2: Final answer should be verified...
  💭 Reasoning Cycle 3: All constraints are satisfied...
  ✨ Improved Answer: Final answer: 23 chickens and 7 cows...

🎉 Final Answer after 2 recursive improvements: 23 chickens and 7 cows...

⏱️  Total time: 45.2 seconds
```

## Test Categories

The script includes several test categories you can expand:

### Mathematics
```python
math_questions = [
    "If I have 3 apples and I give away 2, then buy 5 more, how many apples do I have?",
    "A farmer has chickens and cows. There are 30 heads and 74 legs total. How many chickens and how many cows?",
    "What's the derivative of x^3 + 2x^2 - 5x + 3?"
]
```

### Logic & Reasoning
```python
logic_questions = [
    "All birds can fly. Penguins are birds. Can penguins fly? Explain the contradiction.",
    "If all A are B, and all B are C, and John is A, what can we conclude about John?",
    "You have 12 balls, one weighs different. You have a balance scale. What's the minimum weighings needed?"
]
```

### Pattern Recognition
```python
pattern_questions = [
    "What comes next in this sequence: 2, 6, 12, 20, 30, ?",
    "Complete the pattern: ABC, BCD, CDE, ___",
    "Grid pattern: [1,0,1] [0,1,0] [1,0,1] -> [0,1,0] [1,0,1] [0,1,0]. What's the rule?"
]
```

### ARC-AGI Style Tasks
```python
arc_questions = [
    """Pattern recognition: 
    Input:  [1,0,1]
            [0,1,0] 
            [1,0,1]
    
    Output: [0,1,0]
            [1,0,1]
            [0,1,0]
    
    What transformation rule produces this output?""",
    
    """Color pattern:
    Input:  [R,B,R]
            [B,R,B]
            [R,B,R]
    
    If the rule changes R->G and B->Y, what's the output?"""
]
```

## Performance Tuning

### Speed vs Quality Tradeoffs

```python
# Fast but less thorough
quick_reasoning = trm.recursive_reasoning(question, K_steps=1, L_cycles=2)

# Thorough but slower  
deep_reasoning = trm.recursive_reasoning(question, K_steps=5, L_cycles=6)

# Balanced (recommended)
balanced_reasoning = trm.recursive_reasoning(question, K_steps=3, L_cycles=4)
```

### Temperature Settings

The script uses different temperatures for different phases:
- **Reasoning cycles**: `temperature=0.5` (moderate creativity)
- **Answer updates**: `temperature=0.3` (more focused)
- **Initial answer**: `temperature=0.7` (more creative)

## Troubleshooting

### Common Issues

1. **Ollama not running**:
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   
   # Start Ollama
   ollama serve
   ```

2. **Model not found**:
   ```bash
   # List available models
   ollama list
   
   # Download missing model
   ollama pull gpt-oss-20b
   ```

3. **Connection errors**:
   ```python
   # Check different port/host
   trm = TRMSimulator(ollama_url="http://localhost:11434")
   ```

4. **Slow responses**:
   - Reduce `K_steps` and `L_cycles`
   - Use smaller/faster model
   - Check system resources

### Memory Usage

For large models or many reasoning steps:
- Monitor RAM usage
- Reduce batch processing
- Use smaller models for experimentation

## Comparison to Real TRM

| Feature | Real TRM | This Simulation |
|---------|----------|-----------------|
| **Training** | Trains 7M parameter model | Uses existing LLM |
| **Speed** | Very fast inference | Slower (multiple API calls) |
| **Accuracy** | 45% on ARC-AGI-1 | Depends on base model |
| **Cost** | Requires training | Only inference costs |
| **Flexibility** | Fixed architecture | Easy to modify reasoning |

## Contributing

Feel free to:
- Add new test question categories
- Improve the reasoning prompts
- Optimize for different models
- Add evaluation metrics
- Create domain-specific versions

## License

This simulation script is provided as-is for educational and research purposes.
