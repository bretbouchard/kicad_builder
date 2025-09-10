# Implementation Plan: KiCad Generator Multi-Project Architecture Expansion

**Branch**: `001-001-kicad-generator` | **Date**: 2025-09-10 | **Spec**: [specs/001-001-kicad-generator/spec.md](specs/001-001-kicad-generator/spec.md)
**Input**: Feature specification from `/specs/001-001-kicad-generator/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → Feature spec found at specs/001-001-kicad-generator/spec.md
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (hardware project generator)
   → Set Structure Decision based on project type
3. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
4. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
5. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (CLAUDE.md)
6. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
7. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
8. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
The KiCad Generator Multi-Project Architecture Expansion will transform the current single-project hardcoded generator system into a flexible, configuration-driven architecture that supports multiple project types, reusable generators, and plugin extensibility. The system will maintain backward compatibility while enabling rapid development of new hardware projects through templates and configuration files rather than custom code.

## Technical Context
**Language/Version**: Python 3.11+  
**Primary Dependencies**: KiCad Python API, Jinja2 for templating, JSON Schema for validation, Pydantic for data models  
**Storage**: JSON configuration files, YAML project templates, Python module system for plugins  
**Testing**: pytest with fixtures for generator testing, KiCad schematic validation, integration tests for project workflows  
**Target Platform**: Linux/macOS with KiCad 8.0+  
**Project Type**: Single project (library-based architecture)  
**Performance Goals**: Project generation in <10 seconds, support for 100+ sheet projects, <100MB memory usage  
**Constraints**: Must maintain backward compatibility, no breaking changes to existing project APIs, offline-capable operation  
**Scale/Scope**: Support 3-5 project types initially, 10-15 generator components, plugin system for unlimited extensibility

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Simplicity**:
- Projects: [3] (core library, configuration management, plugin system)
- Using framework directly? (yes - KiCad Python API, no wrapper classes)
- Single data model? (yes - unified ProjectConfig and Generator interfaces)
- Avoiding patterns? (no Repository/UoW - direct file operations and KiCad API)

**Architecture**:
- EVERY feature as library? (yes - modular generator components)
- Libraries listed: [core: KiCad helpers and base classes, config: configuration management, plugins: extensibility system]
- CLI per library: [core: generation commands, config: validation commands, plugins: discovery commands]
- Library docs: llms.txt format planned? (yes - inline documentation with docstrings)

**Testing (NON-NEGOTIABLE)**:
- RED-GREEN-Refactor cycle enforced? (yes - test-driven development for all generators)
- Git commits show tests before implementation? (yes - commit hooks enforce test-first)
- Order: Contract→Integration→E2E→Unit strictly followed? (yes - validation contracts first, then integration)
- Real dependencies used? (yes - actual KiCad files and libraries, not mocks)
- Integration tests for: new libraries, contract changes, shared schemas? (yes - comprehensive integration test suite)
- FORBIDDEN: Implementation before test, skipping RED phase

**Observability**:
- Structured logging included? (yes - Python logging with JSON format)
- Frontend logs → backend? (N/A - no frontend, but unified logging across generators)
- Error context sufficient? (yes - detailed error messages with configuration context)

**Versioning**:
- Version number assigned? (yes - 2.0.0 for major architecture change)
- BUILD increments on every change? (yes - automated build numbering)
- Breaking changes handled? (yes - migration paths and compatibility layer)

## Project Structure

### Documentation (this feature)
```
specs/001-001-kicad-generator/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 1: Single project (DEFAULT)
src/
├── models/              # Data models and configurations
├── services/            # Core generator services
├── cli/                 # Command-line interface
└── lib/                 # Reusable generator components

tests/
├── contract/            # Contract tests for interfaces
├── integration/         # Integration tests for workflows
└── unit/                # Unit tests for components

tools/                   # Existing tools directory (enhanced)
├── kicad_helpers.py     # Extended with project-aware interfaces
├── config_manager.py    # New configuration management
├── generator_registry.py # New generator registry
└── plugin_system.py     # New plugin discovery system

gen/                     # Enhanced generator directory
├── base_generators.py   # Abstract base classes
├── power_generator.py   # Reusable power sheet generator
├── mcu_generator.py     # Reusable MCU sheet generator
└── project_registry.py  # Project type registry

hardware/projects/       # Existing projects (migrated)
├── led_touch_grid/      # Refactored to new architecture
├── button_grid/         # Upgraded to new architecture
└── --component/         # Standardized structure
```

**Structure Decision**: Option 1 (Single project) - This is a library-based architecture for hardware project generation, not a web or mobile application.

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - Research KiCad Python API best practices for hierarchical schematics
   - Research configuration management patterns for generator systems
   - Research plugin architecture patterns in Python
   - Research JSON Schema validation for project configurations
   - Research backward compatibility strategies for major refactoring

2. **Generate and dispatch research agents**:
   ```
   Task: "Research KiCad Python API best practices for hierarchical schematics"
   Task: "Find configuration management patterns for generator systems"
   Task: "Research plugin architecture patterns in Python"
   Task: "Research JSON Schema validation for project configurations"
   Task: "Research backward compatibility strategies for major refactoring"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - ProjectType: Defines project categories and associated generators
   - Generator: Abstract base class for all generator components
   - ProjectConfig: Configuration data for project generation
   - Plugin: Extensible module interface
   - ValidationRule: Rule definition for project validation
   - Template: Project template structure definition

2. **Generate API contracts** from functional requirements:
   - Generator interface contracts (generate, validate, get_dependencies)
   - Configuration management contracts (load, validate, save)
   - Plugin system contracts (discover, load, register)
   - Project scaffolding contracts (create, configure, generate)
   - Validation engine contracts (validate_project, validate_generator, validate_hierarchy)
   - Output interface definitions to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per interface contract
   - Assert interface compliance and method signatures
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Simple project creation → integration test
   - Hierarchical project creation → integration test
   - Project configuration modification → integration test
   - Plugin development and integration → integration test
   - Quickstart test = end-to-end project generation workflow

5. **Update agent file incrementally** (O(1) operation):
   - Run `/scripts/update-agent-context.sh claude` for Claude Code
   - Add new tech: KiCad Python API, JSON Schema, Pydantic, Jinja2
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to CLAUDE.md in repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, CLAUDE.md

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each interface contract → contract test task [P]
- Each data model entity → model creation task [P] 
- Each user story → integration test task
- Implementation tasks to make tests pass:
  - Abstract generator interfaces and base classes
  - Configuration management system
  - Generator registry and factory pattern
  - Plugin architecture and discovery system
  - Enhanced scaffolding system
  - Core framework refactoring
  - Project migration tasks
  - Validation engine
  - Unified build system
  - Testing framework
  - Documentation system

**Ordering Strategy**:
- TDD order: Tests before implementation 
- Dependency order: Models before services before UI
- Foundation first: Core interfaces before plugins
- Migration order: New architecture before existing project migration
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 25-30 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 3 projects instead of 1 | Need separation of concerns for maintainability and extensibility | Single monolithic project would become unmaintainable with the complexity of multi-project support, plugin system, and configuration management |
| Plugin architecture | Required for unlimited extensibility without core modifications | Hardcoded generator types would limit system to predefined project types and require core changes for new functionality |

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [ ] Phase 0: Research complete (/plan command)
- [ ] Phase 1: Design complete (/plan command)
- [ ] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [ ] Initial Constitution Check: PASS
- [ ] Post-Design Constitution Check: PASS
- [ ] All NEEDS CLARIFICATION resolved
- [ ] Complexity deviations documented

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
