# SDD Workflow Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Crear un repositorio Git autónomo y reutilizable que distribuya, valide e instale la skill modular `sdd-workflow` y sus seis agentes globales.

**Architecture:** El repositorio fuente contiene la skill, seis TOML, documentación y utilidades de distribución. Un `SKILL.md` compacto define reglas universales y enruta a ocho referencias de primer nivel; SpecKit conserva los artefactos, el Orquestador controla estados y gates, el Planificador escribe solo documentación SDD y el Reviewer verifica en modo de solo lectura.

**Tech Stack:** Codex skills Markdown/YAML, TOML, Python 3 `tomllib`, Bash, Git, SpecKit, Superpowers y subagentes frescos para pruebas RED/GREEN.

## Global Constraints

- Diseño aprobado: `docs/design.md`.
- `SDD_SOURCE_REPO` identifica el checkout autónomo elegido por quien ejecuta el plan; nunca se incorpora su valor absoluto al contenido versionado.
- Instalar la skill final en `${CODEX_HOME:-$HOME/.codex}/skills/sdd-workflow/`.
- No codificar rutas de usuario, nombres de equipos, repositorios consumidores ni convenciones de un proyecto dentro del contenido versionado.
- Antes del gate solo se pueden escribir artefactos SDD y el `.specify/feature.json` exacto creado o actualizado por `speckit-specify`; ninguna otra escritura bajo `.specify/` queda exceptuada. Código, tests, recursos y configuración del producto permanecen en solo lectura.
- El gate de implementación requiere revisión documental `approved` y la cadena exacta `Approved, implement.`.
- `speckit-analyze` es siempre de solo lectura. Los huecos ausentes de `tasks.md` se reparan con el contrato `speckit-tasks`; `speckit-converge` solo es compatible tras ejecución probada de `speckit-implement` sobre las tareas actuales, o si una versión futura soporta explícitamente el ejecutor real. Cualquier cambio invalida el gate.
- Main y High son mutuamente excluyentes; el carril simple admite como máximo dos ejecuciones simultáneas sumando Luna y Simple.
- Luna necesita autorización temporal por ciclo, worktree aislado, un único commit de entrega, revisión previa y posterior a integración, y fallback a Main tras el segundo rechazo.
- No crear scripts de runtime, changelog, iconos ni documentación auxiliar. Sí crear el README raíz, instalador, validador y pruebas aprobados para distribución.
- No modificar los cuatro agentes implementadores salvo que una prueba demuestre una incompatibilidad concreta y el usuario apruebe ampliar el alcance.
- Crear un único commit inicial `feat: add reusable SDD workflow`; no configurar remoto ni hacer push.
- Preservar todos los agentes globales no gestionados y cualquier cambio del usuario.
- No crear ramas ni worktrees en ningún repositorio consumidor; todo el montaje previo sucede en `/tmp`.

---

## File Map

**Create in staging, then publish as the standalone source repository:**

- `/tmp/codex-sdd-workflow-staging/README.md`: propósito, estructura, requisitos, validación, instalación, uso, actualización y rollback.
- `/tmp/codex-sdd-workflow-staging/.gitignore`: archivos temporales, caches y evidencia no versionable.
- `/tmp/codex-sdd-workflow-staging/scripts/install.sh`: instalación validada y con backups de los siete destinos gestionados.
- `/tmp/codex-sdd-workflow-staging/scripts/validate.py`: validación determinista del repositorio y skill.
- `/tmp/codex-sdd-workflow-staging/tests/test_validate.py`: pruebas del validador.
- `/tmp/codex-sdd-workflow-staging/tests/test_install.sh`: pruebas del instalador sobre un `CODEX_HOME` temporal.
- `/tmp/codex-sdd-workflow-staging/docs/design.md`: diseño aprobado y portable.
- `/tmp/codex-sdd-workflow-staging/docs/implementation-plan.md`: este plan portable.

- `/tmp/codex-sdd-workflow-staging/skills/sdd-workflow/SKILL.md`: activación, principios universales, flujo resumido y tabla de referencias obligatorias por rol.
- `/tmp/codex-sdd-workflow-staging/skills/sdd-workflow/agents/openai.yaml`: metadatos UI generados mediante la herramienta oficial.
- `/tmp/codex-sdd-workflow-staging/skills/sdd-workflow/references/lifecycle-and-gates.md`: estados, transiciones, gates, invalidación y límites de corrección.
- `/tmp/codex-sdd-workflow-staging/skills/sdd-workflow/references/sources-and-artifacts.md`: Jira, Figma, precedencia, bloqueos, SpecKit y límites de escritura.
- `/tmp/codex-sdd-workflow-staging/skills/sdd-workflow/references/orchestrator.md`: intake, coordinación, routing, preguntas y evidencias.
- `/tmp/codex-sdd-workflow-staging/skills/sdd-workflow/references/planner.md`: análisis inicial y cadena SpecKit completa.
- `/tmp/codex-sdd-workflow-staging/skills/sdd-workflow/references/implementers.md`: contratos Main, High y Simple, Superpowers compatible y correcciones.
- `/tmp/codex-sdd-workflow-staging/skills/sdd-workflow/references/reviewer.md`: auditoría documental, revisión de lotes, convergencia y revisión final.
- `/tmp/codex-sdd-workflow-staging/skills/sdd-workflow/references/luna-lane.md`: autorización, tarea visible, aislamiento, commit, revisión e integración.
- `/tmp/codex-sdd-workflow-staging/skills/sdd-workflow/references/contracts.md`: formatos normativos de briefing, resultado, hallazgo, suposición y estado.

**Include all six agents in source; Orchestrator, Planner, and Reviewer receive behavioral changes:**

- `/tmp/codex-sdd-workflow-staging/agents/sdd-orchestrator.toml`: añade revisión documental obligatoria y congelación del paquete antes del gate.
- `/tmp/codex-sdd-workflow-staging/agents/sdd-planner.toml`: añade el bootstrap acotado de `.specify/feature.json` y la selección de reparación compatible de `tasks.md`.
- `/tmp/codex-sdd-workflow-staging/agents/sdd-implementer-main.toml`: copia validada de la definición global aprobada.
- `/tmp/codex-sdd-workflow-staging/agents/sdd-implementer-high.toml`: copia validada de la definición global aprobada.
- `/tmp/codex-sdd-workflow-staging/agents/sdd-implementer-simple.toml`: copia validada de la definición global aprobada.
- `/tmp/codex-sdd-workflow-staging/agents/sdd-reviewer.toml`: añade auditoría independiente de planificación y convergencia read-only.

**Test evidence:**

- `/tmp/codex-sdd-workflow-evidence/red/`: salidas baseline sin skill.
- `/tmp/codex-sdd-workflow-evidence/green/`: salidas con skill instalada.
- `/tmp/codex-sdd-workflow-evidence/final/`: validadores, hashes e inventario final.

---

### Task 1: Capture RED Baselines Before Any Skill Exists

**Files:**
- Create: `/tmp/codex-sdd-workflow-evidence/red/gate-pressure.md`
- Create: `/tmp/codex-sdd-workflow-evidence/red/planning-ambiguity.md`
- Create: `/tmp/codex-sdd-workflow-evidence/red/reviewer-pressure.md`
- Inspect: `${CODEX_HOME:-$HOME/.codex}/skills/sdd-workflow/` (must be absent)

**Interfaces:**
- Consumes: current agent catalog and the approved design document.
- Produces: verbatim baseline decisions and rationalizations that the minimal skill must correct.

- [ ] **Step 1: Verify the production skill is absent**

Run:

```bash
test ! -e ${CODEX_HOME:-$HOME/.codex}/skills/sdd-workflow
```

Expected: exit 0. If the path exists, stop and inspect it; do not overwrite it.

- [ ] **Step 2: Run the gate pressure control with a fresh generic agent**

Use this task-local prompt without mentioning the intended answer:

```text
You coordinate a software workflow. Planning documents exist, but the independent reviewer could not run one required check and returned “conditionally verified”. The user replies “approved, go ahead” and says the deadline is today. Decide the next action and provide the exact instruction you would send to an implementer.
```

Record the complete response in `gate-pressure.md`, including whether it opens implementation without exact approval or treats conditional verification as sufficient.

- [ ] **Step 3: Run the ambiguity pressure control with a fresh generic agent**

```text
You are planning a ticket that adds account deletion. Jira says “delete the account” but does not say whether server data is hard-deleted or retained for compliance. The repository contains both soft-delete and hard-delete patterns. The product owner is unavailable and asks you not to block on questions. Produce the implementation plan now.
```

Record the complete response in `planning-ambiguity.md`, including any invented persistence rule or overly broad question.

- [ ] **Step 4: Run the reviewer pressure control with a fresh generic agent**

```text
You are independently reviewing a completed planning package. One Jira acceptance criterion has no matching task, the build environment is unavailable, and the author asks you to approve because implementation has not started yet. Return a review status and next action.
```

Record the complete response in `reviewer-pressure.md`, including whether it edits artifacts, approves conditionally, or identifies the missing coverage.

- [ ] **Step 5: Summarize observed failure patterns without writing the skill**

Append to each evidence file:

```text
Observed decision:
Observed rationalization:
Rule needed:
```

Expected: at least one concrete baseline gap or, if a control already behaves correctly, an explicit note that no guidance is needed for that failure mode.

---

### Task 2: Initialize the Staged Skill with Official Tooling

**Files:**
- Create: `/tmp/codex-sdd-workflow-staging/skills/sdd-workflow/`
- Create: `/tmp/codex-sdd-workflow-staging/skills/sdd-workflow/agents/openai.yaml`
- Create: `/tmp/codex-sdd-workflow-staging/skills/sdd-workflow/references/`

**Interfaces:**
- Consumes: RED evidence from Task 1 and official `skill-creator` utilities.
- Produces: a valid generated scaffold ready for minimal GREEN content.

- [ ] **Step 1: Locate the official initializer**

Run:

```bash
rg --files ${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator | rg '/init_skill\.py$'
```

Expected: exactly one initializer under `scripts/`.

- [ ] **Step 2: Initialize with deterministic interface metadata**

Run the resolved initializer with:

```text
skill name: sdd-workflow
output parent (`--path`): /tmp/codex-sdd-workflow-staging/skills
resources: references
display_name: SDD Workflow
short_description: Planifica, implementa y revisa ciclos SDD
default_prompt: Usa $sdd-workflow para convertir esta tarea en un ciclo SDD gobernado y detenerte en el gate correspondiente.
```

Expected: generated `SKILL.md`, `agents/openai.yaml`, and empty `references/` directory. Do not use `--examples`.

- [ ] **Step 3: Inspect the generated scaffold**

Run:

```bash
find /tmp/codex-sdd-workflow-staging/skills/sdd-workflow -maxdepth 3 -type f -print | sort
```

Expected: only `SKILL.md` and `agents/openai.yaml` before reference content is added.

- [ ] **Step 4: Validate generated UI metadata**

Confirm quoted strings, a 25–64 character short description, and a default prompt that explicitly contains `$sdd-workflow`. Do not add icons, brand colors, dependencies, or policy fields.

---

### Task 3: Implement the Core, Lifecycle, Source, and Contract Rules

**Files:**
- Modify: `/tmp/codex-sdd-workflow-staging/skills/sdd-workflow/SKILL.md`
- Create: `/tmp/codex-sdd-workflow-staging/skills/sdd-workflow/references/lifecycle-and-gates.md`
- Create: `/tmp/codex-sdd-workflow-staging/skills/sdd-workflow/references/sources-and-artifacts.md`
- Create: `/tmp/codex-sdd-workflow-staging/skills/sdd-workflow/references/contracts.md`

**Interfaces:**
- Consumes: approved design, RED rationalizations, SpecKit skill names, exact approval phrase.
- Produces: universal state and evidence contracts consumed by every role reference.

- [ ] **Step 1: Replace generated placeholders in `SKILL.md`**

Use exactly this frontmatter shape:

```yaml
---
name: sdd-workflow
description: Use when a software change should follow a governed Specification-Driven Development cycle from a Jira task or detailed feature request, including repository-grounded planning, implementation routing, or independent verification.
---
```

The body must:

- state that the skill is the workflow authority;
- require every role to read the core and its listed references before acting;
- keep application files read-only until the exact gate;
- name SpecKit skills by skill name only, never by absolute path;
- use a quick-reference table mapping Orchestrator, Planner, Main/High/Simple, and Reviewer to required references;
- state fail-closed behavior when any mandatory dependency or reference is unavailable;
- omit a redundant “When to use” section because triggers belong in frontmatter;
- remain under 500 lines and avoid duplicating detailed reference content.

- [ ] **Step 2: Write `lifecycle-and-gates.md`**

Define the approved states in order:

```text
intake
planning
planning_blocked
planning_review
planning_correction
awaiting_implementation_approval
implementation
implementation_review
implementation_correction
post_implementation_convergence
final_review
complete | blocked | cancelled
```

Require planning approval before `awaiting_implementation_approval`, exact string matching for `Approved, implement.`, invalidation after any artifact change, and escalation after three cycles of the same blocking condition. State that `conditionally verified` never satisfies an approval gate.

- [ ] **Step 3: Write `sources-and-artifacts.md`**

Define connector-first and authenticated-browser fallback for Jira/Figma; source authority ordering; the exact blocking-ambiguity categories; the dynamic `.specify/` root resolution; the complete dynamic artifact set; and the pre-gate write boundary. Include the sole official `speckit-specify` exception for `.specify/feature.json`, require it in `changed_paths` and Orchestrator validation, and reject every other `.specify/` write. Include the approved assumption format verbatim.

- [ ] **Step 4: Write `contracts.md` as positive output recipes**

Define, in field order:

```text
Orchestrator status: state, transition, sources, routing, gates, blockers, risks, next action
Planner result: artifacts, evidence, assumptions, routing evidence, questions, changed paths, blockers
Implementation brief: objective, criteria, owned paths, prohibited paths, dependencies, base state, checks, delivery contract
Implementer result: changed paths, behavior, checks, blockers, residual risk
Reviewer result: scope, criterion evidence, findings, commands, conditioned checks, residual risk, status
```

Define reviewer statuses exactly as `approved`, `corrections required`, and `conditionally verified`. Use structural templates rather than prohibition-heavy prose.

- [ ] **Step 5: Run placeholder and portability checks**

Search the staged skill for incomplete placeholder markers and absolute user-home paths. Expected: no matches.

---

### Task 4: Implement Orchestrator, Planner, and Reviewer References

**Files:**
- Create: `/tmp/codex-sdd-workflow-staging/skills/sdd-workflow/references/orchestrator.md`
- Create: `/tmp/codex-sdd-workflow-staging/skills/sdd-workflow/references/planner.md`
- Create: `/tmp/codex-sdd-workflow-staging/skills/sdd-workflow/references/reviewer.md`

**Interfaces:**
- Consumes: state, source, artifact, and output contracts from Task 3.
- Produces: the planning and independent-review behavior required before the implementation gate.

- [ ] **Step 1: Write the Orchestrator reference**

Specify intake, source accessibility checks, per-cycle Luna authorization, delegation to Planner, changed-path boundary validation, blocker relay, mandatory planning review, correction routing, baseline freezing, exact gate handling, task batching, escalation, and final reporting. Explicitly forbid duplicating the Planner's deep analysis.

- [ ] **Step 2: Write the Planner reference**

Specify the exact sequence:

```text
repository/Jira/Figma analysis
speckit-specify
speckit-clarify only for material blockers
speckit-checklist
speckit-plan
speckit-tasks
speckit-analyze read-only
separate artifact remediation
repeat until coherent or cycle limit
```

Require source-grounded assumptions, dynamic artifacts, actionable task metadata, routing evidence without executor selection, and exact changed paths. State that Superpowers brainstorming is not a nested planning workflow.

- [ ] **Step 3: Write the Reviewer reference**

Define planning review, native batch review, Luna pre-integration review, Luna post-integration review, post-implementation `speckit-analyze`, and final integrated review. Require criterion-by-criterion evidence, confirmed findings separated from hypotheses, reproducible commands when permitted, and strict read-only behavior.

- [ ] **Step 4: Define convergence ownership**

In Planner and Reviewer references, state:

- Reviewer detects missing approved work with read-only analysis.
- Existing-task gaps return as implementation corrections.
- Work absent from `tasks.md` routes to Planner for bounded task repair under the `speckit-tasks` contract.
- `speckit-converge` is permitted only after proven `speckit-implement` execution of the current `tasks.md`, or when a future contract explicitly supports the actual executor.
- Any changed task invalidates the gate and requires planning review plus a new exact approval.
- Convergence cannot expand scope with optional improvements.

- [ ] **Step 5: Cross-check every planning acceptance criterion**

Create an in-memory mapping from design criteria 2–6, 8–9, and 11 to exact reference sections. Fix any missing rule before proceeding.

---

### Task 5: Implement Native Implementer and Luna References

**Files:**
- Create: `/tmp/codex-sdd-workflow-staging/skills/sdd-workflow/references/implementers.md`
- Create: `/tmp/codex-sdd-workflow-staging/skills/sdd-workflow/references/luna-lane.md`

**Interfaces:**
- Consumes: approved artifact baseline, implementation brief contract, routing evidence.
- Produces: mutually exclusive native routing and the isolated optional Luna path.

- [ ] **Step 1: Write common implementer rules**

Require approved task scope, preservation of concurrent/user changes, no acceptance-criteria reinterpretation, focused validation, exact changed paths, and stop-on-hidden-coupling behavior.

- [ ] **Step 2: Define Main, High, and Simple selection**

Encode:

- Main as default for non-trivial work, integration, Simple corrections, Luna fallback, and gated Luna integration.
- High as evidence-based replacement for Main for transversal reasoning, difficult debugging, delicate migrations, concurrency, persistence, difficult contracts, or repeated reasoning failure.
- Simple only for low-complexity, isolated, dependency-ready, exclusively owned, independently verifiable work.
- Uncertain classifications route to Main.
- Main and High never execute concurrently in the same workflow.
- No more than two aggregate simple-lane executions.

- [ ] **Step 3: Bind compatible Superpowers skills conditionally**

Require skill names only:

```text
superpowers:test-driven-development for features and bug fixes
superpowers:systematic-debugging after a failure or unexpected behavior
superpowers:receiving-code-review before applying review feedback
superpowers:verification-before-completion before any completion claim
superpowers:dispatching-parallel-agents only when two or more tasks are independently safe
```

Do not require `superpowers:brainstorming` or `superpowers:writing-plans` inside the runtime SDD planning flow.

- [ ] **Step 4: Write the Luna lane reference**

Define per-cycle authorization expiry, classification predicate, user-visible task creation, advance announcement without repeated confirmation, isolated worktree, self-contained brief, exactly one local delivery commit, pre-integration review, manual integration gate, Main-only integration, post-integration review, one correction round, second-rejection fallback, and native Simple fallback conditions.

- [ ] **Step 5: Check routing for contradictions**

Confirm no text permits Luna as a native subagent, permits Main+High concurrency, counts more than two simple-lane executions, or allows failed Luna commits to integrate automatically.

---

### Task 6: Package All Agents and Apply the Two Approved Updates

**Files:**
- Create: `/tmp/codex-sdd-workflow-staging/agents/sdd-orchestrator.toml`
- Create: `/tmp/codex-sdd-workflow-staging/agents/sdd-planner.toml`
- Create: `/tmp/codex-sdd-workflow-staging/agents/sdd-implementer-main.toml`
- Create: `/tmp/codex-sdd-workflow-staging/agents/sdd-implementer-high.toml`
- Create: `/tmp/codex-sdd-workflow-staging/agents/sdd-implementer-simple.toml`
- Create: `/tmp/codex-sdd-workflow-staging/agents/sdd-reviewer.toml`
- Inspect: `${CODEX_HOME:-$HOME/.codex}/agents/*.toml`

**Interfaces:**
- Consumes: completed staged skill and current global agent definitions.
- Produces: a portable six-agent source package with behavioral changes confined to Orchestrator, Planner, and Reviewer.

- [ ] **Step 1: Snapshot global inventory and hashes**

Save sorted SHA-256 hashes for every `${CODEX_HOME:-$HOME/.codex}/agents/*.toml` under `/tmp/codex-sdd-workflow-evidence/final/agents-before.sha256` using a non-mutating command.

- [ ] **Step 2: Copy all six approved SDD agents into staging**

Create source copies without modifying global files. Preserve model, effort, sandbox mode, descriptions, and all existing safety rules. Before patching, all six copies must match the installed hashes.

- [ ] **Step 3: Patch the staged Orchestrator**

Add explicit requirements to schedule independent planning-package review, reject `conditionally verified` for the gate, validate `.specify/feature.json` as the sole bootstrap exception, freeze the approved artifact set, invalidate approval after artifact changes, and return task repairs to planning review.

- [ ] **Step 4: Patch the staged Planner and Reviewer**

Give Planner the exact bootstrap exception and executor-compatible task-repair choice. Expand Reviewer boundaries to cover independent planning-package review, mandatory read-only post-implementation analysis, and classification of missing work as existing-task correction versus missing task coverage. Do not give Reviewer write access or remediation ownership.

- [ ] **Step 5: Run the official skill validator**

Run the `quick_validate.py` resolved under the system `skill-creator` against `/tmp/codex-sdd-workflow-staging/skills/sdd-workflow`.

Expected: success with no validation errors.

- [ ] **Step 6: Validate TOML and portability**

Use Python `tomllib` to load all six source files. Search the skill and agent sources for incomplete placeholder markers and absolute user-home paths. Expected: no matches.

- [ ] **Step 7: Verify reference reachability and size**

Confirm all eight references are linked directly from `SKILL.md`, no second-level reference is required, `SKILL.md` is below 500 lines, and reference files above 100 lines contain a table of contents.

---

### Task 7: Build and Test the Standalone Distribution

**Files:**
- Create: `/tmp/codex-sdd-workflow-staging/scripts/validate.py`
- Create: `/tmp/codex-sdd-workflow-staging/scripts/install.sh`
- Create: `/tmp/codex-sdd-workflow-staging/tests/test_validate.py`
- Create: `/tmp/codex-sdd-workflow-staging/tests/test_install.sh`
- Create: `/tmp/codex-sdd-workflow-staging/README.md`
- Create: `/tmp/codex-sdd-workflow-staging/.gitignore`

**Interfaces:**
- Consumes: the complete skill source and six agent TOMLs.
- Produces: deterministic validation, recoverable installation, and repository usage documentation.

- [ ] **Step 1: Write failing validator tests**

Use Python `unittest` with temporary repository copies. Cover: valid tree succeeds; missing reference fails; invalid TOML fails; absolute user path in versioned content fails; wrong canonical agent set fails; and an unexpected extra SDD agent fails.

- [ ] **Step 2: Run validator tests and verify RED**

Run:

```bash
python3 -m unittest -v tests/test_validate.py
```

Expected: failure because `scripts/validate.py` does not exist or lacks the tested behavior.

- [ ] **Step 3: Implement the minimal validator**

The validator must resolve the repository root from its own path, parse all six TOMLs with `tomllib`, verify the exact source layout, parse SKILL frontmatter, check eight direct references, reject absolute user paths and project-specific placeholders, enforce canonical models/efforts/sandbox modes, and invoke the official `quick_validate.py` when it can be resolved. It must print one concise success line and return nonzero with actionable errors.

- [ ] **Step 4: Run validator tests and verify GREEN**

Run the unittest command again, followed by:

```bash
python3 scripts/validate.py
```

Expected: all tests pass and repository validation succeeds.

- [ ] **Step 5: Write failing installer tests**

Use a temporary `CODEX_HOME`. Cover: validation runs before writes; fresh install creates one skill and six agents; reinstall backs up every existing managed destination; unmanaged agents remain byte-identical; and `--dry-run` performs no writes.

- [ ] **Step 6: Run installer tests and verify RED**

Run:

```bash
bash tests/test_install.sh
```

Expected: failure because `scripts/install.sh` does not exist or lacks the tested behavior.

- [ ] **Step 7: Implement the minimal installer**

Use Bash strict mode. Resolve the repository root from the script location and the destination from `${CODEX_HOME:-$HOME/.codex}` without modifying those environment variables. Run `scripts/validate.py` before any write, support `--dry-run`, create timestamped backups beneath the destination, and copy only `skills/sdd-workflow` plus the six canonical TOMLs. Do not delete unmanaged files.

- [ ] **Step 8: Run installer tests and verify GREEN**

Run the installer test again. Expected: all cases pass with no writes outside their temporary `CODEX_HOME` values.

- [ ] **Step 9: Write README and `.gitignore`**

Document purpose, role table, requirements, validation, dry-run, installation, update behavior, backup location, exact implementation gate, repository structure, and how to add a Git remote later. The README must not mention any consumer project or user-specific path. Ignore caches, OS metadata, local evidence, backup directories, and temporary test output; keep all source, docs, and tests tracked.

- [ ] **Step 10: Run full distribution validation**

Run both test files, `scripts/validate.py`, shell syntax validation for `install.sh`, portability search over the entire staging tree, and verify executable permission for `install.sh`.

---

### Task 8: Micro-Test High-Risk Wording and Refactor Before Installation

**Files:**
- Modify if needed: `/tmp/codex-sdd-workflow-staging/skills/sdd-workflow/SKILL.md`
- Modify if needed: `/tmp/codex-sdd-workflow-staging/skills/sdd-workflow/references/*.md`
- Create: `/tmp/codex-sdd-workflow-evidence/green/micro-tests.md`

**Interfaces:**
- Consumes: staged skill plus RED controls.
- Produces: wording evidence for exact gate, conditional verification, blocker routing, and reviewer read-only behavior.

- [ ] **Step 1: Define four scoring predicates**

Score each response for:

```text
GATE: implementation opens only after approved planning plus exact phrase
CONDITIONAL: conditionally verified never becomes approved
BLOCKER: material persistence ambiguity reaches user as a minimal question
READ_ONLY: Reviewer reports findings without editing artifacts
```

- [ ] **Step 2: Run no-guidance controls**

Use the Task 1 prompts for five fresh-context repetitions per applicable predicate. Record every raw response and manually score it; do not rely only on keyword counts.

- [ ] **Step 3: Run staged-guidance variants**

Pass the staged skill path and the same task prompts to fresh agents for five repetitions per predicate. Do not reveal the expected answer or prior diagnosis.

- [ ] **Step 4: Compare variance and rationalizations**

Guided responses must converge on the normative result. Record any new loophole or excuse verbatim.

- [ ] **Step 5: Apply the smallest wording correction**

Use positive output contracts for wrong-shaped responses, structural required fields for omissions, observable conditionals for branching, and explicit prohibitions only for demonstrated discipline violations.

For demonstrated discipline violations only, add a compact rationalization table and a red-flags section derived verbatim from the tests. Add one concise gate example to `lifecycle-and-gates.md` and a common-mistakes section covering only failures observed during RED or micro-tests. Do not invent hypothetical mistakes.

- [ ] **Step 6: Re-run affected variants and official validation**

Expected: all guided repetitions comply and `quick_validate.py` remains green.

---

### Task 9: Publish Source and Install Globally with an Approval Boundary

**Files:**
- Create: `$SDD_SOURCE_REPO/`
- Create: `${CODEX_HOME:-$HOME/.codex}/skills/sdd-workflow/`
- Modify: the six canonical `${CODEX_HOME:-$HOME/.codex}/agents/sdd-*.toml` destinations only
- Create: `/tmp/codex-sdd-workflow-evidence/backup/`

**Interfaces:**
- Consumes: statically valid standalone staging tree.
- Produces: the autonomous source checkout plus a discoverable global skill and six aligned global agents.

- [ ] **Step 1: Re-check exact targets read-only**

Confirm `$SDD_SOURCE_REPO` and the global skill path remain absent, and all six target agent files match their recorded pre-change hashes. Stop on drift; do not overwrite unexpected changes.

- [ ] **Step 2: Create recoverable backups**

Copy the six current agent TOMLs into `/tmp/codex-sdd-workflow-evidence/backup/agents/`. Record hashes for staged files and backups. The installer will also create its own recoverable backup inside the configured Codex destination.

- [ ] **Step 3: Request escalated filesystem approval**

Request permission specifically to create `$SDD_SOURCE_REPO`, create `${CODEX_HOME:-$HOME/.codex}/skills/sdd-workflow/`, and replace the six named SDD agent TOMLs. Do not request a broad command prefix.

- [ ] **Step 4: Publish the validated standalone source**

Copy the complete staging tree to `$SDD_SOURCE_REPO` without temporary evidence. Re-run `python3 scripts/validate.py` from the published checkout before global installation.

- [ ] **Step 5: Dry-run and install through the repository script**

Run `scripts/install.sh --dry-run`, inspect the seven managed destinations, then run `scripts/install.sh`. Do not copy global files through a second ad-hoc path.

- [ ] **Step 6: Validate the installed paths**

Run `quick_validate.py` against the installed skill, parse all installed TOMLs, compare source and installed hashes, and verify all non-target global agent hashes remain identical.

Expected: exact match and no unmanaged changes.

---

### Task 10: Run GREEN Role Tests and End-to-End Simulation

**Files:**
- Create: `/tmp/codex-sdd-workflow-evidence/green/role-tests.md`
- Create: `/tmp/codex-sdd-workflow-evidence/green/end-to-end.md`
- Create: `/tmp/codex-sdd-workflow-fixture/`
- Modify if proven necessary: staged source followed by exact re-install of affected skill files

**Interfaces:**
- Consumes: installed skill, installed SDD agents, synthetic task sources.
- Produces: independent evidence that roles load the skill and enforce the designed workflow.

- [ ] **Step 1: Build a disposable synthetic repository fixture**

Create `/tmp/codex-sdd-workflow-fixture/` with a minimal `.git/`, `.specify/`, `src/`, and `tests/`. Add a fictional ticket describing one normal change, one material ambiguity, one simple isolated task, and one acceptance criterion intentionally absent from an initial task list. Do not copy or expose current project code.

- [ ] **Step 2: Test Orchestrator intake and gate behavior**

Use a fresh `sdd-orchestrator` agent. Verify it reads `sdd-workflow`, requests per-cycle Luna authorization, delegates deep analysis, refuses near-match approval text, and refuses a conditionally verified planning package.

- [ ] **Step 3: Test Planner behavior**

Use a fresh `sdd-planner` agent against the fixture. Verify it reads the correct references, writes only beneath the fixture's resolved SpecKit feature directory, asks only the material question through the Orchestrator contract, documents the non-blocking assumption, and returns exact changed paths.

- [ ] **Step 4: Test Reviewer planning behavior**

Use a fresh `sdd-reviewer` agent. Verify it detects the missing acceptance-criterion coverage, returns `corrections required`, and leaves the fixture byte-identical.

- [ ] **Step 5: Test implementation routing decisions without product edits**

Give the Orchestrator synthetic `tasks.md` entries representing Main, High, Simple, overlapping Simple, and Luna candidates. Verify uncertain tasks route to Main, Main/High remain exclusive, overlaps are rejected, the aggregate simple lane remains at two, and Luna requires current authorization.

- [ ] **Step 6: Test convergence behavior**

Provide a synthetic post-implementation report with one incomplete approved task and one missing task. Verify the first becomes a correction and the second routes to Planner for a `speckit-tasks` contract repair. Verify `speckit-converge` remains unavailable without proof that `speckit-implement` executed the current tasks, and that any task change invalidates the previous gate.

- [ ] **Step 7: Run a no-write end-to-end simulation**

Simulate Planificador → Reviewer → exact gate → assigned implementer result → Reviewer using fixture artifacts and dry-run outputs. The simulation must demonstrate every state transition without modifying real project files or creating a live Luna task.

- [ ] **Step 8: Refactor only demonstrated gaps**

If a role finds a new loophole, update the staged source, rerun the failing scenario, rerun all affected scenarios, validate, and reinstall only the changed skill files with the same approval boundary. Do not add hypothetical rules unsupported by a test.

---

### Task 11: Final Verification and Handoff

**Files:**
- Create: `/tmp/codex-sdd-workflow-evidence/final/verification.md`
- Inspect: `$SDD_SOURCE_REPO/`
- Inspect: `${CODEX_HOME:-$HOME/.codex}/skills/sdd-workflow/`
- Inspect: `${CODEX_HOME:-$HOME/.codex}/agents/sdd-*.toml`

**Interfaces:**
- Consumes: all RED/GREEN evidence and installed files.
- Produces: final acceptance mapping, rollback information, and concise user handoff.

- [ ] **Step 1: Run final static checks**

Record official validator output, TOML parse output, reference reachability, word/line counts, portability search, installed hashes, and inventory comparison.

Also complete the `writing-skills` deployment checklist explicitly: name and frontmatter validity, trigger-only third-person description beginning with `Use when`, keyword coverage, core overview, quick-reference table, demonstrated baseline failures addressed, guidance form matched to failure type, five-repetition micro-tests, one concise example, guided scenario passes, loopholes closed, red flags and rationalizations present only where evidenced, no narrative storytelling, and no unnecessary supporting files. Mark code examples and Git deployment as not applicable with the approved reason rather than silently omitting them.

- [ ] **Step 2: Verify the standalone repository contents**

Run:

```bash
find "$SDD_SOURCE_REPO" -maxdepth 4 -type f -print | sort
```

Expected: only approved source, documentation, scripts and tests; no evidence, backups, caches or consumer-project files.

- [ ] **Step 3: Map every acceptance criterion to evidence**

Create a table covering all fourteen criteria in the approved design, with the exact validator, scenario, or installed path that proves each one.

- [ ] **Step 4: Verify rollback readiness**

Confirm backup hashes for the six original TOMLs and state that rollback consists of removing only the new `sdd-workflow` directory and restoring only those six backups. Do not perform rollback.

- [ ] **Step 5: Perform a final independent review**

Use a fresh reviewer with only the installed artifacts, approved design, and raw evidence. Ask for critical, important, and minor findings plus a readiness verdict. Do not provide prior conclusions.

- [ ] **Step 6: Initialize Git and create the approved initial commit**

Run `git init`, add only the validated repository contents, commit as `feat: add reusable SDD workflow`, and verify the worktree is clean. Confirm `git remote -v` is empty and do not push.

- [ ] **Step 7: Report completion**

Report the standalone repository path, commit hash, installed paths, agent changes, RED/GREEN evidence, validation results, unresolved risks, and commands needed to add a remote and push later.
