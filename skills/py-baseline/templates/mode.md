# Agent mode

The skills read this file at session start. One key per line; unknown keys are ignored.

mode: guide
explain: before-and-after
unattended: never

<!--
mode        guide is the only mode in v1. partner is reserved.
explain     before-and-after (default) or after-only.
unattended  never (default), or ticket:<id> to allow one unattended run on that
            ticket, which must come from a grilled spec and must end in a PR.
            py-implement clears the value when the run ends.
-->
