# Optional local rendering

The editable `.drawio` source is always retained. Rendering improves inspection
and produces document-ready images, but is not a dependency of source generation.
Do not install software, change model settings, or upload diagrams automatically.

## draw.io Desktop

On macOS, first check an existing installation at:

```text
/Applications/draw.io.app/Contents/MacOS/draw.io
```

The executable may also be on `PATH`. Read its `--help` to verify supported options
in the installed version. When available, an ordinary local export is:

```bash
"/Applications/draw.io.app/Contents/MacOS/draw.io" --export --format png \
  --border 20 --scale 2 --output figure.png figure.drawio
```

Use SVG or PDF when requested and supported. Follow the installed version's page
options for multipage diagrams; explicitly choose the intended page or export each
required page, rather than assuming one preview covers the file. Embedding source
XML in a preview is optional and does not replace keeping the `.drawio` file.

Prefer the native renderer to reimplementing the diagram in another drawing
library. An independently drawn SVG cannot prove that the `.drawio` renders well.
Do not globally auto-layout an intentionally composed figure just to export it.

## When only a browser editor is available

The user can open the file in their approved draw.io editor and export it there.
Browser automation may assist only if it is already available and allowed for the
material. A company-hosted editor, Desktop, and a public website have different
data boundaries. Do not assume “browser-based” means an external service is allowed.

If no allowed renderer is available, deliver the source and say that import/export
and visual inspection were not performed. If export succeeds but the model cannot
view images, say that rendering succeeded and visual inspection remains unverified.
Report a failed rendering attempt instead of silently swapping services.

## Visual acceptance

Open the real exported image with the available image-viewing tool. Inspect both
the whole composition and its intended document display width. If the environment
supports it, a browser showing the exported image at that width is useful for
checking scaled readability. Do not judge only a very large source PNG or a small
thumbnail.

Check labels for clipping and awkward wrapping; inspect connector routes, their
endpoints, and label placement. Check meaningful group boundaries, reading order,
balanced spacing, and consistency with the source material. For editable-group
examples or substantial native editing changes, verify moving a node or group and
saving/reopening a copy in the actual editor when available.

Reference: [draw.io Desktop](https://github.com/jgraph/drawio-desktop).
