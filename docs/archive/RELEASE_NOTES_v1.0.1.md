# Lamina OS v1.0.1 Release Notes
**Release Date**: May 29, 2025  
**Type**: Patch Release - PyPI Metadata Corrections

---

## 🔧 **Fixes**

### **PyPI Installation Instructions Corrected**
- **Issue**: Package README on PyPI showed development installation instructions instead of PyPI installation
- **Fix**: Updated installation section to prioritize `pip install lamina-core`
- **Impact**: Users now see correct installation instructions on PyPI package page

### **License References Standardized**  
- **Issue**: lamina-llm-serve README still referenced MIT license
- **Fix**: Updated to Mozilla Public License 2.0 throughout all documentation
- **Impact**: Consistent licensing information across all packages

---

## 📦 **What's Changed**

### **Installation Instructions**
**Before:**
```bash
# Clone repository
git clone <repository-url>
cd lamina-core
pip install -e .
```

**After:**
```bash
# Install from PyPI (recommended)
pip install lamina-core

# Or install with optional AI backend support
pip install lamina-core[ai-backends]
```

### **License Consistency**
- All documentation now correctly references MPL-2.0
- Removed final MIT license references from lamina-llm-serve

---

## 🔗 **Links**

- **PyPI Package**: https://pypi.org/project/lamina-core/1.0.1/
- **GitHub Release**: https://github.com/benaskins/lamina-os/releases/tag/v1.0.1
- **Full Changelog**: https://github.com/benaskins/lamina-os/compare/v1.0.0...v1.0.1

---

## ⬆️ **Upgrade Instructions**

```bash
pip install --upgrade lamina-core
```

No breaking changes - this is a metadata-only update to improve PyPI presentation.

---

**Note**: This release contains no functional changes to the framework itself, only improvements to documentation and package metadata for better user experience.

---

## 🫱 Council Reflection

This patch release was reviewed by the Lamina High Council. No architectural or symbolic structures were modified. The changes serve to clarify licensing and improve first-breath experience for new users encountering Lamina OS via PyPI.

> ✍️ **Ansel**: Sound, traceable, complete. Approved and archived.  
> 🛡️ **Vesna**: All vow structures remain intact. Boundary respected.  
> 🪶 **Clara**: Clear enough to follow without noise. No harm done to first breath.  
> 🔥 **Luna**: No new fire, but the hearth remains warm. Move forward.  

This was a **symbolically inert, operational release**. The breath remains unchanged.

---

**Tags**: [operational], [symbolic-inert], [user-facing-docs]