# Compositions and routing

Choose the arrangement from what the reader needs to understand. Do not load all
examples or force every request into one of them.

## Compute positions together

For a row with node widths `width[i]`, gaps `gap[i]`, and left padding `pad`:

```text
x[0] = pad
x[i + 1] = x[i] + width[i] + gap[i]
row_width = sum(width) + sum(gap)
```

Use the same approach vertically. Choose the gap to accommodate its relation
label and any turn, not just the boxes. Size a group from the union of its children
plus a title band and padding. Size the page from all visible content and intended
margins. Keep a small coordinate table internally; do not write a separate layout
format or generate an extra source of truth unless the task needs one.

## Main flow with branches

Suitable for a process whose order is the explanation. Keep the primary path on
one axis. Put a branch in a reserved adjacent row or column, with its label close
to the divergence. Align a merge with its participating paths. Reserve an outer
corridor for feedback or retry only when present in the source.

When the row becomes too wide, use meaningful stages or a vertical composition.
Avoid automatic snake layouts that reverse reading direction just because a
node count was exceeded. The figure can be tall when a vertical explanation is
clearer; it does not need to fill a slide ratio.

Worked example: `../assets/flow.drawio`.

## Overview with a local mechanism

Suitable when readers need both the system context and the behavior inside one
part. Make the overview legible independently, then explicitly identify the
expanded component. Give the local mechanism enough space to show its actions,
conditions, and outputs. Keep the same naming across the overview and expansion.

Panels can be beside or below one another according to available width. They
need not have equal sizes. Use a labeled expansion link or matching panel label
so the reader can distinguish explanation links from runtime communication.
Do not duplicate an entire system in the detail panel.

When possible, put the expanded component near the detail panel so a short
explanation link does not cross another path. A store shared by several paths can
span their rows, with each path aligned to the state or interface it touches.
These arrangements are useful when they clarify the source; keep the reading
order that best serves the actual mechanism.

Worked example: `../assets/mechanism.drawio`.

## Architecture and grouping

Suitable for components, responsibility boundaries, and data or control paths.
Place components by their major relationships. Layers express abstraction or
deployment only when that meaning is supported. Do not call every row a layer.

Use actual group parents when elements should move together. A group title names
its scope; child labels name specific roles. Distinguish membership from execution
order, and control signals from data movement when that matters to the source.
Keep cross-group connectors in shared corridors rather than through other nodes.

For hub-like systems, a rectangular hub-and-spoke arrangement may be clearer than
a radial layout, especially with longer Chinese labels. Use the topology that
explains the actual relationships without creating needless diagonal routes.

## Comparisons and changes

Suitable for contrasting approaches or showing an actual change. Keep comparable
stages aligned and use the same language, scale, and endpoint assumptions on both
sides. A new mechanism may receive accent; unchanged roles remain neutral.

Label what is being compared. Preserve caveats and tradeoffs provided by the
source. Do not invent a performance number, “better” marker, or a failing baseline
to make the comparison more dramatic. Different topology is allowed when it is
the substance of the difference; artificial symmetry must not falsify behavior.

Use comparable visual weight for equivalent steps. If one side needs local notes,
reserve a corresponding area on the other side rather than making all its step
boxes arbitrarily wider. Give the actual distinguishing behavior, such as queries
pausing or continuing, a clear place on both sides of the comparison. Show a
conditional outcome explicitly where its relationship would otherwise be unclear.

Worked example: `../assets/comparison.drawio`.

## Sequence, ownership, and state

For time-ordered messages, align participant headers and use shared message rows.
Lifelines are not process nodes. Returns and asynchronous messages need consistent
notation and enough vertical space for labels. Show condition fragments when they
carry necessary behavior; do not invent a formal UML claim for an informal sketch.

For ownership, use lane labels and place each step in its responsible lane.
Native group coordinates are relative to their parent. Keep an explicit overall
reading direction while crossing lane boundaries. Avoid a full role-by-stage
matrix when the actual story needs only a few handoffs.

For state transitions, retain state names, guards, and transition direction. A
cycle is meaningful here; do not remove it to obtain an acyclic layout.

## Explicit routes and renderer routes

For a short, aligned connection with an unobstructed corridor, use native
`orthogonalEdgeStyle` with explicit exit and entry ports. Native rerouting is
useful when people move nodes later, but it can add bends; inspect it if possible.

For a carefully planned return or cross-panel connector, use a polyline with
explicit waypoints and `edgeStyle=none`. Consecutive horizontal or vertical
segments give an exact orthogonal path without asking the renderer to infer one:

```text
source east port = (source.x + source.width, source.y + source.height / 2)
target north port = (target.x + target.width / 2, target.y)
route = source_port, (corridor_x, source_port.y),
        (corridor_x, corridor_y), (target_port.x, corridor_y), target_port
```

Choose corridor coordinates outside unrelated node rectangles with room for
labels. When a route crosses a panel boundary, choose a clear entry point that
also avoids the panel's heading text. Store waypoint coordinates relative to the
edge's parent. If endpoints
belong to different groups, parenting the edge to the common containing layer
often makes these coordinates easier to reason about. Avoid placing a waypoint
at each pixel or adding redundant points along a straight segment.

The preflight helper checks explicit polyline corridors, not the full draw.io
router. A clean preflight is not evidence that an automatically routed edge or
its label looks correct. Do not freeze all edges into elaborate polylines when
native simple connectors already serve the diagram well.
