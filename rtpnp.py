#!/usr/bin/env python3
"""Convert KiBot's rt_cpl output into RaptorTech's pick-and-place CSV format.

Usage:
    python3 raptortech_pnp.py <board>_PnP_raw.csv [<board>_PnP.csv]

Output columns:
    Designator,Footprint,Mid X,Mid Y,Ref X,Ref Y,Pad X,Pad Y,Layer,Rotation,Comment
Ref X/Ref Y/Pad X/Pad Y are left blank, Layer is T/B, rotation is 0-359,
and numbers have trailing zeros removed (8.370 -> 8.37, 270.0000 -> 270).
"""
import csv
import sys
from pathlib import Path

OUT_COLUMNS = ["Designator", "Footprint", "Mid X", "Mid Y", "Ref X", "Ref Y",
               "Pad X", "Pad Y", "Layer", "Rotation", "Comment"]


def num(text: str, digits: int = 2) -> str:
    """Round and drop trailing zeros; avoid '-0'."""
    s = f"{round(float(text), digits):.{digits}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def rotation(text: str) -> str:
    return num(str(float(text) % 360))


def layer(text: str) -> str:
    side = text.strip().lower()
    if side in ("top", "t", "front", "f"):
        return "T"
    if side in ("bottom", "b", "back"):
        return "B"
    raise ValueError(f"Unknown side '{text}'")


def convert(src: Path, dst: Path) -> int:
    with src.open(newline="") as f:
        rows = list(csv.DictReader(f))
    with dst.open("w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(OUT_COLUMNS)
        for r in rows:
            w.writerow([
                r["Designator"], r["Footprint"].replace(".", ""),
                num(r["Mid X"]), num(r["Mid Y"]),
                "", "", "", "",
                layer(r["Layer"]), rotation(r["Rotation"]), r["Comment"],
            ])
    return len(rows)


def main() -> None:
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    src = Path(sys.argv[1])
    if len(sys.argv) == 3:
        dst = Path(sys.argv[2])
    else:
        dst = src.with_name(src.name.replace("_PnP_raw", "_PnP"))
        if dst == src:
            dst = src.with_name(src.stem + "_rt.csv")
    n = convert(src, dst)
    print(f"Wrote {n} parts to {dst}")


if __name__ == "__main__":
    main()
