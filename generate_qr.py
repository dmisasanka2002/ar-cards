#!/usr/bin/env python3
"""
Generate one QR code per guest for the AR Time-Capsule Cards project.

Reads a CSV of guests (name, video filename) and writes one PNG QR code per
row. Each QR encodes the URL a guest scans to see their personal AR message:

    https://<your-hosted-page>/?name=<Guest Name>&v=<their-video-filename>

Usage:
    pip install "qrcode[pil]" --break-system-packages
    python generate_qr.py guests.csv --base-url https://yourname.github.io/ar-cards/
"""
import argparse
import csv
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlencode

import qrcode


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[\s_-]+", "-", value) or "guest"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("csv_path", help="CSV file with columns: name,video")
    parser.add_argument(
        "--base-url",
        required=True,
        help="URL where index.html is hosted, e.g. https://yourname.github.io/ar-cards/",
    )
    parser.add_argument("--out-dir", default="qr_codes", help="Folder to write QR PNGs into (default: qr_codes)")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    base_url = args.base_url if args.base_url.endswith("/") else args.base_url + "/"

    with open(args.csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or "name" not in reader.fieldnames or "video" not in reader.fieldnames:
            raise SystemExit('CSV must have a header row with columns: "name,video"')

        count = 0
        for row in reader:
            name = (row.get("name") or "").strip()
            video = (row.get("video") or "").strip()
            if not name or not video:
                continue

            url = base_url + "?" + urlencode({"name": name, "v": video})
            img = qrcode.make(url, box_size=10, border=3)

            filename = out_dir / f"{slugify(name)}.png"
            img.save(filename)
            count += 1
            print(f"{name:20s} -> {filename}   ({url})")

    print(f"\nDone. Generated {count} QR code(s) in {out_dir}/")


if __name__ == "__main__":
    main()
