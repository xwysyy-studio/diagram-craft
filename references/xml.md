# Native draw.io authoring

## Document and page structure

Use readable, uncompressed XML for new files:

```xml
<mxfile host="app.diagrams.net">
  <diagram id="main" name="Main">
    <mxGraphModel grid="1" gridSize="8" page="1" pageScale="1"
      pageWidth="1000" pageHeight="640" background="#FFFFFF" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

IDs are unique within a page. Different pages may reuse cell IDs. Use descriptive
IDs for new nodes and edges to make local changes easier. Preserve existing IDs
when editing. All non-root cells need a real parent; an ordinary new cell normally
uses `parent="1"`.

Use an XML serializer when generating repetitive elements. Attribute text must
escape `&`, `<`, `>`, and quotes correctly. Plain multiline values use `&#xa;`.
If using `html=1`, the HTML markup itself must be escaped for its enclosing XML
attribute. Use simple HTML when it serves a name/description hierarchy; avoid
unnecessary nested layout markup and unrelated inline overrides.

## Nodes

```xml
<mxCell id="indexer" value="Build index&#xa;Validate candidate version"
  vertex="1" parent="1"
  style="rounded=1;arcSize=8;whiteSpace=wrap;html=0;fillColor=#EAF5F3;strokeColor=#147D78;strokeWidth=1.5;fontColor=#243247;fontFamily=Helvetica;fontSize=18;spacing=12;">
  <mxGeometry x="360" y="180" width="240" height="88" as="geometry"/>
</mxCell>
```

Native text, rectangles, diamonds, cylinders, and connectors keep the diagram
editable. Use a shape because of its meaning, not to decorate each node differently.
A rhombus has less usable label space than its bounding rectangle. A longer
condition may need a larger diamond or a clearly labeled rectangular decision.

For a two-tier label, set `html=1` and use a small amount of escaped markup:

```xml
value="&lt;b&gt;查询服务&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 16px;&quot; color=&quot;#526175&quot;&gt;固定活动版本后读取数据&lt;/font&gt;"
```

Use the cell's `fontSize` for the name and an explicit smaller size for the
explanation. Choose sizes for the actual display width. Keep markup simple, such
as `b`, `br`, and a `font` or `span`, and check actual wrapping. Write each style
key once so future edits do not encounter hidden earlier values.
Put named styles such as `swimlane` before the explicit property overrides. Native
draw.io applies those named defaults in order; placing `swimlane` after `fontSize`
can reset the label size even though the XML still contains the requested size.

For standalone titles or annotations, use native text cells with `fillColor=none`
and `strokeColor=none`; give them real geometry and a deliberate alignment. Keep
annotations out of connector corridors.

## Real groups

```xml
<mxCell id="publisher" value="Publishing" vertex="1" parent="1"
  style="swimlane;horizontal=1;startSize=48;container=1;collapsible=0;rounded=1;arcSize=8;fillColor=#F5F7FA;swimlaneFillColor=#F5F7FA;strokeColor=#D8E0E8;fontFamily=Helvetica;fontSize=20;fontColor=#243247;align=left;spacingLeft=20;">
  <mxGeometry x="40" y="120" width="440" height="220" as="geometry"/>
</mxCell>
<mxCell id="publish" value="Switch active version" vertex="1" parent="publisher"
  style="rounded=1;whiteSpace=wrap;html=0;fillColor=#FFFFFF;strokeColor=#147D78;fontFamily=Helvetica;fontSize=18;fontColor=#243247;spacing=12;">
  <mxGeometry x="24" y="80" width="240" height="72" as="geometry"/>
</mxCell>
```

Child coordinates are relative to the parent. Define the container before its
children. Do not compare a child's local rectangle with a top-level rectangle
without resolving the parent translation. Containment is intentional, not a
node-overlap defect. A plain decorative rectangle behind unrelated top-level
cells is not automatically an editable group.

## Connectors

```xml
<mxCell id="build-to-publish" value="validation passed" edge="1" parent="1"
  source="build" target="publish"
  style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=0;endArrow=block;endFill=1;strokeColor=#66788A;strokeWidth=1.5;fontFamily=Helvetica;fontSize=15;fontColor=#526175;labelBackgroundColor=#FFFFFF;exitX=1;exitY=0.5;entryX=0;entryY=0.5;">
  <mxGeometry relative="1" as="geometry">
    <mxPoint x="0" y="-12" as="offset"/>
  </mxGeometry>
</mxCell>
```

An edge needs `mxGeometry`, even if it has no waypoints. For a fixed polyline,
use `edgeStyle=none` and add an `Array as="points"` of `mxPoint x/y` waypoints.
The label position `mxGeometry x` runs along the route; the perpendicular label
distance is `y`, with an optional Cartesian `offset`. Check the result because
route direction affects label placement.

Prefer connected `source` and `target` cells. Native floating connectors may
instead provide `sourcePoint` and/or `targetPoint` for the corresponding unattached
end. They are valid for lifelines and annotations; do not force them to refer to
fake nodes. A valid endpoint is either an existing cell or an explicit point.

An arrowhead denotes a directed relationship. Use `endArrow=none` for boundaries
or explanation links where a directed operation is not intended. Label the
meaning of dashed lines when it is not already clear.

## Existing files and supported preflight input

Native files may contain a raw `mxGraphModel`, an `mxfile` with several pages, or
compressed page text. Object wrappers can carry the ID and label around a child
`mxCell`. The bundled helper reads these forms and preserves wrappers when
unpacking. Embedded `.drawio.png` and `.drawio.svg` containers must first be opened
and saved as `.drawio` by an available draw.io editor; the helper does not pretend
to decode arbitrary images.

Do not rewrite unrelated metadata or styles merely to match a new-file example.
Reference: [draw.io XML guidance](https://github.com/jgraph/drawio-mcp/blob/main/shared/xml-reference.md).
