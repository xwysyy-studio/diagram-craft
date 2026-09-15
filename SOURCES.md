# Sources and design scope

Drawio Craft combines native draw.io authoring with guidance for explanatory
technical figures. These projects informed the design:

| Source | Relevant material | Use in this project |
| --- | --- | --- |
| [FlowForge](https://github.com/wentong2022-arch/flowforge-skill/tree/7a210ccb6f3724f91e15d614726de0be25f9e1a6/skills/FlowForge) | Skill, layout formulas, themes, and examples | Shared coordinate planning, semantic color roles, optional rendered inspection |
| [drawio-generator](https://github.com/vibepm666/drawio-generator/tree/78fe12372c20736cda637291b4737323d2793682) | Native XML templates and Python validation workflow | Local editable delivery and lightweight source checking |
| [diagram-design](https://github.com/cathrynlavery/diagram-design) | Explanatory design guidance and rendered examples | Reading hierarchy, restrained emphasis, and attention to labels and connectors |
| [Official draw.io skill](https://github.com/jgraph/drawio-mcp/tree/main/plugins/codex/drawio/skills/drawio) | Native authoring and optional export workflow | Native format and renderer integration concepts |
| [draw.io XML reference](https://github.com/jgraph/drawio-mcp/blob/main/shared/xml-reference.md) | Cell, geometry, group, style, and edge syntax | File-format conventions |

The upstream projects have their own scopes and licenses. Their complete workflows
are not imported here. Drawio Craft's instructions, Python helper, and fictional
native examples were written for this repository; no upstream implementation,
template, screenshot, icon pack, or font is redistributed.

The figure's explanation and the user's source determine its complexity. This
project does not impose an upstream node-count budget, force one layout, or depend
on upstream services at runtime. Local default colors and typography are design
starting points, not claims about the only valid style.

For maintenance, consult the [draw.io embed protocol](https://www.drawio.com/docs/reference/embed-mode/)
when using an approved browser editor to check native rendering. The embed editor
is a development verification option, not a runtime dependency of the skill.
