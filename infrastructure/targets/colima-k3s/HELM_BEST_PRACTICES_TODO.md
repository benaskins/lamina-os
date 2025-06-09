# Helm Best Practices Implementation TODO

This document outlines remaining Helm best practices to implement across all charts in the colima-k3s target.

## Status: Charts are production-ready for security but need documentation and validation improvements

✅ **RESOLVED**: Critical security issues (hardcoded Grafana password)  
✅ **RESOLVED**: Missing _helpers.tpl files  
✅ **RESOLVED**: Basic chart structure  

## Phase 1: Critical Documentation (High Priority)

### 🔴 Missing Documentation - All Charts
- [ ] **README.md files** for all charts with:
  - Purpose and architecture overview
  - Installation instructions  
  - Configuration examples
  - Troubleshooting guide
- [ ] **NOTES.txt files** for all charts with:
  - Post-installation verification steps
  - Access URLs and credentials
  - Next steps and related documentation
- [ ] **values.yaml inline documentation** explaining all configuration options

### 🔴 Template Quality Issues
- [ ] **Fix indentation inconsistencies** in:
  - `monitoring/templates/prometheus.yaml` line 79: use `nindent` instead of `indent`
  - `observability/templates/jaeger.yaml` line 66: use `nindent` instead of `indent`
- [ ] **Parameterize hardcoded values**:
  - Namespace references should use `{{ .Values.namespace }}`
  - Storage class names should be configurable
  - Service references should use values instead of hardcoded names

## Phase 2: Validation & Testing (Medium Priority)

### 🟡 Input Validation
- [ ] **values.schema.json** files for all charts to validate user inputs
- [ ] **Chart.yaml metadata completion**:
  - Add descriptions, keywords, maintainers to all charts
  - Ensure proper semantic versioning

### 🟡 Testing Infrastructure  
- [ ] **Helm tests** for each chart:
  - Connectivity tests (`test-connection.yaml`)
  - Health check validation
  - Integration tests between components

## Phase 3: Production Hardening (Low Priority)

### 🟢 High Availability
- [ ] **Pod Disruption Budgets** for:
  - Prometheus (monitoring)
  - Grafana (monitoring) 
  - Jaeger (observability)
  - Kiali (observability)

### 🟢 Security Enhancements
- [ ] **Network Policies** where appropriate
- [ ] **Pod Security Standards** implementation
- [ ] **Production authentication strategies** for observability tools

### 🟢 Operational Excellence
- [ ] **ServiceMonitor CRDs** for Prometheus integration
- [ ] **Pre-upgrade hooks** where needed
- [ ] **Affinity rules** for proper pod scheduling
- [ ] **Resource quotas** consideration

## Chart-Specific Notes

### colima-service-mesh
- Needs comprehensive README explaining Istio integration
- Consider adding service mesh connectivity tests

### lamina-llm-serve  
- Already has excellent Chart.yaml metadata
- Needs README with model serving setup guide
- Consider adding model health tests

### metallb
- Needs README with IP pool configuration guide
- Add IP allocation validation tests

### monitoring
- High priority: Fix template indentation
- Add comprehensive monitoring stack documentation
- Consider adding alerting rule templates

### observability
- High priority: Fix template indentation  
- Add observability dashboard access documentation
- Consider production auth strategies

### service-mesh
- Add template reusability documentation
- Parameterize hardcoded service references

## Recommended Implementation Order

1. **Week 1**: Fix template indentation + add NOTES.txt files
2. **Week 2**: Add README.md files + values.schema.json  
3. **Week 3**: Add Helm tests + complete Chart.yaml metadata
4. **Week 4**: Production hardening (PDBs, network policies, etc.)

## Template Structure Target

Each chart should eventually have:
```
chart-name/
├── Chart.yaml                 ✅ (improve metadata)
├── README.md                  ❌ (add)
├── values.yaml               ✅ (add inline docs)  
├── values.schema.json        ❌ (add)
├── templates/
│   ├── NOTES.txt             ❌ (add)
│   ├── _helpers.tpl          ✅ (completed)
│   ├── tests/                ❌ (add)
│   │   └── test-connection.yaml
│   └── [existing templates]  ✅ (fix indentation)
```

---

**Current Status**: Charts are secure and functional for production deployment. Documentation and validation improvements are recommended for long-term maintainability and user experience.