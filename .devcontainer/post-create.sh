#!/bin/bash
# Runs automatically after every container create/rebuild (see devcontainer.json
# postCreateCommand). Restores everything that lives in the ephemeral home
# directory and doesn't survive a rebuild on its own:
#
#   1. Clone the claude-brain memory repo, if it isn't already there.
#   2. Install the brain-* scripts from it into ~/.local/bin.
#   3. Make sure ~/.local/bin is on PATH for future shells.
#   4. Run brain-link (skill/agent symlinks) and brain-pull (routine sync).
#   5. Re-add the codex() shell function (auto brain-pull + DeepSeek profile).
#   6. npm-install the claude-code and codex CLIs (global npm packages live in
#      the ephemeral home dir too, so they vanish on every fresh container —
#      confirmed missing on a codespace created via `gh codespace create`,
#      2026-09-14).
#
# Auth comes from $BRAIN_TOKEN / $OPENROUTER_API_KEY, Codespaces secrets
# injected as env vars — never hardcoded here, since this file is committed
# to the repo.

set -u

MEMORY_PATH="$HOME/.claude/projects/$(pwd | sed 's|/|-|g')/memory"

if [ ! -d "$MEMORY_PATH/.git" ]; then
  if [ -z "${BRAIN_TOKEN:-}" ]; then
    echo "✗ BRAIN_TOKEN is not set — cannot clone claude-brain."
    echo "  Set it as a Codespaces secret, then stop/restart this codespace."
    exit 1
  fi
  echo "Cloning claude-brain into $MEMORY_PATH ..."
  mkdir -p "$MEMORY_PATH"
  git clone "https://wiedenu:${BRAIN_TOKEN}@github.com/wiedenu/claude-brain.git" "$MEMORY_PATH"
else
  echo "Brain repo already present at $MEMORY_PATH"
fi

SRC="$MEMORY_PATH/scripts/brain"
DEST="$HOME/.local/bin"

if [ -d "$SRC" ]; then
  mkdir -p "$DEST"
  echo "Installing brain-* scripts -> $DEST"
  for f in "$SRC"/brain-*; do
    [ -f "$f" ] || continue
    install -m 755 "$f" "$DEST/$(basename "$f")"
  done
else
  echo "✗ No scripts found at $SRC — clone may have failed."
  exit 1
fi

# Make sure ~/.local/bin is on PATH for future interactive shells.
for RC in "$HOME/.bashrc" "$HOME/.zshrc"; do
  if [ -f "$RC" ] && ! grep -q '\.local/bin' "$RC"; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$RC"
    echo "Added ~/.local/bin to PATH in $RC"
  fi
done
export PATH="$HOME/.local/bin:$PATH"

# npm globals (like ~/.local/bin) don't survive a rebuild in the ephemeral
# home dir — reinstall the actual CLI binaries every time. --allow-scripts is
# needed for claude-code's postinstall (npm blocks it by default otherwise).
echo "Installing claude-code + codex CLIs..."
npm install -g --allow-scripts=@anthropic-ai/claude-code @anthropic-ai/claude-code @openai/codex \
  || echo "⚠️  claude-code/codex install failed — check npm output above."

# Re-add the codex() function (auto brain-pull + default DeepSeek/OpenRouter
# profile). The API key itself comes from $OPENROUTER_API_KEY — a Codespaces
# secret — never written to this file.
CODEX_MARKER="# claude-brain: codex bridge"
for RC in "$HOME/.bashrc" "$HOME/.zshrc"; do
  if [ -f "$RC" ] && ! grep -qF "$CODEX_MARKER" "$RC"; then
    cat >> "$RC" <<'EOF'

# claude-brain: codex bridge
codex() {
  command -v brain-pull >/dev/null 2>&1 && brain-pull
  if [[ "$*" == *"--profile"* ]]; then
    command codex "$@"
  else
    command codex --profile deepseek-openrouter "$@"
  fi
}
EOF
    echo "Added codex() bridge to $RC"
  fi
done

if [ -z "${OPENROUTER_API_KEY:-}" ]; then
  echo "⚠️  OPENROUTER_API_KEY is not set — codex's DeepSeek profile won't authenticate."
  echo "  Set it as a Codespaces secret, then stop/restart this codespace."
fi

echo "Running brain-link ..."
brain-link || echo "⚠️  brain-link reported an issue — check output above."

echo "Running brain-pull ..."
brain-pull

echo "✓ post-create bootstrap complete."
