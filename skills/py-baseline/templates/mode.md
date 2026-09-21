# Agent mode

The skills read this file at session start. One key per line; unknown keys are ignored.

mode: guide
explain: before-and-after
unattended: never

<!--
mode        guide is the only mode in v1. partner is reserved.
explain     before-and-after (default) or after-only.
unattended  never (default), or ticket:<id> to allow one unattended run on that
            ticket, which must come from a grilled spec and must end in a pull
            request. the agent clears the value when the run ends.

There is no file guard to configure. Work happens on a branch; main changes only
by a merge you said yes to, and the plugin's hook asks before anything that lands
on main. PYTHON_DEV_GUARD=off silences that ask for one session.
-->
