---
name: video-graphics-pin
description: Manage the pinned HyperFrames version and the skill pack in .claude/skills. Use when graphics renders break or come out blank, when a render capture dies, when the user asks to update/upgrade HyperFrames or the skills, when skills-lock.json fails verification, or before touching anything under .claude/skills.
---

# The HyperFrames pin

Graphics and captions render through **HyperFrames, an npm package** - not a repo
you clone. It is installed through its own CLI and pinned to one version, and
that version is passed on every single invocation.

```bash
workflows/scripts/hf_pin.sh version           # what we are pinned to
workflows/scripts/hf_pin.sh verify            # re-hash every SKILL.md vs the lock
workflows/scripts/hf_pin.sh install           # (re)install at the current pin + sync + lock
workflows/scripts/hf_pin.sh sync              # copy installed skills in, rewrite the lock
workflows/scripts/hf_pin.sh bump 0.7.69       # move the pin, deliberately
```

The pin lives in exactly one place: `VS_HF_VERSION` in `workflows/lib/common.sh`.
Every script reaches HyperFrames through `vs_hf`, which always spells the version
out.

## Why it is pinned

`npx hyperframes` without a version floats to latest, and past releases have
broken the composition contract mid-job:

- **0.7.42** started requiring `data-start`, `data-composition-id`, `data-width`
  and `data-height` on the root composition. Without them the render capture
  dies - it does not warn, it does not degrade.
- **0.7.67** shipped a change that was reverted in **0.7.68**.

We start at **0.7.68** and move the pin one part at a time. Contract breakages
land silently: the capture dies, or the comp renders blank, not a clean error.

## Moving the pin

`hf_pin.sh bump <version>` rewrites the pin, reinstalls through the CLI,
re-syncs, and re-locks. Then, in order:

1. pick the **smallest** graphics part in the active job
2. `workflows/scripts/hf_render.sh <job> <part>` - that part only
3. eyeball it against the previous render before touching any other part
4. if it broke: `hf_pin.sh bump <old-version>`, and write what broke into
   `CLAUDE.md` > Lab Notes

Never bump and re-render everything in one go. That is how a regression gets
baked into a whole video before anyone sees it.

## The skill pack and skills-lock.json

`npx hyperframes@<pin> skills` installs the pack; `hf_pin.sh sync` copies it into
this repo's `.claude/skills/` and rewrites `skills-lock.json`. Each entry records:

- `source` - where it came from
- `sourceType` / `package` / `version` - the npm package and pin
- `skillPath` - the path in this repo
- `computedHash` - sha256 of that SKILL.md's bytes

The hash is a tripwire. `hf_pin.sh verify` re-hashes everything and fails if a
SKILL.md changed without going through the CLI.

**Never hand-edit a file under `.claude/skills/`.** If a skill needs to change,
it changes upstream and comes down through `hf_pin.sh install`. Local edits are
invisible to the lock's intent and are silently destroyed by the next sync.

The roster of skills this release owns lives in
`workflows/hyperframes-skills.txt`, written from the installer's own output -
not guessed, not hand-maintained.

Entries from other packs (higgsfield, hand-written local skills) are read,
preserved and re-verified by the same lock, never clobbered.

## The renderer

```bash
npx hyperframes@<pin> doctor          # what is missing
npx hyperframes@<pin> browser ensure  # download the headless browser
```

`hf_pin.sh install` runs both. `./check-setup.sh` reports whether the browser
cache is present.

## GSAP is vendored, not fetched

Compositions load `shared/gsap.min.js` from disk. A composition that fetches GSAP
from a CDN at render time renders silently wrong the day the network says no:
the capture succeeds, every tween is missing, and the only trace is a
`sub_timeline_script_failure` warning in the log. Refresh it with
`workflows/scripts/vendor_gsap.sh [version]`.

## When a render breaks

1. `workflows/scripts/hf_render.sh <job> --check` - lint, runtime, layout,
   motion and contrast, in seconds
2. `hf_pin.sh verify` - did a skill or the pin drift?
3. check the root composition has all four `data-*` attributes plus
   `data-start="0"` - the builder emits them, so if they are missing someone
   hand-edited a generated file
4. look for `sub_timeline_script_failure` in the render log - that is the
   missing-GSAP signature
