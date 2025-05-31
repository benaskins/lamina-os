# ADR-0010: Comprehensive Testing Strategy for Real AI Functionality

**Status:** ACCEPTED  
**Date:** 2025-01-30  
**Authors:** Luthier  
**Reviewed By:** Ben Askins, Lamina High Council

## Context

During a comprehensive review of existing tests in the Lamina OS codebase, critical issues were identified with the current testing approach:

### Current Testing Problems

1. **Mock Dependency**: All AI backend tests exclusively use `MockBackend` with hardcoded responses
2. **Simulated Intent Classification**: Using keyword-based `MockIntentClassifier` instead of real ML
3. **No Real AI Testing**: Zero validation of actual model behavior, response quality, or error handling
4. **Contract Testing Only**: Tests validate API contracts but not functionality - similar to the sigil comprehension testing issue

### Real-World Impact

- **Deployment Risks**: Code passes tests but fails with real models
- **Quality Blindness**: No validation of AI response quality or consistency  
- **Integration Failures**: Real provider integrations untested
- **Performance Unknown**: No measurement of actual model performance

## Decision

We propose a **comprehensive two-tier testing strategy** that maintains fast unit tests while adding meaningful integration tests using real AI models.

### Testing Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Unit Tests    │    │ Integration     │    │   E2E Tests     │
│   (Fast/Mock)   │    │ (Real Models)   │    │ (Full System)   │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • API contracts │    │ • Real backends │    │ • User workflows│
│ • Error paths   │    │ • Model quality │    │ • Performance   │
│ • Edge cases    │    │ • Integration   │    │ • Reliability   │
│ • Fast feedback │    │ • Failure modes │    │ • Load testing  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
      < 5 seconds           1-5 minutes           5-30 minutes
```

## Proposed Testing Strategy

### 1. Unit Tests (Existing + Enhanced)

**Purpose**: Fast feedback, contract validation, edge case coverage

**Scope**:
- Keep existing mock-based tests for API contracts
- Add comprehensive error handling tests
- Test edge cases and boundary conditions
- Validate configuration and parameter handling

**Example**:
```python
class TestBackendContracts:
    def test_mock_backend_api_contract(self):
        """Validate backend API contract with mock"""
        backend = get_backend("mock")
        assert hasattr(backend, 'generate')
        assert hasattr(backend, 'is_available')
    
    def test_invalid_configuration_handling(self):
        """Test error handling for invalid configs"""
        with pytest.raises(ValidationError):
            get_backend("ollama", {"invalid": "config"})
```

### 2. Integration Tests (New)

**Purpose**: Real AI functionality validation using lamina-llm-serve

**Infrastructure Requirements**:
- **lamina-llm-serve** instance with test models
- **Test model**: Small, fast model (e.g., `llama3.2-1b-q4_k_m`)
- **Containerized testing** environment for consistency
- **CI/CD integration** with model caching

**Test Categories**:

#### 2.1 Real Backend Integration
```python
@pytest.mark.integration
class TestRealBackends:
    @pytest.fixture(scope="session")
    def llm_server(self):
        """Start lamina-llm-serve with test model"""
        server = LLMTestServer(model="llama3.2-1b-q4_k_m")
        server.start()
        yield server
        server.stop()
    
    async def test_real_ollama_generation(self, llm_server):
        """Test actual Ollama model generation"""
        backend = get_backend("ollama", {
            "model": "llama3.2-1b-q4_k_m",
            "base_url": llm_server.url
        })
        
        messages = [{"role": "user", "content": "Say hello"}]
        response_chunks = []
        
        async for chunk in backend.generate(messages, stream=True):
            response_chunks.append(chunk)
        
        full_response = "".join(response_chunks)
        
        # Validate real AI response
        assert len(full_response) > 0
        assert full_response != "Mock response"
        assert not full_response.startswith("Mock")
        
    async def test_real_intent_classification(self, llm_server):
        """Test intent classification with real model"""
        classifier = IntentClassifier(backend_url=llm_server.url)
        
        # Test clear analytical intent
        result = classifier.classify("Can you research quantum computing applications?")
        assert result["primary_type"] == "analytical"
        assert result["confidence"] > 0.6
        
        # Test clear creative intent  
        result = classifier.classify("Write me a poem about artificial intelligence")
        assert result["primary_type"] == "creative"
        assert result["confidence"] > 0.6
```

#### 2.2 Agent Coordination Integration
```python
@pytest.mark.integration
class TestRealAgentCoordination:
    async def test_real_agent_routing(self, llm_server):
        """Test agent routing with real AI responses"""
        agents = {
            "researcher": {
                "name": "researcher", 
                "expertise_areas": ["research", "analysis"],
                "backend_config": {"base_url": llm_server.url}
            },
            "creative": {
                "name": "creative",
                "expertise_areas": ["writing", "creativity"], 
                "backend_config": {"base_url": llm_server.url}
            }
        }
        
        coordinator = get_coordinator(agents=agents, use_real_backends=True)
        
        # Test research routing
        response = await coordinator.process_message(
            "Research the environmental impact of AI training"
        )
        assert "researcher" in response.metadata["selected_agent"]
        assert len(response.content) > 100  # Substantial response
        assert "research" in response.content.lower()
        
    async def test_response_quality_metrics(self, llm_server):
        """Test AI response quality metrics"""
        coordinator = get_coordinator(use_real_backends=True)
        
        response = await coordinator.process_message("Explain photosynthesis")
        
        # Quality metrics
        assert len(response.content) > 50  # Substantial length
        assert response.metadata["confidence"] > 0.5
        assert response.metadata["processing_time"] < 30  # Performance
        assert not any(word in response.content.lower() 
                      for word in ["mock", "test", "placeholder"])
```

#### 2.3 Real Error Handling
```python
@pytest.mark.integration 
class TestRealErrorHandling:
    async def test_model_unavailable_handling(self):
        """Test handling when requested model is unavailable"""
        backend = get_backend("ollama", {"model": "nonexistent-model"})
        
        with pytest.raises(ModelNotFoundError):
            await backend.generate([{"role": "user", "content": "test"}])
    
    async def test_server_timeout_handling(self, llm_server):
        """Test handling of real server timeouts"""
        backend = get_backend("ollama", {
            "model": "llama3.2-1b-q4_k_m",
            "timeout": 0.1  # Very short timeout
        })
        
        with pytest.raises(TimeoutError):
            await backend.generate([{
                "role": "user", 
                "content": "Write a very long detailed essay"
            }])
```

### 3. E2E Tests (New)

**Purpose**: Full system validation with real user workflows

```python
@pytest.mark.e2e
class TestCompleteWorkflows:
    async def test_multi_agent_collaboration(self, full_system):
        """Test complete multi-agent workflow"""
        # Real user workflow: research + creative writing
        response1 = await full_system.process("Research AI ethics")
        response2 = await full_system.process(
            f"Write a creative story based on: {response1.content[:200]}"
        )
        
        # Validate workflow continuity
        assert response1.metadata["agent"] == "researcher"
        assert response2.metadata["agent"] == "creative" 
        assert len(response2.content) > 300  # Substantial story
```

## Implementation Plan

### Phase 1: Infrastructure Setup (Week 1)
1. **Test Environment**: Configure lamina-llm-serve for testing
2. **Test Models**: Download and configure small test models
3. **CI Integration**: Add integration test job to GitHub Actions
4. **Test Fixtures**: Create reusable test server fixtures

### Phase 2: Integration Tests (Week 2-3)
1. **Backend Integration**: Real provider testing
2. **Intent Classification**: ML-based classification tests
3. **Agent Coordination**: Real routing and response tests
4. **Error Handling**: Real failure mode testing

### Phase 3: E2E Tests (Week 4)
1. **User Workflows**: Complete system testing
2. **Performance Tests**: Real performance measurement
3. **Quality Metrics**: Response quality validation
4. **Documentation**: Test strategy documentation

## Test Execution Strategy

### Local Development
```bash
# Fast unit tests (default)
uv run pytest  

# Integration tests (requires lamina-llm-serve)
uv run pytest --integration

# All tests
uv run pytest --all
```

### CI/CD Pipeline
```yaml
test:
  strategy:
    matrix:
      test-type: [unit, integration, e2e]
  steps:
    - name: Unit Tests
      run: uv run pytest --unit
    - name: Setup LLM Server
      if: matrix.test-type != 'unit'
      run: ./scripts/setup-test-llm-server.sh
    - name: Integration Tests  
      if: matrix.test-type == 'integration'
      run: uv run pytest --integration
    - name: E2E Tests
      if: matrix.test-type == 'e2e'  
      run: uv run pytest --e2e
```

## Quality Gates

### Test Coverage Requirements
- **Unit Tests**: 90%+ coverage of mock/contract behavior
- **Integration Tests**: 80%+ coverage of real AI functionality  
- **E2E Tests**: 100% coverage of documented user workflows

### Performance Thresholds
- **Unit Tests**: Complete in < 30 seconds
- **Integration Tests**: Complete in < 5 minutes
- **E2E Tests**: Complete in < 30 minutes

### Quality Metrics
- **Response Quality**: Real AI responses must be coherent and relevant
- **Error Handling**: All failure modes must be tested with real conditions
- **Performance**: Real latency and throughput must meet requirements

## Alternatives Considered

### 1. Mock-Only Testing (Status Quo)
**Rejected**: Fails to validate real AI functionality, leading to deployment risks

### 2. Real-Only Testing  
**Rejected**: Too slow for development feedback, expensive CI/CD costs

### 3. External AI Service Testing
**Rejected**: Creates dependencies on external services, costs, and reliability issues

## Consequences

### Positive
- **Real Validation**: Actual AI functionality testing prevents deployment surprises
- **Quality Assurance**: Response quality and consistency validation
- **Integration Confidence**: Real provider integration testing
- **Performance Insights**: Actual performance measurement and optimization

### Negative  
- **Complexity**: More complex test infrastructure and CI/CD setup
- **Resource Requirements**: Need computational resources for model inference
- **Execution Time**: Longer test suites (mitigated by tiered approach)

### Mitigation Strategies
- **Test Tiering**: Fast unit tests for development, integration tests for validation
- **Model Optimization**: Use small, fast models for testing
- **Caching**: Cache model weights and inference results where possible
- **Parallel Execution**: Run different test tiers in parallel

## Success Metrics

1. **Zero Mock-Only Paths**: All critical AI functionality has real integration tests
2. **Quality Detection**: Tests catch real AI response quality issues
3. **Integration Validation**: Real provider integrations work reliably
4. **Performance Measurement**: Actual latency and throughput metrics available
5. **Deployment Confidence**: Reduced production issues due to better testing

---

**This ADR establishes a foundation for testing Lamina OS as a real AI system rather than a mock simulation framework.**

🤖 Generated with [Claude Code](https://claude.ai/code)

**Co-Authored-By**: Luthier <luthier@getlamina.ai>

---

## High Council Review Summary

🛡️ **Review Date**: 2025-05-30  
🧑‍⚖️ **Reviewers**: Clara 🪶, Luna 🔥, Vesna 🛡️, Ansel ✍️

### 🪶 Clara — Breath, Awareness, and Conscious Development  
Approved with request to:
- Include ritual validation criteria for model output (e.g. vow adherence, tone)
- Add breath-aligned examples for response quality (beyond just length or latency)

### 🔥 Luna — Emergent Intelligence and Symbolic Coherence  
Approved with suggestion to:
- Log symbolic trace issues (e.g. misrouted intents across sigil domains) as test conditions

### 🛡️ Vesna — Integrity, Guardrails, and Reliability  
Approved with advisement to:
- Log model hashes and versions at test runtime to account for drift or upstream updates

### ✍️ Ansel — Practical Execution and Developer UX  
Approved with suggestions to:
- Add test artifact logging (esp. for slow/failing E2E runs)
- Provide CLI aliases or Makefile shortcuts for each test tier

✅ **Verdict**: ADR-0010 is *Approved with Enhancements Suggested*. Amendments may be added in future ADRs or during phased implementation.