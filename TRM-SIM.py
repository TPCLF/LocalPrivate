import requests
import json
import time

class TRMSimulator:
    def __init__(self, ollama_url="http://localhost:11434", model="gpt-oss-20b"):
        self.ollama_url = ollama_url
        self.model = model
    
    def query_ollama(self, prompt, temperature=0.7):
        """Query Ollama instance"""
        try:
            response = requests.post(f"{self.ollama_url}/api/generate", 
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": temperature}
                })
            return response.json().get("response", "").strip()
        except Exception as e:
            print(f"Error querying Ollama: {e}")
            return ""
    
    def recursive_reasoning(self, question, K_steps=3, L_cycles=4):
        """
        Simulate TRM's recursive reasoning process:
        1. Initial answer y
        2. For K improvement steps:
           - Update latent understanding z (L_cycles times)
           - Update answer y based on new understanding
        """
        print(f"🧠 TRM Simulation: {K_steps} improvement steps, {L_cycles} reasoning cycles each\n")
        print(f"❓ Question: {question}\n")
        
        # Step 1: Initial answer
        initial_prompt = f"Solve this problem step by step:\n{question}\n\nAnswer:"
        current_answer = self.query_ollama(initial_prompt)
        print(f"🎯 Initial Answer: {current_answer}\n")
        
        # Step 2: Recursive improvement
        for k in range(K_steps):
            print(f"🔄 Improvement Step {k+1}/{K_steps}")
            
            # Simulate latent state updates (L_cycles)
            latent_understanding = ""
            for cycle in range(L_cycles):
                reasoning_prompt = f"""
Given:
- Original question: {question}
- Current answer: {current_answer}
- Previous reasoning: {latent_understanding}

Cycle {cycle+1}/{L_cycles}: What aspects of this problem need deeper consideration? 
What errors or improvements can be made to the current answer?
Provide brief insights:"""
                
                cycle_insight = self.query_ollama(reasoning_prompt, temperature=0.5)
                latent_understanding += f"Cycle {cycle+1}: {cycle_insight}\n"
                print(f"  💭 Reasoning Cycle {cycle+1}: {cycle_insight}")
            
            # Update answer based on accumulated understanding
            improvement_prompt = f"""
Original question: {question}
Current answer: {current_answer}

Based on these insights:
{latent_understanding}

Provide an improved answer that addresses any issues found:"""
            
            improved_answer = self.query_ollama(improvement_prompt, temperature=0.3)
            
            print(f"  ✨ Improved Answer: {improved_answer}\n")
            current_answer = improved_answer
        
        print(f"🎉 Final Answer after {K_steps} recursive improvements: {current_answer}")
        return current_answer

def main():
    # Test questions (you can modify these)
    test_questions = [
        "If I have 3 apples and I give away 2, then buy 5 more, how many apples do I have?",
        
        "A farmer has chickens and cows. There are 30 heads and 74 legs total. How many chickens and how many cows?",
        
        "What comes next in this sequence: 2, 6, 12, 20, 30, ?",
        
        # Simple ARC-like pattern (you can add more complex ones)
        """Pattern recognition: 
        Input grid:  [1,0,1]
                     [0,1,0] 
                     [1,0,1]
        
        What rule transforms this to output:
                     [0,1,0]
                     [1,0,1]
                     [0,1,0]"""
    ]
    
    trm = TRMSimulator()
    
    for i, question in enumerate(test_questions, 1):
        print("="*80)
        print(f"TEST {i}")
        print("="*80)
        
        start_time = time.time()
        result = trm.recursive_reasoning(question, K_steps=2, L_cycles=3)
        elapsed = time.time() - start_time
        
        print(f"\n⏱️  Total time: {elapsed:.1f} seconds")
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()