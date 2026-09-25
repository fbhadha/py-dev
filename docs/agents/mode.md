# Agent mode

The skills read this file at session start. One key per line; unknown keys are ignored.

mode: guide
explain: decisions
unattended: never

<!--
mode        guide is the only mode in v1. partner is reserved.
explain     decisions (default): the full reasoning at every decision and plan,
            before and after each step, and a verdict for each command.
            teach: also what each command does and the idea behind each rule.
            brief: one sentence before and after a step; decisions keep their reasons.
unattended  never (default), or ticket:<id> to allow one unattended run on that
            ticket, which must come from a grilled spec and must end in a pull
            request. the agent clears the value when the run ends.

There is no file guard to configure. Work happens on a branch; main changes only
by a merge you said yes to, and the plugin's hook asks before anything that lands
on main. A person can set PYTHON_DEV_GUARD=off in their own shell before a
session to silence that ask; set inside a command by the agent it is denied.
-->
