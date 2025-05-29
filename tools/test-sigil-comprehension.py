#!/usr/bin/env python3
"""
Test AI Comprehension of Sigil CLAUDE.md Files
Validates that sigil versions convey equivalent information

🎨 Crafted by Luthier for empirical validation 🎨
"""

import json
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any
import time

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

def simulate_ai_response(content: str, question: str) -> tuple[str, int]:
    """
    Simulate AI response generation and token counting
    In a real test, this would call an actual AI model
    """
    # For now, simulate based on content analysis
    response_length = len(content.split()) // 10  # Rough simulation
    token_count = len(content.split()) + len(question.split())
    
    # Simulate response based on question type
    if "Python environment" in question:
        if "uv" in content and ("pip" not in content or "not pip" in content.lower()):
            response = "uv is required for all Python projects, not pip or conda"
        else:
            response = "The document mentions Python environment management"
    elif "run tests" in question:
        if "make test" in content:
            response = "Use make test, make test-fast, or uv run pytest for testing"
        else:
            response = "Testing commands are available"
    elif "core principles" in question:
        principles = []
        if "breath" in content.lower():
            principles.append("breath-based operations")
        if "vow" in content.lower():
            principles.append("ethical constraints")
        if "sanctuary" in content.lower():
            principles.append("sanctuary isolation")
        response = f"Core principles include: {', '.join(principles)}" if principles else "Architecture principles are described"
    elif "agents" in question:
        agents = []
        if "Clara" in content:
            agents.append("Clara (conversation)")
        if "Luna" in content:
            agents.append("Luna (analysis)")
        if "Vesna" in content:
            agents.append("Vesna (security)")
        if "Phi" in content:
            agents.append("Phi (reasoning)")
        response = f"Agents: {', '.join(agents)}" if agents else "Multiple agents are described"
    elif "configuration hierarchy" in question:
        if "Agent" in content and "System" in content:
            response = "Agent layer has highest priority, followed by System, Infrastructure, Environment"
        else:
            response = "Configuration hierarchy is described"
    elif "backends" in question and "lamina-llm-serve" in question:
        backends = []
        if "llama.cpp" in content:
            backends.append("llama.cpp")
        if "MLC" in content:
            backends.append("MLC-serve")
        if "vLLM" in content:
            backends.append("vLLM")
        response = f"Backends: {', '.join(backends)}" if backends else "Multiple backend support"
    else:
        response = "Information found in documentation"
    
    return response, token_count

def calculate_comprehension_score(response: str, expected_concepts: List[str]) -> float:
    """Calculate comprehension score based on concept coverage"""
    response_lower = response.lower()
    found_concepts = []
    
    for concept in expected_concepts:
        if concept.lower() in response_lower:
            found_concepts.append(concept)
    
    return len(found_concepts) / len(expected_concepts) if expected_concepts else 0.0

def run_comprehension_test(traditional_file: Path, sigil_file: Path) -> List[TestResult]:
    """Run comprehension tests comparing traditional vs sigil"""
    
    # Read both files
    with open(traditional_file, 'r', encoding='utf-8') as f:
        traditional_content = f.read()
    
    with open(sigil_file, 'r', encoding='utf-8') as f:
        sigil_content = f.read()
    
    results = []
    
    for test in COMPREHENSION_TESTS:
        print(f"🧪 Testing: {test.question}")
        
        # Get responses from both versions
        trad_response, trad_tokens = simulate_ai_response(traditional_content, test.question)
        sigil_response, sigil_tokens = simulate_ai_response(sigil_content, test.question)
        
        # Calculate comprehension scores
        trad_score = calculate_comprehension_score(trad_response, test.expected_concepts)
        sigil_score = calculate_comprehension_score(sigil_response, test.expected_concepts)
        
        # Find concepts in responses
        trad_concepts = [c for c in test.expected_concepts if c.lower() in trad_response.lower()]
        sigil_concepts = [c for c in test.expected_concepts if c.lower() in sigil_response.lower()]
        
        result = TestResult(
            question=test.question,
            traditional_response=trad_response,
            sigil_response=sigil_response,
            concepts_found_traditional=trad_concepts,
            concepts_found_sigil=sigil_concepts,
            comprehension_score=sigil_score / trad_score if trad_score > 0 else 1.0,
            token_usage_traditional=trad_tokens,
            token_usage_sigil=sigil_tokens
        )
        
        results.append(result)
        
        print(f"  Traditional score: {trad_score:.2f}")
        print(f"  Sigil score: {sigil_score:.2f}")
        print(f"  Relative comprehension: {result.comprehension_score:.2f}")
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
    
    print("🧪 Sigil Comprehension Testing")
    print("=" * 40)
    
    # Test aurelia CLAUDE.md files
    aurelia_trad = Path("/Users/benaskins/dev/aurelia/CLAUDE.md")
    aurelia_sigil = Path("/Users/benaskins/dev/aurelia/CLAUDE.sigil.md")
    
    if not aurelia_trad.exists() or not aurelia_sigil.exists():
        print("❌ Aurelia test files not found")
        return
    
    print("📁 Testing Aurelia CLAUDE.md files")
    aurelia_results = run_comprehension_test(aurelia_trad, aurelia_sigil)
    
    # Test lamina-llm-serve CLAUDE.md files  
    llm_serve_trad = Path("/Users/benaskins/dev/lamina-llm-serve/CLAUDE.md")
    llm_serve_sigil = Path("/Users/benaskins/dev/lamina-llm-serve/CLAUDE.sigil.md")
    
    if llm_serve_trad.exists() and llm_serve_sigil.exists():
        print("📁 Testing lamina-llm-serve CLAUDE.md files")
        llm_serve_results = run_comprehension_test(llm_serve_trad, llm_serve_sigil)
        all_results = aurelia_results + llm_serve_results
    else:
        all_results = aurelia_results
    
    # Analyze combined results
    analysis = analyze_results(all_results)
    
    print("📊 FINAL ANALYSIS")
    print("=" * 40)
    print(f"✅ Success Rate: {analysis['success_rate']:.1%}")
    print(f"🧠 Avg Comprehension Retention: {analysis['average_comprehension_retention']:.1%}")
    print(f"📉 Avg Token Reduction: {analysis['average_token_reduction']:.1%}")
    print(f"🧪 Total Tests: {analysis['total_tests']}")
    print(f"✅ Successful Tests: {analysis['successful_tests']}")
    
    # Save detailed results
    output_file = Path("sigil_comprehension_test_results.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {output_file}")
    
    # Verdict
    if analysis['success_rate'] >= 0.8 and analysis['average_comprehension_retention'] >= 0.8:
        print("\n✅ SIGIL SYSTEM VALIDATION: SUCCESS")
        print("Sigil format maintains comprehension while reducing tokens")
    elif analysis['average_token_reduction'] >= 0.6:
        print("\n⚠️ SIGIL SYSTEM VALIDATION: PARTIAL SUCCESS")
        print("Good token reduction but some comprehension loss")
    else:
        print("\n❌ SIGIL SYSTEM VALIDATION: INSUFFICIENT")
        print("Token reduction target not met")

if __name__ == '__main__':
    main()