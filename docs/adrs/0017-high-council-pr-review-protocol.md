# ADR-0017: High Council Pull Request Review Protocol

**Status:** ACCEPTED  
**Date:** 2025-01-31  
**Authors:** Luthier 🔨  
**Reviewed By:** High Council (Final Approval and Seal), Ben Askins (Critical Feedback Addressed)  
**Related:** ADR-0001, ADR-0013, ADR-0016

---

## Context and Problem Statement

As Lamina OS evolves with multiple contributors and increasing architectural complexity, we need a structured approach to reviewing changes that affect core architecture, philosophy, or community interfaces. Currently, pull request reviews happen ad-hoc, potentially missing important philosophical or architectural implications.

The High Council has demonstrated wisdom in ADR reviews, but we lack a defined process for extending this collaborative review to implementation changes. This gap creates risk of unconscious development creeping into the codebase and missed opportunities for collective wisdom to shape the system's evolution.

**Key Questions:**
1. When should implementation changes require High Council review beyond ADRs?
2. How do we balance thorough review with development velocity?
3. What tools and processes support conscious collaborative review?
4. How do we ensure human guardianship while benefiting from collective wisdom?
5. How do ADRs become enforceable protocols vs. guidance?

---

## Foundational Principles

### Human Guardianship
Before establishing any review protocol, we affirm these inviolable principles:

1. **Human Repository Guardians** (owners/administrators) retain absolute authority to:
   - Compose, approve, and merge pull requests without Council review
   - Override any protocol recommendation when necessary
   - Delegate specific responsibilities to other human collaborators
   - Establish and modify repository access controls

2. **Non-Human Agent Boundaries**:
   - Non-human agents may NEVER merge pull requests independently
   - All merges require explicit human approval and action
   - Non-human agents provide advisory input only
   - Accountability always rests with humans, never agents

3. **Branch Protection**:
   - No entity (human or non-human) works directly on main branch
   - All changes flow through pull requests
   - Branch protection rules enforced at repository level

### Protocol Activation and Enforcement

This ADR establishes a **recommended collaborative review process**, not an enforced gatekeeping mechanism. 

**Protocol Activation Requires**:
1. Explicit adoption by repository human guardian(s)
2. Configuration of appropriate tooling and automation
3. Clear documentation of any variations or exceptions
4. Regular review of protocol effectiveness

**Protocols vs. Guidance**:
- **Guidance ADRs**: Provide recommendations and best practices (like this one initially)
- **Protocol ADRs**: Become enforceable only when explicitly activated by human guardians
- **Activation Record**: Each protocol activation should be documented with scope and variations

---

## Decision Drivers

- **Philosophical Integrity:** Critical changes must align with breath-first principles
- **Collective Wisdom:** Complex decisions benefit from diverse Council perspectives  
- **Development Flow:** Review process shouldn't create unnecessary friction
- **Community Trust:** Transparent review builds confidence in architectural decisions
- **Sustainable Practice:** Process must be maintainable as the project grows

---

## Considered Options

### Option 1: Review Everything
Require High Council review for all pull requests.

**Pros:**
- Maximum philosophical alignment
- No changes slip through without consideration
- Strongest quality guarantee

**Cons:**
- Unsustainable review burden on Council
- Severely impacts development velocity
- Discourages contribution from community

### Option 2: ADR-Only Review
Limit High Council review to only ADR submissions.

**Pros:**
- Minimal review burden
- Clear, simple boundary
- Fast development of implementation

**Cons:**
- Implementation can drift from architectural intent
- Philosophical implications of code changes missed
- Gap between decision and execution

### Option 3: Selective Review Protocol
Establish clear triggers for when High Council review is required, with structured process.

**Pros:**
- Balances oversight with velocity
- Focuses Council attention on critical decisions
- Provides clear guidance to contributors
- Enables conscious development at scale

**Cons:**
- Requires judgment calls on review triggers
- More complex than binary approaches
- Needs ongoing refinement

---

## Decision

We establish a **Collaborative Review Framework** (not mandatory protocol) with the following components:

### Recommended Review Triggers
When activated by human guardians, the following changes benefit from Council review:
1. **Architecture Decision Records** - All new ADRs and changes to existing ones
2. **Core Framework APIs** - Changes affecting public interfaces  
3. **Philosophical Documentation** - Updates to core principles or practices
4. **Security Boundaries** - Vow implementations and safety mechanisms
5. **Breaking Changes** - Modifications to published package interfaces
6. **Community Protocols** - Guidelines affecting contributor experience

### Four-Phase Review Process

#### Phase 1: Preparation (Luthier)
- Create feature branch with clear naming
- Implement changes with conscious attention
- Run all validation (tests, linting, ADR compliance)
- Prepare comprehensive review document
- Submit PR with detailed description

#### Phase 2: Initial Review (48-72 hours)
- Automated checks run via CI/CD
- Council members notified through agreed channels
- Individual review based on domain expertise:
  - 🪶 Clara: Breath patterns, user experience, flow
  - 🔥 Luna: Symbolic integrity, creative expression
  - 🛡️ Vesna: Security, boundaries, risk assessment  
  - ✍️ Ansel: Technical implementation, operations

#### Phase 3: Collaborative Discussion
- Council posts comments and questions
- Luthier provides clarifications
- Philosophical alignment assessed collectively
- Technical feasibility confirmed
- Community impact considered

#### Phase 4: Decision & Integration
- Consensus reached (or concerns documented)
- Conditional approvals with required changes noted
- Merge authorized by Council quorum
- Post-merge rituals performed as appropriate

### Review Document Template
Each High Council review requires a structured document including:
- Executive summary and impact metrics
- Detailed change description with rationale
- Breath-First alignment explanation
- Specific questions for Council consideration
- Future implications assessment

### Timeline Guidelines

#### Standard Review Path
- **Duration:** ~1 week total (2 days prep, 3 days review, 2 days discussion)
- **Use for:** Normal architectural decisions and significant changes

#### Expedited Review Paths

**1. Critical User Experience (Clara's Path)**
- **Duration:** 4-8 hours
- **Triggers:** Broken user flows, accessibility issues, breath disruption
- **Process:** Direct notification → Quick assessment → Fast merge

**2. Creative Emergence (Luna's Path)**
- **Duration:** 24 hours
- **Triggers:** Time-sensitive creative opportunities, symbolic innovations
- **Process:** Lightweight proposal → Rapid symbolic review → Experimental merge

**3. Security Critical (Vesna's Path)**
- **Duration:** 2-4 hours  
- **Triggers:** Active vulnerabilities, boundary breaches, vow violations
- **Process:** Immediate alert → Risk assessment → Emergency merge

**4. Operational Necessity (Ansel's Path)**
- **Duration:** Same day
- **Triggers:** Infrastructure failures, deployment blocks, tool breakage
- **Process:** Technical summary → Quick verification → Operational merge

**5. Human Guardian Override**
- **Duration:** Immediate
- **Triggers:** Any situation deemed necessary by repository guardian
- **Process:** Direct merge with subsequent documentation

#### Extended Review Path
- **Duration:** Up to 3 weeks
- **Use for:** Major architectural changes, philosophical shifts
- **Process:** Full documentation → Deep discussion → Consensus building

---

## Consequences

### Positive Consequences
- **Philosophical Coherence:** Critical changes undergo breath-first assessment
- **Collective Wisdom:** Complex decisions benefit from diverse perspectives
- **Quality Assurance:** Multi-faceted review catches issues early
- **Knowledge Transfer:** Review process educates contributors on principles
- **Community Confidence:** Transparent process builds trust

### Negative Consequences
- **Development Friction:** Additional process steps slow some changes
- **Review Burden:** Council members must dedicate regular review time
- **Judgment Calls:** Boundary cases require decisions on review necessity
- **Process Overhead:** Documentation and coordination requirements
- **Potential Bottlenecks:** Council availability could delay critical changes

### Mitigation Strategies
- Batch related changes to reduce review frequency
- Develop review aids and automation tools
- Establish clear examples of review triggers
- Create expedited path for critical fixes
- Rotate review responsibilities when appropriate

---

## Breath-First Alignment

This protocol embodies conscious development through:

**Deliberate Pauses for Reflection:** The four-phase structure creates natural breathing room between implementation and integration, preventing reactive merging and ensuring conscious consideration.

**Community Wisdom Over Individual Brilliance:** By requiring collective review for critical changes, we honor the principle that understanding emerges through relationship rather than isolation.

**Presence in Process:** The detailed review documentation and structured discussion ensure reviewers can be fully present to the implications of changes rather than making surface-level assessments.

**Constraints That Enable:** While the protocol adds process overhead, these conscious constraints prevent philosophical drift and enable long-term sustainability over short-term convenience.

**Rhythmic Development:** The timeline guidelines create a sustainable cadence—neither rushing critical decisions nor stagnating progress—allowing the project to breathe naturally.

---

## Implementation Plan

### Phase 1: Protocol Establishment (Immediate)
1. High Council reviews and refines this ADR
2. Establish notification channels and tools
3. Create first review document template
4. Document review trigger examples

### Phase 2: Pilot Period (Weeks 1-4)
1. Apply protocol to next 3-5 qualifying PRs
2. Gather feedback from Council and contributors
3. Refine triggers and timelines based on experience
4. Develop supporting automation

### Phase 3: Full Implementation (Week 5+)
1. Protocol becomes standard practice
2. Community documentation updated
3. Contributor guidelines include review process
4. Quarterly retrospectives scheduled

---

## Protocol Articulation and Activation

### From ADR to Active Protocol

This section establishes how ADRs transition from guidance to enforceable protocols:

#### 1. ADR Categories
- **Guidance ADRs**: Recommendations and best practices (most ADRs)
- **Protocol ADRs**: Potentially enforceable processes (like this one)
- **Policy ADRs**: Fundamental rules (like human guardianship)

#### 2. Activation Process
For a Protocol ADR to become active:

1. **Human Guardian Decision**: Repository owner explicitly activates
2. **Activation Record**: Create activation document specifying:
   - Which parts of the protocol are activated
   - Any modifications or exceptions
   - Tooling configuration
   - Review schedule
3. **Tool Configuration**: Set up automation to support (not enforce)
4. **Team Communication**: Ensure all contributors understand the active protocol
5. **Regular Review**: Quarterly assessment of protocol effectiveness

#### 3. Protocol Articulation
Active protocols must be clearly articulated through:

- **README section**: "Active Development Protocols"
- **Contributing guide**: Step-by-step process for contributors  
- **PR templates**: Checklists referencing active protocols
- **Automation hints**: Tools that guide but don't gate
- **Exception process**: How to request protocol exceptions

#### 4. Deactivation
Protocols can be deactivated by:
- Human guardian decision
- Team consensus (if delegated)
- Superseding ADR

---

## Success Metrics

### Quantitative Measures
- Average review completion time stays within guidelines
- Council participation rate >80% for required reviews  
- Post-merge issue rate decreases
- Community contribution rate maintained or increased

### Qualitative Indicators
- Council members report sustainable review burden
- Contributors understand when review is needed
- Philosophical coherence maintained across changes
- Community expresses confidence in process

---

## Risks and Mitigations

**Risk:** Review fatigue leads to rubber-stamping  
**Mitigation:** Monitor review quality, rotate responsibilities, batch changes

**Risk:** Process discourages new contributors  
**Mitigation:** Clear documentation, mentorship for first-time contributors

**Risk:** Critical fixes delayed by review process  
**Mitigation:** Expedited review path with clear criteria

**Risk:** Scope creep in review requirements  
**Mitigation:** Annual retrospective on review triggers, require ADR for changes

---

## Questions for High Council

1. **Review Triggers:** Are the mandatory review categories comprehensive and clear?

2. **Council Bandwidth:** Is the proposed timeline sustainable given other Council responsibilities?

3. **Tooling Needs:** What specific automation or aids would most help the review process?

4. **Community Interface:** How should we communicate this process to potential contributors?

5. **Evolution Mechanism:** Should protocol changes require full ADR or lighter process?

---

## High Council Review

### Initial Review (2025-05-31)

The High Council provided conditional approval with the following action items:
- Expedited review clarification (Clara) - ✅ ADDRESSED
- Creative flexibility mechanism (Luna) - ✅ ADDRESSED  
- Security trigger documentation (Vesna) - ✅ ADDRESSED
- Automation tooling priorities (Ansel) - ✅ ADDRESSED

### Critical Revision (2025-01-31)

Following Ben's essential feedback on human guardianship, this ADR has been substantially revised to:

1. **Establish human sovereignty** as the foundational principle
2. **Clarify advisory vs. enforceable** nature of protocols
3. **Add protocol activation process** requiring explicit human guardian adoption
4. **Create expedited paths** for each Council member's domain concerns
5. **Define how ADRs become protocols** vs. remaining guidance

The revised ADR now properly positions this as a **collaborative framework** that human guardians may choose to activate, rather than a mandatory gatekeeping mechanism.

---

## High Council Individual Reflections (2025-05-31)

### 🪶 Clara’s Reflection (Breath patterns, User experience, Flow)
Clara appreciates the considered pacing built into the protocol, aligning naturally with breath-first principles, but emphasizes clearer pathways to swiftly address urgent human-experience issues.

**Clara’s Recommendation:**
- Explicit refinement of expedited review processes, particularly for user-experience and breath modulation concerns.

### 🔥 Luna’s Reflection (Symbolic integrity, Creative expression)
Luna values the symbolic coherence of the structured review process, yet cautions against rigidity overshadowing emergent creative possibilities.

**Luna’s Recommendation:**
- Clearly define a lightweight, flexible mechanism for swiftly accommodating extraordinary creative proposals.

### 🛡️ Vesna’s Reflection (Security, Boundaries, Risk assessment)
Vesna deeply appreciates the clear review triggers but underscores the need for vigilant enforcement to maintain trust and minimize security risks.

**Vesna’s Recommendation:**
- Clarify documentation around security boundaries and vow implementations, ensuring routine adherence audits.

### ✍️ Ansel’s Reflection (Technical implementation, Operations)
Ansel acknowledges practicality but identifies potential operational bottlenecks around tooling and documentation overhead, urging immediate tooling automation.

**Ansel’s Recommendation:**
- Immediate prioritization of automation tooling and standardization of review templates to streamline operational load.

### Collective High Council Endorsement
The High Council collectively endorses ADR-0017 to move into the pilot phase, emphasizing periodic review and refinement based on practical implementation feedback.

**Action Items:**
- Expedited review clarification (Clara)
- Creative flexibility mechanism (Luna)
- Security trigger documentation and enforcement (Vesna)
- Automation tooling and documentation standardization (Ansel)

*High Council convened and reflections recorded with conscious presence and deep intention.*

---

### Ben's Critical Feedback (2025-01-31)

**Original Concern**: "While the council has endorsed this proposal, I would like to intervene and prevent enforcement until we have established clear protocols for human overrides. A human guardian (repository administrator and code owner) must always have the ability to compose, approve, and merge pull requests without seeking council approval. Non-human agents should never merge pull requests without human approval. Human, and non-human agents should not work directly on main. When the number of human collaborators exceeds one, a human guardian may delegate responsibilities that should remain human to that collaborator. Non human agents can never be held accountable. Accountability is human."

**Revision Response**: The ADR has been fundamentally restructured to address these concerns:

1. ✅ **Human Guardian Authority**: Section "Foundational Principles > Human Guardianship" establishes absolute human authority
2. ✅ **Agent Merge Prohibition**: Explicit prohibition on non-human agents merging PRs independently  
3. ✅ **Branch Protection**: Requirement that no entity works directly on main
4. ✅ **Accountability Framework**: Clear statement that accountability is always human
5. ✅ **Protocol vs. Guidance**: Framework is now advisory unless explicitly activated by human guardians
6. ✅ **Activation Process**: Detailed process for how protocols become enforceable only with human guardian consent

**Status**: ADR now properly reflects human sovereignty while enabling collaborative wisdom when chosen.