#!/usr/bin/env python3
"""
Generates target-card.svg: the front-of-card artwork used as the AR
tracking target for the AR Time-Capsule Cards project.

Deliberately dense and asymmetric (scattered embers, uneven candle
heights, corner detail) because MindAR's tracker needs plenty of
distinguishable local texture spread across the whole frame -- a plain
or symmetric design tracks poorly.

Usage:
    python make_target_card.py
Produces target-card.svg and target-card.png (2x resolution for print).
"""
import random

import cairosvg

random.seed(42)

W, H = 1800, 1000  # 1.8:1, matches index.html's default a-video ratio

INK = "#14110F"
INK_RAISED = "#1D1914"
GOLD = "#E8A33D"
GOLD_DIM = "#A5762C"
CREAM = "#F1E9DD"
EMBER = "#C97B4A"

parts = []
parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">')

# --- defs: soft glow filter for flames ---
parts.append(f'''
<defs>
  <filter id="glow" x="-100%" y="-100%" width="300%" height="300%">
    <feGaussianBlur stdDeviation="10" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
  <radialGradient id="warmth" cx="50%" cy="42%" r="65%">
    <stop offset="0%" stop-color="#2A2015"/>
    <stop offset="100%" stop-color="{INK}"/>
  </radialGradient>
</defs>
''')

# --- background ---
parts.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#warmth)"/>')

# --- scattered embers across the whole canvas (fine, unique texture) ---
ember_palette = [GOLD, GOLD_DIM, CREAM, EMBER]
for _ in range(260):
    x = random.uniform(0, W)
    y = random.uniform(0, H)
    r = random.uniform(1.2, 5.5)
    color = random.choice(ember_palette)
    op = random.uniform(0.12, 0.75)
    parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{color}" opacity="{op:.2f}"/>')

# --- a few larger soft embers for scale variety ---
for _ in range(14):
    x = random.uniform(0.05 * W, 0.95 * W)
    y = random.uniform(0.05 * H, 0.95 * H)
    r = random.uniform(8, 18)
    parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{GOLD}" opacity="{random.uniform(0.05, 0.15):.2f}" filter="url(#glow)"/>')

# --- corner accent marks (asymmetric, breaks up empty corners) ---
def star(cx, cy, size, rot, color, op):
    pts = []
    for i in range(10):
        ang = rot + i * (360 / 10)
        rad = size if i % 2 == 0 else size * 0.42
        import math
        px = cx + rad * math.cos(math.radians(ang))
        py = cy + rad * math.sin(math.radians(ang))
        pts.append(f"{px:.1f},{py:.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{color}" opacity="{op}"/>'

corner_marks = [
    (90, 80, 16, 12, GOLD, 0.55),
    (150, 140, 8, 40, CREAM, 0.4),
    (W - 110, 70, 12, 65, GOLD, 0.5),
    (W - 60, 150, 7, 100, CREAM, 0.35),
    (80, H - 90, 10, 20, CREAM, 0.4),
    (W - 90, H - 70, 14, 200, GOLD, 0.45),
]
for cx, cy, size, rot, color, op in corner_marks:
    parts.append(star(cx, cy, size, rot, color, op))

# --- title ---
parts.append(f'''
<text x="{W/2}" y="185" text-anchor="middle"
      font-family="Georgia, 'Times New Roman', serif" font-size="92"
      fill="{CREAM}" letter-spacing="1">Happy Birthday</text>
''')

# --- ledge line the candles sit on ---
ledge_y = 760
parts.append(f'<rect x="0" y="{ledge_y}" width="{W}" height="4" fill="{GOLD_DIM}" opacity="0.6"/>')
parts.append(f'<rect x="0" y="{ledge_y+4}" width="{W}" height="1" fill="{CREAM}" opacity="0.25"/>')

# --- candles: uneven heights and positions, striped bodies, flame + glow ---
candle_specs = [
    # (center_x, height, width, stripe_color)
    (560, 300, 46, GOLD),
    (660, 430, 52, EMBER),
    (760, 240, 40, GOLD_DIM),
    (900, 500, 58, GOLD),
    (1020, 340, 44, EMBER),
    (1140, 260, 42, GOLD_DIM),
    (1250, 420, 50, GOLD),
]

for cx, h, w, stripe in candle_specs:
    top = ledge_y - h
    # body
    parts.append(f'<rect x="{cx - w/2:.1f}" y="{top:.1f}" width="{w}" height="{h}" rx="{w*0.18:.1f}" fill="{CREAM}" opacity="0.92"/>')
    # stripes
    n_stripes = random.randint(3, 5)
    for i in range(n_stripes):
        sy = top + h * (i + 0.5) / n_stripes
        sh = h / n_stripes * random.uniform(0.28, 0.4)
        parts.append(f'<rect x="{cx - w/2:.1f}" y="{sy:.1f}" width="{w}" height="{sh:.1f}" fill="{stripe}" opacity="0.75"/>')
    # a couple of wax-drip bumps down one side for extra asymmetric texture
    drip_side = random.choice([-1, 1])
    for _ in range(random.randint(1, 2)):
        dy = top + random.uniform(0.2, 0.7) * h
        dr = random.uniform(4, 8)
        dx = cx + drip_side * (w / 2)
        parts.append(f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="{dr:.1f}" fill="{CREAM}" opacity="0.7"/>')
    # wick
    parts.append(f'<line x1="{cx}" y1="{top}" x2="{cx}" y2="{top-14}" stroke="{INK_RAISED}" stroke-width="3"/>')
    # flame (two-layer, glowing)
    parts.append(f'''
    <g filter="url(#glow)">
      <path d="M {cx} {top-70} C {cx-16} {top-40}, {cx-16} {top-16}, {cx} {top-8}
               C {cx+16} {top-16}, {cx+16} {top-40}, {cx} {top-70} Z" fill="{GOLD}" opacity="0.95"/>
      <path d="M {cx} {top-48} C {cx-7} {top-32}, {cx-7} {top-18}, {cx} {top-12}
               C {cx+7} {top-18}, {cx+7} {top-32}, {cx} {top-48} Z" fill="{CREAM}"/>
    </g>
    ''')

# --- subtitle ---
parts.append(f'''
<text x="{W/2}" y="{H-40}" text-anchor="middle"
      font-family="Georgia, 'Times New Roman', serif" font-size="30"
      fill="{GOLD_DIM}" opacity="0.85">someone lit a candle for you</text>
''')

parts.append('</svg>')

svg = "\n".join(parts)

with open("target-card.svg", "w") as f:
    f.write(svg)

cairosvg.svg2png(bytestring=svg.encode(), write_to="target-card.png", output_width=W * 2, output_height=H * 2)
print("Wrote target-card.svg and target-card.png")
