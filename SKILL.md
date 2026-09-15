---
name: drawio-craft
description: >-
  Create or edit native, editable draw.io diagrams that explain technical ideas,
  system designs, mechanisms, and workflows through clear visual structure.
  Use for .drawio files, technical explanatory figures, architecture diagrams,
  flowcharts, and requests to improve diagram layout, connectors, typography,
  or colors. Preserve a requested alternative format; statistical plots and
  raster illustrations belong to their own tools.
---

# Drawio Craft

Make the figure carry the explanation. A reader should understand the important
parts, their relationships, and how the mechanism works from the diagram itself.
Use the source material and intended reader to choose the necessary detail and
visual structure. Translate relationships into the picture rather than assigning
one box to every sentence.

Deliver native editable `.drawio` XML. Work with local files and bundled resources;
image generation, browser automation, network access, and a running server are not
required. Python 3.9+ enables the optional standard-library preflight helper.

## Read the relevant resources

Resolve `{skill_dir}` to the directory containing this `SKILL.md`, wherever it is
installed. Resource paths below are relative to that directory.

| Resource | Read when |
| --- | --- |
| [Design](references/design.md) | Creating a figure or substantially changing its presentation |
| [Layouts](references/layouts.md) | Choosing a composition and planning coordinates and routes |
| [XML](references/xml.md) | Authoring native cells, groups, labels, and connectors |
| [Editing](references/editing.md) | Modifying an existing diagram, including compressed or multipage files |
| [Rendering](references/rendering.md) | A local renderer is available or an image export is requested |

The examples in `assets/` are editable, fictional technical figures. Read the
closest example as a worked composition, not as a compulsory topology:

- `mechanism.drawio`: a system overview with an expanded publishing mechanism.
- `flow.drawio`: a main path, a decision, and an explicit failure outcome.
- `comparison.drawio`: two approaches compared on the same operation.

## Understand what the figure must explain

Read the user-specified material, including conditions and qualifications needed
to interpret it. Identify the entities, actions, directed relationships, grouping,
and any mechanism the reader must follow. Distinguish a proposed design from
observed behavior; do not invent metrics, guarantees, benefits, or components.

Choose a reading structure that fits those relationships: a flow, a layered
system, a comparison, an overview with a local expansion, or another suitable
composition. These are options, not required panels.

For a long document, select information according to the requested figure's
purpose while keeping the necessary causal and conditional links. Preserve
information that changes the meaning. Group related detail, show a local
expansion, or use linked panels before cutting content or shrinking text. There
is no fixed node count, label character limit, or compulsory single-page limit.
If a meaningful omission or split conflicts with the requested scope, ask.

State the intended composition and output briefly, then proceed when the input is
sufficient. Ask only about ambiguities that would change the explanation. Do not
require an ASCII proposal, approval round, or separate specification file for
every diagram. Preserve the user's terminology and language.

## Design at the size people will read

Follow [design.md](references/design.md) and the selected section of
[layouts.md](references/layouts.md). Establish the intended display width before
laying out the diagram. In the absence of a specified placement, use about
1000 CSS pixels wide as a working document preview and state that assumption.
This is a design reference, not a guaranteed size in the user's document system.

Plan node sizes and connector corridors together. Compute shared row/column
positions, group padding, and page bounds from the content. Avoid placing all
nodes first and improvising edges afterward. Keep the main explanation visually
continuous; place secondary branches where they can be followed without weaving
through unrelated modules.

Use readable labels, restrained color roles, and purposeful whitespace. When a
label will not fit, change wrapping, box size, or composition before making the
type smaller. Keep important conditions close to the element they qualify.
When a mechanism depends on changing state, make that state visible where it
clarifies the explanation. Place consequential outcomes next to their decision
or action, with an explicit relationship when proximity alone is ambiguous.
Group titles and local annotations can carry information without extra boxes or
arrows; preserve a connector whenever its relation would otherwise be ambiguous.

## Author and check

Generate an uncompressed `<mxfile>` containing native vertices and edges using
[xml.md](references/xml.md). Keep text editable and attach connectors to cells
where practical. A single embedded image of the whole figure does not satisfy
native editability. Preserve the `.drawio` source after any export.

Save to the user's requested location or the project's existing diagram folder.
If neither exists, use a topic-relevant filename in the working directory and
state it. Do not change application settings, install dependencies, create a
new repository, or upload project material as a side effect of drawing.

When Python is available, run:

```bash
python3 "{skill_dir}/scripts/drawio.py" check figure.drawio --display-width 1000
```

Use the chosen display width rather than mechanically copying `1000`.
Fix structural errors. Review each warning against the actual figure: text-fit,
overlap, and route estimates are not proof of a rendering defect. The helper
understands groups, page-local IDs, compressed pages, and explicitly routed
polylines; it does not reproduce draw.io's automatic routing or font rendering.
Do not delete relationships, shrink fonts, or exempt real defects merely to
obtain a clean report. If Python is absent, check the source and state that the
script was not run rather than claiming an equivalent automated check.

When a renderer is available, follow [rendering.md](references/rendering.md).
If image inspection is available, inspect the actual draw.io output at the
intended display size. Check the reading order, labels, routes, balance, and
faithfulness to the source. Correct observed defects and inspect the changed
result. Do not start browser services or switch to an external renderer just to
satisfy a checklist; any external processing must respect the user's data policy.

## Deliver a useful figure

Give the `.drawio` path and any requested exports. Briefly identify what the figure
explains, relevant assumptions or omissions, and the checks actually performed.
Distinguish source validation, renderer import/export, and visual inspection.
Without a renderer or image-reading capability, deliver the source with that
specific limitation. Never present a heuristic check as visual approval.

When revising, read the latest file and preserve unrelated labels, relationships,
pages, and manual adjustments. Follow [editing.md](references/editing.md) rather
than regenerating the entire diagram for a local change.
