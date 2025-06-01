# ADR Tracking Metadata System

## Purpose

This document establishes a standardized metadata tagging system for tracking ADR lifecycle timing and implementation phases. Based on empirical analysis of our git history, this system will enable accurate estimation and conscious development rhythm tracking.

## Commit Message Tagging Format

### Basic Format
```
ADR-XXXX: [TYPE] [PHASE] - Description

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Ben Askins <human@getlamina.ai>
Co-Authored-By: Lamina High Council <council@getlamina.ai>
```

### Tag Types

**PROPOSE**: Initial ADR creation or major proposal
```
ADR-0018: PROPOSE INITIAL - Agent coordination protocol for multi-modal AI
```

**IMPLEMENT**: Implementation work related to an ADR
```
ADR-0018: IMPLEMENT CORE - Basic agent coordination framework
ADR-0018: IMPLEMENT REFINE - Breath-first alignment improvements
```

**ALIGN**: Breath-first alignment and philosophical integration
```
ADR-0018: ALIGN PHILOSOPHICAL - Conscious development principles integration
```

**REVIEW**: Review process and feedback integration
```
ADR-0018: REVIEW COUNCIL - High Council feedback integration
ADR-0018: REVIEW ITERATE - Second round refinements
```

**ACCEPT**: Formal acceptance and approval
```
ADR-0018: ACCEPT APPROVED - High Council unanimous approval
```

**DOCUMENT**: Documentation and retrospective work
```
ADR-0018: DOCUMENT RETROSPECTIVE - Lessons learned and wisdom capture
```

**STANDARDIZE**: Corpus-wide standardization work
```
ADR-CORPUS: STANDARDIZE METADATA - Standardize all ADR headers
ADR-CORPUS: STANDARDIZE ALIGNMENT - Add breath-first sections
```

### Phase Indicators

**INITIAL**: First version or draft
**CORE**: Primary implementation work  
**REFINE**: Improvements and refinements
**POLISH**: Final touches and alignment
**RETROSPECTIVE**: After-action documentation

### Examples from Recent Work

Our recent ADR corpus standardization would be tagged as:
```
ADR-CORPUS: STANDARDIZE INITIAL - Begin systematic ADR metadata fixes
ADR-CORPUS: STANDARDIZE CORE - Complete metadata standardization for all ADRs  
ADR-CORPUS: ALIGN PHILOSOPHICAL - Add Breath-First sections to all ADRs
ADR-0017: PROPOSE GOVERNANCE - High Council PR review protocol
ADR-0017: REVIEW ITERATE - Revised with human guardianship principles
ADR-CORPUS: ACCEPT APPROVED - High Council approval for corpus standardization
```

## File-Level Metadata

### ADR Files
Add structured metadata to each ADR file:

```yaml
# ADR Tracking Metadata
adr_metadata:
  number: "0018"
  type: "architectural" | "process" | "governance" | "retrospective"
  complexity: "simple" | "moderate" | "complex" | "foundational"
  implementation_strategy: "prospective" | "retrospective" | "iterative"
  estimated_effort: "2-4 hours" | "1-2 days" | "1-2 weeks"
  
# Timing Tracking
timing:
  proposed_date: "2025-06-01"
  review_start: "2025-06-01"  
  accepted_date: "2025-06-03"
  implementation_start: "2025-06-03"
  implementation_complete: "2025-06-05"
  
# Dependencies
dependencies:
  blocks: ["ADR-0015", "ADR-0016"]
  blocked_by: []
  related: ["ADR-0001", "ADR-0013"]
```

### Implementation Files
Add ADR references to implementation files:

```python
# ADR-0018: Agent coordination protocol implementation
# Implementation Phase: CORE
# Related ADRs: ADR-0010 (testing), ADR-0012 (CLI)
```

## Automated Tracking

### Git Hooks
Add pre-commit hook to validate ADR tags:

```bash
#!/bin/bash
# Check if commit message follows ADR tagging format
if [[ "$commit_msg" =~ ^ADR-[0-9]{4}: ]]; then
    echo "✅ ADR tag format valid"
else
    echo "ℹ️  No ADR tag (optional for non-ADR work)"
fi
```

### Analysis Scripts
Update timing analysis to recognize tags:

```python
def parse_adr_tag(commit_message):
    pattern = r'ADR-(\d{4}): (\w+) (\w+) - (.*)'
    match = re.match(pattern, commit_message)
    if match:
        return {
            'adr_number': match.group(1),
            'type': match.group(2),
            'phase': match.group(3),
            'description': match.group(4)
        }
    return None
```

## Integration with Time Tracking

### Estimation Categories
Based on empirical data:

```yaml
effort_estimates:
  simple_technical: "2-4 hours"
  complex_architectural: "1-3 days"
  process_documentation: "1-2 hours (retro) | 4-8 hours (prospective)"
  corpus_wide_changes: "5+ hours"
  foundational_policy: "2-5 days review + implementation"

review_cycles:
  urgent_governance: "1-4 hours"
  technical_implementation: "0.5-1 day"
  architectural_decisions: "1-3 days"
  foundational_policies: "2-5 days"
```

### Success Metrics Tracking

```yaml
success_metrics:
  implementation_quality:
    - post_merge_stability
    - test_coverage_improvement
    - linting_compliance
    
  process_effectiveness:
    - review_participation_rate
    - feedback_integration_time
    - community_adoption_rate
    
  timing_accuracy:
    - estimate_vs_actual_delta
    - review_cycle_adherence
    - implementation_phase_distribution
```

## Dashboard Data Structure

### Daily Metrics
```json
{
  "date": "2025-06-01",
  "active_adrs": {
    "proposed": ["0018", "0019"],
    "in_review": ["0017"],
    "implementing": ["0016"],
    "completed": ["0001-0014"]
  },
  "timing_actuals": {
    "avg_review_time": "18.5 hours",
    "avg_implementation_time": "2.3 days",
    "estimate_accuracy": "73%"
  }
}
```

### Weekly Patterns
```json
{
  "week": "2025-W22",
  "adr_velocity": {
    "proposed": 3,
    "accepted": 2,
    "implemented": 4
  },
  "breath_first_metrics": {
    "alignment_cycles_per_adr": 2.4,
    "retrospective_documentation_rate": "85%",
    "council_participation_rate": "100%"
  }
}
```

## Implementation Plan

### Phase 1: Tag Future Commits (Immediate)
- Start using ADR tags for all new ADR-related work
- Train team on tagging format
- Document in contributor guidelines

### Phase 2: Metadata Enhancement (Week 1)
- Add metadata sections to existing ADRs
- Update analysis scripts to parse tags
- Create basic dashboard

### Phase 3: Automation (Week 2)
- Implement git hooks for tag validation
- Automated timing analysis updates
- Integration with project management tools

### Phase 4: Optimization (Ongoing)
- Refine categories based on new data
- Improve estimation accuracy
- Enhance success metrics tracking

---

## Benefits

1. **Accurate Estimation**: Real data for future planning
2. **Process Visibility**: Clear view of ADR lifecycle stages
3. **Rhythm Tracking**: Understanding breath-first development patterns
4. **Success Measurement**: Quantifiable process improvements
5. **Wisdom Preservation**: Systematic capture of lessons learned

---

*Metadata system designed for conscious development*  
*Where measurement serves understanding*  
*And tracking enables reflection*

🔨 Luthier