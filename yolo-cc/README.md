# yolo-cc

Run Claude Code in isolated container with credential proxy.

## Architecture

```
Host                           Container (OrbStack)
┌─────────────────────┐        ┌──────────────────────────┐
│ CLAUDE_CODE_OAUTH_  │        │ YOLO Claude Code         │
│ TOKEN (env)         │        │                          │
│        │            │        │ ANTHROPIC_BASE_URL=      │
│        ▼            │        │   http://localhost:9999  │
│ ┌─────────────────┐ │        │                          │
│ │ Auth Proxy      │◀├────────┤ (no credentials here!)   │
│ │ localhost:9999  │ │        │                          │
│ └────────┬────────┘ │        │ .git: read-only          │
│          │          │        │ workspace: read-write    │
│          ▼          │        └──────────────────────────┘
│   api.anthropic.com │
└─────────────────────┘
```

## Security

- **Credentials never enter container** - proxy injects auth headers
- **.git is read-only** - always recoverable via `git checkout .`
- **Internet access allowed** - same as Anthropic's gVisor environment

## Usage

```bash
# Basic
yolo-cc "fix all TypeScript errors"

# With Python (uv)
yolo-cc --uv "create a FastAPI server"

# Specify workspace
yolo-cc -w ~/projects/myapp "refactor auth module"

# Force rebuild images
yolo-cc --build "update dependencies"
```

## Setup

1. **Set token**:
   ```bash
   export CLAUDE_CODE_OAUTH_TOKEN='your-token'
   ```

2. **Add to PATH** (after moving to dotfiles):
   ```bash
   export PATH="$HOME/dotfiles/yolo-cc/bin:$PATH"
   ```

3. **First run** will build Docker images (takes a few minutes)

## Requirements

- OrbStack (or Docker Desktop)
- bun (for auth proxy)
- CLAUDE_CODE_OAUTH_TOKEN environment variable

## Recovery

If YOLO-CC makes unwanted changes:

```bash
cd /your/workspace
git checkout .      # Restore tracked files
git clean -fd       # Remove untracked files
```

## Testing

```bash
# Run e2e happy path test
./test/e2e-happy-path.sh

# Keep temp dir for inspection
./test/e2e-happy-path.sh --keep
```

The test creates a temp workspace, runs yolo-cc with a simple math prompt, and verifies the result.

## Files

```
yolo-cc/
├── bin/yolo-cc           # CLI entrypoint
├── test/
│   └── e2e-happy-path.sh # E2E test
├── compose/docker-compose.yml
├── images/
│   ├── base.Dockerfile   # bun + CC
│   └── uv.Dockerfile     # + Python (uv)
└── README.md
```
