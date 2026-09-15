#!/usr/bin/env python3
"""Read native draw.io files and preflight source without external dependencies."""

from __future__ import annotations

import argparse
import base64
import binascii
from dataclasses import asdict, dataclass, field
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
import sys
import unicodedata
from urllib.parse import unquote
import xml.etree.ElementTree as ElementTree
import zlib


def parse_xml(source: str) -> ElementTree.Element:
    if re.search(r"<!\s*(DOCTYPE|ENTITY)\b", source, re.IGNORECASE):
        raise ValueError(
            "DTD and entity declarations are not accepted in diagram input"
        )
    return ElementTree.fromstring(source)


def read_document(path: Path) -> ElementTree.Element:
    root = parse_xml(path.read_text(encoding="utf-8-sig"))
    if root.tag == "mxGraphModel":
        wrapper = ElementTree.Element("mxfile")
        page = ElementTree.SubElement(
            wrapper, "diagram", {"id": "main", "name": "Main"}
        )
        page.append(root)
        return wrapper
    if root.tag != "mxfile":
        raise ValueError(
            "Expected native mxfile or mxGraphModel XML, not an image or other format"
        )
    pages = root.findall("diagram")
    if not pages:
        raise ValueError("The mxfile has no diagram pages")
    for page in pages:
        if page.find("mxGraphModel") is not None:
            continue
        payload = (page.text or "").strip()
        if not payload:
            raise ValueError(
                f"Page {page.get('name', page.get('id', 'unnamed'))!r} has no graph"
            )
        try:
            if payload.startswith("<"):
                graph = parse_xml(payload)
            else:
                compressed = base64.b64decode("".join(payload.split()), validate=True)
                encoded = zlib.decompress(compressed, -15).decode("utf-8")
                graph = parse_xml(unquote(encoded, encoding="utf-8", errors="strict"))
        except (ValueError, zlib.error, UnicodeError, ElementTree.ParseError) as error:
            raise ValueError(
                f"Cannot decode page {page.get('id', 'unnamed')!r}: {error}"
            ) from error
        if graph.tag != "mxGraphModel":
            raise ValueError("Decoded page is not an mxGraphModel")
        page.text = None
        page.append(graph)
    return root


VOID_TAGS = {"br", "hr", "img", "wbr"}
BLOCK_TAGS = {"div", "p", "li", "tr"}


class LabelText(HTMLParser):
    """Flatten an html=1 label into (text, font_size) runs.

    Inline ``font-size: Npx`` declarations on nested tags change the size of
    their contents, so a name/description label estimates each line at its
    own size instead of the cell's base fontSize.
    """

    def __init__(self, base_size=None):
        super().__init__(convert_charrefs=True)
        self.runs = []
        self.sizes = [base_size]
        self.pending_boundary = False

    def handle_starttag(self, tag, attrs):
        if tag == "br" or (
            tag in BLOCK_TAGS and self.runs and not self.runs[-1][0].endswith("\n")
        ):
            self.runs.append(("\n", self.sizes[-1]))
            self.pending_boundary = False
        if tag in VOID_TAGS:
            return
        size = self.sizes[-1]
        for name, value in attrs:
            if name == "style" and value:
                match = re.search(r"font-size\s*:\s*([\d.]+)px", value)
                if match:
                    size = float(match.group(1))
        self.sizes.append(size)

    def handle_endtag(self, tag):
        if tag in BLOCK_TAGS:
            self.pending_boundary = True
        if tag not in VOID_TAGS and len(self.sizes) > 1:
            self.sizes.pop()

    def handle_data(self, data):
        if self.pending_boundary and self.runs and not self.runs[-1][0].endswith("\n"):
            self.runs.append(("\n", self.sizes[-1]))
        self.pending_boundary = False
        self.runs.append((data, self.sizes[-1]))

    @property
    def parts(self):
        return [text for text, _ in self.runs]


@dataclass
class Cell:
    identity: str
    element: ElementTree.Element
    label: str
    style: dict = field(default_factory=dict)

    @property
    def parent(self):
        return self.element.get("parent")

    @property
    def vertex(self):
        return self.element.get("vertex") == "1"

    @property
    def edge(self):
        return self.element.get("edge") == "1"

    @property
    def geometry(self):
        return self.element.find("mxGeometry")

    @property
    def text(self):
        if self.style.get("html") != "1":
            return self.label
        parser = LabelText()
        parser.feed(self.label)
        return "".join(parser.parts).strip()

    def runs(self, base_size):
        """Label text as (text, font_size) runs; sizes follow inline html styles."""
        if self.style.get("html") != "1":
            return [(self.label, base_size)]
        parser = LabelText(base_size)
        parser.feed(self.label)
        return [
            (text, size if size is not None else base_size)
            for text, size in parser.runs
        ]


def page_cells(graph):
    graph_root = graph.find("root")
    if graph_root is None:
        raise ValueError("mxGraphModel is missing its root element")
    cells = []
    for wrapper in graph_root:
        element = wrapper if wrapper.tag == "mxCell" else wrapper.find("mxCell")
        if element is None:
            continue
        identity = wrapper.get("id", element.get("id", ""))
        label = wrapper.get("label", element.get("value", ""))
        style = {}
        for token in element.get("style", "").split(";"):
            if token:
                name, separator, value = token.partition("=")
                style[name] = value if separator else "1"
        cells.append(Cell(identity, element, label, style))
    return cells


@dataclass
class Issue:
    level: str
    code: str
    page: str
    cell: str
    message: str


def number(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"non-finite number {value!r}")
    return result


def ancestors(cell, cells):
    result = set()
    parent = cell.parent
    while parent in cells and parent not in result:
        result.add(parent)
        parent = cells[parent].parent
    return result


def absolute_box(cell, cells):
    chain = [cell]
    parent = cell.parent
    while parent in cells:
        chain.append(cells[parent])
        parent = cells[parent].parent
    left = top = 0.0
    for current in reversed(chain):
        geometry = current.geometry
        if geometry is None:
            continue
        if geometry.get("relative") == "1":
            return None
        left += number(geometry.get("x", 0))
        top += number(geometry.get("y", 0))
    geometry = cell.geometry
    if geometry is None:
        return None
    return (
        left,
        top,
        number(geometry.get("width", 0)),
        number(geometry.get("height", 0)),
    )


def intersects(first, second):
    return (
        min(first[0] + first[2], second[0] + second[2]) > max(first[0], second[0]) + 0.5
        and min(first[1] + first[3], second[1] + second[3])
        > max(first[1], second[1]) + 0.5
    )


def segment_hits_box(start, end, box):
    left, top, width, height = box
    if abs(start[0] - end[0]) < 0.01:
        return (
            left + 1 < start[0] < left + width - 1
            and min(start[1], end[1]) < top + height - 1
            and max(start[1], end[1]) > top + 1
        )
    if abs(start[1] - end[1]) < 0.01:
        return (
            top + 1 < start[1] < top + height - 1
            and min(start[0], end[0]) < left + width - 1
            and max(start[0], end[0]) > left + 1
        )
    return False


def explicit_route(edge, boxes, cells):
    if edge.style.get("edgeStyle") not in {"none", ""}:
        return None
    geometry = edge.geometry
    parent_box = boxes.get(edge.parent)
    parent_cell = cells.get(edge.parent)
    if parent_cell is not None and parent_cell.vertex and parent_box is None:
        return None
    shift = parent_box[:2] if parent_box else (0, 0)
    endpoints = []
    for side, prefix in (("source", "exit"), ("target", "entry")):
        identity = edge.element.get(side)
        if identity:
            box = boxes.get(identity)
            if (
                box is None
                or prefix + "X" not in edge.style
                or prefix + "Y" not in edge.style
            ):
                return None
            point = (
                box[0] + box[2] * number(edge.style[prefix + "X"]),
                box[1] + box[3] * number(edge.style[prefix + "Y"]),
            )
        else:
            explicit = geometry.find(f"mxPoint[@as='{side}Point']")
            if explicit is None:
                return None
            point = (
                number(explicit.get("x", 0)) + shift[0],
                number(explicit.get("y", 0)) + shift[1],
            )
        endpoints.append(point)
    waypoints = [
        (number(point.get("x", 0)) + shift[0], number(point.get("y", 0)) + shift[1])
        for point in geometry.findall("Array[@as='points']/mxPoint")
    ]
    route = [endpoints[0], *waypoints, endpoints[1]]
    if any(
        abs(start[0] - end[0]) > 0.01 and abs(start[1] - end[1]) > 0.01
        for start, end in zip(route, route[1:])
    ):
        return None
    return route


def glyph_width(character, font_size):
    if unicodedata.combining(character):
        return 0
    return font_size * (
        1 if unicodedata.east_asian_width(character) in {"W", "F"} else 0.55
    )


def check_page(page, display_width, issues, coverage):
    page_name = page.get("name", page.get("id", "unnamed"))

    def issue(level, code, cell, message):
        issues.append(Issue(level, code, page_name, cell, message))

    graph = page.find("mxGraphModel")
    try:
        all_cells = page_cells(graph)
    except ValueError as error:
        issue("ERROR", "MISSING_ROOT", "", str(error))
        return
    cells = {}
    for cell in all_cells:
        if not cell.identity:
            issue("ERROR", "MISSING_ID", "", "Cell has no ID")
        elif cell.identity in cells:
            issue(
                "ERROR",
                "DUPLICATE_ID",
                cell.identity,
                "Cell ID is duplicated within this page",
            )
        else:
            cells[cell.identity] = cell
    if "0" not in cells or cells["0"].parent is not None:
        issue("ERROR", "ROOT_CELL", "0", "Expected a root cell with ID 0 and no parent")
    if not any(cell.parent == "0" for cell in all_cells):
        issue(
            "ERROR", "MISSING_LAYER", "", "The graph has no layer under the root cell"
        )
    for cell in all_cells:
        if cell.identity != "0" and cell.parent not in cells:
            issue(
                "ERROR",
                "MISSING_PARENT",
                cell.identity,
                f"Parent {cell.parent!r} does not exist",
            )
        if cell.identity in ancestors(cell, cells):
            issue(
                "ERROR", "PARENT_CYCLE", cell.identity, "Parent references form a cycle"
            )
        geometry = cell.geometry
        if cell.vertex or cell.edge:
            if geometry is None:
                issue(
                    "ERROR",
                    "MISSING_GEOMETRY",
                    cell.identity,
                    "Vertex or edge has no mxGeometry",
                )
                continue
            try:
                for element in geometry.iter():
                    for attribute in ("x", "y", "width", "height"):
                        if attribute in element.attrib:
                            number(element.get(attribute))
                for attribute in (
                    "fontSize",
                    "spacing",
                    "spacingLeft",
                    "spacingRight",
                    "spacingTop",
                    "spacingBottom",
                    "startSize",
                    "exitX",
                    "exitY",
                    "entryX",
                    "entryY",
                ):
                    if attribute in cell.style:
                        number(cell.style[attribute])
                if cell.vertex and geometry.get("relative") != "1":
                    if (
                        number(geometry.get("width", 0)) <= 0
                        or number(geometry.get("height", 0)) <= 0
                    ):
                        issue(
                            "ERROR",
                            "INVALID_SIZE",
                            cell.identity,
                            "Regular vertices need positive width and height",
                        )
            except ValueError as error:
                issue("ERROR", "INVALID_NUMBER", cell.identity, str(error))
        if cell.edge:
            for side in ("source", "target"):
                endpoint = cell.element.get(side)
                if endpoint and endpoint not in cells:
                    issue(
                        "ERROR",
                        "MISSING_ENDPOINT",
                        cell.identity,
                        f"{side} cell {endpoint!r} does not exist",
                    )
                elif (
                    not endpoint
                    and geometry.find(f"mxPoint[@as='{side}Point']") is None
                ):
                    issue(
                        "ERROR",
                        "MISSING_ENDPOINT",
                        cell.identity,
                        f"{side} needs a cell reference or explicit point",
                    )
    if any(item.level == "ERROR" and item.page == page_name for item in issues):
        return
    boxes = {
        identity: absolute_box(cell, cells)
        for identity, cell in cells.items()
        if cell.vertex
    }
    boxes = {identity: box for identity, box in boxes.items() if box is not None}
    visible = {
        identity: box
        for identity, box in boxes.items()
        if cells[identity].element.get("visible") != "0"
        and cells[identity].style.get("opacity") != "0"
    }
    groups = {cell.parent for cell in all_cells if cell.vertex}
    relations = {identity: ancestors(cell, cells) for identity, cell in cells.items()}
    for index, (identity, box) in enumerate(visible.items()):
        for other, other_box in list(visible.items())[index + 1 :]:
            if identity in relations[other] or other in relations[identity]:
                continue
            if intersects(box, other_box):
                issue(
                    "WARN",
                    "OVERLAP",
                    identity,
                    f"Bounding rectangle intersects {other!r}; inspect intentional overlays and shapes",
                )
        parent_box = boxes.get(cells[identity].parent)
        if parent_box and (
            box[0] < parent_box[0]
            or box[1] < parent_box[1]
            or box[0] + box[2] > parent_box[0] + parent_box[2]
            or box[1] + box[3] > parent_box[1] + parent_box[3]
        ):
            issue(
                "WARN",
                "OUTSIDE_GROUP",
                identity,
                "Child rectangle extends beyond its parent group",
            )
    if not visible:
        issue(
            "WARN",
            "NO_REGULAR_VERTICES",
            "",
            "No visible regular vertices were available for layout estimates",
        )
    routes = {}
    for cell in all_cells:
        if not cell.edge:
            continue
        route = explicit_route(cell, boxes, cells)
        if route is None:
            coverage["unresolved_routes"] += 1
            continue
        coverage["explicit_routes"] += 1
        routes[cell.identity] = route
        endpoints = {cell.element.get("source"), cell.element.get("target")}
        for identity, box in visible.items():
            if identity in endpoints or identity in groups:
                continue
            if any(
                segment_hits_box(start, end, box)
                for start, end in zip(route, route[1:])
            ):
                issue(
                    "WARN",
                    "EDGE_THROUGH_NODE",
                    cell.identity,
                    f"Explicit orthogonal corridor crosses {identity!r}'s bounding rectangle",
                )
    extents = [(box[0], box[0] + box[2]) for box in visible.values()]
    extents.extend((point[0], point[0]) for route in routes.values() for point in route)
    approximate_width = (
        max((extent[1] for extent in extents), default=0)
        - min((extent[0] for extent in extents), default=0)
        + 40
    )
    scale = display_width / approximate_width if display_width else None
    for cell in all_cells:
        if not cell.text or cell.element.get("visible") == "0":
            continue
        font_size = number(cell.style.get("fontSize", 12))
        inline_sizes = (
            re.findall(r"font-size\s*:\s*([\d.]+)px", cell.label)
            if cell.style.get("html") == "1"
            else []
        )
        smallest_font = min([font_size] + [number(size) for size in inline_sizes])
        if scale is not None and smallest_font * scale < (12 if cell.edge else 14):
            issue(
                "WARN",
                "SMALL_DISPLAY_TEXT",
                cell.identity,
                f"Estimated displayed type is {smallest_font * scale:.1f}px at {display_width:g}px figure width; verify actual export bounds and role",
            )
        box = boxes.get(cell.identity)
        if box is None:
            continue
        spacing = number(cell.style.get("spacing", 2))
        usable_width = (
            box[2]
            - spacing * 2
            - number(cell.style.get("spacingLeft", 0))
            - number(cell.style.get("spacingRight", 0))
        )
        usable_height = (
            box[3]
            - spacing * 2
            - number(cell.style.get("spacingTop", 0))
            - number(cell.style.get("spacingBottom", 0))
        )
        if "swimlane" in cell.style or cell.style.get("shape") == "swimlane":
            if cell.style.get("horizontal", "1") == "1":
                usable_height = number(cell.style.get("startSize", 40)) - spacing * 2
            else:
                continue
        if "rhombus" in cell.style or cell.style.get("shape") == "rhombus":
            usable_width *= 0.65
            usable_height *= 0.65
        lines = [[]]
        for text, size in cell.runs(font_size):
            for index, piece in enumerate(text.split("\n")):
                if index:
                    lines.append([])
                if piece:
                    lines[-1].append((piece, size))
        estimated_height = 0.0
        too_wide = False
        for line in lines:
            estimated_width = sum(
                glyph_width(character, size)
                for piece, size in line
                for character in piece
            )
            line_size = max((size for _, size in line), default=font_size)
            if cell.style.get("whiteSpace") == "wrap":
                wrapped = max(1, math.ceil(estimated_width / max(usable_width, 1)))
            else:
                wrapped = 1
                too_wide |= estimated_width > usable_width
            estimated_height += wrapped * line_size * 1.3
        if too_wide or estimated_height > usable_height:
            issue(
                "WARN",
                "TEXT_FIT",
                cell.identity,
                "Estimated label extent exceeds the available label area; verify actual font, wrapping, and shape",
            )


def check_document(root, display_width=None):
    issues = []
    coverage = {"explicit_routes": 0, "unresolved_routes": 0}
    pages = root.findall("diagram")
    for page in pages:
        check_page(page, display_width, issues, coverage)
    return {
        "ok": not any(issue.level == "ERROR" for issue in issues),
        "pages": len(pages),
        "issues": [asdict(issue) for issue in issues],
        "coverage": coverage,
    }


def inspect_document(root):
    pages = []
    for page in root.findall("diagram"):
        entries = []
        for cell in page_cells(page.find("mxGraphModel")):
            entry = {
                "id": cell.identity,
                "kind": "edge" if cell.edge else "vertex" if cell.vertex else "layer",
                "parent": cell.parent,
                "label": cell.text,
            }
            if cell.edge:
                entry["source"] = cell.element.get("source")
                entry["target"] = cell.element.get("target")
                for side in ("sourcePoint", "targetPoint"):
                    point = (
                        cell.geometry.find(f"mxPoint[@as='{side}']")
                        if cell.geometry is not None
                        else None
                    )
                    if point is not None:
                        entry[side] = dict(point.attrib)
            entries.append(entry)
        pages.append({"id": page.get("id"), "name": page.get("name"), "cells": entries})
    return {"pages": pages}


def positive_number(value):
    try:
        result = number(value)
        if result <= 0:
            raise ValueError("must be positive")
        return result
    except ValueError as error:
        raise argparse.ArgumentTypeError(str(error)) from error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser(
        "check", help="Check structure and heuristic geometry; never renders"
    )
    check.add_argument("source", type=Path)
    check.add_argument(
        "--display-width",
        type=positive_number,
        help="Intended figure display width in CSS pixels",
    )
    check.add_argument(
        "--json", action="store_true", help="Print the complete machine-readable report"
    )
    inspect = commands.add_parser(
        "inspect", help="Print complete page-local labels and relationships as JSON"
    )
    inspect.add_argument("source", type=Path)
    unpack = commands.add_parser(
        "unpack", help="Write all pages as readable XML to a new file"
    )
    unpack.add_argument("source", type=Path)
    unpack.add_argument("destination", type=Path)
    arguments = parser.parse_args()
    try:
        root = read_document(arguments.source)
        if arguments.command == "unpack":
            ElementTree.indent(root, space="  ")
            with arguments.destination.open("x", encoding="utf-8") as output:
                output.write(
                    ElementTree.tostring(root, encoding="unicode", xml_declaration=True)
                )
                output.write("\n")
            print(f"Wrote {arguments.destination}; source unchanged")
            return 0
        if arguments.command == "inspect":
            print(json.dumps(inspect_document(root), ensure_ascii=False, indent=2))
            return 0
        report = check_document(root, arguments.display_width)
    except (
        OSError,
        ValueError,
        UnicodeError,
        ElementTree.ParseError,
        binascii.Error,
    ) as error:
        if arguments.command != "check":
            print(f"ERROR: {error}", file=sys.stderr)
            return 1
        report = {
            "ok": False,
            "pages": 0,
            "issues": [asdict(Issue("ERROR", "READ_ERROR", "", "", str(error)))],
            "coverage": {"explicit_routes": 0, "unresolved_routes": 0},
        }
    if arguments.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(
            f"Structure: {'PASS' if report['ok'] else 'FAIL'}; pages: {report['pages']}"
        )
        for issue in report["issues"]:
            print(
                f"{issue['level']} [{issue['code']}] {issue['page']} / {issue['cell']}: {issue['message']}"
            )
        coverage = report["coverage"]
        print(
            f"Routes: {coverage['explicit_routes']} explicit orthogonal corridors checked; {coverage['unresolved_routes']} left to renderer inspection"
        )
        print(
            "Warnings are estimates. Final routing, font rendering, and visual quality are NOT verified."
        )
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
