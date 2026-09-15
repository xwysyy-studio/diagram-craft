# Visual design for explanatory figures

## Explanation and fidelity

A figure should establish the objects being discussed and make their important
relationships visible. A module catalog needs grouping; a mechanism needs actions
and connections; a comparison needs a shared basis. Labels such as “platform”,
“processing”, or “capability” need enough context to explain their actual role.

Use layout to express information: containment for membership, aligned stages for
order, matched positions for comparisons, and an explicitly linked expansion for
local detail. Do not let decorative placement imply an unsupported dependency.
Do not draw a physical connection merely because two components share a section.

When state is central to the mechanism, show what is being changed: for example,
the current and candidate versions and the pointer that selects between them.
Place these objects near the operations that act on them. A consequential outcome
often reads more clearly as a nearby branch than as a distant footnote. Use a
local note when the relationship is already unambiguous; not every qualification
needs another node.

When adapting a document, maintain an internal list of the essential entities,
relations, conditions, and stated uncertainties. Check these against the figure
after layout changes. Do not create a second permanent requirements document
unless requested. An abbreviated label must keep its distinction from other
labels; a short caption may carry a necessary condition that does not fit a node.

## Size and typography

Design in approximate display pixels. A practical document starting point is a
1000-unit-wide composition, with height determined by its content. For a different
placement, adjust the composition and type together.

The apparent size is approximately:

```text
displayed_font = source_font * displayed_figure_width / exported_figure_width
```

Increasing PNG export resolution does not improve a label's apparent size when
the document scales that image back down. A 20-unit label in a 1600-unit drawing
appears about 10 pixels tall at an 800-pixel display width.

Suggested starting roles at roughly 1000 units of display width:

| Role | Starting size | Treatment |
| --- | --- | --- |
| Figure title, if useful | 26–30 | Dark, bold; omit if the surrounding document already supplies it |
| Section or panel title | 20–22 | Dark, bold; clear separation from content |
| Main node label | 18–20 | Short, specific names or actions |
| Explanatory text | 16–18 | Plain language; enough space for natural wrapping |
| Connector or auxiliary label | 14–16 | Readable contrast; keep essential conditions at body size when needed |

These are starting values, not universal thresholds. Use draw.io's default font
family for new figures and omit explicit font-family overrides unless the user
requests a different family. Do not download fonts. Size, weight, and spacing
provide the hierarchy. Technical abbreviations can remain in English; do not
force whole labels into monospace.

Give text real room. Estimate CJK glyphs near one font-size in width and typical
Latin glyphs around half a font-size, with line height around 1.3–1.4 times font
size. The estimate varies with font, weight, punctuation, and language. Validate
rendered labels when possible, especially long Chinese text and mixed scripts.

If text is crowded: improve phrasing without changing meaning, wrap at a semantic
boundary, widen or deepen the node, redistribute the panel, or expose detail in
a related subpanel. If the figure feels empty: tighten unrelated gaps or remove
redundant frames, not useful explanation. Never stretch a small diagram just to
fill a preset aspect ratio.

For a node containing both a name and an explanation, distinguish their roles.
Use the name in bold at the main label size and the explanation one size step
smaller in a secondary color. Simple `html=1` markup supports this while keeping
the text editable; see [xml.md](xml.md). Supporting text around 14–16 display
pixels can work in a compact node when it remains readable; give central
conditions more space rather than automatically treating them as small print.
Break longer text at a semantic boundary and inspect for isolated last characters
or words. Do not impose a character count or shrink the text until it fits.

## A restrained default palette

Use these roles consistently unless the user or existing document supplies a
different style. Values are design defaults, not a palette-validation gate.

| Role | Color | Use |
| --- | --- | --- |
| Paper | `#FFFFFF` | Figure background |
| Ink | `#243247` | Main labels and important outlines |
| Secondary text | `#526175` | Supporting explanation |
| Connector | `#66788A` | Normal relationship lines |
| Node outline | `#9AAABA` | Ordinary node borders |
| Boundary | `#D8E0E8` | Subtle group outlines |
| Surface | `#F5F7FA` | Neutral groups or ordinary nodes |
| Main accent | `#147D78` | The focal mechanism or primary path |
| Accent surface | `#EAF5F3` | Light fill behind focal content |
| Caution | `#A56320` | A pending state or expected rejection that preserves the current state |
| Caution surface | `#FBF2E5` | Light fill for that state |
| Failure | `#A64236` | An actual execution error or failed operation |
| Failure surface | `#FAEEE9` | Light fill for that outcome |

Use ordinary modules mostly in neutral colors. Introduce accent where it conveys
focus or meaning. Do not color each box differently or rotate through a palette
to avoid adjacent equal colors. Text, shape, or labels must also communicate any
distinction carried by color. A decision does not automatically need a warning
color, and a terminal node does not automatically mean failure.

Prefer clean borders, modest corner radii, and no shadows or gradients by default.
Use icons only when they clarify a recognizable component; use native shapes
before external image assets. Do not add badges, decorative legends, or slogans
that compete with the explanation.

## Spacing and density

Start with 16–24 units of node padding, 24–32 units inside groups, and 40–64 units
between connected nodes when connector labels need room. Use a small consistent
grid, such as 8 units, for structural geometry. Text baselines and computed
connection points do not need forced grid rounding.

Align related nodes by meaningful rows, columns, or centers. Use matching sizes
for equivalent roles, allowing different sizes for genuinely different content.
Whitespace should separate topics, reserve connector corridors, or establish
hierarchy. Avoid arbitrary gaps and invisible spacer vertices used to force
export bounds; derive page bounds from real content and use export borders.

No fixed node budget applies. Inspect whether readers can follow relationships
at the chosen size. Grouping, local expansions, and linked panels often preserve
both detail and readability. If a complete explanation cannot fit the requested
frame, explain the tradeoff rather than quietly dropping conditions.

## Connectors and annotations

Give each connector a clear meaning. Label ambiguous relations with verbs such
as “writes”, “reads”, “publishes”, or “acknowledges”; match the document language.
For branches, label the condition on its own outgoing edge near the decision.
Prefer a short question inside a diamond, using a rectangle when a longer
condition would be more readable there.

Choose an edge convention deliberately. Call or action arrows start at the actor
and point to the object acted on; data-flow arrows follow the data and can name
the payload. A sequence of actions is a different convention and should identify
who performs them. Avoid implying that a store performs a worker's status update
merely because the store is the preceding box. Keep the convention consistent
within a view, and explain a necessary mixture.

Place a qualifying note beside the element it qualifies, not beneath a different
outcome. If the reader needs to follow a branch to understand the consequence,
draw that branch and its outcome rather than relying on distant annotation.

Keep labels off strokes with sufficient offset. Use a background matching the
surface behind the label when masking is needed; an already clear off-line label
does not need an opaque white patch.
Do not let labels collide with boxes or each other. Separate ports when multiple
edges approach one side of a node. Reserve return paths outside the main flow.
Avoid shared segments unless they intentionally depict a shared bus, which should
be identified as such. Crossings are still crossings when a line-jump decoration
is added; fix the layout when a clearer arrangement is possible.

Draw architectural group boundaries softly enough that they do not compete with
the operational path. A detail panel should say which part it expands, and a
dashed link should be identified as an expansion rather than an operational call.

## Inspect the actual figure

At the intended display size, follow the figure without referring back to the
source. Can you identify the subject, start where appropriate, follow the important
relationships, and understand each condition? Then compare against the source.
Check crowded labels, isolated fragments, overlong empty connectors, unexplained
color changes, and detail that became unreadable after scaling.

Source checks cannot establish final font metrics, renderer routing, or visual
balance. If rendered inspection is unavailable, state exactly that limitation.
