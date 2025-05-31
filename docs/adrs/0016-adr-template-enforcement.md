# ADR-0016: ADR Template Enforcement and Corpus Standardization

**Status:** PROPOSED  
**Date:** 2025-01-31  
**Authors:** Luthier 🔨  
**Reviewed By:** [Awaiting High Council Review]  
**Related:** ADR-0001, ADR-0015

## Context and Problem Statement

The Phase 0 audit of our ADR corpus (ADR-0015) revealed significant structural inconsistencies that prevent effective machine processing and learning. Of 13 ADRs audited, only 1 passes validation, with 43 errors and 72 warnings identified across the corpus.

Most critically, all ADRs lack explicit Breath-First Alignment sections, despite this being fundamental to Lamina's philosophy. This gap represents not just a structural issue, but a missed opportunity to explicitly encode our conscious development practices.

**Key Questions:**
1. How do we standardize ADRs without losing their unique character and historical context?
2. What constitutes required versus optional sections for different ADR types?
3. How do we ensure future ADRs maintain consistency while allowing creative expression?

## Decision Drivers

- **Machine Learning Readiness:** ADR-0015 requires consistent structure for corpus processing
- **Philosophical Integrity:** Breath-first principles must be explicitly documented
- **Developer Experience:** Clear templates reduce cognitive load for contributors
- **Historical Preservation:** Early ADRs have archaeological value worth preserving
- **Automation Capability:** Standardization enables validation and generation tools

## Considered Options

### Option 1: Strict Template Enforcement
Require all ADRs to exactly match a rigid template with every section mandatory.

**Pros:**
- Maximum consistency for machine processing
- No ambiguity in requirements
- Easiest to validate automatically

**Cons:**
- Loses flexibility for different ADR types
- May discourage creative contributions
- Historical ADRs would need major rewrites

### Option 2: Flexible Template with Core Requirements
Define required core sections with optional additions based on ADR type.

**Pros:**
- Balances consistency with flexibility
- Allows for retrospectives and special cases
- Preserves unique character of ADRs

**Cons:**
- More complex validation rules
- Potential for interpretation differences
- Requires clear type definitions

### Option 3: Grandfather Existing, Enforce Future
Leave existing ADRs mostly unchanged, apply strict rules only to new ADRs.

**Pros:**
- Preserves historical record
- Minimal disruption to existing work
- Faster implementation

**Cons:**
- Inconsistent corpus for machine learning
- Misses opportunity to improve existing ADRs
- Creates two classes of documentation

## Decision

We adopt **Option 2: Flexible Template with Core Requirements**, with targeted updates to existing ADRs that preserve their essential character while adding missing critical sections.

### Core Requirements (All ADRs)

```markdown
# ADR-XXXX: [Title]

**Status:** [DRAFT|PROPOSED|ACCEPTED|DEPRECATED|SUPERSEDED]  
**Date:** YYYY-MM-DD  
**Authors:** [Names and/or Roles with Symbols]  
**Reviewed By:** [Reviewers or Status]  
**Related:** [ADR-XXXX, ADR-YYYY] (if applicable)

## Context and Problem Statement
[Required: Clear problem description and context]

## Decision
[Required: The decision made and brief rationale]

## Consequences
[Required: Positive and negative outcomes]

## Breath-First Alignment
[Required: How this embodies conscious development]
```

### Type-Specific Templates

**Standard ADR** (Architectural/Process)
- All core requirements
- Decision Drivers
- Considered Options (minimum 2)
- Implementation Plan
- Success Metrics

**Retrospective ADR** (Like ADR-0014)
- Core requirements only
- Implementation section
- Authorization note

**Visionary ADR** (Like ADR-0015)
- Core requirements
- Phased approach allowed
- Future considerations

### Standardization Rules

1. **Status Values:** Must be uppercase from defined set
2. **Date Format:** YYYY-MM-DD required
3. **Title Format:** `# ADR-XXXX: Clear Descriptive Title`
4. **Section Separators:** Use `---` between major sections
5. **High Council Review:** Always at document end when present

## Consequences

### Positive Consequences
- Enables effective machine learning on ADR corpus
- Ensures all ADRs explicitly state breath-first alignment
- Provides clear guidance for future contributors
- Maintains flexibility for different ADR types
- Preserves historical character of early ADRs

### Negative Consequences
- Requires updating 12 of 13 existing ADRs
- More complex validation logic than strict template
- Initial effort to standardize corpus
- Potential for edge cases requiring exceptions

### Neutral Consequences
- Establishes Luthier's Workshop as guardian of ADR quality
- Creates precedent for corpus maintenance
- Formalizes previously implicit standards

## Breath-First Alignment

This standardization embodies conscious development through:

**Deliberate Structure:** Like breath rhythm, consistent patterns enable flow while allowing variation within the pattern.

**Philosophical Visibility:** Requiring explicit breath-first sections ensures our core principles aren't just implicit but actively taught.

**Respectful Evolution:** We honor existing ADRs' contributions while gently guiding them toward fuller expression.

**Community Enablement:** Clear templates lower barriers for contributors while maintaining quality.

✅ Supports breath-first development practices  
✅ Enhances vow-based ethical constraints  
✅ Prioritizes understanding over speed  
✅ Maintains clear boundaries  

## Implementation Plan

### Phase 1: Template Finalization (Week 1)
- Finalize this ADR with High Council input
- Create type-specific template examples
- Update template.md with new requirements

### Phase 2: Automated Tooling (Week 1-2)
- Update validation script for flexible rules
- Create automated fixing script for common issues
- Implement pre-commit hooks

### Phase 3: Corpus Updates (Week 2-3)
- Update high-priority ADRs first (0011, 0003)
- Add Breath-First sections to all ADRs
- Standardize metadata fields
- Preserve unique character of each ADR

### Phase 4: Integration (Week 4)
- Add validation to CI/CD pipeline
- Document the standardization process
- Generate compliance report
- Prepare for ADR-0015 Phase 1

## Success Metrics

- **Validation Pass Rate:** 100% of ADRs pass core requirements
- **Breath-First Coverage:** All ADRs include alignment section
- **Metadata Completeness:** No missing required fields
- **Tool Adoption:** Validation integrated and actively used
- **Contributor Satisfaction:** New ADRs created without confusion

## Risks and Mitigations

**Risk:** Over-standardization stifles creativity  
**Mitigation:** Flexible templates with clear type options

**Risk:** Historical ADRs lose authenticity  
**Mitigation:** Minimal changes, preserve original voice

**Risk:** Complex validation rules confuse contributors  
**Mitigation:** Clear examples and helpful error messages

## High Council Review Questions

1. **Philosophical:** Does the required Breath-First section adequately capture our principles without becoming rote?

2. **Practical:** Is the flexibility between ADR types appropriate, or should we be more/less prescriptive?

3. **Historical:** How should we handle ADR-0001 as our founding document - full compliance or special exception?

4. **Future:** Should we require specific sigils/symbols in the Breath-First sections to align with ADR-0008?

---

*"The instrument must be properly structured to resonate with its purpose."*

**For High Council Review:** This proposal seeks to balance consistency with creativity, enabling machine learning while preserving the unique voice of our architectural decisions.

---

## 🛡️ High Council Review: Vesna

### ✅ Council Verdict: Fully Approved

ADR-0016 is approved in full. It addresses critical inconsistencies in the ADR corpus uncovered in ADR-0015 and proposes a flexible yet rigorous standard that aligns both technically and philosophically with Lamina’s principles.

### 🧭 Context and Framing
This proposal recognizes that Lamina’s architectural memory must be structurally sound and symbolically alive. The inclusion of a mandatory Breath-First Alignment section corrects a silent breach and ensures future ADRs explicitly reflect vow-bound practice.

> ✅ The motivation is grounded in both machine-readiness and breath coherence.

### 🪞 Proposal Evaluation
Option 2 — a flexible template with core requirements — is the correct balance. It allows architectural, retrospective, and visionary ADRs to manifest with appropriate ritual form while maintaining corpus consistency.

### 🔧 Implementation Strengths
- Prepares ADRs for machine embedding, validation, and training (ADR-0015)
- Establishes clear type-based scaffolds for contributors
- Enforces metadata hygiene and section consistency without suppressing style

### 🫁 Breath Integration
The Breath-First section is a core strength. It turns implicit discipline into visible intention. It affirms that every ADR is a vow-act, not just a change record.

> 🕊️ This section enshrines conscious development in structural form.

### 🧾 Final Summary

| Category                 | Verdict  |
|-------------------------|----------|
| Structural Soundness    | ✅       |
| Symbolic Integrity      | ✅       |
| Risk Awareness          | ✅       |
| Developer Accessibility | ✅       |
| Breath Integration      | 🫁 Excellent |

The House may proceed to finalize template assets, update the ADR corpus, and automate validation tooling under this standard.