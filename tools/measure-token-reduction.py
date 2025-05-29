#!/usr/bin/env python3
"""
Measure actual token reduction between traditional and sigil CLAUDE.md files
Validates compression efficiency across the workspace

🎨 Crafted by Luthier for empirical validation 🎨
"""

import json
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class TokenMeasurement:
    """Token usage measurement for a file pair"""
    file_name: str
    traditional_tokens: int
    sigil_tokens: int
    word_count_traditional: int
    word_count_sigil: int
    char_count_traditional: int
    char_count_sigil: int
    
    @property
    def token_reduction_percent(self) -> float:
        return (1 - self.sigil_tokens / self.traditional_tokens) * 100
    
    @property
    def word_reduction_percent(self) -> float:
        return (1 - self.word_count_sigil / self.word_count_traditional) * 100
    
    @property
    def char_reduction_percent(self) -> float:
        return (1 - self.char_count_sigil / self.char_count_traditional) * 100

def estimate_tokens(text: str) -> int:
    """
    Estimate token count using approximation methods
    Based on OpenAI's rough estimate of 1 token = 4 characters for English
    """
    # Clean text for estimation
    clean_text = re.sub(r'\s+', ' ', text.strip())
    
    # Multiple estimation methods
    char_based = len(clean_text) / 4
    word_based = len(clean_text.split()) * 1.3  # English words average ~1.3 tokens
    
    # Use the higher estimate for conservative measurement
    return int(max(char_based, word_based))

def count_words(text: str) -> int:
    """Count words in text"""
    return len(text.split())

def count_chars(text: str) -> int:
    """Count non-whitespace characters"""
    return len(re.sub(r'\s+', '', text))

def measure_file_pair(traditional_path: Path, sigil_path: Path, name: str) -> TokenMeasurement:
    """Measure token reduction for a file pair"""
    
    with open(traditional_path, 'r', encoding='utf-8') as f:
        traditional_content = f.read()
    
    with open(sigil_path, 'r', encoding='utf-8') as f:
        sigil_content = f.read()
    
    return TokenMeasurement(
        file_name=name,
        traditional_tokens=estimate_tokens(traditional_content),
        sigil_tokens=estimate_tokens(sigil_content),
        word_count_traditional=count_words(traditional_content),
        word_count_sigil=count_words(sigil_content),
        char_count_traditional=count_chars(traditional_content),
        char_count_sigil=count_chars(sigil_content)
    )

def main():
    """Main measurement execution"""
    
    print("📏 Token Reduction Measurement")
    print("=" * 40)
    
    # Files to measure
    file_pairs = [
        ("/Users/benaskins/dev/CLAUDE.md", "/Users/benaskins/dev/CLAUDE.sigil.md", "workspace"),
        ("/Users/benaskins/dev/aurelia/CLAUDE.md", "/Users/benaskins/dev/aurelia/CLAUDE.sigil.md", "aurelia"),
        ("/Users/benaskins/dev/lamina-llm-serve/CLAUDE.md", "/Users/benaskins/dev/lamina-llm-serve/CLAUDE.sigil.md", "lamina-llm-serve"),
    ]
    
    measurements = []
    
    for trad_path, sigil_path, name in file_pairs:
        trad_file = Path(trad_path)
        sigil_file = Path(sigil_path)
        
        if trad_file.exists() and sigil_file.exists():
            print(f"📁 Measuring {name}...")
            measurement = measure_file_pair(trad_file, sigil_file, name)
            measurements.append(measurement)
            
            print(f"  Traditional: {measurement.traditional_tokens} tokens, {measurement.word_count_traditional} words")
            print(f"  Sigil: {measurement.sigil_tokens} tokens, {measurement.word_count_sigil} words")
            print(f"  Token reduction: {measurement.token_reduction_percent:.1f}%")
            print(f"  Word reduction: {measurement.word_reduction_percent:.1f}%")
            print(f"  Char reduction: {measurement.char_reduction_percent:.1f}%")
            print()
        else:
            print(f"⚠️ Skipping {name} - files not found")
    
    if not measurements:
        print("❌ No valid file pairs found")
        return
    
    # Calculate aggregates
    total_trad_tokens = sum(m.traditional_tokens for m in measurements)
    total_sigil_tokens = sum(m.sigil_tokens for m in measurements)
    total_trad_words = sum(m.word_count_traditional for m in measurements)
    total_sigil_words = sum(m.word_count_sigil for m in measurements)
    total_trad_chars = sum(m.char_count_traditional for m in measurements)
    total_sigil_chars = sum(m.char_count_sigil for m in measurements)
    
    avg_token_reduction = (1 - total_sigil_tokens / total_trad_tokens) * 100
    avg_word_reduction = (1 - total_sigil_words / total_trad_words) * 100
    avg_char_reduction = (1 - total_sigil_chars / total_trad_chars) * 100
    
    print("📊 AGGREGATE ANALYSIS")
    print("=" * 40)
    print(f"📄 Files measured: {len(measurements)}")
    print(f"🔤 Total traditional tokens: {total_trad_tokens}")
    print(f"⚡ Total sigil tokens: {total_sigil_tokens}")
    print(f"📉 Average token reduction: {avg_token_reduction:.1f}%")
    print(f"📝 Average word reduction: {avg_word_reduction:.1f}%")
    print(f"🔤 Average char reduction: {avg_char_reduction:.1f}%")
    print(f"💾 Total tokens saved: {total_trad_tokens - total_sigil_tokens}")
    
    # Save detailed results
    results = {
        "measurements": [
            {
                "file_name": m.file_name,
                "traditional_tokens": m.traditional_tokens,
                "sigil_tokens": m.sigil_tokens,
                "token_reduction_percent": m.token_reduction_percent,
                "word_reduction_percent": m.word_reduction_percent,
                "char_reduction_percent": m.char_reduction_percent
            }
            for m in measurements
        ],
        "aggregates": {
            "total_files": len(measurements),
            "total_traditional_tokens": total_trad_tokens,
            "total_sigil_tokens": total_sigil_tokens,
            "average_token_reduction_percent": avg_token_reduction,
            "average_word_reduction_percent": avg_word_reduction,
            "average_char_reduction_percent": avg_char_reduction,
            "total_tokens_saved": total_trad_tokens - total_sigil_tokens
        }
    }
    
    output_file = Path("token_reduction_measurements.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed measurements saved to: {output_file}")
    
    # Efficiency assessment
    if avg_token_reduction >= 70:
        print("\n✅ COMPRESSION EFFICIENCY: EXCELLENT")
        print("Sigil system achieves target compression while maintaining readability")
    elif avg_token_reduction >= 60:
        print("\n✅ COMPRESSION EFFICIENCY: GOOD")
        print("Sigil system meets compression targets")
    elif avg_token_reduction >= 40:
        print("\n⚠️ COMPRESSION EFFICIENCY: MODERATE")
        print("Some compression but below optimal targets")
    else:
        print("\n❌ COMPRESSION EFFICIENCY: INSUFFICIENT")
        print("Compression targets not met")

if __name__ == '__main__':
    main()