#!/usr/bin/env bash

# Run normal git fetch and print the evidence needed to reconcile a workspace.
# This script never stages, commits, merges, rebases, pulls, pushes, stashes,
# deletes, or directly changes the worktree, index, local branches, or worktrees.

set -u

if [ "$#" -eq 0 ]; then
  set -- "$PWD"
fi

exit_code=0
# Bash 3.2 with `set -u` cannot safely expand an empty array.
seen_roots=("")

inspect_repo() {
  requested_dir=$1

  printf '\n=== WORKSPACE %s ===\n' "$requested_dir"

  if [ ! -d "$requested_dir" ]; then
    printf 'REPO=missing\nNEXT=stop:missing-path\n'
    exit_code=1
    return
  fi

  repo_root=$(git -C "$requested_dir" rev-parse --show-toplevel 2>/dev/null) || {
    printf 'REPO=not-git\nNEXT=skip:not-git\n'
    return
  }

  for seen_root in "${seen_roots[@]}"; do
    if [ -n "$seen_root" ] && [ "$seen_root" = "$repo_root" ]; then
      printf 'REPO=%s\nNEXT=skip:duplicate\n' "$repo_root"
      return
    fi
  done
  seen_roots[${#seen_roots[@]}]=$repo_root

  printf 'REPO=%s\n' "$repo_root"

  remotes=$(git -C "$repo_root" remote 2>/dev/null) || {
    printf 'FETCH=unknown\nNEXT=stop:inspection-failed\n'
    exit_code=1
    return
  }
  if [ -n "$remotes" ]; then
    if GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/usr/bin/false SSH_ASKPASS=/usr/bin/false git -C "$repo_root" fetch --quiet; then
      printf 'FETCH=ok\n'
    else
      printf 'FETCH=failed\nNEXT=stop:fetch-failed\n'
      exit_code=1
      return
    fi
  else
    printf 'FETCH=skipped:no-remote\n'
  fi

  branch=$(git -C "$repo_root" symbolic-ref --quiet --short HEAD 2>/dev/null) || branch=
  if [ -n "$branch" ]; then
    printf 'HEAD=branch:%s\n' "$branch"
  else
    printf 'HEAD=detached\n'
  fi

  inspection_failed=0
  if git_dir=$(git -C "$repo_root" rev-parse --absolute-git-dir 2>/dev/null); then
    operation=none
    if [ -e "$git_dir/MERGE_HEAD" ]; then
      operation=merge
    elif [ -d "$git_dir/rebase-merge" ]; then
      operation=rebase
    elif [ -d "$git_dir/rebase-apply" ]; then
      operation=rebase-or-am
    elif [ -e "$git_dir/CHERRY_PICK_HEAD" ]; then
      operation=cherry-pick
    elif [ -e "$git_dir/REVERT_HEAD" ]; then
      operation=revert
    elif [ -e "$git_dir/BISECT_LOG" ]; then
      operation=bisect
    fi
  else
    operation=unknown
    inspection_failed=1
  fi
  printf 'OPERATION=%s\n' "$operation"

  porcelain=$(git -C "$repo_root" status --porcelain=v1 --untracked-files=normal 2>/dev/null) || {
    printf 'DIRTY=unknown\nNEXT=stop:classification-failed\n'
    exit_code=1
    return
  }
  if [ -n "$porcelain" ]; then
    printf 'DIRTY=1\n'
  else
    printf 'DIRTY=0\n'
  fi

  conflicts=$(git -C "$repo_root" diff --name-only --diff-filter=U 2>/dev/null) || {
    printf 'CONFLICTS=unknown\nNEXT=stop:classification-failed\n'
    exit_code=1
    return
  }
  if [ -n "$conflicts" ]; then
    printf 'CONFLICTS=1\n'
  else
    printf 'CONFLICTS=0\n'
  fi

  upstream=
  upstream_label=none
  if [ -n "$branch" ]; then
    if upstream=$(git -C "$repo_root" rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null); then
      upstream_label=$upstream
    else
      configured_remote=$(git -C "$repo_root" config --get "branch.$branch.remote" 2>/dev/null)
      remote_status=$?
      configured_merge=$(git -C "$repo_root" config --get "branch.$branch.merge" 2>/dev/null)
      merge_status=$?
      if [ "$remote_status" -gt 1 ] || [ "$merge_status" -gt 1 ]; then
        upstream_label=unknown
        inspection_failed=1
      elif [ -n "$configured_remote" ] || [ -n "$configured_merge" ]; then
        upstream_label=unknown
        inspection_failed=1
      fi
    fi
  fi

  ahead=unknown
  behind=unknown
  if [ -n "$upstream" ]; then
    printf 'UPSTREAM=%s\n' "$upstream_label"
    counts=$(git -C "$repo_root" rev-list --left-right --count 'HEAD...@{upstream}' 2>/dev/null) || {
      printf 'AHEAD=unknown\nBEHIND=unknown\n'
      exit_code=1
      inspection_failed=1
      counts=
    }
    if [ -n "$counts" ]; then
      ahead=$(printf '%s\n' "$counts" | awk '{print $1}')
      behind=$(printf '%s\n' "$counts" | awk '{print $2}')
      printf 'AHEAD=%s\nBEHIND=%s\n' "$ahead" "$behind"
    fi
  else
    printf 'UPSTREAM=%s\nAHEAD=unknown\nBEHIND=unknown\n' "$upstream_label"
  fi

  outgoing_commits='(unavailable: no upstream)'
  outgoing_stat='(unavailable: no upstream)'
  if [ -n "$upstream" ]; then
    outgoing_commits=$(git -C "$repo_root" log --oneline '@{upstream}..HEAD' 2>&1) || {
      outgoing_commits='(failed)'
      inspection_failed=1
      exit_code=1
    }
    outgoing_stat=$(git -C "$repo_root" diff --stat '@{upstream}..HEAD' 2>&1) || {
      outgoing_stat='(failed)'
      inspection_failed=1
      exit_code=1
    }
  fi
  stashes=$(git -C "$repo_root" stash list 2>&1) || {
    stashes='(failed)'
    inspection_failed=1
    exit_code=1
  }
  worktrees=$(git -C "$repo_root" worktree list 2>&1) || {
    worktrees='(failed)'
    inspection_failed=1
    exit_code=1
  }

  next=none
  if [ "$inspection_failed" -eq 1 ]; then
    next=stop:inspection-failed
  elif [ "$operation" != none ]; then
    next=stop:operation
  elif [ -z "$branch" ]; then
    next=stop:detached-head
  elif [ -n "$conflicts" ]; then
    next=stop:conflicts
  elif [ "$ahead" != unknown ] && [ "$ahead" -gt 0 ] && [ "$behind" -gt 0 ]; then
    next=stop:diverged
  elif [ -n "$porcelain" ]; then
    next=review-dirty
  elif [ -z "$upstream" ]; then
    next=stop:confirm-upstream
  elif [ "$behind" -gt 0 ]; then
    next=pull-ff-only
  elif [ "$ahead" -gt 0 ]; then
    next=review-outgoing
  fi
  printf 'NEXT=%s\n' "$next"

  printf '%s\n' '--- CHANGES ---'
  if [ -n "$porcelain" ]; then
    printf '%s\n' "$porcelain"
  else
    printf '(none)\n'
  fi

  printf '%s\n' '--- OUTGOING COMMITS ---'
  if [ -n "$outgoing_commits" ]; then
    printf '%s\n' "$outgoing_commits"
  else
    printf '(none)\n'
  fi

  printf '%s\n' '--- OUTGOING DIFF STAT ---'
  if [ -n "$outgoing_stat" ]; then
    printf '%s\n' "$outgoing_stat"
  else
    printf '(none)\n'
  fi

  printf '%s\n' '--- STASHES ---'
  if [ -n "$stashes" ]; then
    printf '%s\n' "$stashes"
  else
    printf '(none)\n'
  fi

  printf '%s\n' '--- WORKTREES ---'
  if [ -n "$worktrees" ]; then
    printf '%s\n' "$worktrees"
  else
    printf '(none)\n'
  fi
}

repo_dirs=("$@")
if [ -n "${HOME:-}" ] && [ -d "$HOME/dotfiles" ]; then
  repo_dirs[${#repo_dirs[@]}]="$HOME/dotfiles"
fi

for repo_dir in "${repo_dirs[@]}"; do
  inspect_repo "$repo_dir"
done

exit "$exit_code"
