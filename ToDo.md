# ToDo

## GitHub README.md 작성

### 배경
CommonClaude.md 내용을 설명하는 README.md를 작성한다.
IDECommand.png, ShortCut.png 내용을 포함한다.

### 할 일

- [x] CommonClaude.md에 영어 작성 규칙 추가
- [x] README.md 작성 (영어)
  - [x] CommonClaude.md 내용 요약 및 설명
  - [x] IDE 명령어 정보 (IDECommand.png 참고)
  - [x] 단축키 정보 (ShortCut.png 참고)
- [x] GitHub 이슈 등록
- [x] 커밋 및 푸시
- [x] GitHub 이슈 업데이트

---

## CLAUDE.md 규칙을 Claude Code Hooks로 구현

### 배경
CLAUDE.md에 정의된 코딩 규칙(린트, 디버그 파일 배치, 작업관리 등)을 Claude Code hooks로 자동 강제하여, "읽고 따르는" 수준에서 "시스템이 자동 검증하는" 수준으로 강화한다.

### 할 일

- [x] `ruff.toml` 생성 (line-length=80, indent-width=4)
- [x] `.claude/hooks/` 디렉토리 생성
- [x] `pre-write-guard.sh` 작성 — tests/에 디버그 파일 쓰기 차단 (§2)
- [x] `post-write-lint.sh` 작성 — Python 파일 ruff check + format 피드백 (§5)
- [x] `post-write-debug-remind.sh` 작성 — claude_test/ 파일 추가 시 README 리마인더 (§2)
- [x] `.claude/settings.json` 작성 — Hook 설정 + Stop prompt hook (§3 ToDo/이슈 확인)
- [x] GitHub 이슈 등록
- [x] 커밋 및 푸시
- [x] GitHub 이슈 업데이트

---

## README.md에 /output-style 명령어 및 Hook 설명 추가

### 배경
README.md의 IDE Commands 표에 `/output-style`이 누락되어 있고, 직전에 추가된 Claude Code hooks 자동 강제 메커니즘에 대한 설명이 README에 없어 사용자가 프로젝트의 규칙 강제 방식을 이해하기 어렵다.

### 할 일

- [x] IDE Commands 표에 `/output-style` 행 추가
- [x] `Automated Enforcement (Hooks)` 섹션 신규 추가 (Convention Summary와 IDE Commands 사이)
- [x] GitHub 이슈 등록
- [x] 커밋 및 푸시
- [x] GitHub 이슈 업데이트

---

## Concept.md 내용 정리

### 배경
사용자가 Concept.md에 CommonClaude 개선 아이디어(ECC에서 선별 흡수할
Rule 재구조화, Token 최적화, Search-first, Learned Patterns 마이그레이션
등)를 작성하였다. 이를 읽고 섹션별로 구조화하여 사용자가 전체 구상을
한눈에 파악할 수 있도록 정리한다.
실제 적용은 본 작업 범위에서 제외하며, 이후 별도 세션에서 새 ToDo로
착수한다.

### 할 일

- [x] Concept.md 전체 내용 읽기
- [x] 6개 섹션으로 구조화된 요약 제공
      (철학 진단 / Rule 관점 / Rule 외 / 제외 항목 /
      Continuous-Learning 마이그레이션 Phase 0–5 / 최종 적용 순서)
- [x] GitHub 이슈 등록 (#12)
- [x] 커밋 및 푸시
- [x] GitHub 이슈 업데이트

---

## CommonClaude Improvement Track (from Concept.md)

### Background
Concept.md proposes seven incremental improvements adopted selectively
from ECC to strengthen CommonClaude while preserving its minimalist
philosophy. This entry decomposes that plan into seven independently
executable, independently rollbackable tasks. Each task gets its own
GitHub issue and its own commit. User approval is required at every
checkpoint marked **[APPROVAL]**. Phase 4 (continuous accumulation) is
a standing practice that begins once Tasks 1-7 land, and is therefore
not a discrete task here.

### Diagnosis Baseline (captured 2026-04-22)
- ToDo.md Completed: 4 top-level doc/setup tasks. Sample below the
  10-item threshold for pattern extraction; Task 5 will follow the
  "insufficient sample -> Phase 2 only" branch (Concept.md L99-101).
- CLAUDE.md: sections Overview, Environment, §1-§5 present. Missing:
  priority-override statement, Exceptions subsections, Research
  Before Coding section, Learned Patterns Reference section.
- Hooks present: pre-write-guard, post-write-lint,
  post-write-debug-remind, Stop prompt. Missing: Bash secret scan,
  Read env-file guard.
- MCP: no MCP config exists in repo. Task 3 is effectively null op
  unless the user decides to add filesystem MCP.

### Task 1. Restructure CLAUDE.md rule layer
Risk: low. Rollback: `git revert`.
Bundled with Tasks 2 and 4 under issue #14 per user decision.
- [x] Add priority-override statement near the top of CLAUDE.md
      ("Project-level CLAUDE.md rules override this global file")
- [x] Add Exceptions subsection under §2 Debug Files (waive 80-col
      and docstring requirements inside `claude_test/`)
- [x] Add Exceptions subsection under §4 Testing (allow magic
      numbers in one-off exploratory scripts when intent comment
      is present at file top)
- [x] **[APPROVAL]** Bundled approval granted 2026-04-22
- [x] GitHub issue register and cross-link (#14)
- [x] Commit and push (aa15cb9)
- [x] GitHub issue update (#14 closed)

### Task 2. Add token-optimization env vars
Risk: low. Rollback: `git revert`.
Bundled with Tasks 1 and 4 under issue #14 per user decision.
- [x] Add `env` block to `.claude/settings.json` with
      `MAX_THINKING_TOKENS=10000` and
      `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=50`
- [x] Verify existing `hooks` block is untouched
- [x] **[APPROVAL]** Values confirmed as-is per user 2026-04-22
- [x] GitHub issue register (#14)
- [x] Commit and push (aa15cb9)
- [x] GitHub issue update (#14 closed)

### Task 3. MCP reconfiguration decision
Risk: low (decision only). Rollback: n/a (no repo change).
Resolved by user 2026-04-22: keep Context7 MCP as-is. No repo MCP
config is introduced. This task closes without file changes.
- [x] User decision: keep Context7 MCP, add nothing else
- [ ] GitHub issue register and close immediately as "no change"

### Task 4. Add Search-first section to CLAUDE.md
Risk: low. Rollback: `git revert`.
Bundled with Tasks 1 and 2 under issue #14 per user decision.
- [x] Draft a new §6 "Research Before Coding" covering doc lookup,
      prior-implementation search, and the rule against guessing
      APIs from memory
- [x] **[APPROVAL]** Bundled approval granted 2026-04-22
- [x] GitHub issue register (#14)
- [x] Commit and push (aa15cb9)
- [x] GitHub issue update (#14 closed)

### Task 5. Phase 0-1 diagnosis and (abridged) pattern extraction
Risk: low. Rollback: discard draft file.
Tracked under issue #16.
- [x] Document diagnosis outcome: sample < 10, Phase 1 extraction
      skipped per Concept.md L99-101 (recorded in #16 body)
- [x] Produce a short seed list of candidate patterns from the
      four Completed tasks plus current session — five
      workflow-level lessons L1-L5 (recorded in #16 body)
- [x] Superseded by #19 which applied the full §10 Bootstrap
      extraction across all ToDo.md Completed items; seed list
      content preserved in LearnedPatterns.md §4 Workflow Lessons
      (commit 24b6349). #16 closed 2026-04-22.

### Task 6. Create LearnedPatterns.md and wire it into CLAUDE.md
Risk: low. Rollback: delete file + `git revert` CLAUDE.md.
- [ ] Create `LearnedPatterns.md` seeded with Task 5 output and
      the section skeleton (§1-§5) from Concept.md L131-164
- [ ] Add §7 "Learned Patterns Reference" to CLAUDE.md instructing
      Claude to consult `LearnedPatterns.md` before drafting ToDo
- [ ] **[APPROVAL]** Show both artifacts
- [ ] GitHub issue register
- [ ] Commit and push
- [ ] GitHub issue update

### Task 7. Add secret-scan and env-file-guard hooks
Risk: medium (false positives can block legitimate work).
Rollback: disable in `settings.json` + `git revert` scripts.
- [x] Write `.claude/hooks/pre-bash-secret-scan.sh` blocking
      Bash commands that contain `sk-`, `ghp_`, `AKIA`, or
      obvious password literals (expanded to cover more vendor
      prefixes and `api_key=` / `access_token=` / etc.)
- [x] Write `.claude/hooks/pre-read-env-guard.sh` blocking
      reads of `.env`, `.pem`, `.key` (renamed from
      `pre-read-envfile-guard.sh` per user 2026-04-22)
- [x] ~~Add fixture scripts under `claude_test/`~~ dropped per
      user 2026-04-22; manual verification scenarios used instead
- [x] Wire both hooks into `.claude/settings.json` under
      `PreToolUse` with matchers `Bash` and `Read` respectively
- [x] **[APPROVAL]** Demonstrated block behaviour live in session
- [x] GitHub issue register (#15)
- [x] Commit and push (72fef2c — landed alongside Task 5 update)
- [x] GitHub issue update (#15 closed)

### Task Ordering and Independence
- Tasks 1, 2, 4 are independent and may be executed in any order.
- Task 3 is a decision gate and can run in parallel with others.
- Task 5 must precede Task 6.
- Task 7 is self-contained but its fixtures must land together
  with the hook scripts.

### Out of Scope
- Phase 4 ongoing accumulation: standing workflow, begins after
  Tasks 1-7 land.
- Phase 5 Stop-hook extension: deferred until pattern accumulation
  demonstrates a real need.

### Meta-task checklist (this drafting session)
- [x] GitHub umbrella issue registered (#13)
- [x] Commit and push draft (84d99f5)
- [x] User approved plan; Tasks 1+2+4 bundle executed in aa15cb9
- [x] Umbrella issue updated to reflect bundle closure

---

## Task 7 execution: secret-scan and env-file-guard hooks

### Background
Executing Task 7 from the umbrella plan (#13). Scope refinements
agreed with the user on 2026-04-22:
- Rename `pre-read-envfile-guard.sh` -> `pre-read-env-guard.sh`
  to match the user's preferred filename.
- Expand Bash scan to include `api_key=` literal in addition to
  `sk-`, `ghp_`, `AKIA`, `password=`.
- Drop `claude_test/` fixtures; use manual verification scenarios
  supplied by the assistant.

Verification strings such as `sk-test1234567890abcdef` are
illustrative test tokens, not real credentials.

### Work items
- [x] Write `.claude/hooks/pre-bash-secret-scan.sh`
- [x] Write `.claude/hooks/pre-read-env-guard.sh`
- [x] `chmod +x` both scripts
- [x] Register both hooks in `.claude/settings.json`
- [x] Manual verification: `sk-*`, `ghp_*`, `password=`, `api_key=`
      blocked via Bash; `.env` blocked via Read; benign `ls`
      command and `README.md` read pass through
- [x] GitHub issue register (#15)
- [x] Commit and push (72fef2c)
- [x] GitHub issue update and tick remaining Task 7 boxes

### Side fix
- [x] Install `jq` via apt; the existing three hooks also depend on
      it and were silently no-op'd before this fix.

### Scope notes
Bash pattern set finalized as: `sk-`, `ghp_`, `gho_`, `ghu_`, `ghs_`,
`github_pat_`, `AKIA*`, `AIza*`, `xox[baprs]-*`, `glpat-*`, plus
generic literal assignments `password=`, `api_key=`, `access_token=`,
`secret_key=`, `auth_token=`. Expanded beyond the original five per
user direction "암호 뿐만 아니라 API 키도 거부하도록".

---

## CLAUDE.md §7 — Learned Patterns Bootstrap rule

### Background
Splits Task 6 of the umbrella plan (#13) into Part A (rule) and
Part B (generate the file). User directed adding the bootstrap
procedure to `CLAUDE.md` now, so future sessions know how to
generate `LearnedPatterns.md` from `ToDo.md` when it is absent.
Tracked under issue #17.

### Rule outline
- Classify `[x]` items into §1-§5 plus §99 fallback.
- Each entry: Problem / Cause / Fix / Rule (one-liner each).
- Append `(from ToDo#N)` for traceability.
- `ToDo.md` stays append-only; `LearnedPatterns.md` is a new
  file in repo root; content in English; ambiguous items go
  to §99 rather than being guessed.

### Work items
- [x] Add §7 "Learned Patterns Bootstrap" to `CLAUDE.md`
- [x] GitHub issue register (#17)
- [x] Commit and push (4628a61)
- [x] GitHub issue update (#17 closed)

---

## CLAUDE.md restructure — Rule Priority, Exceptions, Learned Patterns Reference

### Background
User direction 2026-04-22: promote the existing `## Priority`
subsection and the two `### Exceptions` subsections to proper
numbered top-level sections, and add a new `Learned Patterns
Reference` section (distinct from the generation-rule §7
`Learned Patterns Bootstrap` that just landed). Tracked under
issue #18. No file change until the diff preview is approved.

### Work items
- [x] Draft proposed numbering map and new-section text
- [x] GitHub issue register (#18)
- [x] **[APPROVAL]** User approved 2026-04-22
- [x] Apply restructure (renumber §1-§7, add §1 Rule Priority,
      add §8 Exceptions, add §9 Learned Patterns Reference,
      move former §7 to §10 Learned Patterns Bootstrap)
- [x] Update internal cross-references (§1 Structure ->
      §2 Structure; §1 Documentation -> §2 Documentation;
      §1 Language rule -> §2 Language rule)
- [x] Commit and push (b2a39a1)
- [x] GitHub issue update (#18 closed)

---

## CLAUDE.md §8 — ToDo.md checkbox update exception

### Background
User direction 2026-04-22: the append-only rule in §4 Task
Management Rule 2 and the "do not modify ToDo.md" constraint in
§10 Learned Patterns Bootstrap were written to preserve history,
not to prohibit progress marking. Every task-completion step
flips a `[ ]` to `[x]`; this behavior needs an explicit carve-out
so future sessions do not misread the rule. Tracked under issue
#20.

### Work items
- [x] Add `ToDo.md checkbox updates` subsection under §8
- [x] GitHub issue register (#20)
- [x] Commit and push (17dee39)
- [x] GitHub issue update (#20 closed)

---

## Task 6 Part B — generate LearnedPatterns.md

### Background
Executes the §10 Learned Patterns Bootstrap procedure (added in
commit 4628a61, §7 at the time, §10 after restructure b2a39a1) to
materialize `LearnedPatterns.md` in the repo root. Classifies every
`[x]` item across `ToDo.md` into §1-§5 plus §99 per the bootstrap
rules. Task 5 seed list (#16) feeds into §4 Workflow Lessons but
the full analysis scans every Completed item, not just that seed.
Tracked under issue #19.

### Work items
- [x] Classify every `[x]` item in `ToDo.md` per CLAUDE.md §10
- [x] Write `LearnedPatterns.md` in repo root with 15 patterns
      across §1-§5 plus a §99 Uncategorized residual
- [x] GitHub issue register (#19)
- [x] Commit and push (24b6349)
- [x] GitHub issue update (#19 closed)

---

## Concept.md coverage verification

### Background
User asked whether every recommendation in `Concept.md` has been
reflected in the repo. This task cross-checks Concept.md's two parts
(Part 1 items 1-7, Part 2 Phase 0-5) and the final application order
L197-204 against landed commits, surfacing any gaps for decision.
Tracked under issue #21.

### Work items
- [x] Map each Concept.md recommendation to a commit or decision
- [x] Produce Done / Partial / Deferred table
- [x] Identify remaining gaps for user decision
- [x] GitHub issue register (#21)
- [ ] Commit and push
- [ ] GitHub issue update

---

## APT NVIDIA CUDA repo "Conflicting values set for option Signed-By" fix

### Background
`apt update` fails with:
`E: Conflicting values set for option Signed-By regarding source
https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/ /:
/usr/share/keyrings/cuda-archive-keyring.gpg !=`
followed by `E: The list of sources could not be read.`

Cause: `/etc/apt/sources.list.d/` holds two entries for the same NVIDIA
CUDA repo with conflicting keyrings —
- `cuda-ubuntu2404-x86_64.list` (2024-03-27): `signed-by=/usr/share/keyrings/cuda-archive-keyring.gpg`
- `cuda.list` (2025-09-08): no `signed-by=`

The unsigned `cuda.list` was likely added by re-running an NVIDIA install
snippet that omitted the `signed-by=` option. Keep the signed one; remove
the duplicate. Plan: `/root/.claude/plans/e-conflicting-values-set-groovy-goblet.md`.

### Work items
- [x] Confirm ToDo contents with user
- [x] Register GitHub issue via `gh issue create` (#1)
- [x] `sudo rm /etc/apt/sources.list.d/cuda.list` (root in container, no sudo needed)
- [x] `sudo apt update` and confirm no `Conflicting values` error
- [x] `apt-cache policy cuda-toolkit | head` to verify NVIDIA repo is a candidate (cuda-toolkit 13.2.1-1)
- [x] Update GitHub issue with outcome (#1 closed)
- [x] Commit and push (ToDo update + any artefact)

---

## Upgrade libnccl2 / libnccl-dev to 2.28.9-1+cuda13.0

### Background
The system NCCL packages are currently held at 2.28.3-1+cuda13.0
(`hi` flag in `dpkg -l`). The newest available `+cuda13.0` build on
the NVIDIA repo is 2.28.9-1, which also matches the NCCL version
PyTorch 2.11.0+cu130 ships in its wheel (`torch.cuda.nccl.version()
== (2, 28, 9)`). Upgrading the system package aligns the two so any
non-PyTorch usage of NCCL (raw C++, JAX, etc.) sees the same version
PyTorch is already running with. Decision recorded in plan:
`/root/.claude/plans/e-conflicting-values-set-groovy-goblet.md`
(NCCL-version section). Note: this upgrade is **not** expected to
affect the `nccl_check.py` hang because PyTorch uses its bundled
NCCL, not the system package — the hang is a separate issue.

### Work items
- [x] Confirm ToDo contents with user
- [x] Register GitHub issue via `gh issue create` (#2)
- [x] `apt-mark unhold libnccl2 libnccl-dev`
- [x] `apt install libnccl2=2.28.9-1+cuda13.0 libnccl-dev=2.28.9-1+cuda13.0`
- [x] `apt-mark hold libnccl2 libnccl-dev`
- [x] Verify with `dpkg -l | grep -E '^hi\s+(libnccl2|libnccl-dev)'`
       (both at 2.28.9-1+cuda13.0, status `hi`)
- [x] Update GitHub issue with outcome (#2 closed)
- [x] Commit and push (ToDo update)

---

## Debug nccl_check.py hang on 2x H200 NVL

### Background
Running `bash nccl_check_bash.sh` (which is `NCCL_DEBUG=INFO python3
nccl_check.py`) hangs with both worker processes pegged at 99% CPU
and 100% GPU-Util, no stdout for 4+ minutes, before being killed.
The current `nccl_check_bash.sh` pipes through `| tail -40` which
buffers all output, hiding NCCL's INFO trace. PyTorch's bundled NCCL
2.28.9 (matches just-installed system NCCL, but PyTorch uses its
bundled copy regardless). User selected option 2 — debug before
pushing the local commits a033dd5 and 0d2caf1.

### Approach
- Re-run the test directly without the buffering tail, capture full
  NCCL_DEBUG=INFO trace to a log file via `tee`.
- If it hangs again, kill after a bounded timeout and inspect the
  init phase from the log to identify where NCCL is stuck (rendezvous,
  P2P negotiation, IB/RoCE detection, shm, etc.).
- Try common bypasses (`NCCL_IB_DISABLE=1`, `NCCL_P2P_DISABLE=1`,
  `NCCL_SOCKET_IFNAME=lo`) only after the log tells us where the hang
  is — don't shotgun-tune.

### Work items
- [x] Confirm with user (option 2 selected)
- [x] Register GitHub issue (#3)
- [ ] Run `NCCL_DEBUG=INFO python3 nccl_check.py 2>&1 | tee /tmp/nccl.log`
       with bounded timeout (paused — superseded by README task)
- [ ] If hung: read /tmp/nccl.log, identify the last NCCL phase before
       the silence, share with user (paused)
- [ ] If passed: confirm output is correct, proceed to push gated
       commits (paused)
- [ ] Update GitHub issue with findings (paused — #3 stays open)
- [ ] Commit and push (ToDo update) (paused)

---

## Write NCCLTester README documenting progress so far

### Background
User direction 2026-04-27: pause the NCCL hang debug and write a
GitHub-facing README that summarises the work done so far on the
new `coport-uni/NCCLTester` repo, then commit and push. The current
`README.md` is a leftover from the CommonClaude conventions project
and is not relevant to NCCLTester. Two local commits are unpushed
(a033dd5 apt fix, 0d2caf1 NCCL upgrade); pushing the README will
also push those.

### Scope
- Replace `README.md` with NCCLTester-focused content: project
  purpose, environment, files, progress tracker (#1, #2, #3),
  known issue (NCCL hang), how to run.
- Include the test scripts and the project conventions file in the
  same commit so the README's references resolve on the remote.
  Files: `README.md`, `ToDo.md`, `CLAUDE.md`, `nccl_check.py`,
  `nccl_check_bash.sh`, `ruff.toml`, `.claude/`.
- Skip clearly unrelated artefacts: `CLAUDECowork.md`, `Concept.md`,
  `LearnedPatterns.md`, `getpip.py`, `cuda-keyring_1.1-1_all.deb`.

### Work items
- [x] Confirm with user (explicit directive received)
- [x] Register GitHub issue (#4)
- [x] Write new `README.md`
- [x] Stage README + ToDo + project files; commit
- [x] `git push -u origin master` (also pushes a033dd5, 0d2caf1)
- [x] Comment on #4 with outcome and close
- [x] Final ToDo tick + amend if needed

---

## NCCL transport availability diagnosis (SHM / P2P / NET)

### Background
컨테이너 내에서 NCCL이 어떤 transport(SHM, P2P, NET)를 실제로 쓸 수
있는지 파악한다. 환경은 Docker `--shm-size=60g`, GPU 2x H200 NVL.
범위는 single-node multi-GPU(같은 컨테이너 안 2 GPU)로 한정한다.
외부로 개방된 포트는 17040-17046이지만 single-node에서는 loopback만
쓰므로 외부 포트 개방 여부는 NCCL transport 가용성에 영향이 없다
(메모용 기록). 본 진단은 ToDo#3의 `nccl_check.py` hang(paused)과 같은
컨테이너에서 진행되므로 hang 원인 후보를 좁히는 근거로도 활용된다.

### Scope
- Single-node multi-GPU (intra-container, 2x H200 NVL).
- Multi-node는 범위 외.
- LP §1 R1 / §4 W1: 진단/정보성 작업도 ToDo + 이슈 풀 워크플로우 적용.

### Approach
1. SHM 정적 진단 — `df -h /dev/shm`, mount option, `ipcs -m`.
2. P2P 정적 진단 — `nvidia-smi topo -m`, `nvidia-smi nvlink -s`,
   `/dev/nvidia*` 접근성, IOMMU group 상태.
3. NET 정적 진단 — `ip -br link`, `ibv_devinfo`(있으면), lo 상태.
4. (옵션) bounded NCCL run: `NCCL_DEBUG=INFO`
   `NCCL_DEBUG_SUBSYS=INIT,NET,P2P,SHM` 90s timeout, log를
   `claude_test/logs/nccl_init.log`에 캡처.
5. SHM/P2P/NET 가용성 표 작성 (Available / Blocked / Conditional).

### Work items
- [x] Confirm scope with user (single-node, ports 17040-17046)
- [x] Register GitHub issue (`gh issue create`) — #5
- [x] SHM static checks
- [x] P2P static checks
- [x] NET static checks
- [x] Bounded NCCL run with NCCL_DEBUG=INFO + log capture
      (default, NCCL_P2P_DISABLE=1, NCCL_P2P_DISABLE+NCCL_SHM_DISABLE,
      and a set_device-first variant)
- [x] Summary table (SHM/P2P/NET — Available / Blocked / Conditional)
- [x] Commit and push (ToDo update + claude_test additions) (a3fb564)
- [x] GitHub issue update (#5 closed via Closes-trailer; outcome comment added)

### Outcome — transport availability matrix

| Transport | Available? | Default-selected? | Evidence |
|-----------|-----------|-------------------|----------|
| **SHM**   | Yes       | No (P2P preferred) | `/dev/shm` is 126 GB tmpfs `rw,nosuid,nodev` (no `noexec`), 1777 perms. With `NCCL_P2P_DISABLE=1` NCCL uses `SHM/direct/direct` and `all_reduce` returns the correct sum (`logs/nccl_p2p_disabled.log`). |
| **P2P (CUDA peer-to-peer)** | Selectable but hangs | Yes (`P2P/CUMEM`) | `cudaCanAccessPeer(0,1)`/`(1,0)` both `True`. GPUs 0000:76:00.0 / 0000:77:00.0 share PCIe switch `0000:71:00.0` (PIX). PCIe Gen5 x16, **no NVLink bridge**. NCCL chooses `P2P/CUMEM` for all 4 channels and finishes init in 0.8 s, but `all_reduce` hangs (timeout 90 s — `logs/nccl_init.log`). Calling `cuda.set_device` before `init_process_group` does **not** unstick it (`logs/nccl_devfix.log`). Root cause is out of scope for this issue and stays under #3. |
| **NET (Socket)** | Yes | No (loopback path inferred from PCIe) | InfiniBand absent (`/sys/class/infiniband` empty, `ibv_devinfo` not installed; NCCL logs `transport/net_ib.cc:852 -> 3` and falls back). With `NCCL_P2P_DISABLE=1 NCCL_SHM_DISABLE=1` NCCL uses `NET/Socket/0` over `eth0` (172.17.0.2) and `all_reduce` succeeds (`logs/nccl_net_only.log`). External port range 17040-17046 does not bear on single-node operation. |

### Practical guidance
- For single-node 2x H200 NVL with NCCL **today**, the working transports
  are **SHM** and **NET**.
- A correct collective can be obtained by running with
  `NCCL_P2P_DISABLE=1` until the P2P/CUMEM hang in #3 is resolved.
- The hang is **not** caused by SHM size, port openness, IOMMU directive
  (none on the host cmdline), or `set_device` ordering.
