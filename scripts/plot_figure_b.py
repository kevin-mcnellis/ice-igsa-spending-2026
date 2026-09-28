"""Render Figure B from its auditable three-row calculation table."""
import csv
from decimal import Decimal, ROUND_HALF_UP
import os
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', str(Path(__file__).resolve().parents[1] / '.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
from matplotlib import rc_context
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch, Rectangle
from scripts import chart_style as style

TITLE = 'State and Local Agreement Types Cover Most ICE Detention Facilities but Barely Appear in Award-Linked Facility Obligations'
SUBTITLE = 'Facility agreements and average daily population: July 9, 2026 · Award-linked obligations: February 2025–July 2026'
NOTES = [
    "Graphic based on facility designations in ICE's July 9, 2026 snapshot; restricted to IGSA, DIGSA, and U.S. Marshals Service IGA facilities.",
    'Average daily population is the reported fiscal-year-to-July 9 average, summed from Levels A-D; all 208 facilities have complete levels.',
    'File C covers award-linked obligations in object class 25.4, accounts 070-0540 and 070-0545.',
    'Two local governments (three recipient IDs) show a net reduction of $28,520 because reported reductions exceeded increases; the net share is shown as 0%.',
    'All three rows use the same 0-100% scale; percentages are rounded to whole numbers. Sources: ICE detention statistics (Deportation Data Project archive); USAspending.gov File C. See methodology.'
]
PNG_DPI = 180


def percent(value):
    rounded = Decimal(value).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    return f"{rounded:.0f}%" if rounded else '0%'


def display_percent(row):
    return percent(row['share_percent'])


def whole(value):
    return f"{Decimal(value).quantize(Decimal('1'), rounding=ROUND_HALF_UP):,.0f}"


def secondary_label(row):
    if row['metric'] == 'facility_obligations':
        numerator = Decimal(row['numerator'])
        return f"net {'−' if numerator < 0 else ''}${abs(numerator):,.0f} of {style.money(row['denominator'])}"
    return f"{whole(row['numerator'])} of {whole(row['denominator'])}"


def rounded_navy(axis, y, width, radius_x, radius_y):
    """Square baseline, rounded data edge; dimensions are data units."""
    top, bottom = y - .16, y + .16
    rx, ry = min(radius_x, width / 2), min(radius_y, .16)
    vertices = [(0, top), (width-rx, top), (width, top), (width, top+ry),
                (width, bottom-ry), (width, bottom), (width-rx, bottom),
                (0, bottom), (0, top)]
    codes = [MplPath.MOVETO, MplPath.LINETO, MplPath.CURVE3, MplPath.CURVE3,
             MplPath.LINETO, MplPath.CURVE3, MplPath.CURVE3,
             MplPath.LINETO, MplPath.CLOSEPOLY]
    patch = PathPatch(MplPath(vertices, codes), facecolor=style.STATE_LOCAL_TYPE,
                      edgecolor='none', zorder=3)
    axis.add_patch(patch)
    return patch


def plot(source, output, *, scale_note=False):
    with Path(source).open(newline='', encoding='utf-8') as handle:
        rows = list(csv.DictReader(handle, strict=True))
    if [r['metric'] for r in rows] != ['facilities', 'reported_adp', 'facility_obligations']:
        raise ValueError('Figure B requires the approved three rows in order')
    for row in rows:
        expected = Decimal(row['numerator']) / Decimal(row['denominator']) * 100
        if Decimal(row['share_percent']) != expected:
            raise ValueError('Figure B stored share differs from numerator and denominator')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    result = {}
    for mobile in (False, True):
        variant = 'mobile' if mobile else 'desktop'
        with rc_context(style.rc_params('file-c-figure-b')):
            available = (288 - 24) if mobile else (style.FIGURE_WIDTH * 72 - 36)
            plot_width_px = available / 72 * PNG_DPI
            denominator = Decimal(rows[2]['denominator'])
            dollars_per_pixel = denominator / Decimal(str(plot_width_px))
            local_percent_of_pixel = abs(Decimal(rows[2]['numerator'])) / dollars_per_pixel * 100
            notes = list(NOTES)
            if scale_note:
                notes.append('At this scale, one pixel equals about '
                             f'${dollars_per_pixel / Decimal(1_000_000):.2f} million of award-linked obligations; '
                             f'the state and local amount is about {local_percent_of_pixel:.1f}% of one pixel.')
            figure, axis, _ = style.page(TITLE, SUBTITLE, notes, mobile=mobile,
                                         body_height=390 if mobile else 345)
            FigureCanvasAgg(figure)
            axis.set_xlim(0, 100)
            axis.set_ylim(3.05, -.8)
            axis.set_yticks([])
            axis.set_xticks([])
            for spine in axis.spines.values():
                spine.set_visible(False)
            axis.text(0, 2.9, '0%', va='top', fontsize=style.NOTE_SIZE, color=style.SECONDARY)
            axis.text(100, 2.9, '100%', ha='right', va='top', fontsize=style.NOTE_SIZE, color=style.SECONDARY)
            px_to_x = 100 / plot_width_px
            px_to_y = (3.85 / (390 if mobile else 345)) * 72 / PNG_DPI
            bars = []
            for i, row in enumerate(rows):
                y = (0, 1.18, 2.36)[i]
                share = Decimal(row['share_percent'])
                axis.text(0, y-.44, style.wrap_text(row['label'], available * (.82 if mobile else .72),
                                                    style.ROW_SIZE),
                          va='bottom', fontsize=style.ROW_SIZE, color=style.INK)
                axis.text(100, y-.2, secondary_label(row).replace('$', r'\$'), ha='right', va='bottom',
                          fontsize=style.NOTE_SIZE, color=style.SECONDARY)
                axis.add_patch(Rectangle((0, y-.16), 100, .32, color=style.GRIDLINE, zorder=1))
                width = float(share) if i < 2 else 2 * px_to_x
                navy = rounded_navy(axis, y, width, 4*px_to_x, 4*px_to_y)
                navy.set_gid('bar-'+row['metric'])
                axis.add_patch(Rectangle((width, y-.16), 2*px_to_x, .32,
                                         color=style.BACKGROUND, zorder=4))
                if i < 2:
                    axis.text(width-1.5, y, display_percent(row), ha='right', va='center',
                              color='white', fontsize=style.VALUE_SIZE, weight='bold', zorder=5)
                else:
                    axis.text(width + 4*px_to_x, y, display_percent(row), va='center',
                              color=style.INK, fontsize=style.VALUE_SIZE, weight='bold', zorder=5)
                    axis.text(18, y, 'Other records, mostly private contractors: 100%',
                              va='center', fontsize=style.NOTE_SIZE if not mobile else 8.5,
                              color=style.INK, zorder=5)
                bars.append({'metric': row['metric'], 'track_end_percent': 100,
                             'navy_width_px': width / px_to_x, 'label': display_percent(row),
                             'secondary_label': secondary_label(row)})
            figure.canvas.draw()
            renderer = figure.canvas.get_renderer()
            for label in (*figure.texts, *axis.texts):
                box = label.get_window_extent(renderer)
                if box.x0 < -1 or box.x1 > figure.bbox.x1+1 or box.y0 < -1 or box.y1 > figure.bbox.y1+1:
                    raise ValueError('Figure B text extends outside the image')
            stem = 'figure_b' + ('_mobile' if mobile else '')
            figure.savefig(output/f'{stem}.svg', metadata={'Date': None, 'Creator': 'File C blog Figure B'})
            figure.savefig(output/f'{stem}.png', dpi=PNG_DPI,
                           metadata={'Software': 'File C blog Figure B'})
            result[variant] = {'plot_width_px': plot_width_px,
                               'dollars_per_pixel': float(dollars_per_pixel),
                               'local_percent_of_pixel': float(local_percent_of_pixel),
                               'bars': bars}
    description = TITLE + '. ' + ' '.join(
        f"{row['label']}: {secondary_label(row)}, {display_percent(row)}." for row in rows)
    description += ' ' + ' '.join(NOTES)
    style.web_preview(output, 'figure_b', TITLE, description, 'figure_b_data.csv',
                      methodology='../../methodology.md')
    return result
