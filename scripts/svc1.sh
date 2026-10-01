#!/usr/bin/env bash
# Drive training on SVC1 (DCISM's shared GB10 server) from this laptop.
# Needs an SSH host alias "svc1" in ~/.ssh/config with key auth; no credentials
# live in this repo. Code travels by git push over SSH; the gitignored
# data travels once by tar. Jobs run in detached tmux sessions, so they survive
# the laptop disconnecting.
#
#   scripts/svc1.sh sync              push this branch to the server checkout over SSH
#   scripts/svc1.sh data [PATH...]    gitignored data -> server (default: corpus + feature caches, ~0.8 GB)
#   scripts/svc1.sh setup             create ~/thesis/.venv (ARM + CUDA 13 torch)
#   scripts/svc1.sh run NAME CMD...   start CMD in tmux session NAME, logged to logs/NAME.log
#   scripts/svc1.sh log NAME          follow a job's log (Ctrl+C stops watching, not the job)
#   scripts/svc1.sh jobs              list running sessions + GPU load
#   scripts/svc1.sh pull              reports/ and assets/figures/ -> laptop
#
# Example:
#   scripts/svc1.sh run sweep .venv/bin/python src/model/sweep.py
set -euo pipefail
cd "$(dirname "$0")/.."
REMOTE=thesis   # relative to the server home directory
BRANCH=$(git branch --show-current)

case "${1:-}" in
  sync)
    # Pushed from here over SSH, not pulled from GitHub: the server's outbound
    # internet is blocked at night, inbound SSH is not. Commits only -- commit first.
    # Server-written results may since have been committed here; git refuses to
    # overwrite an untracked file. Copy anything new back first. Then, only for
    # untracked server files the push would overwrite: identical to the committed
    # version -> remove (the checkout restores it); different -> stash, with a warning.
    # Untracked files the push does not touch stay where later jobs can read them.
    ssh svc1 "[ -d $REMOTE/.git ] || git init -q $REMOTE; cd $REMOTE && git config receive.denyCurrentBranch updateInstead && mkdir -p logs"
    "$0" pull
    ssh svc1 "cd $REMOTE && git ls-files --others --exclude-standard -- reports assets/figures |
              while read -r f; do echo \"\$(git hash-object \"\$f\") \$f\"; done" |
    while read -r sha path; do
      want=$(git rev-parse -q --verify "HEAD:$path" 2>/dev/null) || continue
      if [ "$sha" = "$want" ]; then ssh -n svc1 "rm '$REMOTE/$path'"
      else ssh -n svc1 "cd $REMOTE && git stash push -q -u -m 'svc1 sync: $path' -- '$path'"; echo "warning: server's $path differs from the commit; stashed on the server"; fi
    done
    git push -q "svc1:$REMOTE" "$BRANCH:$BRANCH"
    ssh svc1 "cd $REMOTE && git checkout -q $BRANCH && git log --oneline -1" ;;
  data)
    shift; [ $# -gt 0 ] || set -- data/corpus data/features
    tar -czf - "$@" | ssh svc1 "tar -xzf - -C $REMOTE"
    echo "copied $*" ;;
  setup)
    # The pinned torch in requirements.txt is an x86 CUDA 12.4 build; the GB10 is
    # aarch64 + Blackwell, so torch and torchvision come from the CUDA 13 index, the rest from the pins.
    ssh svc1 "cd $REMOTE && python3 -m venv .venv && .venv/bin/pip install -q --upgrade pip &&
      .venv/bin/pip install -q torch torchvision --index-url https://download.pytorch.org/whl/cu130 &&
      grep -v -E '^torch(vision)?==' requirements.txt > /tmp/req-\$USER.txt &&
      .venv/bin/pip install -q -r /tmp/req-\$USER.txt &&
      .venv/bin/python -c 'import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))'" ;;
  run)
    name=$2; shift 2
    # Never start a job on code other than what is committed here.
    here=$(git rev-parse HEAD); there=$(ssh svc1 "cd $REMOTE && git rev-parse HEAD")
    if [ "$here" != "$there" ]; then
      echo "refusing to run: server is at ${there:0:7}, laptop at ${here:0:7} -- run sync first" >&2; exit 1
    fi
    ssh svc1 "cd $REMOTE && tmux new-session -d -s $name \"$* 2>&1 | tee logs/$name.log\""
    echo "started '$name'; watch with: scripts/svc1.sh log $name" ;;
  log)
    ssh -t svc1 "tail -n 30 -f $REMOTE/logs/$2.log" ;;
  jobs)
    ssh svc1 "tmux ls 2>/dev/null || echo 'no jobs'; nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader" ;;
  pull)
    # Never overwrite: an existing local file may be a committed laptop result the
    # server re-ran under the same name. Rename or delete it to take the server's.
    ssh svc1 "cd $REMOTE && tar -czf - reports assets/figures" | tar -xzf - --skip-old-files
    echo "pulled new files from reports/ and assets/figures/ (existing local files kept)" ;;
  *)
    sed -n '2,17p' "$0"; exit 1 ;;
esac
