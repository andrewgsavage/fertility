import json

INPUT = "data/LAD_MAY_2025_UK_BFE_V2_5966901361471275117.geojson"
OUTPUT = "outputs/lad_boundaries_simplified.geojson"

EPSILON = 0.0015  # degrees (~150m) minimum spacing kept between consecutive ring points
ROUND = 5  # decimal places (~1.1m precision)


def dist2(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def simplify_ring(ring, epsilon):
    if len(ring) <= 4:
        return ring
    eps2 = epsilon * epsilon
    kept = [ring[0]]
    for pt in ring[1:-1]:
        if dist2(pt, kept[-1]) >= eps2:
            kept.append(pt)
    kept.append(ring[-1])
    if len(kept) < 4:
        return ring
    return kept


def round_pt(pt):
    return [round(pt[0], ROUND), round(pt[1], ROUND)]


def simplify_geometry(geom):
    t = geom["type"]
    if t == "Polygon":
        geom["coordinates"] = [
            [round_pt(p) for p in simplify_ring(ring, EPSILON)] for ring in geom["coordinates"]
        ]
    elif t == "MultiPolygon":
        geom["coordinates"] = [
            [[round_pt(p) for p in simplify_ring(ring, EPSILON)] for ring in poly]
            for poly in geom["coordinates"]
        ]
    return geom


with open(INPUT, "r", encoding="utf-8") as f:
    data = json.load(f)

out_features = []
for feat in data["features"]:
    props = feat["properties"]
    out_features.append(
        {
            "type": "Feature",
            "properties": {"code": props["LAD25CD"], "name": props["LAD25NM"]},
            "geometry": simplify_geometry(feat["geometry"]),
        }
    )

out = {"type": "FeatureCollection", "features": out_features}

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(out, f, separators=(",", ":"))

print(f"Wrote {OUTPUT} ({len(out_features)} features)")
