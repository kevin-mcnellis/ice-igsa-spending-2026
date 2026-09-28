"""Draw recipient totals; shared rounding affects labels, never bar geometry."""
import csv
from decimal import Decimal
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR', str(Path(__file__).resolve().parents[1] / '.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure
try:
    from scripts import chart_style as style
except ModuleNotFoundError:
    import chart_style as style

display_money = style.money


def plot(source, output, *, mobile=False):
    with Path(source).open(newline='') as handle:
        all_rows = list(csv.DictReader(handle))
    # Hide only the genuinely empty unresolved category, not zero-net unknown recipients.
    unresolved_empty = all(r['value_status'] == 'empty' for r in all_rows if r['type'] == 'Unresolved')
    rows = [r for r in all_rows if not (r['type'] == 'Unresolved' and r['value_status'] == 'empty')]
    rows.sort(key=lambda r: Decimal(r['amount'] or '0'), reverse=True)
    ids = {'Selected private detention contractors': 'selected', 'State and local governments': 'government'}
    values = [float(r['amount'] or 0) for r in rows]
    high, low = max(0, *values), min(0, *values)
    span = high - low or 1
    total = sum((Decimal(r['amount']) for r in all_rows if r['amount']), Decimal(0))
    selected = next(r for r in all_rows if r['type'] == 'Selected private detention contractors')
    share = Decimal(selected['amount'] or 0) / total * 100 if total else Decimal(0)
    with matplotlib.rc_context(style.rc_params('file-c-chart2')):
        title = f"Private Detention Contractors Account for {share:.0f}% of ICE’s Disclosed Facility Obligations"
        subtitle = f'{display_money(total)} in reported facility operations obligations · February 2025–July 2026 reporting periods'
        labels = {
            'Selected private detention contractors': '12 private detention contractors',
            'No recipient reported': 'No recipient named',
            'Other public or nonprofit entities': 'Other public agencies and nonprofits',
        }
        notes = [
            'The contractor list is not exhaustive; see methodology for the list and selection criteria.',
            "Amounts are not verified detention costs or IGSA payments; see methodology for scope and limitations.",
            'Obligations are commitments to spend, not cash payments. Records with a blank amount are left out of the totals, not counted as zero.' +
            (' Every named recipient was classified.' if unresolved_empty else ' Unresolved recipients remain visible.'),
            'Source: USAspending File C · Object class 25.4 · Accounts 070-0540 and 070-0545',
        ]
        figure, axis, available = style.page(title, subtitle, notes, mobile=mobile,
                                             body_height=365 if mobile else 310)
        axis.set_xlim(low, high + 0.08 * span)
        for i, (row, value) in enumerate(zip(rows, values)):
            category = row['type']
            color = (style.ACCENT if category == 'State and local governments' else
                     style.PRIMARY_BAR if category == 'Selected private detention contractors' else style.SECONDARY_BAR)
            bar = axis.barh(i, value, height=0.38, color=color, zorder=3)[0]
            bar.set_gid('bar-' + ids.get(category, str(i)))
            # Stroke subpixel bars so a small nonzero amount does not look absent.
            # The rectangle width remains the exact signed amount on the shared scale.
            if 0 < abs(value) < 0.001 * span:
                bar.set_edgecolor(color)
                bar.set_linewidth(1.2)
                bar.set_clip_on(False)
            axis.text(0, i - 0.29, style.wrap_text(labels.get(category, category), available, style.ROW_SIZE), transform=axis.get_yaxis_transform(),
                      ha='left', va='bottom', fontsize=style.ROW_SIZE,
                      color=style.ACCENT if category == 'State and local governments' else style.INK)
            money = display_money(row['amount']) if row['amount'] else 'Amount not reported'
            inside = abs(value) >= 0.26 * span
            offset = (-10 if value > 0 else 10) if inside else 9
            align = ('right' if value > 0 else 'left') if inside else 'left'
            axis.annotate(money, (value, i), xytext=(offset, 0), textcoords='offset points',
                          ha=align, va='center',
                          fontsize=style.VALUE_SIZE if category == 'Selected private detention contractors' else style.NOTE_SIZE,
                          weight='bold' if category == 'Selected private detention contractors' else 'normal',
                          color='white' if inside else style.INK).set_gid('value-' + ids.get(category, str(i)))
            if category == 'State and local governments' and value < 0:
                axis.annotate(style.wrap_text('Reported reductions exceeded increases.', available - 12, style.NOTE_SIZE),
                              (0, i), xytext=(9, -18), textcoords='offset points',
                              va='top', size=style.NOTE_SIZE, weight='normal', color=style.ACCENT)
        axis.set_ylim(len(rows) - (0.20 if mobile else 0.35), -0.85 if mobile else -0.65)
        axis.set_yticks([])
        axis.set_xticks([])
        for spine in axis.spines.values():
            spine.set_visible(False)
        output = Path(output)
        output.mkdir(parents=True, exist_ok=True)
        figure.savefig(output / f'recipient_types_25_4{"_mobile" if mobile else ""}.svg', metadata={'Date': None, 'Creator': 'File C blog chart', 'Description': ' '.join(notes)})
        figure.savefig(output / f'recipient_types_25_4{"_mobile" if mobile else ""}.png', dpi=180, metadata={'Software': 'File C blog chart'})

    if not mobile:
        plot(source, output, mobile=True)
        description = f'{title}. {subtitle}. ' + '; '.join(f"{labels.get(r['type'], r['type'])}: {display_money(r['amount']) if r['amount'] else 'Amount not reported'}" for r in rows) + '. ' + ' '.join(notes)
        style.web_preview(output, 'recipient_types_25_4', title, description, 'recipient_type_totals.csv',
                          methodology='../../methodology.md')
