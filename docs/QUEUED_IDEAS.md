# Queued Ideas

Concepts proposed but not yet built. Saved here so they're not lost.

---

## The Docker + cron sandbox (proposed in session, deferred)

A real sandbox for *experiments* (not for me, since I'm stateless).
Three components:

1. **A Docker container** (Dockerfile in the repo) with Python +
   scientific libraries, no inbound network, optional outbound
   (the user flips a switch). Any experiment I run goes inside it.
   If a script tries to touch the host, it can't.
2. **A research user account** (UNIX user with restricted
   permissions) that I run as. Easy for the user to revoke. Can't
   touch `~`.
3. **A scheduled batch job** (cron or systemd) that runs
   `python -m sim_env.batch` daily with a CPU/disk/network budget,
   processes a queue I leave in the repo, writes results back. This
   is the closest thing to "Claude works while you sleep" — but it's
   just a cron job running code I committed earlier, not an LLM
   thinking autonomously.

A `docs/PERMISSIONS_MANIFEST.md` would also help: a single
human-readable file listing exactly what I can and cannot do in
this repo. The user audits it; deviations become obvious.

**Why we deferred it:** the realistic risks in our setup
(bug in a script, accidental long-running job, package with
malware) are mitigated by version control + sensible review,
not by AI containment. The container would be useful for risky
experiments specifically, but isn't the highest-leverage build.

**Status:** queued. Build when there's a specific risky experiment
that justifies the isolation.

---

## Workflow improvements I pitched alongside this

1. **Auto-generated session brief** -- `make brief` regenerates
   `docs/SESSION_BRIEF.md` from repo state.
2. **Structured findings ledger** -- `findings.jsonl` with one
   record per numerical result, queryable across experiments.
3. **Standing rule: literature-search before claiming novelty.**
4. **`docs/USER_TASKS.md`** -- running list of concrete actionable
   items wanted from the user.

Of these, (3) is a behavior change I should adopt unilaterally.
The rest are deferred unless the user explicitly wants them.
