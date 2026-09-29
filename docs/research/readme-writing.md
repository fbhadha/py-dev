# Research: what a good README contains, and what GitHub renders

Verified 2026-09-28 by fetching each page below. The question: what should this repo's README contain, in what order, how long, and which visuals can it rely on?

## What goes in, and in what order

- GitHub names five things a README answers: what the project does, why it is useful, how to get started, where to get help, who maintains it. ([GitHub Docs, About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes))
- Standard Readme fixes the order: title, short description, table of contents, install, usage, contributing, licence. The licence is the last section. ([Standard Readme spec](https://github.com/RichardLitt/standard-readme/blob/main/spec.md))
- Standard Readme limits the short description to under 120 characters, on its own line, matching the repository's description on GitHub. (same spec)
- Standard Readme requires a table of contents unless the README is shorter than 100 lines. (same spec)
- Standard Readme's Contributing section must say where to ask questions, whether pull requests are accepted, and what a contribution must meet. (same spec)
- Make a README lists: name, description, badges, visuals, installation, usage, support, roadmap, contributing, authors, licence, project status. Install steps are written for a novice, with the required versions. Usage shows examples and the expected output. ([makeareadme.com](https://www.makeareadme.com/))

## Length

- Make a README: "too long is better than too short", and a long project moves detail to "another form of documentation" instead of cutting it. (makeareadme.com)
- GitHub cuts a rendered README off past 500 KiB. This repo's README is 28 KB, so the limit is not the problem. (GitHub Docs, About READMEs)

## One document, one need

- Diátaxis names four kinds of documentation, each for one need: tutorials (to learn), how-to guides (to get a task done), reference (to look something up), explanation (to understand). Documentation is organised around those needs. ([diataxis.fr](https://diataxis.fr/))

## Visuals and navigation on GitHub

- GitHub renders Mermaid in Markdown files, issues, pull requests, discussions and wikis, from a code fence whose language is `mermaid`. It also renders GeoJSON, TopoJSON and ASCII STL. ([GitHub Docs, Creating diagrams](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams))
- A Mermaid block holding the one word `info` prints the Mermaid version GitHub runs. (same page)
- GitHub builds an outline (a table of contents) from a Markdown file's headings, and relative links follow the branch being viewed. (GitHub Docs, About READMEs)

## Contributing

- GitHub reads `CONTRIBUTING.md` from `.github/`, then the root, then `docs/`. It links the file when someone opens an issue or a pull request, and shows a Contributing tab and sidebar link on the repository page. ([GitHub Docs, Setting guidelines for repository contributors](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors))

## What this repo has today (read from the tree, same date)

- `README.md`: 161 lines, 28,289 characters, no diagram, no table of contents, no Contributing section.
- No `CONTRIBUTING.md` in the root, `.github/` or `docs/`.
- A knowledge pack is selected by a fixed table in `skills/py-intake/SKILL.md` (step 1, the row "Packs"), which names each pack and the dependencies that select it. `packs/TEMPLATE.md` does not name that step.

## UNVERIFIED

- Art of README ([hackergrrl/art-of-readme](https://github.com/hackergrrl/art-of-readme)) answered 404 to a direct fetch. Its "cognitive funnelling" (broadest information first, narrowing to detail fewer readers need) is known here only from a search result's summary, not from the text.
- Mermaid does not render on PyPI or in most editors' plain preview. Not checked; this repo publishes no package, so only GitHub's rendering matters today.
