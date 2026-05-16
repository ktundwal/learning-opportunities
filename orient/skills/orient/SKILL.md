---
name: orient
description: Generates a repo-specific orientation.md resource for the learning-opportunities skill. Invoke directly when the user asks for repo orientation; do not trigger automatically.
argument-hint: "[showboat]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash, Write
---

# Create Orientation

## Purpose

Generate a repo-specific `orientation.md` file inside the `learning-opportunities` skill's `resources/` directory. This file is used by that skill when invoked with the `orient` argument to run a structured learning exercise for someone new to the codebase.

---

## Step 1: Find where to write orientation.md

Always write to the **project level**, regardless of where the `learning-opportunities` skill is installed.

When running in Codex, write to:

```
.codex/skills/learning-opportunities/resources/orientation.md
```

When running in Claude Code, write to:

```
.claude/skills/learning-opportunities/resources/orientation.md
```

When running in GitHub Copilot CLI, write to:

```
.github/copilot-orientation.md
```

(Copilot CLI plugins live under `~/.copilot/installed-plugins/` and don't expose a stable project-level skill resource path, so we use a conventional repo-level file instead. The `learning-opportunities` skill will look for this file when invoked with the `orient` argument under Copilot CLI.)

All paths are relative to the current working directory.

If the target directory does not exist, create it. If it already exists, leave it and any files inside it untouched — only write `orientation.md`.

This keeps orientation files co-located with the repo they describe — they can be committed to version control, shared with teammates, and never collide across projects.

---

## Argument check

You were invoked with arguments: `$ARGUMENTS`

If the argument is `showboat`, skip to the **Showboat Path** section below.

Otherwise, continue with Steps 2–5 (the default path).

---

## Step 2: Detect the repo's primary language(s)

Check for these manifest/config files at the project root and note all that exist. A repo may use multiple languages.

| Language   | Signal files                                              |
|:-----------|:----------------------------------------------------------|
| Python     | `pyproject.toml`, `setup.py`, `setup.cfg`, `Pipfile`, `requirements.txt` |
| JavaScript | `package.json` (no `tsconfig.json`)                      |
| TypeScript | `package.json` + `tsconfig.json`                         |
| R          | `DESCRIPTION`, `NAMESPACE`, any `*.Rproj`                |
| Ruby       | `Gemfile`, any `*.gemspec`                                |
| Go         | `go.mod`                                                  |
| Rust       | `Cargo.toml`                                              |
| C/C++      | `CMakeLists.txt`, `configure.ac`, root-level `Makefile`  |
| Java/Kotlin| `pom.xml`, `build.gradle`, `build.gradle.kts`            |
| C#         | any `*.csproj`, `*.sln`, `*.slnx`, `Directory.Packages.props`, `global.json` |

Record all detected languages. For each detected language, read its primary manifest file in full — it contains declared purpose, dependencies, entry points, and scripts/commands that are essential for orientation.

---

## Step 2.5: Inherit from existing onboarding docs

Before re-deriving anything in Step 3, check whether the repo already invests in agent or contributor onboarding. If any of the following exist, **read them in full first** and treat them as the primary source of truth for purpose, architecture, conventions, and gotchas. The Step 3 exploration then becomes a sanity check and gap-fill rather than a from-scratch discovery.

Files to check (in priority order):

1. `.github/copilot-instructions.md` — repo-scoped Copilot guidance
2. `AGENTS.md`, `CLAUDE.md`, `.cursorrules` — agent instruction files at the repo root
3. `CONTRIBUTING.md` — human contributor onboarding
4. `docs/`, `Docs/`, or `documentation/` directory — read the index (`README.md`, `index.md`, or `_toc.md`) plus any file that looks like an "architecture", "getting started", "overview", or "onboarding" doc
5. Any `*.md` at the repo root that isn't `README`, `CHANGELOG`, `LICENSE`, `SECURITY`, or `CODE_OF_CONDUCT`

When generating `orientation.md` in Step 4, **cite these inherited sources** in the "Sources consulted" section and **defer to them** when their content conflicts with what you'd otherwise infer from code. The goal is to amplify existing onboarding investment, not to duplicate or contradict it.

If none of these exist, skip this step and proceed to Step 3.

---

## Step 3: Explore the repo

Use the following sequence, drawn from research on expert program comprehension strategies. Experts read **strategically and selectively**, not exhaustively. The goal is a mental model of structure, not line-by-line understanding.

### 3a. README and top-level docs
Read `README.md`, `README.rst`, or `README` at the project root. Also check for a `docs/` directory — read its index or table of contents if present. This gives the stated purpose and intended audience.

*Source: Spinellis, "Code Reading: The Open Source Perspective" (2003) — start with the build system and README before reading any application code.*

### 3b. Directory tree
Get the top-level structure (depth 3, excluding build/VCS/dependency caches). Pick the variant that matches the shell you're in.

**bash / zsh (macOS, Linux, Git Bash):**
```sh
find . -maxdepth 3 \
  -not -path '*/.git/*' \
  -not -path '*/node_modules/*' \
  -not -path '*/__pycache__/*' \
  -not -path '*/.venv/*' \
  -not -path '*/bin/*' \
  -not -path '*/obj/*' \
  -not -path '*/out/*' \
  -not -path '*/dist/*' \
  -not -path '*/target/*' \
  -not -path '*/packages/*' \
  -not -path '*/.vs/*' \
  -not -path '*/TestResults/*'
```

**PowerShell (Windows pwsh, also works on macOS/Linux pwsh):**
```powershell
$exclude = @('.git','node_modules','__pycache__','.venv','bin','obj','out','dist','target','packages','.vs','TestResults')
Get-ChildItem -Recurse -Depth 3 -Force |
  Where-Object { $p = $_.FullName; -not ($exclude | Where-Object { $p -match "[\\/]$_[\\/]?" }) } |
  Select-Object -ExpandProperty FullName
```

Read the directory tree as an architectural table of contents — naming conventions (`src/`, `lib/`, `tests/`, `cmd/`, `pkg/`) reveal intent before any code is read.

*Source: Spinellis (2003) — "directory tree as table of contents."*

### 3c. Entry points
Identify and read the main entry points based on detected language:

- **Python**: `__main__.py`, `cli.py`, `main.py`, or the `[tool.poetry.scripts]` / `[project.scripts]` section of `pyproject.toml`
- **JavaScript/TypeScript**: `main` field in `package.json`, `index.js`, `src/index.ts`
- **Go**: files in `cmd/*/main.go` or root `main.go`
- **Rust**: `src/main.rs` or `src/lib.rs`
- **R**: `R/` directory, the `DESCRIPTION` file's `Imports`
- **Ruby**: files in `bin/`, `lib/<gem-name>.rb`
- **C/C++**: `main.c`, `main.cpp`, or the primary target in `CMakeLists.txt`
- **C#/.NET**: `Program.cs` (top-level statements or `Main`); for ASP.NET Core, also read the `WebApplication.CreateBuilder` / `IHostBuilder` configuration and any `Startup.cs`. If multiple projects exist, locate the executable projects (`<OutputType>Exe</OutputType>` in `*.csproj`, or projects referenced as startup in `*.sln` / `*.slnx`) and read their `Program.cs` files. Also skim `Directory.Packages.props` (central package management) and `global.json` (SDK pin) for stack signals.
- **Java/Kotlin**: classes with a `public static void main` / `fun main`; for Spring Boot, the `@SpringBootApplication`-annotated class

*Source: Hermans, "The Programmer's Brain" (2021, Manning) — follow the entry point and call graph one level at a time.*

### 3d. Test files
Read 2–3 test files, prioritizing integration or end-to-end tests over unit tests. Tests are executable specifications — reading test names and assertions is one of the fastest ways to understand what a module is meant to do.

*Source: Storey et al., "How Software Developers Use Tools, Cognitive Strategies, and Representations to Navigate Code" (IEEE TSE, 2006) — use the test suite as a specification.*

### 3e. Core modules
Identify the 5–8 most important source files based on what you have learned. Read their top-level structure (class/function names, imports, docstrings) without necessarily reading every implementation in full.

### 3f. Recent git history (if git is available)
Run `git log --oneline -20` to see recent activity. Then identify the most-edited files. Pick the variant that matches the shell you're in.

**bash / zsh:**
```sh
git log --format='' --name-only | grep -v '^$' | sort | uniq -c | sort -rn | head -10
```

**PowerShell:**
```powershell
git log --format='' --name-only |
  Where-Object { $_ -ne '' } |
  Group-Object |
  Sort-Object Count -Descending |
  Select-Object -First 10 Count, Name
```

High-churn files are usually the core of the system.

*Source: Spolsky practitioner writing — "find the biggest, most-edited file; read git history to understand why code is the way it is."*

---

## Step 4: Synthesize and write orientation.md

Write the file to the path identified in Step 1. Use this exact structure:

```markdown
# Repo Orientation: [repo name]

> Generated by orient. Re-run to update.

## One-line purpose
[Single sentence: what this repo does and why it exists. Written for someone with no prior context.]

## Primary language(s)
[List languages detected, with the dominant one first.]

## Pipeline / workflow stages
[Ordered list of the main stages data or requests flow through. One line each. If the repo has no pipeline, describe the main modules and their relationships instead.]

## Key files
[6–10 entries in this format:]
- `path/to/file.py` — [what it does] | [why a new developer should read it]

## Core concepts
[3–5 domain or architectural concepts essential to working in this codebase. For each:]
**[Concept name]**: [Plain-English definition. Where in the code it lives.]

## Prerequisites & secrets
[Anything required to build, run, or test this repo locally that isn't installed by a package manager. Be specific. Examples:
- Required environment variables (look for `Environment.GetEnvironmentVariable`, `process.env.`, `os.environ`, `os.getenv`, `dotenv`/`.env.example` files, and the README's "Setup", "Getting Started", or "Environment" sections)
- Required SDKs/toolchains beyond the language manifest (e.g., specific .NET SDK pinned in `global.json`, Node version in `.nvmrc`, Python version in `.python-version`)
- Required cloud auth (e.g., a logged-in `az` / `gh` / `gcloud` CLI session, a managed-identity context, a service-principal credential file)
- Required local services (databases, message brokers, emulators)
- Platform-specific notes (Windows-only scripts, WSL requirements, native dependencies)

If everything needed is fully captured by the package manifest and there are no extra prerequisites, write "None beyond `<manifest file>`." Do NOT pad this section.]

## Common gotchas
[2–3 things that commonly trip up new developers. Be specific — reference actual file paths or function names.]

## Suggested exercise sequence
[EXACTLY 2 exercises. These are orientation exercises — their job is to build a high-level mental model of the repo, not to drill implementation details.

Orientation exercises follow this pattern: direct the learner to read one specific, short artifact first, then ask them to synthesize or explain what they just read. Never ask them to predict something they couldn't know without reading — the goal is comprehension and synthesis, not prior knowledge.

Good orientation exercises:
- "Open README.md and read the Features section. Then close it and explain to a non-developer what this tool produces and why someone would use it."
- "Open `models.py`. Find the dataclass that represents everything the pipeline produces for one audio file. What fields does it have, and what does that tell you about the pipeline's stages?"
- "Open `config/default.yaml` and skim it. What are the two or three settings you'd most likely need to change for a new project, and why?"

Bad orientation exercises (save these for later sessions):
- "Without opening any files, predict the pipeline stages" — learner has no basis for this
- Predicting specific function outputs, column names, or algorithmic behavior
- Tracing through individual method implementations
- Debugging specific logic (e.g. merge suffix behavior, metadata propagation)

For each exercise, specify: the exact file to open, what to read, and what synthesis question to answer after reading.]

## Sources consulted
[List the files and paths you actually read while generating this file.]
```

Keep each section concise. This is a teaching scaffold, not documentation. Prioritize clarity over completeness.

---

## Step 5: Confirm to the user

> **Note for skill maintainers**: Academic and practitioner sources for the exploration methodology in Steps 3a–3f are documented in [resources/orient-bibliography.md](resources/orient-bibliography.md). Load that file only if you need to update or cite sources — it is not needed during normal skill execution.

Tell the user:
- Where the file was written
- How many key files and concepts were identified
- How to use it: invoke `learning-opportunities` with the `orient` argument
- That they can re-run orient at any time to regenerate it as the codebase evolves

---

## Showboat Path

This path replaces Steps 2–5 when the argument is `showboat`. It produces `orientation.md` at the same location identified in Step 1, but uses the `showboat` CLI tool (via `uvx`) to build a detailed, linear code walkthrough.

### Showboat Step 1: Check for uv

Run `command -v uv` to verify that `uv` is installed.

If `uv` is not found, tell the user:

> `uv` is required for showboat mode but was not found on your PATH.
> Install it from: https://docs.astral.sh/uv/getting-started/installation/

Then stop — do not proceed further.

### Showboat Step 2: Read the repo and plan the document

Read the repo to understand its structure, purpose, and key code paths. Then plan a linear walkthrough document with:

- A title and table of contents
- Commentary sections that explain the codebase narratively, in reading order
- A Code Listings appendix containing the actual code snippets referenced by commentary
- A suggested exercise sequence (same criteria as Step 4's exercise requirements — exactly 2 orientation exercises)

Plan all section headings, code snippets, and sequential listing numbers **upfront before writing anything**. Each listing gets a sequential number (Listing 1, Listing 2, etc.) and a short description.

### Showboat Step 3: Learn the showboat tool

Run `uvx showboat --help` to learn the available commands and their syntax.

### Showboat Step 4: Build orientation.md using showboat commands

Use the showboat CLI to build the file. The output path is the same `orientation.md` from Step 1. Execute commands in this order:

#### 4a. Initialize the document

```
uvx showboat init <path-to-orientation.md> "<Title>"
```

Then add a table of contents via `uvx showboat note`.

#### 4b. Write all commentary sections

Add each commentary section using `uvx showboat note`. Follow these rules for note content:

- **No fenced code blocks** inside notes — use inline backtick code (`` `like_this` ``) instead
- Reference code listings with inline links: `*([Listing N: description](#listing-N))*`
- Write narratively — explain *why* the code is structured this way, not just *what* it does

#### 4c. Write the Code Listings appendix

For each listing planned in Showboat Step 2:

1. Add an anchor note: `uvx showboat note` with a heading like `### Listing N: description` and an HTML anchor `<a id="listing-N"></a>`
2. Add the code via `uvx showboat exec` to capture the actual file content (e.g., using `cat` or `sed` to extract the relevant lines)

#### 4d. Append suggested exercise sequence

Add a final section via `uvx showboat note` with exactly 2 orientation exercises. These follow the same criteria as the default path's Step 4:

- Direct the learner to read one specific, short artifact first
- Then ask them to synthesize or explain what they just read
- Never ask them to predict something they couldn't know without reading
- Specify: the exact file to open, what to read, and what synthesis question to answer

#### 4e. Verify the document

Run:

```
uvx showboat verify <path-to-orientation.md>
```

Fix any issues reported before proceeding.

### Showboat Step 5: Confirm to the user

Tell the user:

- Where the file was written
- That it was generated using showboat mode (a linear code walkthrough)
- How to use it: `/learning-opportunities orient`
- That they can re-run `/orient showboat` at any time to regenerate it
