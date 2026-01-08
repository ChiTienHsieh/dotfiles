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

## Ralph Mode (Iterative Execution)

Ralph mode enables iterative execution using the [Ralph Wiggum technique](https://ghuntley.com/ralph/). Claude runs in a loop, seeing its own previous work in files, until a completion promise is detected or max iterations reached.

```bash
# Basic ralph mode with completion promise
yolo-cc --ralph "fix all type errors" --completion-promise "ALL ERRORS FIXED"

# With iteration limit
yolo-cc --ralph --max-iterations 20 "improve test coverage to 80%"

# Combined with other flags
yolo-cc --ralph --uv "create and test a FastAPI server" --completion-promise "TESTS PASSING"
```

### How Ralph Mode Works

1. **First iteration**: Claude receives the prompt with `-p`
2. **Subsequent iterations**: Same prompt fed via `--continue`
3. **Self-reference**: Claude sees its previous work in files
4. **Exit conditions**:
   - `<promise>TEXT</promise>` detected in output
   - Max iterations reached (default: 10)

### Completion Promises

To exit the loop, Claude must output:
```
[[PROMISE: YOUR_PROMISE_TEXT]]
```

The promise phrase must match exactly. Claude is instructed to only output the promise when the statement is truly complete.

**Note:** We use `[[PROMISE: ...]]` instead of XML tags because Claude Code has issues parsing `<promise>` tags in prompts.

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
├── bin/yolo-cc              # CLI entrypoint
├── test/
│   ├── e2e-happy-path.sh    # Basic E2E test
│   └── e2e-ralph-mode.sh    # Ralph mode E2E test
├── compose/docker-compose.yml
├── images/
│   ├── base.Dockerfile      # bun + CC
│   └── uv.Dockerfile        # + Python (uv)
└── README.md
```
