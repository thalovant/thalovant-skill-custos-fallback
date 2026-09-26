# Keeping CI useful and affordable

- A new run cancels an older verification run for the same PR or branch. Release jobs are separate.
- Pip and uv downloads are cached by OS, architecture, Python, dependency files, and workflow configuration. Every run still installs dependencies; no virtual environment or test result is cached.
- Runtime and lint jobs keep their existing Python versions. Prose-only edits skip dependency installation inside those jobs, so required check names still report a result. Missing history, manual runs, and any other changed file run the checks in full.
- Package jobs still run for prose changes, since the README is part of package metadata. Easter Eggs keeps its combined package/test matrix on every change.
- Test jobs have finite timeouts. Diagnostic artifacts are retained for seven days where uploaded.

To request all checks, use a workflow’s manual trigger when available, or include a code, test, resource, or workflow change. Caches accelerate downloads; they do not pin dependency versions or prevent fresh resolution.
