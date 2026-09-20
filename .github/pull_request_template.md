## What changes

<!-- One or two sentences. Which skill, template, script or doc, and why. -->

## Type of change

- [ ] Persona (`agents/python-dev.md`)
- [ ] A skill or its templates
- [ ] Baseline check or template (`skills/py-baseline/templates/`)
- [ ] Upstream pin (`upstream.json`), in its own commit
- [ ] Knowledge pack (`skills/pack-<domain>/`)
- [ ] Docs, ADR or research
- [ ] Repo tooling

## Checklist

- [ ] `python scripts/validate_skills.py` passes
- [ ] `python scripts/check_invocation_sync.py` passes
- [ ] `python scripts/check_upstream_skills.py` passes (if `upstream.json` or any skill name we call changed)
- [ ] Every claim about a tool or an upstream skill was verified by running it; `docs/research/` says what and when
- [ ] No second store for anything derived from the code (ADR 0005)
- [ ] Bundled scripts contain no obfuscated or remote-execution code
- [ ] DCO: I have the right to submit this under Apache-2.0 (`git commit -s`)

## Notes for reviewers

<!-- Edge cases, what you tested it on, anything UNVERIFIED. -->
