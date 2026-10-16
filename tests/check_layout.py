"""Offline house-layout checks for trusted local Q-SYS Lua source, not rendering."""
import argparse
import base64
import hashlib
import json
import math
from pathlib import Path


class LayoutError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise LayoutError(message)


def plain(value):
    if hasattr(value, "items"):
        items = dict(value.items())
        if items and set(items) == set(range(1, len(items) + 1)):
            return [plain(items[i]) for i in range(1, len(items) + 1)]
        return {k: plain(v) for k, v in items.items()}
    return value


def box(obj):
    values = list(obj["Position"]) + list(obj["Size"])
    require(len(values) == 4 and all(type(n) in (int, float) and math.isfinite(n) for n in values), "invalid geometry")
    x, y, w, h = values
    require(w > 0 and h > 0, "nonpositive size")
    return x, y, w, h


def contains(outer, inner):
    x, y, w, h = outer
    a, b, c, d = inner
    return x <= a and y <= b and a+c <= x+w and b+d <= y+h


def overlaps(a, b):
    x, y, w, h = a
    q, r, s, t = b
    return min(x+w, q+s) > max(x, q) and min(y+h, r+t) > max(y, r)


def expanded_definitions(definitions):
    result = {}
    for name, definition in definitions.items():
        count = definition.get("Count", 1)
        require(type(count) is int and count > 0, f"invalid Count: {name}")
        for key in ([name] if count == 1 else [f"{name} {i}" for i in range(1, count+1)]):
            require(key not in result, f"colliding expanded control name: {key}")
            result[key] = definition
    return result


def flatten(layout, definitions):
    expected = expanded_definitions(definitions)
    require(set(layout) == set(expected), "layout bindings differ from declared controls")
    require(all(isinstance(v, dict) for v in layout.values()), "expected flat SDK layout tables")
    return layout


def check_page(layout, graphics, definitions, spec, version):
    layout = flatten(layout, definitions)
    visible = {k: v for k, v in layout.items() if v.get("Style") != "None"}
    require(all(v.get("PrettyName", "").strip() for v in layout.values()), "missing PrettyName")
    objects = graphics + list(visible.values())
    orders = [o.get("ZOrder") for o in objects]
    require(all(type(n) is int for n in orders) and len(set(orders)) == len(orders), "duplicate or absent ZOrder")
    width, height = spec["size"]
    for obj in objects:
        require(contains((0, 0, width, height), box(obj)), "out of page bounds")
    text = [o for o in graphics if o.get("Type") in ("Label", "Header")]
    texts = {o.get("Text", "") for o in text}
    require(set(spec["captions"]) <= texts, "required caption missing")
    footer_text = "Version " + version
    footer = [o for o in text if o.get("Text") == footer_text]
    require(len(footer) == 1, "version footer missing or duplicated")
    require(box(footer[0]) == (width-195, height-22, 180, 16), "footer geometry")
    titles = [o for o in text if o.get("Text") == spec["name"]]
    require(len(titles) == 1 and box(titles[0]) == tuple(spec["title_box"]), "page title geometry")
    panels = [o for o in graphics if o.get("Type") == "GroupBox"]
    for field, color in (("canvas", [255,255,255]), ("brand_panel", [230,230,230]), ("content_panel", [230,230,230])):
        matches = [p for p in panels if box(p) == tuple(spec[field])]
        require(len(matches) == 1 and matches[0].get("Fill") == color, f"{field} geometry or fill")
    for outer in panels:
        for inner in panels:
            if outer is not inner and contains(box(outer), box(inner)):
                require(inner["ZOrder"] > outer["ZOrder"], "panel behind containing background")
    for obj in objects:
        if obj.get("Type") != "GroupBox":
            for panel in panels:
                if overlaps(box(obj), box(panel)):
                    require(obj["ZOrder"] > panel["ZOrder"], "foreground behind panel")
        if box(obj)[1] >= spec["content_panel"][1] and obj.get("Text") != footer_text:
            require(contains(spec["content_panel"], box(obj)), "outside content panel")
    for index, obj in enumerate(text):
        require(not any(overlaps(box(obj), box(other)) for other in text[index+1:]), "overlapping static text")
    for i, (name, obj) in enumerate(visible.items()):
        for other in list(visible.values())[i+1:]:
            require(not overlaps(box(obj), box(other)), f"overlapping controls: {name}")
        require(not any(overlaps(box(obj), box(t)) for t in text), f"control overlaps text: {name}")
        for field in ("TextColor", "OffColor", "UnlinkOffColor"):
            if field in obj:
                reason = spec.get("intentional_overrides", {}).get(f"{name}.{field}", "")
                require(isinstance(reason, str) and bool(reason.strip()), f"unexplained {field}: {name}")
        definition = expanded_definitions(definitions)[name]
        if definition.get("ButtonType") == "Trigger":
            require(obj.get("Style") == "Button" and obj.get("ButtonStyle") == "Trigger", f"trigger style mismatch: {name}")
            require(obj.get("Color") == [255,255,255] and obj.get("CornerRadius") == 2 and obj.get("Margin") == 2, f"native trigger defaults: {name}")
        if not obj.get("Legend", "").strip():
            caption = spec["labels"].get(name)
            require(bool(caption) and caption in texts, f"control label missing: {name}")
            candidates = [t for t in text if t.get("Text") == caption]
            x,y,w,h = box(obj)
            def adjacent(t):
                a,b,c,d = box(t)
                return (b == y and 0 <= x-(a+c) <= 12) or (b+d <= y and y-(b+d) <= 80 and a < x+w and x < a+c)
            require(any(adjacent(t) for t in candidates), f"control label misplaced: {name}")
    for names in spec["rows"]:
        require(all(name in visible for name in names), "row references hidden or absent control")
        rows = [visible[name] for name in names]
        require(len({box(r)[0] for r in rows}) == 1, "field column misaligned")
        require(all(box(b)[1]-box(a)[1] == spec.get("row_pitch", 25) for a,b in zip(rows, rows[1:])), "row pitch")
    if "logo" in spec:
        logos = [o for o in graphics if o.get("Type") in ("Svg", "Image")]
        require(len(logos) == 1, "logo missing or duplicated")
        require(box(logos[0]) == tuple(spec["logo"]["box"]), "logo geometry")
        digest = hashlib.sha256(base64.b64decode(logos[0]["Image"], validate=True)).hexdigest()
        require(digest == spec["logo"]["sha256"], "logo identity")
    return set(visible)


def snapshots(source, overrides, specs):
    from lupa.lua53 import LuaRuntime
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(source)
    g = lua.globals()
    properties = lua.table()
    if g.GetProperties is not None:
        for definition in g.GetProperties().values():
            properties[definition.Name] = lua.table_from({"Value": definition.Value})
    properties.plugin_show_debug = lua.table_from({"Value": False})
    for name, value in overrides.items():
        require(properties[name] is not None, f"unknown property override: {name}")
        properties[name].Value = value
    if g.RectifyProperties is not None:
        g.RectifyProperties(properties)
    pages = [p.name for p in g.GetPages(properties).values()] if g.GetPages else [specs[0]["name"]]
    require(pages == [s["name"] for s in specs], "page order/names differ")
    output = []
    for index, spec in enumerate(specs, 1):
        properties.page_index = lua.table_from({"Value": index})
        declared = list(g.GetControls(properties).values())
        definitions = {d.Name: plain(d) for d in declared}
        require(len(definitions) == len(declared), "duplicate control names")
        layout, graphics = g.GetControlLayout(properties)
        output.append((plain(layout), [plain(v) for v in graphics.values()], definitions, spec, g.PluginInfo.Version))
    return output


def validate(source, contract):
    require(bool(contract["variants"]) and bool(contract["pages"]), "empty variants or pages")
    checked = 0
    for overrides in contract["variants"]:
        seen, expected, pretty = set(), set(), {}
        for args in snapshots(source, overrides, contract["pages"]):
            flattened = flatten(args[0], args[2])
            expected.update(flattened)
            for name, obj in flattened.items():
                require(name not in pretty or pretty[name] == obj.get("PrettyName"), f"PrettyName changes by page: {name}")
                pretty[name] = obj.get("PrettyName")
            seen.update(check_page(*args))
            checked += 1
        require(seen == expected, "declared controls missing from visible pages")
    return {"ok": True, "page_variants_checked": checked, "scope": "offline layout only; no Designer or device acceptance"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--contract", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = validate(args.source.read_text(encoding="utf-8-sig"), json.loads(args.contract.read_text(encoding="utf-8-sig")))
    except Exception as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        raise SystemExit(1)
    print(json.dumps(result))
