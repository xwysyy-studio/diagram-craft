import base64
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import quote
import xml.etree.ElementTree as ElementTree
import zlib


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "drawio.py"


def node(identity, text="Example", parent="1", horizontal=40, vertical=40):
    return (
        f'<mxCell id="{identity}" value="{text}" vertex="1" parent="{parent}" '
        'style="html=0;fontSize=18;spacing=8;whiteSpace=wrap;">'
        f'<mxGeometry x="{horizontal}" y="{vertical}" width="160" height="72" '
        'as="geometry"/></mxCell>'
    )


def model(content):
    return (
        '<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
        f"{content}</root></mxGraphModel>"
    )


def document(content):
    return f'<mxfile><diagram id="main" name="Main">{model(content)}</diagram></mxfile>'


class DrawioCommandTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.directory = Path(self.workspace.name)
        self.source = self.directory / "source.drawio"

    def invoke(self, command, content, *arguments):
        self.source.write_text(content, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPT), command, str(self.source), *arguments],
            text=True,
            capture_output=True,
            check=False,
        )

    def check(self, content, *arguments):
        result = self.invoke("check", content, "--json", *arguments)
        self.assertIn(result.returncode, (0, 1), result.stderr)
        return json.loads(result.stdout)

    def codes(self, report):
        return {issue["code"] for issue in report["issues"]}

    def test_valid_native_diagram_keeps_all_labels_in_inspection(self):
        label = "关键机制：校验候选版本后切换活动版本"
        result = self.invoke("inspect", document(node("build", label)))
        self.assertEqual(result.returncode, 0, result.stderr)
        cells = json.loads(result.stdout)["pages"][0]["cells"]
        self.assertEqual(
            next(cell for cell in cells if cell["id"] == "build")["label"], label
        )

    def test_invalid_xml_and_unsupported_images_fail_explicitly(self):
        for content in ("<mxfile>", "<svg/>", "not XML"):
            with self.subTest(content=content):
                report = self.check(content)
                self.assertFalse(report["ok"])

    def test_duplicate_ids_fail_within_a_page(self):
        report = self.check(document(node("duplicate") + node("duplicate")))
        self.assertFalse(report["ok"])
        self.assertIn("DUPLICATE_ID", self.codes(report))

    def test_identical_ids_on_distinct_pages_are_valid(self):
        graph = model(node("same"))
        source = f'<mxfile><diagram id="one">{graph}</diagram><diagram id="two">{graph}</diagram></mxfile>'
        report = self.check(source)
        self.assertTrue(report["ok"], report)
        self.assertEqual(report["pages"], 2)

    def test_missing_parent_and_parent_cycle_fail(self):
        report = self.check(document(node("child", parent="absent")))
        self.assertIn("MISSING_PARENT", self.codes(report))
        cycle = node("first", parent="second") + node("second", parent="first")
        report = self.check(document(cycle))
        self.assertFalse(report["ok"])
        self.assertIn("PARENT_CYCLE", self.codes(report))

    def test_missing_edge_endpoint_fails_but_floating_endpoint_is_valid(self):
        edge = '<mxCell id="edge" edge="1" parent="1" source="source"><mxGeometry relative="1" as="geometry">{point}</mxGeometry></mxCell>'
        report = self.check(document(node("source") + edge.format(point="")))
        self.assertIn("MISSING_ENDPOINT", self.codes(report))
        point = '<mxPoint x="320" y="76" as="targetPoint"/>'
        report = self.check(document(node("source") + edge.format(point=point)))
        self.assertTrue(report["ok"], report)

    def test_nonfinite_geometry_fails(self):
        for value in ("nan", "inf", "nonsense"):
            with self.subTest(value=value):
                report = self.check(document(node("bad", horizontal=value)))
                self.assertFalse(report["ok"])
                self.assertIn("INVALID_NUMBER", self.codes(report))

    def test_real_group_containment_is_not_overlap(self):
        group = '<mxCell id="group" vertex="1" parent="1" style="group;"><mxGeometry x="100" y="100" width="400" height="260" as="geometry"/></mxCell>'
        report = self.check(document(group + node("child", parent="group")))
        self.assertTrue(report["ok"], report)
        self.assertNotIn("OVERLAP", self.codes(report))

    def test_nested_coordinates_are_resolved_for_sibling_overlap(self):
        group = '<mxCell id="group" vertex="1" parent="1" style="group;"><mxGeometry x="300" y="100" width="400" height="260" as="geometry"/></mxCell>'
        content = (
            group
            + node("child", parent="group")
            + node("outside", horizontal=340, vertical=140)
        )
        report = self.check(document(content))
        self.assertIn("OVERLAP", self.codes(report))

    def test_wrapper_label_and_id_are_preserved(self):
        wrapped = '<object id="wrapped" label="服务 &amp; 状态" custom="retain"><mxCell vertex="1" parent="1" style="fontSize=18;"><mxGeometry x="40" y="40" width="200" height="72" as="geometry"/></mxCell></object>'
        source = document(wrapped)
        self.assertTrue(self.check(source)["ok"])
        result = self.invoke("inspect", source)
        cells = json.loads(result.stdout)["pages"][0]["cells"]
        self.assertEqual(
            next(cell for cell in cells if cell["id"] == "wrapped")["label"],
            "服务 & 状态",
        )

    def test_compressed_multipage_unpack_preserves_input_and_wrapper(self):
        graph = model(node("first", "中文内容"))
        compressor = zlib.compressobj(wbits=-15)
        compressed = (
            compressor.compress(quote(graph, safe="~()*!.'").encode())
            + compressor.flush()
        )
        payload = base64.b64encode(compressed).decode()
        source = f'<mxfile><diagram id="one">{payload}</diagram><diagram id="two">{model(node("second"))}</diagram></mxfile>'
        self.assertTrue(self.check(source)["ok"])
        destination = self.directory / "readable.drawio"
        result = self.invoke("unpack", source, str(destination))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.source.read_text(encoding="utf-8"), source)
        parsed = ElementTree.parse(destination)
        self.assertEqual(len(parsed.findall("diagram/mxGraphModel")), 2)
        self.assertEqual(parsed.find('.//mxCell[@id="first"]').get("value"), "中文内容")
        second = self.invoke("unpack", source, str(destination))
        self.assertNotEqual(second.returncode, 0)
        self.assertIn("exists", second.stderr)

    def test_long_labels_warn_without_truncating_source(self):
        source = document(node("long", "这是一段需要保留完整语义的中文说明" * 8))
        report = self.check(source)
        self.assertTrue(report["ok"])
        self.assertIn("TEXT_FIT", self.codes(report))
        self.assertEqual(self.source.read_text(encoding="utf-8"), source)

    def test_font_warning_uses_display_width(self):
        source = document(node("left") + node("right", horizontal=1240))
        report = self.check(source, "--display-width", "800")
        self.assertIn("SMALL_DISPLAY_TEXT", self.codes(report))
        report = self.check(source, "--display-width", "1600")
        self.assertNotIn("SMALL_DISPLAY_TEXT", self.codes(report))

    def test_two_tier_html_label_uses_its_actual_line_sizes(self):
        card = '<mxCell id="card" vertex="1" parent="1" value="&lt;b&gt;查询服务&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size:14px&quot;&gt;逐请求固定活动版本&lt;br&gt;读取后返回检索结果&lt;/font&gt;" style="html=1;fontSize=18;spacing=6;whiteSpace=wrap;"><mxGeometry x="40" y="40" width="240" height="76" as="geometry"/></mxCell>'
        report = self.check(document(card))
        self.assertNotIn("TEXT_FIT", self.codes(report))

    def test_large_inline_type_still_warns_when_it_exceeds_label_height(self):
        card = '<mxCell id="card" vertex="1" parent="1" value="Title&lt;br&gt;&lt;font style=&quot;font-size:32px&quot;&gt;Detail&lt;/font&gt;" style="html=1;fontSize=18;spacing=6;whiteSpace=wrap;"><mxGeometry x="40" y="40" width="240" height="76" as="geometry"/></mxCell>'
        report = self.check(document(card))
        self.assertIn("TEXT_FIT", self.codes(report))

    def test_html_block_boundary_does_not_add_a_visible_empty_line(self):
        card = '<mxCell id="card" vertex="1" parent="1" value="&lt;div&gt;Title&lt;/div&gt;" style="html=1;fontSize=18;spacing=0;"><mxGeometry x="40" y="40" width="160" height="26" as="geometry"/></mxCell>'
        report = self.check(document(card))
        self.assertNotIn("TEXT_FIT", self.codes(report))

    def test_explicit_edge_through_a_node_warns(self):
        edge = '<mxCell id="route" edge="1" parent="1" source="left" target="right" style="edgeStyle=none;exitX=1;exitY=0.5;entryX=0;entryY=0.5;"><mxGeometry relative="1" as="geometry"/></mxCell>'
        content = (
            node("left")
            + node("obstacle", horizontal=260)
            + node("right", horizontal=480)
            + edge
        )
        report = self.check(document(content))
        self.assertIn("EDGE_THROUGH_NODE", self.codes(report))
        self.assertEqual(report["coverage"]["explicit_routes"], 1)

    def test_renderer_routed_edge_is_reported_as_unresolved(self):
        edge = '<mxCell id="route" edge="1" parent="1" source="left" target="right" style="edgeStyle=orthogonalEdgeStyle;"><mxGeometry relative="1" as="geometry"/></mxCell>'
        report = self.check(
            document(node("left") + node("right", horizontal=300) + edge)
        )
        self.assertTrue(report["ok"])
        self.assertEqual(report["coverage"]["unresolved_routes"], 1)

    def test_relative_ports_are_valid_but_not_treated_as_regular_boxes(self):
        port = '<mxCell id="port" vertex="1" parent="host" style="shape=ellipse;"><mxGeometry x="1" y="0.5" width="0" height="0" relative="1" as="geometry"/></mxCell>'
        report = self.check(document(node("host") + port))
        self.assertTrue(report["ok"], report)

    def test_dtd_is_rejected_at_the_input_boundary(self):
        report = self.check(
            '<!DOCTYPE mxfile [<!ENTITY label "injected">]>' + document(node("node"))
        )
        self.assertFalse(report["ok"])
        self.assertIn("READ_ERROR", self.codes(report))


if __name__ == "__main__":
    unittest.main()
