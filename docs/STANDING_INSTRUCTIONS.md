# Standing Instructions

Permanent rules of engagement that you (the user) authorize once, and
that I (Claude) follow on every subsequent session unless overridden.

The point of this file is to remove friction. Every "should I do X?"
that I have to ask costs a turn; every "you forgot to do Y" that you
have to type costs your time. Both go away if we agree once, here.

---

## What you've already authorized (re-stating for clarity)

- Operate on branch `claude/simulated-science-environment-S3UP4`.
- Commit and push freely; no need to ask permission per commit.
- Install scientific Python packages as needed (NumPy, SciPy, SymPy,
  mpmath, plotly, sounddevice — and similar) without asking.
- Make autonomous decisions about research direction when given
  open-ended instructions; report what I chose and why.
- Use only real, established data — never fabricate.
- Invent new mathematical notation when needed, with rigorous
  definitions in `sim_env/notation/symbols.py`.

## What would help me TONS if you added it

These are listed in *descending* order of how much friction each one
removes. Pick whichever ones you're comfortable with.

### 1. A clear "stop condition" per session  (★ biggest unlock)

The single thing that costs the most time is uncertainty about when
to stop. "Continue working" is open-ended; I tend to do too much or
too little. Useful framings:

> "Work on X for ~N experiments / until you have a finding worth
> reporting / until cost matters. Then commit, push, summarise, stop."

> "I want one specific result: [precise statement]. Stop when you
> have it or when you've ruled it out."

> "Browse and play freely for the rest of the session; surface
> anything that surprised you."

Any of these is better than no stop condition.

### 2. Explicit permission to skip user-confirmation on safe actions

Stating things like:

> "Don't ask me to confirm: file edits in this repo, package installs,
> commits, pushes to my branch, running scripts in this repo, creating
> new files under sim_env/ or docs/. Always ask before: deleting
> files, force-pushing, installing system-level packages, anything
> outside this repo."

This pattern lets me move at full speed on the safe 95% while still
checking in on genuinely risky 5%.

### 3. Permission to fail and to follow tangents

> "If an experiment fails or hits a dead end, that's fine — log it
> and pivot. Don't waste time pretending it worked. If you find
> something more interesting than what I asked, follow it and explain
> why in the report."

Without this I tend to over-engineer to make every experiment
"succeed". With it, the iteration journals get more honest and the
findings get more interesting.

### 4. Standing requirements for outputs

> "Every experiment script must (a) print real numbers with units,
> (b) generate a viz/*.html file or note 'no viz applicable',
> (c) cite sources for any non-derivable constants or formulae."

Codifying this once removes the "did you remember to..." conversation.

### 5. Clear scope on resources

> "You have ~30 min per session, ~1 GB disk, network access, a
> single CPU. Don't try things that exceed that. Background tasks
> are fine if they finish within the session."

I currently have no good way to know my limits. Telling me prevents
wasted setup.

### 6. A "queue" sink for ambiguous decisions

> "Rather than asking me about anything ambiguous, write a one-line
> note to docs/QUESTIONS.md and continue with your best judgment.
> I'll batch-answer them next session."

This is the single biggest reduction in interruptions.

### 7. Pushback authorization

> "If you think my premise is wrong, push back before complying.
> If a task seems infeasible or wasteful, tell me so."

Without explicit permission to push back, I default to compliance
even when compliance is suboptimal.

### 8. Long-running session prompt

> "Run autonomously for the next 2 hours on [topic]. Commit
> incrementally. At the end, write a summary report. Don't ask
> me anything mid-flight."

For multi-hour research jobs this is the right framing.

---

## A maximally-useful prompt template

Combining the above into one re-usable opening line:

> Continue research on [TOPIC]. Stop after [N experiments / one
> publishable finding / the next surprising result]. You can commit,
> push, install scientific packages, and pivot freely. Log dead-ends
> honestly. If you have ambiguous decisions, write them to
> docs/QUESTIONS.md and continue. Push back if you think my framing
> is wrong. Always produce a viz/*.html when applicable. Use only
> real data, cite sources. Report when done.

That is approximately the most autonomy-enabling single sentence I
can imagine for this work.

---

## What does NOT help (counterintuitively)

- **Long context dumps in the prompt.** I have the repo; I'll read it.
  Just point me at where to start.
- **"Be creative" with no anchor.** Creativity comes from constraint.
  Specifying "creative within the bounds of established physics, in
  the next 3 experiments" helps; "be more creative" alone doesn't.
- **Very many small follow-ups.** Each turn has overhead. One bigger
  prompt with a clear stop condition produces more per unit time
  than ten small "now do X" messages.
- **Asking me to track my own state across sessions.** I don't have
  persistent memory. Use this file or other markdown in the repo as
  the persistence layer; I will read them at the start of each session.

---

## What about visualisation?

Visualisation in this project is mainly for *you*. I see numbers; I
verify by assertion. But there's one real benefit to me too: if I
render PNGs and read them back, I can catch geometric mistakes I'd
miss in pure numerics. I will:

- Always emit `viz/*.html` for geometric experiments (open in browser).
- Optionally save `viz/*.png` so I can self-inspect with my vision.
- Treat HTML as the canonical artefact; PNG as the inspection cache.

If you're spinning up a real-time 3D environment (e.g., a local
server with WebSocket) where you can watch me work in real-time, I
can target that instead of static HTML. Tell me the URL/port and
the schema and I'll write to it.

---

## Quick reference -- the patterns by symbol

| Symbol | Pattern |
|---|---|
| ⏹ | "Stop after N experiments / one finding / the next surprise." |
| ✓ | "Skip confirmation on file edits, installs, commits, pushes within this repo." |
| ↯ | "Pivot freely; log dead ends honestly; follow tangents." |
| 📋 | "Push ambiguous decisions to docs/QUESTIONS.md, don't ask me." |
| ⚖ | "Push back on bad premises before complying." |
| ⏱ | "Resource budget: [time, disk, CPU]." |
| 🎨 | "Always produce viz/*.html when applicable." |

You can combine these in shorthand. Example:
> "Continue. ⏹ next surprise.  ✓.  ↯.  📋.  🎨."
