from pathlib import Path

REPLACEMENTS = [
    ('\u2014', '--'),    # em dash
    ('\u2013', '-'),     # en dash
    ('\u2500', '-'),     # box drawing horizontal
    ('\u2192', '->'),    # right arrow
    ('\u2190', '<-'),    # left arrow
    ('\u2019', "'"),     # right single quote
    ('\u2018', "'"),     # left single quote
    ('\u201c', '"'),     # left double quote
    ('\u201d', '"'),     # right double quote
    ('\u2026', '...'),   # ellipsis
    ('\u00b0', ' deg'),  # degree sign
    ('\U0001f3e2', ''),  # building emoji
    ('\U0001f321', ''),  # thermometer emoji
    ('\U0001f3af', ''),  # target emoji
    ('\u26a1', ''),      # lightning emoji
    ('\U0001f3c6', ''),  # trophy emoji
    ('\U0001f4e1', ''),  # antenna emoji
    ('\U0001f6e1', ''),  # shield emoji
    ('\U0001f9e0', ''),  # brain emoji
    ('\U0001f552', ''),  # clock emoji
    ('\u25cf', '*'),     # bullet
    ('\u2022', '*'),     # bullet
    ('\ufe0f', ''),      # variation selector
    ('\u2264', '<='),    # less than or equal to
]

files = [
    'dashboard/dashboard.py',
    'dashboard/components.py',
    'dashboard/styles.py',
    'dashboard/utils.py',
    'dashboard/savings_report.py',
]

for path in files:
    src = Path(path).read_text(encoding='utf-8')
    for old, new in REPLACEMENTS:
        src = src.replace(old, new)
    Path(path).write_text(src, encoding='utf-8')
    bad = [c for c in src if ord(c) > 127]
    if bad:
        print(f'STILL BAD  {path}  chars: {set(hex(ord(c)) for c in bad)}')
    else:
        print(f'CLEAN      {path}')
