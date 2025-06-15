# 📦 Archive Directory

This directory contains development files, legacy components, and testing utilities that are not needed for production use but are preserved for reference.

## 📁 Directory Structure

### `legacy_gui/`
**Original PyQt6 GUI components** from the initial prototype:
- `fieldmappingwidget.py` - GUI form field mapping widget
- `main.py` - Original GUI entry point

### `development/`
**Development utilities and testing files**:
- `legal_form_processor.py` - Extended legal processor (superseded by universal_form_processor.py)
- `show_extracted_data.py` - Data extraction demonstration
- `create_demo_form.py` - Form creation utilities
- `create_fillable_form.py` - PDF form creation tools
- `fl142_fillable_template.pdf` - Sample fillable form
- `universal_extraction.json` - Real test results (95% accuracy)
- `agentic_form_filler.log` - Debug logs

### `testing/`
**Test files and old versions**:
- `test_agentic_system.py` - Comprehensive test suite
- `test_integration.py` - Integration testing
- `test_universal_processor.py` - Universal processor tests
- `quick_test_old.py` - Previous version of health checker

## 🚮 **Safe to Delete**

These files are archived for reference but are not required for the production system. The main directory contains all active, production-ready components.

## 📋 **If You Need Them**

- **GUI Development**: Use files from `legacy_gui/` as a starting point
- **Testing Reference**: Check `testing/` for comprehensive test examples  
- **Development Tools**: Use utilities from `development/` for custom extensions

---

*These files represent the development history and are preserved for reference purposes.*
