#!/usr/bin/env python3
"""Build a text-only EDA Lab paper deck from a JSON spec.

The script keeps the bundled PowerPoint template as the visual source of truth
and edits only slide text, slide order, and slide numbers.
"""

from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree


NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
}

SOURCE_SLIDES = {
    "title": 1,
    "outline": 2,
    "outline-introduction": 3,
    "outline-preliminaries": 7,
    "outline-problem-formulation": 9,
    "outline-methodology": 11,
    "outline-experimental-results": 15,
    "outline-conclusion": 18,
    "content": 16,
    "previous-work": 5,
    "remarks": 20,
    "thank-you": 21,
}

SECTIONS = [
    "Introduction",
    "Preliminaries",
    "Problem Formulation",
    "Methodology",
    "Experimental Results",
    "Conclusion",
]

TITLE_SIZE = 2800
TOPIC_SIZE = 2400
DETAIL_SIZE = 2000
EQUATION_SIZE = 2000
REFERENCE_SIZE = 1000
BODY_CITATION_SIZE = 1800
OUTLINE_ITEM_SIZE = 2400
TITLE_COLOR = "333399"
TITLE_BOX = {"x": "711200", "y": "240000", "cx": "10668000", "cy": "685800"}
BODY_BOX = {"x": "711200", "y": "990600", "cx": "10769600", "cy": "5105400"}
AUTHOR_BOX = {"x": "1700000", "y": "2500000", "cx": "8800000", "cy": "460000"}
TITLE_INFO_BOX = {"x": "2156048", "y": "3050000", "cx": "7772400", "cy": "700000"}
TITLE_LINE_COVER = {"x": "0", "y": "1840000", "cx": "12192000", "cy": "180000"}
TITLE_SEPARATOR = {"x": "609600", "y": "1900000", "cx": "10920000", "cy": "17000"}


def q(tag: str) -> str:
    prefix, local = tag.split(":")
    return f"{{{NS[prefix]}}}{local}"


def read_package(path: Path) -> dict[str, bytes]:
    with ZipFile(path, "r") as zin:
        return {name: zin.read(name) for name in zin.namelist()}


def write_package(path: Path, files: dict[str, bytes]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(path, "w", ZIP_DEFLATED) as zout:
        for name, data in files.items():
            zout.writestr(name, data)


def shape_by_id(root, shape_id: str):
    for sp in root.xpath(".//p:sp", namespaces=NS):
        c_nv_pr = sp.find(".//p:cNvPr", namespaces=NS)
        if c_nv_pr is not None and c_nv_pr.get("id") == shape_id:
            return sp
    return None


def text_values(root):
    return root.xpath(".//a:t", namespaces=NS)


def detach_placeholder(shape):
    """Detach slide text from placeholder inheritance so font size stays editable."""
    if shape is None:
        return
    nv_pr = shape.find(".//p:nvPr", namespaces=NS)
    if nv_pr is None:
        return
    for ph in nv_pr.findall("p:ph", namespaces=NS):
        nv_pr.remove(ph)


def ensure_textbox_geometry(shape, box: dict[str, str] | None = None):
    """Give formerly-placeholder text a concrete editable text-box geometry."""
    if shape is None or box is None:
        return
    sp_pr = shape.find("p:spPr", namespaces=NS)
    if sp_pr is None:
        sp_pr = etree.Element(q("p:spPr"))
        nv = shape.find("p:nvSpPr", namespaces=NS)
        insert_at = list(shape).index(nv) + 1 if nv is not None else 0
        shape.insert(insert_at, sp_pr)
    xfrm = sp_pr.find("a:xfrm", namespaces=NS)
    if xfrm is None:
        xfrm = etree.Element(q("a:xfrm"))
        sp_pr.insert(0, xfrm)
    off = xfrm.find("a:off", namespaces=NS)
    if off is None:
        off = etree.SubElement(xfrm, q("a:off"))
    off.set("x", box["x"])
    off.set("y", box["y"])
    ext = xfrm.find("a:ext", namespaces=NS)
    if ext is None:
        ext = etree.SubElement(xfrm, q("a:ext"))
    ext.set("cx", box["cx"])
    ext.set("cy", box["cy"])
    if sp_pr.find("a:prstGeom", namespaces=NS) is None:
        geom = etree.SubElement(sp_pr, q("a:prstGeom"))
        geom.set("prst", "rect")
        etree.SubElement(geom, q("a:avLst"))
    if sp_pr.find("a:noFill", namespaces=NS) is None:
        etree.SubElement(sp_pr, q("a:noFill"))
    if sp_pr.find("a:ln", namespaces=NS) is None:
        ln = etree.SubElement(sp_pr, q("a:ln"))
        etree.SubElement(ln, q("a:noFill"))


def add_white_cover(root, box: dict[str, str]):
    tree = root.find(".//p:spTree", namespaces=NS)
    if tree is None:
        return
    shape_id = str(
        max(
            [
                int(c.get("id"))
                for c in root.xpath(".//p:cNvPr", namespaces=NS)
                if c.get("id", "").isdigit()
            ]
            or [1000]
        )
        + 1
    )
    sp = etree.Element(q("p:sp"))
    nv = etree.SubElement(sp, q("p:nvSpPr"))
    etree.SubElement(nv, q("p:cNvPr"), id=shape_id, name="title separator cover")
    etree.SubElement(nv, q("p:cNvSpPr"))
    etree.SubElement(nv, q("p:nvPr"))
    sp_pr = etree.SubElement(sp, q("p:spPr"))
    xfrm = etree.SubElement(sp_pr, q("a:xfrm"))
    etree.SubElement(xfrm, q("a:off"), x=box["x"], y=box["y"])
    etree.SubElement(xfrm, q("a:ext"), cx=box["cx"], cy=box["cy"])
    geom = etree.SubElement(sp_pr, q("a:prstGeom"), prst="rect")
    etree.SubElement(geom, q("a:avLst"))
    fill = etree.SubElement(sp_pr, q("a:solidFill"))
    etree.SubElement(fill, q("a:srgbClr"), val="FFFFFF")
    ln = etree.SubElement(sp_pr, q("a:ln"))
    etree.SubElement(ln, q("a:noFill"))
    tree.append(sp)


def add_black_separator(root, box: dict[str, str]):
    tree = root.find(".//p:spTree", namespaces=NS)
    if tree is None:
        return
    shape_id = str(
        max(
            [
                int(c.get("id"))
                for c in root.xpath(".//p:cNvPr", namespaces=NS)
                if c.get("id", "").isdigit()
            ]
            or [1000]
        )
        + 1
    )
    sp = etree.Element(q("p:sp"))
    nv = etree.SubElement(sp, q("p:nvSpPr"))
    etree.SubElement(nv, q("p:cNvPr"), id=shape_id, name="title separator")
    etree.SubElement(nv, q("p:cNvSpPr"))
    etree.SubElement(nv, q("p:nvPr"))
    sp_pr = etree.SubElement(sp, q("p:spPr"))
    xfrm = etree.SubElement(sp_pr, q("a:xfrm"))
    etree.SubElement(xfrm, q("a:off"), x=box["x"], y=box["y"])
    etree.SubElement(xfrm, q("a:ext"), cx=box["cx"], cy=box["cy"])
    geom = etree.SubElement(sp_pr, q("a:prstGeom"), prst="rect")
    etree.SubElement(geom, q("a:avLst"))
    fill = etree.SubElement(sp_pr, q("a:solidFill"))
    etree.SubElement(fill, q("a:srgbClr"), val="333333")
    ln = etree.SubElement(sp_pr, q("a:ln"))
    etree.SubElement(ln, q("a:noFill"))
    tree.append(sp)


def make_run(text: str, size: int | None = None, color: str | None = None, bold: bool = False):
    run = etree.Element(q("a:r"))
    r_pr = etree.SubElement(run, q("a:rPr"))
    r_pr.set("lang", "en-US")
    r_pr.set("altLang", "zh-TW")
    if size is not None:
        r_pr.set("sz", str(size))
    if bold:
        r_pr.set("b", "1")
    if color is not None:
        fill = etree.SubElement(r_pr, q("a:solidFill"))
        etree.SubElement(fill, q("a:srgbClr")).set("val", color)
    t = etree.SubElement(run, q("a:t"))
    t.text = text
    return run


def apply_math_font(r_pr, size: int = EQUATION_SIZE):
    r_pr.set("lang", "en-US")
    r_pr.set("altLang", "zh-TW")
    r_pr.set("sz", str(size))
    fill = etree.SubElement(r_pr, q("a:solidFill"))
    etree.SubElement(fill, q("a:srgbClr")).set("val", "000000")
    for tag in ["a:latin", "a:ea", "a:cs"]:
        etree.SubElement(r_pr, q(tag), typeface="Cambria Math")


def make_equation_para(text: str, *, size: int = EQUATION_SIZE):
    para = etree.Element(q("a:p"))
    p_pr = etree.SubElement(para, q("a:pPr"))
    p_pr.set("marL", "742950")
    p_pr.set("indent", "0")
    p_pr.set("algn", "l")
    etree.SubElement(p_pr, q("a:buNone"))
    spc_bef = etree.SubElement(p_pr, q("a:spcBef"))
    etree.SubElement(spc_bef, q("a:spcPts"), val="400")
    spc_aft = etree.SubElement(p_pr, q("a:spcAft"))
    etree.SubElement(spc_aft, q("a:spcPts"), val="200")
    def_r_pr = etree.SubElement(p_pr, q("a:defRPr"))
    apply_math_font(def_r_pr, size)

    run = etree.SubElement(para, q("a:r"))
    r_pr = etree.SubElement(run, q("a:rPr"))
    apply_math_font(r_pr, size)
    t = etree.SubElement(run, q("a:t"))
    t.text = text

    end = etree.SubElement(para, q("a:endParaRPr"))
    end.set("lang", "en-US")
    end.set("altLang", "zh-TW")
    end.set("sz", str(size))
    return para


def make_outline_para(text: str, *, inactive: bool = False):
    para = etree.Element(q("a:p"))
    run = etree.SubElement(para, q("a:r"))
    r_pr = etree.SubElement(run, q("a:rPr"))
    r_pr.set("lang", "en-US")
    r_pr.set("altLang", "zh-TW")
    r_pr.set("dirty", "0")
    if inactive:
        fill = etree.SubElement(r_pr, q("a:solidFill"))
        scheme = etree.SubElement(fill, q("a:schemeClr"))
        scheme.set("val", "bg1")
        etree.SubElement(scheme, q("a:lumMod")).set("val", "85000")
    t = etree.SubElement(run, q("a:t"))
    t.text = text
    return para


def make_para(
    text: str,
    *,
    size: int,
    color: str = "000000",
    bold: bool = False,
    bullet: bool = True,
    level: int = 0,
    align: str | None = None,
    citation_size: int | None = BODY_CITATION_SIZE,
):
    para = etree.Element(q("a:p"))
    p_pr = etree.SubElement(para, q("a:pPr"))
    if bullet:
        p_pr.set("lvl", str(level))
    else:
        p_pr.set("marL", "0")
    if align is not None:
        p_pr.set("algn", align)
    if not bullet:
        def_r_pr = etree.SubElement(p_pr, q("a:defRPr"))
        def_r_pr.set("sz", str(size))
    if bullet and level == 0 and citation_size is not None:
        parts = re.split(r"(\[[^\]]+\])", text)
        for part in parts:
            if not part:
                continue
            if part.startswith("[") and part.endswith("]"):
                para.append(make_run(part, citation_size))
            else:
                para.append(make_run(part))
    elif bullet:
        para.append(make_run(text))
    elif citation_size is None:
        para.append(make_run(text, size, color=color, bold=bold))
    else:
        parts = re.split(r"(\[[^\]]+\])", text)
        for part in parts:
            if not part:
                continue
            if part.startswith("[") and part.endswith("]"):
                para.append(make_run(part, citation_size, color=color, bold=bold))
            else:
                para.append(make_run(part, size, color=color, bold=bold))
    end = etree.SubElement(para, q("a:endParaRPr"))
    end.set("lang", "en-US")
    end.set("altLang", "zh-TW")
    if not bullet:
        end.set("sz", str(size))
    return para


def replace_tx_body(shape, paragraphs, wrap="square", box: dict[str, str] | None = None):
    if shape is None:
        return
    ensure_textbox_geometry(shape, box)
    tx_body = shape.find("p:txBody", namespaces=NS)
    if tx_body is None:
        return
    body_pr = tx_body.find("a:bodyPr", namespaces=NS)
    body_pr = deepcopy(body_pr) if body_pr is not None else etree.Element(q("a:bodyPr"))
    body_pr.set("wrap", wrap)
    body_pr.set("anchor", "t")
    for no_autofit in body_pr.xpath("./a:noAutofit", namespaces=NS):
        body_pr.remove(no_autofit)
    old_lst_style = tx_body.find("a:lstStyle", namespaces=NS)
    lst_style = deepcopy(old_lst_style) if old_lst_style is not None else etree.Element(q("a:lstStyle"))
    new_body = etree.Element(q("p:txBody"))
    new_body.append(body_pr)
    new_body.append(lst_style)
    for para in paragraphs:
        new_body.append(para)
    tx_body.getparent().replace(tx_body, new_body)


def set_shape_text(
    shape,
    text: str,
    size: int | None = None,
    color: str | None = None,
    bold: bool | None = None,
    box: dict[str, str] | None = None,
    align: str | None = None,
):
    if shape is None:
        return
    ensure_textbox_geometry(shape, box)
    detach_placeholder(shape)
    texts = text_values(shape)
    if not texts:
        return
    texts[0].text = text
    for extra in texts[1:]:
        extra.text = ""
    if size is not None:
        for r_pr in shape.xpath(".//a:rPr", namespaces=NS):
            r_pr.set("sz", str(size))
        for def_r_pr in shape.xpath(".//a:defRPr", namespaces=NS):
            def_r_pr.set("sz", str(size))
    if align is not None:
        paragraphs = shape.xpath(".//a:p", namespaces=NS)
        for para in paragraphs:
            if para.find("a:pPr", namespaces=NS) is None:
                para.insert(0, etree.Element(q("a:pPr")))
        for p_pr in shape.xpath(".//a:pPr", namespaces=NS):
            p_pr.set("algn", align)
    if color is not None or bold is not None:
        for r_pr in shape.xpath(".//a:rPr", namespaces=NS):
            if bold is not None:
                r_pr.set("b", "1" if bold else "0")
            if color is not None:
                for fill in r_pr.findall("a:solidFill", namespaces=NS):
                    r_pr.remove(fill)
                fill = etree.SubElement(r_pr, q("a:solidFill"))
                etree.SubElement(fill, q("a:srgbClr")).set("val", color)


def clear_shape(shape):
    if shape is not None:
        set_shape_text(shape, "")


def strip_non_text_media(root):
    tree = root.find(".//p:spTree", namespaces=NS)
    if tree is None:
        return
    for node in list(tree):
        tag = etree.QName(node).localname
        if tag in {"pic", "graphicFrame", "grpSp"}:
            tree.remove(node)


def prune_extra_text_shapes(root, keep_ids: set[str]):
    tree = root.find(".//p:spTree", namespaces=NS)
    if tree is None:
        return
    for node in list(tree):
        if etree.QName(node).localname != "sp":
            continue
        c_nv_pr = node.find(".//p:cNvPr", namespaces=NS)
        shape_id = c_nv_pr.get("id") if c_nv_pr is not None else None
        if shape_id not in keep_ids:
            tree.remove(node)


def normalize_fonts(root):
    return


def strip_no_autofit(root):
    for no_autofit in root.xpath(".//a:noAutofit", namespaces=NS):
        parent = no_autofit.getparent()
        if parent is not None:
            parent.remove(no_autofit)


def topic_paragraphs(topics):
    paragraphs = []
    for item in topics:
        if isinstance(item, str):
            paragraphs.append(make_para(item, size=TOPIC_SIZE, bold=False, level=0))
            continue
        topic = item.get("topic", "")
        details = item.get("details", [])
        if topic:
            paragraphs.append(make_para(topic, size=TOPIC_SIZE, bold=False, level=0))
        for detail in details:
            if isinstance(detail, dict):
                kind = detail.get("kind") or detail.get("type")
                text = detail.get("text") or detail.get("equation") or ""
                if kind == "equation" or "equation" in detail:
                    paragraphs.append(make_equation_para(str(text)))
                elif text:
                    paragraphs.append(make_para(str(text), size=DETAIL_SIZE, color="333399", level=1))
                continue
            paragraphs.append(make_para(str(detail), size=DETAIL_SIZE, color="333399", level=1))
    return paragraphs


def reference_paragraphs(refs):
    return [make_para(ref, size=REFERENCE_SIZE, bullet=False, citation_size=None) for ref in refs]


def edit_outline(root, current: str | None):
    title = shape_by_id(root, "2")
    body = shape_by_id(root, "3")
    set_shape_text(
        title,
        "Outline",
        size=TITLE_SIZE,
        color=TITLE_COLOR,
        bold=True,
        box=TITLE_BOX,
        align="ctr",
    )
    paragraphs = []
    for section in SECTIONS:
        active = current and section.lower() == current.lower()
        paragraphs.append(make_outline_para(section, inactive=bool(current and not active)))
    replace_tx_body(body, paragraphs, box=BODY_BOX)


def edit_title(root, spec):
    add_white_cover(root, TITLE_LINE_COVER)
    add_black_separator(root, TITLE_SEPARATOR)
    set_shape_text(
        shape_by_id(root, "97"),
        spec.get("title", ""),
        size=TITLE_SIZE,
        color=TITLE_COLOR,
        bold=True,
        align="ctr",
    )
    venue = spec.get("venue", "")
    set_shape_text(shape_by_id(root, "103"), f"Published in {venue}" if venue else "")
    authors = spec.get("authors", "")
    affiliations = spec.get("affiliations", "")
    if authors or affiliations:
        replace_tx_body(
            shape_by_id(root, "100"),
            [
                make_para(authors, size=1400, color="000000", bullet=False, align="ctr", citation_size=None),
                make_para(affiliations, size=1400, color="000000", bullet=False, align="ctr", citation_size=None),
            ],
            box=AUTHOR_BOX,
        )
    info = []
    if spec.get("date"):
        info.append(spec["date"])
    if spec.get("presenter"):
        info.append(f"Presenter: {spec['presenter']}")
    if info:
        presenter_line = f"Presenter: {spec['presenter']}" if spec.get("presenter") else ""
        replace_tx_body(
            shape_by_id(root, "98"),
            [
                make_para(spec.get("date", ""), size=DETAIL_SIZE, color=TITLE_COLOR, bold=True, bullet=False, align="ctr"),
                make_para(presenter_line, size=DETAIL_SIZE, color=TITLE_COLOR, bold=True, bullet=False, align="ctr"),
            ],
            box=TITLE_INFO_BOX,
        )
    else:
        clear_shape(shape_by_id(root, "98"))


def edit_content(root, spec):
    set_shape_text(
        shape_by_id(root, "2"),
        spec.get("title", ""),
        size=TITLE_SIZE,
        color=TITLE_COLOR,
        bold=True,
        box=TITLE_BOX,
        align="ctr",
    )
    replace_tx_body(shape_by_id(root, "3"), topic_paragraphs(spec.get("topics", [])), box=BODY_BOX)
    refs = spec.get("references", [])
    if refs:
        replace_tx_body(shape_by_id(root, "6"), reference_paragraphs(refs), wrap="none")
    else:
        clear_shape(shape_by_id(root, "6"))


def edit_slide_number(root, number: int):
    num_shape = shape_by_id(root, "5")
    if num_shape is None:
        num_shape = shape_by_id(root, "562")
    if num_shape is None:
        num_shape = shape_by_id(root, "96")
    if num_shape is not None:
        for t in text_values(num_shape):
            t.text = str(number)


def edit_slide(root, spec, number: int):
    kind = spec.get("kind", "content")
    if spec.get("strip_media", kind in {"content", "previous-work", "remarks"}):
        strip_non_text_media(root)
    if kind in {"content", "previous-work", "remarks"}:
        prune_extra_text_shapes(root, {"2", "3", "4", "5", "6"})
    elif kind.startswith("outline"):
        prune_extra_text_shapes(root, {"2", "3", "4", "5"})
    if kind == "title":
        edit_title(root, spec)
    elif kind.startswith("outline"):
        edit_outline(root, spec.get("current"))
    elif kind == "thank-you":
        pass
    else:
        edit_content(root, spec)
    edit_slide_number(root, number)
    normalize_fonts(root)
    strip_no_autofit(root)


def max_rid(root):
    max_id = 1
    for rel in root.xpath(".//rel:Relationship", namespaces=NS):
        match = re.fullmatch(r"rId(\d+)", rel.get("Id", ""))
        if match:
            max_id = max(max_id, int(match.group(1)))
    return max_id


def remove_notes_rels(rels_xml: bytes | None):
    if rels_xml is None:
        return None
    root = etree.fromstring(rels_xml)
    for rel in list(root):
        if rel.get("Type", "").endswith("/notesSlide"):
            root.remove(rel)
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def rebuild_presentation(files, slide_count: int):
    parser = etree.XMLParser(remove_blank_text=False, recover=True)
    rels = etree.fromstring(files["ppt/_rels/presentation.xml.rels"])
    for rel in list(rels):
        if rel.get("Type", "").endswith("/slide"):
            rels.remove(rel)
    slide_rids = [f"rId{max_rid(rels) + idx}" for idx in range(1, slide_count + 1)]

    pres = etree.fromstring(files["ppt/presentation.xml"], parser)
    sld_id_lst = pres.find("p:sldIdLst", namespaces=NS)
    for child in list(sld_id_lst):
        sld_id_lst.remove(child)
    for idx in range(1, slide_count + 1):
        sld_id = etree.Element(q("p:sldId"))
        sld_id.set("id", str(2000 + idx))
        sld_id.set(q("r:id"), slide_rids[idx - 1])
        sld_id_lst.append(sld_id)
    files["ppt/presentation.xml"] = etree.tostring(
        pres, xml_declaration=True, encoding="UTF-8", standalone=True
    )

    insert_at = 0
    for idx in range(1, slide_count + 1):
        rel = etree.Element(f"{{{NS['rel']}}}Relationship")
        rel.set("Id", slide_rids[idx - 1])
        rel.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide")
        rel.set("Target", f"slides/slide{idx}.xml")
        rels.insert(insert_at, rel)
        insert_at += 1
    files["ppt/_rels/presentation.xml.rels"] = etree.tostring(
        rels, xml_declaration=True, encoding="UTF-8", standalone=True
    )


def update_content_types(files, slide_count: int):
    root = etree.fromstring(files["[Content_Types].xml"])
    slide_content_type = "application/vnd.openxmlformats-officedocument.presentationml.slide+xml"
    existing = {
        child.get("PartName")
        for child in root.findall("ct:Override", namespaces=NS)
        if child.get("ContentType") == slide_content_type
    }
    for idx in range(1, slide_count + 1):
        part_name = f"/ppt/slides/slide{idx}.xml"
        if part_name in existing:
            continue
        override = etree.Element(f"{{{NS['ct']}}}Override")
        override.set("PartName", part_name)
        override.set("ContentType", slide_content_type)
        root.append(override)
    files["[Content_Types].xml"] = etree.tostring(
        root, xml_declaration=True, encoding="UTF-8", standalone=True
    )


def update_app_slide_count(files, slide_count: int):
    parser = etree.XMLParser(remove_blank_text=False, recover=True)
    app = etree.fromstring(files["docProps/app.xml"], parser)
    slides = app.find("{http://schemas.openxmlformats.org/officeDocument/2006/extended-properties}Slides")
    if slides is not None:
        slides.text = str(slide_count)
    files["docProps/app.xml"] = etree.tostring(
        app, xml_declaration=True, encoding="UTF-8", standalone=True
    )


def build(spec_path: Path, output: Path, template: Path):
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    files = read_package(template)
    parser = etree.XMLParser(remove_blank_text=False, recover=True)
    slides = spec.get("slides", [])
    if not slides:
        raise ValueError("spec must contain at least one slide")

    original = dict(files)
    for idx, slide_spec in enumerate(slides, start=1):
        source_kind = slide_spec.get("source") or slide_spec.get("kind", "content")
        source_num = int(source_kind) if str(source_kind).isdigit() else SOURCE_SLIDES.get(source_kind, 16)
        source_name = f"ppt/slides/slide{source_num}.xml"
        root = etree.fromstring(original[source_name], parser)
        edit_slide(root, slide_spec, idx)
        files[f"ppt/slides/slide{idx}.xml"] = etree.tostring(
            root, xml_declaration=True, encoding="UTF-8", standalone=True
        )

        rel_name = f"ppt/slides/_rels/slide{source_num}.xml.rels"
        if rel_name in original:
            out_rel = f"ppt/slides/_rels/slide{idx}.xml.rels"
            files[out_rel] = remove_notes_rels(original[rel_name])

    rebuild_presentation(files, len(slides))
    update_content_types(files, len(slides))
    update_app_slide_count(files, len(slides))
    write_package(output, files)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--template",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "assets" / "template.pptx",
    )
    args = parser.parse_args()
    build(args.spec, args.output, args.template)
    print(args.output)


if __name__ == "__main__":
    main()
