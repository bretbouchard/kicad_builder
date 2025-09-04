#!/usr/bin/env bash
# Installs the local precommit_check.sh as .git/hooks/pre-commit (opt-in)
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
HOOK_DIR=$ROOT/.git/hooks
FALLBACK_DIR=$ROOT/.githooks
SRC=$ROOT/tools/scripts/precommit_check.sh
if [ ! -f "$SRC" ]; then echo "precommit_check.sh not found"; exit 1; fi
if [ -d "$ROOT/.git" ]; then
	mkdir -p "$HOOK_DIR"
	HOOK=$HOOK_DIR/pre-commit
	cat > "$HOOK" <<'HOOK'
#!/usr/bin/env bash
$(dirname "$0")/../../tools/scripts/precommit_check.sh
HOOK
	chmod +x "$HOOK"
	echo "Installed pre-commit hook at $HOOK"
else
	mkdir -p "$FALLBACK_DIR"
	HOOK=$FALLBACK_DIR/pre-commit
	cat > "$HOOK" <<'HOOK'
#!/usr/bin/env bash
$(dirname "$0")/../../tools/scripts/precommit_check.sh
HOOK
	chmod +x "$HOOK"
	echo "No .git directory found. Wrote hook to $HOOK"
	echo "To use it, copy or symlink it into .git/hooks/pre-commit in your repository, or configure git to use .githooks by setting:\n  git config core.hooksPath .githooks"
fi
