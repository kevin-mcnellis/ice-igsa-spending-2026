"""Shared display tokens; rounding never changes the analytical CSV values."""
from decimal import Decimal, ROUND_HALF_UP

BACKGROUND = '#F7F5F0'
INK = '#26221B'
SECONDARY = '#6E6759'
ACCENT = '#BF3B14'
PRIMARY_BAR = '#2E3B47'
SECONDARY_BAR = '#7C8DA0'
GRIDLINE = '#DDD8CC'
# Semantic color key: each hue keeps the same meaning across the post.
# Federal and state/local type colors match the published map.
FEDERAL_TYPE = '#2E3B47'
STATE_LOCAL_TYPE = '#7C8DA0'
TIED = '#7A7468'
NOT_TIED = '#8E2F5A'
TITLE_FONT = 'DejaVu Serif'
BODY_FONT = 'DejaVu Sans'
TITLE_SIZE = 22
SUBTITLE_SIZE = 13
ROW_SIZE = 14
VALUE_SIZE = 16
NOTE_SIZE = 12
NOTE_LEADING = 14  # Baseline-to-baseline points for compact, readable notes.
FIGURE_WIDTH = 8
LEFT = 0.055
BORDER_WIDTH = 1


def money(value):
    """Three significant figures, with a true minus sign and spelled-out units."""
    value = Decimal(value)
    if not value.is_finite():
        raise ValueError('display amount must be finite')
    if not value:
        return '$0'
    magnitude = abs(value)
    rounded = magnitude.quantize(Decimal(1).scaleb(magnitude.adjusted() - 2), rounding=ROUND_HALF_UP)
    divisor, suffix = ((Decimal('1e9'), ' billion') if rounded >= Decimal('1e9') else
                       (Decimal('1e6'), ' million') if rounded >= Decimal('1e6') else (Decimal(1), ''))
    scaled = rounded / divisor
    decimals = max(0, 2 - scaled.adjusted())
    return f"{'−' if value < 0 else ''}${scaled:,.{decimals}f}{suffix}"


def percentage(value):
    """Input is already in percentage points, rather than a fraction."""
    return f'{Decimal(value):.1f}%'


def rc_params(salt):
    return {'font.family': BODY_FONT, 'font.size': SUBTITLE_SIZE,
            'text.color': INK, 'axes.labelcolor': INK, 'xtick.color': SECONDARY,
            'ytick.color': INK, 'text.usetex': False, 'svg.fonttype': 'path',
            'svg.hashsalt': salt}


def wrap_text(text, width, size, *, title=False, bold=False):
    """Wrap at measured font widths in points, so phone exports do not shrink text."""
    from matplotlib.font_manager import FontProperties
    from matplotlib.textpath import TextPath
    font = FontProperties(family=TITLE_FONT if title else BODY_FONT,
                          size=size, weight='bold' if bold else 'normal')
    lines, line = [], ''
    for word in text.split():
        trial = f'{line} {word}'.strip()
        if line and TextPath((0, 0), trial, prop=font).get_extents().width > width:
            lines.append(line)
            line = word
        else:
            line = trial
    return '\n'.join(lines + [line])


def page(title, subtitle, notes, *, mobile, body_height):
    """Lay out text in physical points; allocate only the height its lines need."""
    from matplotlib.figure import Figure
    width = 288 if mobile else FIGURE_WIDTH * 72
    margin = 12 if mobile else 18
    available = width - 2 * margin
    title_size = 18 if mobile else TITLE_SIZE
    blocks = [(wrap_text(title, available, title_size, title=True, bold=True), title_size, 1.12, 8),
              (wrap_text(subtitle, available, SUBTITLE_SIZE), SUBTITLE_SIZE, 1.15, 12)]
    header = margin + sum((text.count('\n') + 1) * size * leading + after
                          for text, size, leading, after in blocks)
    footer = [wrap_text(note, available, NOTE_SIZE) for note in notes]
    footer_height = sum((text.count('\n') + 1) * NOTE_LEADING + 3 for text in footer)
    height = header + body_height + 12 + footer_height + margin
    figure = Figure(figsize=(width / 72, height / 72), facecolor=BACKGROUND)
    figure.patch.set_edgecolor(INK)
    figure.patch.set_linewidth(BORDER_WIDTH)
    top = margin
    for i, (text, size, leading, after) in enumerate(blocks):
        figure.text(margin / width, 1 - top / height, text, va='top', size=size,
                    linespacing=leading, color=INK if i == 0 else SECONDARY,
                    fontfamily=TITLE_FONT if i == 0 else BODY_FONT,
                    weight='bold' if i == 0 else 'normal')
        top += (text.count('\n') + 1) * size * leading + after
    axis = figure.add_axes((margin / width, (height - header - body_height) / height,
                            available / width, body_height / height), facecolor=BACKGROUND)
    top = header + body_height + 12
    for text in footer:
        figure.text(margin / width, 1 - top / height, text, va='top', size=NOTE_SIZE,
                    linespacing=NOTE_LEADING / NOTE_SIZE, color=SECONDARY)
        top += (text.count('\n') + 1) * NOTE_LEADING + 3
    return figure, axis, available


def web_preview(output, stem, title, description, csv_name, *, methodology=None):
    """Use art-directed SVGs rather than shrinking a desktop image on phones."""
    from html import escape
    method_link = f' · <a href="{escape(methodology, quote=True)}">Methodology</a>' if methodology else ''
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<style>body{{margin:0;background:{BACKGROUND};color:{INK};font:16px/1.4 sans-serif}}
figure{{margin:0 auto;max-width:960px}}picture,img{{display:block;width:100%;height:auto}}
figcaption{{padding:8px 16px}}a{{color:{INK}}}</style></head>
<body><figure><picture>
<source media="(max-width: 640px)" srcset="{stem}_mobile.svg">
<img src="{stem}.svg" alt="{escape(description, quote=True)}">
</picture><figcaption><a href="{csv_name}">Download the chart data (CSV)</a>{method_link}</figcaption>
</figure></body></html>
"""
    (output / f'{stem}.html').write_text(html, encoding='utf-8')
