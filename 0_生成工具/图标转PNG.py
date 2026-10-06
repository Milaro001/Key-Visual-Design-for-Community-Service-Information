#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图标转 PNG（SVG → PDF → PNG）
=============================
用途：把从开源图标库（Iconify / Tabler / Lucide 等）下载的线性 SVG，
      在**不改形状**的前提下转成任意尺寸、任意颜色的 PNG —— 供海报排版用。

为什么自己写：本机没有 rsvg-convert / inkscape / magick / cairosvg / chromium，
pip 也装不了（沙箱限制）；但 Ghostscript 有。所以走 SVG → 最小 PDF → gs 光栅化。

支持：<path>（M L H V C S Q T A Z，含相对指令）· <circle> · <rect> · <line> · <polyline>
      描边属性：stroke / stroke-width / stroke-linecap / stroke-linejoin / fill

用法：
    python3 图标转PNG.py <输入.svg> <输出.png> --size 512 --color "#1B2A38"
    python3 图标转PNG.py --batch manifest.txt        # 每行：svg路径,输出png,尺寸,颜色
"""

import io
import math
import os
import re
import subprocess
import sys

# ---------------------------------------------------------------- SVG 解析
NUM = r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?"


def parse_path(d):
    """把 SVG path 的 d 拆成 [(cmd, [args...]), ...]"""
    out, i, n = [], 0, len(d)
    while i < n:
        m = re.match(r"\s*([MmLlHhVvCcSsQqTtAaZz])([^MmLlHhVvCcSsQqTtAaZz]*)", d[i:])
        if not m:
            i += 1
            continue
        cmd, raw = m.group(1), m.group(2)
        nums = [float(x) for x in re.findall(NUM, raw)]
        out.append((cmd, nums))
        i += m.end()
    return out


def arc_to_beziers(x1, y1, rx, ry, phi, large, sweep, x2, y2):
    """SVG 圆弧 → 三次贝塞尔（标准端点参数化换算）"""
    if rx == 0 or ry == 0:
        return [("L", [x2, y2])]
    phi = math.radians(phi)
    cos_p, sin_p = math.cos(phi), math.sin(phi)
    dx2, dy2 = (x1 - x2) / 2.0, (y1 - y2) / 2.0
    x1p, y1p = cos_p * dx2 + sin_p * dy2, -sin_p * dx2 + cos_p * dy2
    rx, ry = abs(rx), abs(ry)
    lam = x1p ** 2 / rx ** 2 + y1p ** 2 / ry ** 2
    if lam > 1:
        s = math.sqrt(lam)
        rx, ry = rx * s, ry * s
    num = rx ** 2 * ry ** 2 - rx ** 2 * y1p ** 2 - ry ** 2 * x1p ** 2
    den = rx ** 2 * y1p ** 2 + ry ** 2 * x1p ** 2
    co = math.sqrt(max(num / den, 0.0))
    if large == sweep:
        co = -co
    cxp, cyp = co * rx * y1p / ry, -co * ry * x1p / rx
    cx = cos_p * cxp - sin_p * cyp + (x1 + x2) / 2.0
    cy = sin_p * cxp + cos_p * cyp + (y1 + y2) / 2.0

    def ang(ux, uy, vx, vy):
        dot = ux * vx + uy * vy
        norm = math.hypot(ux, uy) * math.hypot(vx, vy)
        a = math.acos(max(min(dot / norm, 1.0), -1.0))
        return -a if ux * vy - uy * vx < 0 else a

    th1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dth = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not sweep and dth > 0:
        dth -= 2 * math.pi
    elif sweep and dth < 0:
        dth += 2 * math.pi
    segs = max(1, int(math.ceil(abs(dth) / (math.pi / 2))))
    step = dth / segs
    out = []
    for k in range(segs):
        t1, t2 = th1 + k * step, th1 + (k + 1) * step
        a = (4.0 / 3.0) * math.tan((t2 - t1) / 4.0)
        p1 = (cx + rx * math.cos(t1) * cos_p - ry * math.sin(t1) * sin_p,
              cy + rx * math.cos(t1) * sin_p + ry * math.sin(t1) * cos_p)
        p2 = (cx + rx * math.cos(t2) * cos_p - ry * math.sin(t2) * sin_p,
              cy + rx * math.cos(t2) * sin_p + ry * math.sin(t2) * cos_p)
        d1 = (-rx * math.sin(t1) * cos_p - ry * math.cos(t1) * sin_p,
              -rx * math.sin(t1) * sin_p + ry * math.cos(t1) * cos_p)
        d2 = (-rx * math.sin(t2) * cos_p - ry * math.cos(t2) * sin_p,
              -rx * math.sin(t2) * sin_p + ry * math.cos(t2) * cos_p)
        c1 = (p1[0] + a * d1[0], p1[1] + a * d1[1])
        c2 = (p2[0] - a * d2[0], p2[1] - a * d2[1])
        out.append(("C", [c1[0], c1[1], c2[0], c2[1], p2[0], p2[1]]))
    return out


def path_ops(d):
    """SVG path → PDF 路径操作符列表（y 轴翻转由外层 cm 处理）"""
    ops, cx, cy, start, prev_c, prev_q = [], 0.0, 0.0, (0.0, 0.0), None, None
    for cmd, a in parse_path(d):
        rel = cmd.islower()
        C = cmd.upper()
        if C == "M":
            for k in range(0, len(a) - 1, 2):
                x, y = a[k] + (cx if rel else 0), a[k + 1] + (cy if rel else 0)
                ops.append(("m", [x, y]))
                if k == 0:
                    start = (x, y)
                cx, cy = x, y
        elif C == "L":
            for k in range(0, len(a) - 1, 2):
                x, y = a[k] + (cx if rel else 0), a[k + 1] + (cy if rel else 0)
                ops.append(("l", [x, y]))
                cx, cy = x, y
        elif C == "H":
            for v in a:
                x = v + (cx if rel else 0)
                ops.append(("l", [x, cy]))
                cx = x
        elif C == "V":
            for v in a:
                y = v + (cy if rel else 0)
                ops.append(("l", [cx, y]))
                cy = y
        elif C in ("C", "S", "Q", "T"):
            if C == "C":
                step, i = 6, 0
            elif C == "S":
                step, i = 4, 0
            elif C == "Q":
                step, i = 4, 0
            else:
                step, i = 2, 0
            while i + step <= len(a):
                seg = a[i:i + step]
                if C == "C":
                    p = [seg[0] + (cx if rel else 0), seg[1] + (cy if rel else 0),
                         seg[2] + (cx if rel else 0), seg[3] + (cy if rel else 0),
                         seg[4] + (cx if rel else 0), seg[5] + (cy if rel else 0)]
                    prev_c = (p[2], p[3])
                elif C == "S":
                    c1 = (2 * cx - prev_c[0], 2 * cy - prev_c[1]) if prev_c else (cx, cy)
                    p = [c1[0], c1[1], seg[0] + (cx if rel else 0), seg[1] + (cy if rel else 0),
                         seg[2] + (cx if rel else 0), seg[3] + (cy if rel else 0)]
                    prev_c = (p[2], p[3])
                elif C == "Q":
                    qx, qy = seg[0] + (cx if rel else 0), seg[1] + (cy if rel else 0)
                    ex, ey = seg[2] + (cx if rel else 0), seg[3] + (cy if rel else 0)
                    p = [cx + 2 / 3 * (qx - cx), cy + 2 / 3 * (qy - cy),
                         ex + 2 / 3 * (qx - ex), ey + 2 / 3 * (qy - ey), ex, ey]
                    prev_c, prev_q = (p[2], p[3]), (qx, qy)
                else:  # T
                    qx, qy = (2 * cx - prev_q[0], 2 * cy - prev_q[1]) if prev_q else (cx, cy)
                    ex, ey = seg[0] + (cx if rel else 0), seg[1] + (cy if rel else 0)
                    p = [cx + 2 / 3 * (qx - cx), cy + 2 / 3 * (qy - cy),
                         ex + 2 / 3 * (qx - ex), ey + 2 / 3 * (qy - ey), ex, ey]
                    prev_c, prev_q = (p[2], p[3]), (qx, qy)
                ops.append(("c", p))
                cx, cy = p[-2], p[-1]
                i += step
        elif C == "A":
            i = 0
            while i + 7 <= len(a):
                rx, ry, rot, laf, sf = a[i], a[i + 1], a[i + 2], a[i + 3], a[i + 4]
                ex = a[i + 5] + (cx if rel else 0)
                ey = a[i + 6] + (cy if rel else 0)
                for sub in arc_to_beziers(cx, cy, rx, ry, rot, int(laf), int(sf), ex, ey):
                    ops.append((sub[0].lower(), sub[1]))
                cx, cy = ex, ey
                i += 7
        elif C == "Z":
            ops.append(("h", []))
            cx, cy = start
    return ops


# ---------------------------------------------------------------- 最小 PDF
def pdf_from_svg(svg_text, color_override=None, size_pt=24.0):
    vb = re.search(r'viewBox="([^"]+)"', svg_text)
    if vb:
        v = [float(x) for x in re.split(r"[ ,]+", vb.group(1).strip())]
        minx, miny, vbw, vbh = v[0], v[1], v[2], v[3]
    else:
        minx = miny = 0.0
        vbw = vbh = size_pt

    def attrs(tag):
        return dict(re.findall(r'([a-zA-Z][a-zA-Z0-9-]*)="([^"]*)"', tag))

    def parse_color(v):
        """把颜色写法统一成 (r,g,b)；无法解析（none/url()/渐变/currentColor）返回 None"""
        if not v or v in ("none", "transparent"):
            return None
        v = v.strip()
        if v.startswith("url(") or v.startswith("var("):
            return None
        if v == "currentColor":
            v = color_override or "#000000"
        v = v.lstrip("#")
        if len(v) == 3:
            v = "".join(c * 2 for c in v)
        if len(v) != 6 or any(c not in "0123456789abcdefABCDEF" for c in v):
            return None
        return tuple(int(v[i:i + 2], 16) / 255 for i in (0, 2, 4))

    body = []
    # 按文档顺序遍历，支持 <g> 属性继承（描边/填充常写在父级 g 上）
    tag_re = re.compile(r"<(/?)(g|path|circle|rect|line|polyline|polygon)\b([^>]*?)(/?)>", re.S)
    stack = []
    for m in tag_re.finditer(svg_text):
        closing, el, raw, selfclose = m.group(1), m.group(2), m.group(3), m.group(4)
        if el == "g":
            if closing:
                if stack:
                    stack.pop()
            elif not selfclose:
                stack.append(attrs(raw))
            continue
        if closing:
            continue
        at = {}
        for d in stack:          # 由外到内合并，内层覆盖外层
            at.update(d)
        at.update(attrs(raw))    # 元素自身属性优先
        stroke = at.get("stroke", "none")
        if color_override and stroke not in ("none", None):
            stroke = color_override
        if stroke == "currentColor":
            stroke = color_override or "#000000"
        fill = at.get("fill", "none")
        if fill == "currentColor":
            fill = color_override or "#000000"
        if fill not in ("none", None) and color_override and not fill.startswith(("url(", "var(")):
            fill = color_override
        sw = float(at.get("stroke-width", 1))
        cap = {"round": 1, "square": 2}.get(at.get("stroke-linecap", "butt"), 0)
        join = {"round": 1, "bevel": 2}.get(at.get("stroke-linejoin", "miter"), 0)

        ops = []
        if el == "path":
            ops = path_ops(at.get("d", ""))
        elif el == "circle":
            cx, cy, r = float(at["cx"]), float(at["cy"]), float(at["r"])
            ops = path_ops(f"M {cx - r} {cy} A {r} {r} 0 1 0 {cx + r} {cy} A {r} {r} 0 1 0 {cx - r} {cy} Z")
        elif el == "rect":
            x, y, w, h = float(at["x"]), float(at["y"]), float(at["width"]), float(at["height"])
            rx = float(at.get("rx", 0))
            if rx > 0:
                ops = path_ops(f"M {x+rx} {y} H {x+w-rx} A {rx} {rx} 0 0 1 {x+w} {y+rx} V {y+h-rx} "
                               f"A {rx} {rx} 0 0 1 {x+w-rx} {y+h} H {x+rx} A {rx} {rx} 0 0 1 {x} {y+h-rx} "
                               f"V {y+rx} A {rx} {rx} 0 0 1 {x+rx} {y} Z")
            else:
                ops = path_ops(f"M {x} {y} H {x+w} V {y+h} H {x} Z")
        elif el == "line":
            ops = path_ops(f"M {at['x1']} {at['y1']} L {at['x2']} {at['y2']}")
        elif el in ("polyline", "polygon"):
            pts = [float(v) for v in re.findall(NUM, at.get("points", ""))]
            d = "M " + " L ".join(f"{pts[i]} {pts[i+1]}" for i in range(0, len(pts) - 1, 2))
            if el == "polygon":
                d += " Z"
            ops = path_ops(d)

        if not ops:
            continue
        body.append("%.3f w %d J %d j" % (sw, cap, join))
        sc = parse_color(stroke)
        if sc:
            body.append("%.4f %.4f %.4f RG" % sc)
        fc = parse_color(fill)
        if fc:
            body.append("%.4f %.4f %.4f rg" % fc)
        for op, args in ops:
            if op == "h":
                body.append("h")
            else:
                body.append(" ".join("%.3f" % a for a in args) + " " + op)
        if fc:
            body.append("B" if sc else "f")
        elif sc:
            body.append("S")

    content = ("q 1 0 0 -1 %.3f %.3f cm\n" % (-minx, vbh + miny)) + "\n".join(body) + "\nQ"
    objs = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %.3f %.3f] /Contents 4 0 R >>" % (vbw, vbh),
        "<< /Length %d >>\nstream\n%s\nendstream" % (len(content), content),
    ]
    out = io.StringIO()
    out.write("%PDF-1.4\n")
    offsets = []
    for i, o in enumerate(objs, 1):
        offsets.append(out.tell())
        out.write("%d 0 obj\n%s\nendobj\n" % (i, o))
    xref = out.tell()
    out.write("xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1))
    for off in offsets:
        out.write("%010d 00000 n \n" % off)
    out.write("trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, xref))
    return out.getvalue().encode("latin-1"), vbw


def convert(svg_path, png_path, size_px=512, color=None, transparent=True):
    svg = io.open(svg_path, encoding="utf-8").read()
    pdf_bytes, vbw = pdf_from_svg(svg, color_override=color)
    tmp_pdf = png_path + ".tmp.pdf"
    with open(tmp_pdf, "wb") as f:
        f.write(pdf_bytes)
    res = int(round(size_px * 72.0 / vbw))
    dev = "pngalpha" if transparent else "png16m"
    cmd = ["gs", "-q", "-dNOPAUSE", "-dBATCH", "-dSAFER", "-sDEVICE=" + dev,
           "-r%d" % res, "-dTextAlphaBits=4", "-dGraphicsAlphaBits=4",
           "-sOutputFile=" + png_path, tmp_pdf]
    r = subprocess.run(cmd, capture_output=True)
    os.remove(tmp_pdf)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode()[:300])
    return png_path


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--batch":
        for line in io.open(sys.argv[2], encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split(",")]
            svg, png = parts[0], parts[1]
            size = int(parts[2]) if len(parts) > 2 else 512
            col = parts[3] if len(parts) > 3 else None
            convert(svg, png, size, col)
            print("  ✓", png)
        return
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    svg, png = sys.argv[1], sys.argv[2]
    size, color = 512, None
    if "--size" in sys.argv:
        size = int(sys.argv[sys.argv.index("--size") + 1])
    if "--color" in sys.argv:
        color = sys.argv[sys.argv.index("--color") + 1]
    convert(svg, png, size, color)
    print("  ✓", png)


if __name__ == "__main__":
    main()
