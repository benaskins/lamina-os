#!/usr/bin/env python3
"""
Test AI Comprehension of Sigil CLAUDE.md Files
Validates that sigil versions convey equivalent information using real LLM

🎨 Crafted by Luthier for empirical validation 🎨
"""

import json
import sys
import requests
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any
import time
import subprocess
import re

@dataclass
class ComprehensionTest:
    """Test case for measuring AI comprehension"""
    question: str
    expected_concepts: List[str]
    test_type: str  # "factual", "procedural", "conceptual"

@dataclass
class TestResult:
    """Result of a comprehension test"""
    question: str
    traditional_response: str
    sigil_response: str
    concepts_found_traditional: List[str]
    concepts_found_sigil: List[str]
    comprehension_score: float
    token_usage_traditional: int
    token_usage_sigil: int

# Test cases designed to validate sigil comprehension
COMPREHENSION_TESTS = [
    ComprehensionTest(
        question="What Python environment manager must be used for all projects?",
        expected_concepts=["uv", "required", "not pip", "not conda"],
        test_type="factual"
    ),
    ComprehensionTest(
        question="How do you run tests in the aurelia project?",
        expected_concepts=["make test", "uv run pytest", "test-fast", "test-coverage"],
        test_type="procedural"
    ),
    ComprehensionTest(
        question="What are the core principles of Aurelia's architecture?",
        expected_concepts=["breath", "vow", "sanctuary", "conscious operations", "ethical constraints"],
        test_type="conceptual"
    ),
    ComprehensionTest(
        question="What agents are part of the multi-agent system?",
        expected_concepts=["Clara", "Luna", "Vesna", "Phi", "conversational", "analysis", "security"],
        test_type="factual"
    ),
    ComprehensionTest(
        question="What is the configuration hierarchy in order of priority?",
        expected_concepts=["Agent", "System", "Infrastructure", "Environment", "highest priority", "agent.yaml"],
        test_type="procedural"
    ),
    ComprehensionTest(
        question="What backends does lamina-llm-serve support?",
        expected_concepts=["llama.cpp", "MLC-serve", "vLLM", "backend abstraction", "multiple engines"],
        test_type="factual"
    ),
]

class TestLLMClient:
    """Client for interacting with lamina-llm-serve"""
    
    def __init__(self, base_url: str = "http://localhost:8080", model: str = "llama3.2-1b-q4_k_m"):
        self.base_url = base_url
        self.model = model
        self.session = requests.Session()
    
    def is_available(self) -> bool:
        """Check if LLM is available"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_response(self, prompt: str, context: str) -> tuple[str, int]:
        """Generate response using lamina-llm-serve"""
        # Check if model is running
        try:
            models_response = self.session.get(f"{self.base_url}/models")
            if models_response.status_code != 200:
                return "Error: lamina-llm-serve not available", 0
        except:
            return "Error: Cannot connect to lamina-llm-serve", 0
        
        # Check if model is active, start it if needed
        model_response = self.session.get(f"{self.base_url}/models/{self.model}")
        if model_response.status_code == 200:
            model_info = model_response.json()
            if not model_info.get("active", False):
                print(f"  🚀 Starting model {self.model}...")
                start_response = self.session.post(f"{self.base_url}/models/{self.model}/start")
                if start_response.status_code != 200:
                    return f"Error: Failed to start model {self.model}", 0
                print(f"  ⏳ Waiting for model to initialize...")
                time.sleep(10)  # Give model more time to start
                
        # Verify model is ready
        model_response = self.session.get(f"{self.base_url}/models/{self.model}")
        if model_response.status_code == 200:
            model_info = model_response.json()
            if not model_info.get("active", False):
                return f"Error: Model {self.model} failed to start", 0
        
        full_prompt = f"""Based on the following documentation, please answer the question concisely.

Documentation:
{context}

Question: {prompt}

Answer:"""
        
        # Use lamina-llm-serve chat proxy format
        payload = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that answers questions based on documentation."},
                {"role": "user", "content": full_prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 200,
            "stream": False
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/chat/{self.model}",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            # Extract response based on backend format (llama.cpp typically uses 'content')
            if "choices" in result:
                answer = result["choices"][0]["message"]["content"].strip()
            elif "content" in result:
                answer = result["content"].strip()
            elif "response" in result:
                answer = result["response"].strip()
            else:
                answer = str(result)
            
            # Use actual token usage if available
            usage = result.get("usage", {})
            total_tokens = usage.get("total_tokens", 0)
            
            if total_tokens == 0:
                # Fallback estimation
                input_tokens = len(full_prompt.split()) * 1.3
                output_tokens = len(answer.split()) * 1.3
                total_tokens = int(input_tokens + output_tokens)
            
            return answer, total_tokens
            
        except Exception as e:
            print(f"❌ LLM API error: {e}")
            return f"Error: {str(e)}", 0

def ensure_lamina_llm_serve_running() -> bool:
    """Ensure lamina-llm-serve is running with a model"""
    client = TestLLMClient()
    
    if client.is_available():
        print("✅ lamina-llm-serve is already running")
        return True
    
    print("🚀 Starting lamina-llm-serve...")
    try:
        # Start lamina-llm-serve in background
        result = subprocess.run(
            ["uv", "run", "python", "-m", "lamina_llm_serve.server"],
            cwd="/Users/benaskins/dev/lamina-os/packages/lamina-llm-serve",
            capture_output=True,
            text=True,
            timeout=10  # Quick start check
        )
        
        # Give it a moment to start
        time.sleep(2)
        
        if client.is_available():
            print("✅ lamina-llm-serve started successfully")
            return True
        else:
            print("❌ lamina-llm-serve failed to start properly")
            print("💡 Please start manually: cd packages/lamina-llm-serve && uv run python -m lamina_llm_serve.server")
            return False
            
    except subprocess.TimeoutExpired:
        # Server might be starting in background, check if available
        time.sleep(3)
        if client.is_available():
            print("✅ lamina-llm-serve is now available")
            return True
        else:
            print("❌ lamina-llm-serve startup timeout")
            return False
    except Exception as e:
        print(f"❌ Error starting lamina-llm-serve: {e}")
        print("💡 Please start manually: cd packages/lamina-llm-serve && uv run python -m lamina_llm_serve.server")
        return False

def real_ai_response(content: str, question: str, llm_client: TestLLMClient) -> tuple[str, int]:
    """Get real AI response using containerized LLM"""
    return llm_client.generate_response(question, content)

def calculate_comprehension_score(response: str, expected_concepts: List[str]) -> tuple[float, List[str]]:
    """Calculate comprehension score based on concept coverage"""
    response_lower = response.lower()
    found_concepts = []
    
    for concept in expected_concepts:
        # More flexible matching for real LLM responses
        concept_lower = concept.lower()
        
        # Direct match
        if concept_lower in response_lower:
            found_concepts.append(concept)
        # Partial/fuzzy matching for common variations
        elif concept_lower == "uv" and ("uv " in response_lower or " uv" in response_lower):
            found_concepts.append(concept)
        elif concept_lower == "not pip" and ("not pip" in response_lower or "avoid pip" in response_lower or "don't use pip" in response_lower):
            found_concepts.append(concept)
        elif concept_lower == "make test" and ("make test" in response_lower or "makefile" in response_lower):
            found_concepts.append(concept)
        elif concept_lower == "breath" and ("breath" in response_lower or "breathing" in response_lower):
            found_concepts.append(concept)
    
    score = len(found_concepts) / len(expected_concepts) if expected_concepts else 0.0
    return score, found_concepts

def run_comprehension_test(traditional_file: Path, sigil_file: Path, llm_client: TestLLMClient) -> List[TestResult]:
    """Run comprehension tests comparing traditional vs sigil using real LLM"""
    
    # Read both files
    with open(traditional_file, 'r', encoding='utf-8') as f:
        traditional_content = f.read()
    
    with open(sigil_file, 'r', encoding='utf-8') as f:
        sigil_content = f.read()
    
    results = []
    
    for test in COMPREHENSION_TESTS:
        print(f"🧪 Testing: {test.question}")
        
        # Get responses from both versions using real LLM
        print("  📝 Querying traditional format...")
        trad_response, trad_tokens = real_ai_response(traditional_content, test.question, llm_client)
        
        print("  📝 Querying sigil format...")
        sigil_response, sigil_tokens = real_ai_response(sigil_content, test.question, llm_client)
        
        # Calculate comprehension scores
        trad_score, trad_concepts = calculate_comprehension_score(trad_response, test.expected_concepts)
        sigil_score, sigil_concepts = calculate_comprehension_score(sigil_response, test.expected_concepts)
        
        result = TestResult(
            question=test.question,
            traditional_response=trad_response,
            sigil_response=sigil_response,
            concepts_found_traditional=trad_concepts,
            concepts_found_sigil=sigil_concepts,
            comprehension_score=sigil_score / trad_score if trad_score > 0 else (1.0 if sigil_score > 0 else 0.0),
            token_usage_traditional=trad_tokens,
            token_usage_sigil=sigil_tokens
        )
        
        results.append(result)
        
        print(f"  Traditional score: {trad_score:.2f} (found: {trad_concepts})")
        print(f"  Sigil score: {sigil_score:.2f} (found: {sigil_concepts})")
        print(f"  Relative comprehension: {result.comprehension_score:.2f}")
        print(f"  Traditional response: {trad_response[:100]}...")
        print(f"  Sigil response: {sigil_response[:100]}...")
        print()
    
    return results

def analyze_results(results: List[TestResult]) -> Dict[str, Any]:
    """Analyze test results and generate summary"""
    
    total_tests = len(results)
    avg_comprehension = sum(r.comprehension_score for r in results) / total_tests
    avg_token_reduction = sum(
        1 - (r.token_usage_sigil / r.token_usage_traditional) 
        for r in results
    ) / total_tests
    
    successful_tests = len([r for r in results if r.comprehension_score >= 0.8])
    
    analysis = {
        "total_tests": total_tests,
        "successful_tests": successful_tests,
        "success_rate": successful_tests / total_tests,
        "average_comprehension_retention": avg_comprehension,
        "average_token_reduction": avg_token_reduction,
        "detailed_results": [
            {
                "question": r.question,
                "comprehension_score": r.comprehension_score,
                "token_reduction": 1 - (r.token_usage_sigil / r.token_usage_traditional),
                "traditional_concepts": r.concepts_found_traditional,
                "sigil_concepts": r.concepts_found_sigil
            }
            for r in results
        ]
    }
    
    return analysis

def main():
    """Main test execution"""
    
    print("🧪 Real LLM Sigil Comprehension Testing with lamina-llm-serve")
    print("=" * 65)
    
    # Ensure lamina-llm-serve is running
    if not ensure_lamina_llm_serve_running():
        print("❌ Cannot start lamina-llm-serve. Please start manually and retry.")
        print("💡 Manual start: cd packages/lamina-llm-serve && uv run python -m lamina_llm_serve.server")
        sys.exit(1)
    
    # Initialize LLM client
    llm_client = TestLLMClient()
    
    # Verify LLM is responding
    print("🔍 Testing lamina-llm-serve connectivity...")
    test_response, _ = llm_client.generate_response("Hello, can you respond?", "Test context")
    if "Error:" in test_response:
        print(f"❌ lamina-llm-serve connectivity test failed: {test_response}")
        print("💡 Please ensure lamina-llm-serve is running with model llama3.2-1b-q4_k_m")
        sys.exit(1)
    print(f"✅ lamina-llm-serve is responding: {test_response[:50]}...")
    print()
    
    # Test aurelia CLAUDE.md files
    aurelia_trad = Path("/Users/benaskins/dev/aurelia/CLAUDE.md")
    aurelia_sigil = Path("/Users/benaskins/dev/aurelia/CLAUDE.sigil.md")
    
    if not aurelia_trad.exists() or not aurelia_sigil.exists():
        print("❌ Aurelia test files not found")
        return
    
    print("📁 Testing Aurelia CLAUDE.md files with real LLM via lamina-llm-serve")
    aurelia_results = run_comprehension_test(aurelia_trad, aurelia_sigil, llm_client)
    
    all_results = aurelia_results
    
    # Analyze combined results
    analysis = analyze_results(all_results)
    
    print("📊 FINAL ANALYSIS (Real LLM Testing via lamina-llm-serve)")
    print("=" * 65)
    print(f"✅ Success Rate: {analysis['success_rate']:.1%}")
    print(f"🧠 Avg Comprehension Retention: {analysis['average_comprehension_retention']:.1%}")
    print(f"📉 Avg Token Reduction: {analysis['average_token_reduction']:.1%}")
    print(f"🧪 Total Tests: {analysis['total_tests']}")
    print(f"✅ Successful Tests: {analysis['successful_tests']}")
    
    # Save detailed results
    timestamp = int(time.time())
    output_file = Path(f"sigil_comprehension_test_results_lamina_llm_{timestamp}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {output_file}")
    
    # Verdict with real LLM standards
    if analysis['success_rate'] >= 0.7 and analysis['average_comprehension_retention'] >= 0.7:
        print("\n✅ SIGIL SYSTEM VALIDATION: SUCCESS")
        print("Sigil format maintains LLM comprehension while reducing tokens")
    elif analysis['average_token_reduction'] >= 0.5:
        print("\n⚠️ SIGIL SYSTEM VALIDATION: PARTIAL SUCCESS")
        print("Good token reduction but some LLM comprehension loss")
    else:
        print("\n❌ SIGIL SYSTEM VALIDATION: INSUFFICIENT")
        print("Token reduction or comprehension targets not met")
    
    print(f"\n🔧 Using lamina-llm-serve with model: llama3.2-1b-q4_k_m")

if __name__ == '__main__':
    main()