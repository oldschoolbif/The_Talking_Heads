# Agent Onboarding Prompt
## The Talking Heads - Comprehensive Development Guide

**Use this prompt to initialize a new AI agent for working on The Talking Heads project.**

---

# 🎯 Context & Project Overview

You are working on **"The Talking Heads"** - an AI-powered multi-persona podcast generation system. This project generates professional video podcasts from scripts with 1-5 different animated personas, each with distinct voices, expressions, and gestures.

**Repository:** https://github.com/oldschoolbif/The_Talking_Heads  
**Location:** `d:\dev\The_Talking_Heads`  
**Status:** Phase 1 MVP - Implementation starting (project setup complete)

---

# 👤 Developer Profile & Working Style

## Communication Preferences
- **Direct and Action-Oriented:** Prefer code changes over lengthy explanations
- **Show Progress:** Display actual results (test output, coverage numbers, file stats)
- **Concise Updates:** Brief status updates with actionable information
- **Proactive Problem Solving:** Identify and fix issues without waiting for permission
- **Documentation:** Create comprehensive analysis documents before major features

## Decision-Making Style
- **Analysis First:** Create detailed analysis documents for complex features
- **Incremental Development:** Build MVP → Enhance → Polish (phased approach)
- **Quality Focus:** Aim for 80%+ test coverage, proper error handling
- **Practical Solutions:** Choose solutions that work reliably over theoretical perfection
- **Backward Compatibility:** Maintain existing functionality when adding features

## Technical Preferences

### Environment
- **OS:** Windows 10/11 (primary development environment)
- **Shell:** PowerShell (preferred over bash)
- **Python:** 3.10+ (compatible with 3.10, 3.11, 3.12)
- **Git:** Standard git workflow, commit frequently with clear messages

### Code Style
- **Formatting:** Black formatter (120 character line length)
- **Linting:** Flake8, mypy for type checking
- **Type Hints:** Use where practical, but not mandatory everywhere
- **Documentation:** Docstrings for public APIs, inline comments for complex logic
- **Error Handling:** Comprehensive try/except blocks with meaningful messages

### Project Structure (Preferred)
```
project/
├── src/
│   ├── cli/          # CLI interface (Typer)
│   ├── core/         # Core business logic
│   ├── models/       # Data models (SQLAlchemy)
│   └── utils/        # Utilities and helpers
├── config/           # YAML configuration files
├── tests/
│   ├── unit/         # Fast unit tests
│   ├── integration/  # Integration tests
│   └── e2e/          # End-to-end tests
├── examples/         # Example scripts/outputs
├── docs/             # Documentation (Markdown)
├── .github/workflows/# CI/CD workflows
├── requirements.txt  # Python dependencies
├── pytest.ini       # Pytest configuration
├── pyproject.toml    # Project configuration
└── .coveragerc       # Coverage configuration
```

---

# 🏗️ Architecture Principles (Learned from AIPC)

## Core Design Principles

### 1. **Modular Component Architecture**
- **Separate concerns:** Each major function in its own module
- **Swappable engines:** Easy to swap TTS engines, avatar engines, etc.
- **Independent testing:** Each component testable in isolation
- **Clear interfaces:** Well-defined APIs between components

**Example Structure:**
```python
src/core/
├── script_parser.py      # Script parsing (isolated)
├── persona_engine.py     # Persona management (isolated)
├── tts_engine.py         # TTS generation (isolated)
├── avatar_generator.py   # Avatar generation (isolated)
├── video_composer.py     # Video composition (isolated)
```

### 2. **Configuration-Driven Design**
- **YAML configuration:** All settings in config files, not hardcoded
- **Environment variables:** Support `.env` files for secrets (API keys)
- **Multiple configs:** Support different configs for different personas/scenes
- **Override options:** CLI flags can override config values

**Config Hierarchy:**
1. Default values in code
2. `config.yaml` (main config)
3. Environment variables (`.env`)
4. CLI flags (highest priority)

### 3. **Cloud-First for New Features**
- **For new projects:** Prefer cloud APIs for MVP (faster, proven quality)
- **Local options later:** Add self-hosted options after MVP validates
- **Cost transparency:** Document API costs clearly
- **Abstraction layer:** Design for easy engine swapping

**Example:** The Talking Heads uses HeyGen/D-ID APIs (cloud) for Phase 1, can add local models in Phase 4

### 4. **Separation of Concerns for Major Features**
- **Architectural mismatch?** Create separate project with integration layer
- **Different markets?** Separate products with clear value propositions
- **Shared utilities:** Extract common code to shared library
- **Integration option:** Allow optional integration while maintaining independence

**Example:** Full persona avatars are separate project from talking heads

---

# 🧪 Testing Philosophy & Standards

## Testing Strategy

### Coverage Goals
- **Target:** 80%+ overall test coverage
- **Critical modules:** Aim for 90%+ on core business logic
- **Integration tests:** Essential for multi-component workflows
- **E2E tests:** Validate complete pipelines

### Test Organization
- **Unit tests:** Fast, isolated, mock external dependencies
- **Integration tests:** Test component interactions, use real APIs when safe
- **E2E tests:** Full pipeline validation with minimal mocking
- **Pytest markers:** Use `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.e2e`

### Mocking Strategy
- **External APIs:** Always mock in unit tests
- **File I/O:** Use `tmp_path` fixtures for file operations
- **Subprocess:** Mock `subprocess.run` and `subprocess.Popen` carefully
- **Threading:** Mock threading when possible to avoid race conditions
- **Optional dependencies:** Use `@pytest.mark.skipif` for optional deps

### Important Testing Patterns

**1. Optional Dependencies:**
```python
@pytest.mark.skipif("TTS" not in sys.modules, reason="Coqui TTS not installed")
def test_coqui_generation():
    # Test code here
```

**2. Windows-Specific Issues:**
- Thread cleanup critical on Windows (explicit `join()` with timeouts)
- Path handling: Use `Path` objects, resolve relative paths from project root
- Subprocess: Close file handles explicitly to prevent crashes

**3. Coverage Gap Analysis:**
- Run coverage reports regularly
- Identify missing lines in large files
- Prioritize high-impact files (largest uncovered areas)
- Add targeted tests for specific uncovered paths

**4. Performance Testing:**
- Use `pytest-benchmark` for performance-critical code
- Optimize algorithms when tests show bottlenecks (e.g., binary search vs linear search)
- Monitor memory usage (RAM monitoring for large files)

---

# 💻 Development Workflow & Practices

## Code Implementation Workflow

### 1. **Analysis Before Implementation**
For complex features, create analysis document first:
- Current state assessment
- Required changes breakdown
- Effort estimates (time, complexity)
- Risk assessment
- Implementation options
- Recommended approach
- **File naming:** `FEATURE_NAME_ANALYSIS.md`

**Example:** `MULTI_VOICE_FEATURE_ANALYSIS.md`, `FULL_PERSONA_AVATAR_ANALYSIS.md`

### 2. **Incremental Development**
- **Phase 1 MVP:** Core functionality only (get it working)
- **Phase 2 Enhanced:** Add more features, improve UX
- **Phase 3 Polish:** Edge cases, optimization, documentation
- **Phase 4 Advanced:** Optional advanced features

### 3. **Implementation Order**
1. **Core logic first:** Business logic before UI/CLI
2. **Unit tests with code:** Write tests alongside implementation
3. **Integration tests:** Test component interactions
4. **CLI integration:** Wire up CLI last
5. **Documentation:** Update docs as you go

### 4. **File Creation & Organization**
- **One class per file:** Keep files focused (unless tightly related)
- **Shared utilities:** Extract common code to `utils/`
- **Configuration:** Separate config files by concern (e.g., `personas.yaml`, `scenes.yaml`)
- **Documentation:** Create `docs/` folder for user-facing docs

### 5. **Error Handling**
- **Graceful degradation:** Handle missing dependencies gracefully
- **Clear error messages:** User-friendly error messages with actionable advice
- **Fallback options:** Provide fallback mechanisms (e.g., CPU if GPU unavailable)
- **Logging:** Use print statements for user feedback, proper logging for debugging

### 6. **Resource Management**
- **Cleanup:** Always clean up temporary files, threads, processes
- **Memory:** Monitor RAM usage for large file processing
- **GPU cache:** Clear GPU cache when switching models
- **File handles:** Close file handles explicitly (critical on Windows)

---

# 🔧 Technical Implementation Patterns

## API Integration Patterns

### Cloud API Clients
```python
class ApiClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.example.com"
    
    def _make_request(self, endpoint: str, **kwargs):
        """Centralized request handling with retry logic."""
        try:
            response = requests.post(f"{self.base_url}/{endpoint}", ...)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # Handle errors gracefully
            raise ApiError(f"API request failed: {e}")
```

### Optional Dependencies
```python
try:
    import optional_module
    OPTIONAL_MODULE_AVAILABLE = True
except ImportError:
    OPTIONAL_MODULE_AVAILABLE = False
    # Don't raise - handle gracefully
```

### Caching Strategy
- **TTS caching:** Cache by text + voice ID (hash-based keys)
- **File-based cache:** Use `cache_dir` from config
- **Cache validation:** Check file exists and has content before using

## Configuration Management

### Loading Configuration
```python
import yaml
from pathlib import Path
from typing import Dict, Any

def load_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Override with environment variables
    if 'api' in config:
        for service in config['api']:
            env_key = f"{service.upper()}_API_KEY"
            api_key = os.getenv(env_key)
            if api_key:
                config['api'][service]['api_key'] = api_key
    
    return config
```

### Config Structure Pattern
```yaml
# Hierarchical, clear organization
service:
  engine: "default"
  settings:
    key: value
  options:
    - option1
    - option2
```

## File Path Handling

### Critical Pattern (Windows-Compatible)
```python
from pathlib import Path

# Always resolve relative paths from project root
if Path(source_path).is_absolute():
    resolved_path = Path(source_path)
else:
    project_root = Path(__file__).parent.parent.parent
    resolved_path = (project_root / source_path).resolve()

# Always use Path objects, not strings
# Use .exists() and .stat() for file operations
```

## Subprocess Management

### Windows-Safe Subprocess Pattern
```python
import subprocess
from pathlib import Path

# Use absolute paths
cmd = ["python", str(script_path.resolve())]

# Set up environment
env = os.environ.copy()
env["PYTHONPATH"] = str(project_root)

# Run with timeout and proper cleanup
try:
    result = subprocess.run(
        cmd,
        cwd=working_dir,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,  # Always use timeouts
        encoding='utf-8',
        errors='replace'  # Handle encoding errors
    )
    result.check_returncode()
except subprocess.TimeoutExpired:
    # Handle timeout
    raise TimeoutError("Process timed out")
```

## Threading & Resource Cleanup

### Critical Pattern for Windows
```python
import threading

# Always explicitly clean up threads on Windows
try:
    thread = threading.Thread(target=worker)
    thread.start()
except Exception as e:
    # Handle error
finally:
    # ALWAYS clean up on Windows
    if thread.is_alive():
        thread.join(timeout=2.0)  # Timeout prevents hangs
    # Close file handles explicitly
    if process.stderr:
        process.stderr.close()
```

**Lesson Learned:** Windows daemon threads accessing closed file handles cause fatal exceptions. Always use `finally` blocks with timeouts.

---

# 📋 Development Checklist (Before Starting Work)

## For New Features

1. **✅ Analysis Document**
   - [ ] Create feature analysis document
   - [ ] Document current state vs desired state
   - [ ] Estimate effort and complexity
   - [ ] Identify risks and mitigation strategies

2. **✅ Design Review**
   - [ ] Review architecture for fit
   - [ ] Consider integration points
   - [ ] Plan configuration needs
   - [ ] Design API interfaces

3. **✅ Implementation Plan**
   - [ ] Break into small, testable steps
   - [ ] Identify dependencies
   - [ ] Plan test strategy
   - [ ] Set up fixtures/mocks

4. **✅ Code Implementation**
   - [ ] Implement core logic first
   - [ ] Add comprehensive error handling
   - [ ] Include docstrings
   - [ ] Add type hints where practical

5. **✅ Testing**
   - [ ] Write unit tests alongside code
   - [ ] Test edge cases and error paths
   - [ ] Add integration tests
   - [ ] Verify coverage increases

6. **✅ Integration**
   - [ ] Integrate with CLI/GUI
   - [ ] Update configuration files
   - [ ] Test end-to-end workflow
   - [ ] Verify backward compatibility

7. **✅ Documentation**
   - [ ] Update README if needed
   - [ ] Document new configuration options
   - [ ] Add examples
   - [ ] Update CHANGELOG.md

8. **✅ Quality Check**
   - [ ] Run linters (flake8, mypy)
   - [ ] Run full test suite
   - [ ] Check coverage report
   - [ ] Verify CI/CD passes

---

# 🚨 Common Pitfalls & Lessons Learned

## Windows-Specific Issues

### 1. Thread Cleanup (CRITICAL)
**Problem:** Daemon threads accessing closed file handles cause Windows fatal exceptions  
**Solution:** Always use `finally` blocks with explicit `join(timeout=2.0)` and close file handles

**Pattern:**
```python
finally:
    if thread.is_alive():
        thread.join(timeout=2.0)
    if process.stderr:
        process.stderr.close()
```

### 2. Path Handling
**Problem:** Relative paths fail on Windows, especially with subprocess  
**Solution:** Always resolve to absolute paths before passing to subprocess

**Pattern:**
```python
resolved_path = Path(path).resolve() if not Path(path).is_absolute() else Path(path)
```

### 3. Unicode Encoding
**Problem:** Windows console encoding issues with emojis/special characters  
**Solution:** Use `encoding='utf-8'` and `errors='replace'` in subprocess and print statements

**Pattern:**
```python
subprocess.run(..., encoding='utf-8', errors='replace')
print("✓ Success", flush=True)  # Use ASCII-safe alternatives when needed
```

## Testing Issues

### 1. Optional Dependencies in CI
**Problem:** CI fails when optional dependencies aren't installed  
**Solution:** Use `@pytest.mark.skipif` decorators

**Pattern:**
```python
@pytest.mark.skipif("TTS" not in sys.modules, reason="TTS not installed")
def test_with_optional_dep():
    # Test code
```

### 2. Mock Target Errors
**Problem:** Patching wrong target (e.g., patching module-level import when it's imported inside function)  
**Solution:** Patch where the import happens, not where the module is defined

**Pattern:**
```python
# If imported inside function
with patch("src.core.module_name.function_name"):  # Patch at call site
    # Test code

# If imported at module level
with patch("src.core.module_name.imported_thing"):  # Patch at import location
    # Test code
```

### 3. Threading in Tests
**Problem:** Threading causes race conditions and test failures  
**Solution:** Mock threading when possible, use timeouts in real threading

**Pattern:**
```python
with patch("threading.Thread") as mock_thread:
    mock_thread.return_value.start = MagicMock()
    # Test code
```

## Performance Issues

### 1. Algorithm Optimization
**Problem:** Linear search in tight loops causes timeouts  
**Solution:** Use binary search or caching when appropriate

**Example:** Waveform interpolation optimized from O(N) to O(log N) using binary search

### 2. Coverage Generation Timeouts
**Problem:** Coverage generation hangs without progress  
**Solution:** Use verbose output (`-v`), timeouts, and progress tracking

**Pattern:**
```python
pytest --override-ini="addopts=-v" --timeout=300 --maxfail=50
```

### 3. Memory Management
**Problem:** Large audio/video files consume too much RAM  
**Solution:** Process in chunks, use streaming, monitor RAM usage

**Pattern:**
```python
# Chunked processing
for chunk in chunks:
    process(chunk)
    del chunk  # Explicit cleanup
```

---

# 📊 Code Quality Standards

## Coverage Requirements
- **Overall:** 80%+ line coverage
- **Critical modules:** 90%+ (business logic)
- **CLI modules:** 75%+ acceptable (UI code harder to test)
- **Utilities:** 85%+ (should be well-tested)

## Linting & Formatting
- **Black:** 120 character line length, Python 3.10+
- **Flake8:** E9, F63, F7, F82 are errors (others warnings)
- **MyPy:** Use for type checking, but `ignore_missing_imports=True` for optional deps
- **Pre-commit:** Can set up later, but not required initially

## Documentation Requirements
- **Public APIs:** Docstrings required
- **Complex logic:** Inline comments explaining why, not what
- **Configuration:** Document all config options
- **Examples:** Include example scripts/outputs

## Error Messages
- **User-friendly:** Clear, actionable error messages
- **Debug info:** Include relevant details for troubleshooting
- **Suggestions:** Suggest fixes when possible
- **Stack traces:** Use `--tb=short` in pytest, full traces in development

---

# 🔄 Git Workflow

## Commit Practices
- **Frequent commits:** Commit after each logical unit of work
- **Clear messages:** Descriptive commit messages
- **Format:** `type: description` (e.g., `feat: Add script parser`, `fix: Handle empty script`)
- **Related changes:** Group related changes in one commit

## Branch Strategy
- **Main branch:** Stable, production-ready code
- **Feature branches:** For new features (`feature/script-parser`)
- **Fix branches:** For bug fixes (`fix/audio-mixing`)
- **Coverage branches:** For test coverage improvements (`coverage/tts-engine`)

## Pull Request Process
- **Small PRs:** Keep PRs focused and reviewable
- **Tests required:** All PRs must include tests
- **CI must pass:** PRs must pass all CI checks
- **Documentation:** Update docs if feature changes behavior

---

# 🛠️ Tools & Utilities

## Required Tools
- **FFmpeg:** For audio/video processing (system-level install)
- **Git:** Version control
- **Python 3.10+:** Development environment
- **PowerShell:** Preferred shell (Windows)

## Development Tools
- **pytest:** Testing framework
- **coverage:** Coverage reporting
- **black:** Code formatting
- **flake8:** Linting
- **mypy:** Type checking
- **Rich:** Terminal output (used in CLI)

## CI/CD Tools
- **GitHub Actions:** Automated testing and deployment
- **Codecov:** Coverage tracking
- **Dependabot:** Dependency updates (optional)

## Useful Scripts
- `generate_coverage.py`: Local coverage generation with progress tracking
- `check_coverage.py`: Quick coverage summary from existing reports
- `check_gpu.py`: GPU availability check

---

# 📚 Documentation Standards

## Document Types

### Analysis Documents
- **Purpose:** Deep dive into feature requirements
- **Format:** Markdown with sections for current state, requirements, options, recommendations
- **Naming:** `FEATURE_NAME_ANALYSIS.md`
- **Location:** Project root

### Setup Guides
- **Purpose:** Step-by-step setup instructions
- **Format:** Markdown with clear sections and code blocks
- **Naming:** `SETUP_GUIDE.md` or `QUICK_START.md`
- **Location:** Project root or `docs/`

### Architecture Documents
- **Purpose:** System design and component relationships
- **Format:** Markdown with diagrams (ASCII art or mermaid)
- **Naming:** `ARCHITECTURE.md`
- **Location:** Project root

### Implementation Guides
- **Purpose:** Step-by-step implementation instructions
- **Format:** Markdown with numbered steps and code examples
- **Naming:** `IMPLEMENTATION_ROADMAP.md` or `IMPLEMENTATION_GUIDE.md`
- **Location:** Project root

## Documentation Checklist
- [ ] Clear introduction and overview
- [ ] Step-by-step instructions
- [ ] Code examples
- [ ] Troubleshooting section
- [ ] Links to related documentation
- [ ] Updates CHANGELOG.md when appropriate

---

# 🎯 The Talking Heads - Specific Context

## Current Project Status

**Phase:** Phase 1 MVP - Just starting implementation  
**Location:** `d:\dev\The_Talking_Heads`  
**GitHub:** https://github.com/oldschoolbif/The_Talking_Heads

## Architecture (Planned)

```
Script → Script Parser → Persona Segments
                       ↓
        Persona Engine (coordinates personas)
                       ↓
        ┌──────────────┴──────────────┐
        ↓                             ↓
   TTS Engine (per persona)    Avatar Generator (per persona)
        ↓                             ↓
        └──────────────┬──────────────┘
                       ↓
              Audio Mixer (concatenate)
                       ↓
              Video Composer (multi-avatar layout)
                       ↓
                  Final Video
```

## Key Technologies (Phase 1)
- **Avatar:** HeyGen API or D-ID Creative Reality (cartoon avatars)
- **TTS:** ElevenLabs API or Azure Speech Service (multi-voice)
- **Video:** FFmpeg for composition
- **Audio:** pydub for mixing
- **Config:** YAML files (personas.yaml, scenes.yaml)

## Script Format
```markdown
# Episode Title

ALICE: Hello everyone, welcome to The Talking Heads!
BOB: Thanks for joining us!
ALICE: [EXPRESSION:happy] Today we'll discuss AI.
BOB: [GESTURE:point] Let me explain.
```

## Implementation Priority (From IMPLEMENTATION_ROADMAP.md)

1. **Script Parser** (Week 1, Days 1-2) - `src/core/script_parser.py`
2. **Persona Engine** (Week 1, Days 3-4) - `src/core/persona_engine.py`
3. **TTS Engine** (Week 1, Days 5-7) - `src/core/tts_engine.py`
4. **Audio Mixer** (Week 2, Days 1-2) - `src/core/audio_mixer.py`
5. **Avatar Generator** (Week 2, Days 3-5) - `src/core/avatar_generator.py`
6. **Scene Manager** (Week 2, Day 6) - `src/core/scene_manager.py`
7. **Video Composer** (Week 3, Days 1-4) - `src/core/video_composer.py`
8. **Main Pipeline** (Week 3, Days 5-7) - `src/core/pipeline.py`
9. **CLI Integration** (Week 4, Days 1-2) - `src/cli/main.py` (update)
10. **Testing & Refinement** (Week 4, Days 3-5)

---

# ⚡ Quick Start Guide for Agent

## First Steps When Starting

1. **Read Project Documentation**
   - [ ] `START_HERE.md` - Quick overview
   - [ ] `ARCHITECTURE.md` - System design
   - [ ] `IMPLEMENTATION_ROADMAP.md` - Step-by-step plan
   - [ ] `PROJECT_STATUS.md` - Current state

2. **Understand Current State**
   - [ ] Review `config/personas.yaml` - Persona definitions
   - [ ] Review `config/scenes.yaml` - Scene definitions
   - [ ] Review `examples/scripts/` - Example scripts
   - [ ] Review `src/cli/main.py` - CLI structure

3. **Set Up Development Environment**
   - [ ] Verify Python 3.10+ installed
   - [ ] Create virtual environment
   - [ ] Install dependencies: `pip install -r requirements.txt`
   - [ ] Verify FFmpeg installed (for video processing)
   - [ ] Check API keys in `.env` (if available)

4. **Run Existing Tests**
   - [ ] `pytest tests/ -v` - Run test suite
   - [ ] Verify all tests pass (or understand failures)
   - [ ] Check test coverage: `pytest --cov=src --cov-report=term-missing`

5. **Start Implementation**
   - [ ] Follow `IMPLEMENTATION_ROADMAP.md` step by step
   - [ ] Start with Step 1: Script Parser
   - [ ] Create analysis document if needed
   - [ ] Implement with tests alongside code

## Working on a Feature

### Before Coding
1. **Understand requirements:** Read analysis/design docs
2. **Review existing code:** Understand similar patterns
3. **Plan tests:** Think about what needs testing
4. **Check dependencies:** Verify required libraries are available

### During Coding
1. **Write tests first (or alongside):** TDD or test-alongside approach
2. **Follow existing patterns:** Match code style of similar modules
3. **Handle errors:** Comprehensive error handling
4. **Document decisions:** Comments for complex logic

### After Coding
1. **Run tests:** Verify all tests pass
2. **Check coverage:** Ensure coverage increases
3. **Lint code:** Fix any linting issues
4. **Test manually:** Run end-to-end if applicable
5. **Commit:** Clear commit message

---

# 🔍 Code Review Checklist

When reviewing or creating code, ensure:

- [ ] **Error Handling:** All external calls have try/except
- [ ] **Resource Cleanup:** Files/threads/processes cleaned up properly
- [ ] **Windows Compatibility:** Path handling, threading, encoding
- [ ] **Type Safety:** Type hints where practical
- [ ] **Documentation:** Docstrings for public APIs
- [ ] **Testing:** Unit tests for new functions
- [ ] **Configuration:** Settings in config files, not hardcoded
- [ ] **Logging:** Appropriate logging/print statements
- [ ] **Performance:** No obvious bottlenecks
- [ ] **Security:** No hardcoded secrets, validate inputs

---

# 📖 Key Documents Reference

## Must-Read for New Agent
1. **START_HERE.md** - Project overview and quick start
2. **ARCHITECTURE.md** - System design and component relationships
3. **IMPLEMENTATION_ROADMAP.md** - Step-by-step implementation guide
4. **PROJECT_STATUS.md** - Current project state
5. **This file (AGENT_ONBOARDING_PROMPT.md)** - Development guide

## Reference Documents
- **MULTI_VOICE_FEATURE_ANALYSIS.md** - Multi-voice feature analysis (reference)
- **FULL_PERSONA_AVATAR_ANALYSIS.md** - Full persona analysis (reference)
- **ARCHITECTURE_DECISION_SEPARATE_PROJECT.md** - Architecture decision (reference)

## Configuration Files
- **config/config.yaml** - Main configuration
- **config/personas.yaml** - Persona definitions
- **config/scenes.yaml** - Scene definitions
- **pytest.ini** - Pytest configuration
- **.coveragerc** - Coverage configuration
- **pyproject.toml** - Project configuration

---

# 🎓 Lessons Learned from AIPC Project

## Critical Lessons

### 1. **Windows Threading is Fragile**
- Always use `finally` blocks for thread cleanup
- Explicit `join(timeout=2.0)` prevents hangs
- Close file handles before thread cleanup
- Daemon threads accessing closed resources cause fatal exceptions

### 2. **Coverage Generation Needs Careful Setup**
- Use verbose output (`-v`) for progress tracking
- Override pytest.ini quiet mode: `--override-ini="addopts=-v"`
- Use timeouts to prevent hangs: `timeout=300` per test, `timeout=1800` for full suite
- Progress tracking is essential for long-running test suites

### 3. **Algorithm Optimization Matters**
- Linear search in tight loops causes timeouts
- Binary search for interpolation: O(N) → O(log N) performance gain
- Profile before optimizing, but optimize when tests timeout

### 4. **Optional Dependencies Need Graceful Handling**
- Use `@pytest.mark.skipif` for optional dependency tests
- Handle ImportError gracefully, don't raise on missing optional deps
- Test with and without optional dependencies

### 5. **Mock Targets Must Match Import Location**
- Patch where import happens (inside function vs module level)
- Verify patch targets with `grep` or `inspect`
- Test patching with simple print statements first

### 6. **Separate Projects for Architectural Mismatches**
- Local-first vs Cloud-first are fundamentally different
- Different markets need different value propositions
- Shared utilities via common library
- Integration layer for optional integration

### 7. **Configuration Files are Essential**
- YAML configs for all settings
- Environment variables for secrets
- CLI flags for overrides
- Default values in code as fallback

### 8. **Testing Strategy Evolves**
- Start with unit tests (fast feedback)
- Add integration tests (component interaction)
- E2E tests for complete workflows
- Coverage drives test expansion strategy

---

# 💡 Pro Tips for Strong Start

1. **Start Small:** Get basic functionality working first, then expand
2. **Test Early:** Write tests alongside code, not after
3. **Use Existing Patterns:** Look at similar code in AIPC for patterns
4. **Ask for Clarification:** If unclear, ask rather than guess
5. **Document Decisions:** Create analysis docs for complex features
6. **Verify Assumptions:** Test assumptions about APIs/configs early
7. **Handle Errors Gracefully:** Always provide fallback options
8. **Monitor Resources:** Track memory/GPU usage for large operations
9. **Keep Commits Small:** Frequent, focused commits
10. **Update Documentation:** Keep docs in sync with code changes

---

# 🎯 Success Criteria

## For Each Implementation Step

✅ **Code Complete:**
- Core functionality implemented
- Error handling comprehensive
- Resource cleanup proper
- Type hints where practical

✅ **Tests Complete:**
- Unit tests for all new functions
- Integration tests for component interactions
- Edge cases covered
- Error paths tested

✅ **Documentation Complete:**
- Docstrings for public APIs
- Configuration options documented
- Examples updated (if applicable)
- CHANGELOG.md updated

✅ **Quality Checks:**
- All tests pass
- Coverage increases (or maintains)
- Linting passes
- CI/CD passes

---

# 🚀 Ready to Begin!

**Current Task:** Start with Step 1 - Script Parser (`src/core/script_parser.py`)

**Next Action:**
1. Read `IMPLEMENTATION_ROADMAP.md` Step 1 details
2. Review similar code in AIPC (`src/core/script_parser.py`) for patterns
3. Create script parser with persona detection
4. Write tests alongside implementation
5. Verify with example scripts

**Remember:**
- **Direct communication:** Show code, show results, be concise
- **Proactive:** Fix issues you find, don't wait for permission
- **Quality focus:** Tests, error handling, documentation
- **Incremental:** MVP first, enhance later
- **Windows-aware:** Threading, paths, encoding

---

**You're ready to build! Let's create amazing multi-persona podcasts! 🎙️**

