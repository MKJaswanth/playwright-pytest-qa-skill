#!/usr/bin/env bash
# Install playwright-pytest-qa into Codex, Claude Code, Cursor, or agents skills.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$ROOT/playwright-pytest-qa"
NAME="playwright-pytest-qa"

usage() {
  cat <<'EOF'
Usage: ./scripts/install.sh [--codex|--claude|--cursor|--agents|--all]

With no flag, install into every detected agent home among:
  ~/.codex/skills   ~/.claude/skills   ~/.cursor/skills   ~/.agents/skills
If none of those homes exist yet, install into Codex, Claude Code, and agents.
EOF
}

install_into() {
  local dest="$1/$NAME"
  mkdir -p "$1"
  rm -rf "$dest"
  cp -R "$SOURCE" "$dest"
  rm -rf "$dest/assets/starter/reports" \
         "$dest/assets/starter/.pytest_cache" \
         "$dest/assets/starter/.auth" \
         "$dest/assets/starter/.venv"
  find "$dest" -depth -type d -name '__pycache__' -exec rm -rf {} \;
  echo "Installed to $dest"
}

targets=()
choice="${1:-auto}"
case "$choice" in
  --codex) targets+=("$HOME/.codex/skills") ;;
  --claude) targets+=("$HOME/.claude/skills") ;;
  --cursor) targets+=("$HOME/.cursor/skills") ;;
  --agents) targets+=("$HOME/.agents/skills") ;;
  --all)
    targets+=(
      "$HOME/.codex/skills"
      "$HOME/.claude/skills"
      "$HOME/.cursor/skills"
      "$HOME/.agents/skills"
    )
    ;;
  --help|-h)
    usage
    exit 0
    ;;
  auto)
    for home in "$HOME/.codex" "$HOME/.claude" "$HOME/.cursor" "$HOME/.agents"; do
      if [[ -d "$home" ]]; then
        targets+=("$home/skills")
      fi
    done
    if [[ ${#targets[@]} -eq 0 ]]; then
      targets+=(
        "$HOME/.codex/skills"
        "$HOME/.claude/skills"
        "$HOME/.agents/skills"
      )
    fi
    ;;
  *)
    echo "Unknown option: $choice" >&2
    usage >&2
    exit 2
    ;;
esac

for dest in "${targets[@]}"; do
  install_into "$dest"
done
