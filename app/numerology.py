"""
Numerology engine for Numero Annand AI Premium.

Ported and cleaned from the original monolith so the blueprint app can generate
a structured Lo Shu Grid / Chaldean numerology report. `build_report()` returns a
plain dict that `templates/report.html` renders, keeping calculation and
presentation cleanly separated.
"""

import re
from datetime import datetime

MASTER_NUMBERS = {11, 22, 33}

# Chaldean letter-to-number map used for the name-vibration calculation.
CHALDEAN_MAP = {
    'A': 1, 'I': 1, 'J': 1, 'Q': 1, 'Y': 1,
    'B': 2, 'K': 2, 'R': 2,
    'C': 3, 'G': 3, 'L': 3, 'S': 3,
    'D': 4, 'M': 4, 'T': 4,
    'E': 5, 'H': 5, 'N': 5, 'X': 5,
    'U': 6, 'V': 6, 'W': 6,
    'O': 7, 'Z': 7,
    'F': 8, 'P': 8,
}

# Friend / neutral / enemy relationships between root numbers.
NUM_RELATIONS = {
    1: {'friends': [1, 2, 3, 5, 7, 9], 'neutral': [4, 8], 'enemy': [6]},
    2: {'friends': [1, 2, 3, 5], 'neutral': [4, 7, 8, 9], 'enemy': [6]},
    3: {'friends': [1, 2, 3, 5, 7, 9], 'neutral': [6, 8], 'enemy': [4]},
    4: {'friends': [1, 5, 6, 7], 'neutral': [2, 8, 9], 'enemy': [3]},
    5: {'friends': [1, 2, 3, 5, 6, 8], 'neutral': [4, 7, 9], 'enemy': []},
    6: {'friends': [5, 6, 7, 8], 'neutral': [3, 4, 9], 'enemy': [1, 2]},
    7: {'friends': [1, 3, 4, 5, 6], 'neutral': [2, 8, 9], 'enemy': []},
    8: {'friends': [4, 5, 6, 7], 'neutral': [1, 2, 3], 'enemy': [8, 9]},
    9: {'friends': [1, 2, 3, 5, 7], 'neutral': [4, 6], 'enemy': [8, 9]},
}

# Standard Lo Shu Grid layout (rows top -> bottom).
LOSHU_LAYOUT = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]

# Lo Shu "planes" (rows/columns) with the numbers that form them.
PLANES = {
    'Mental Plane': [4, 9, 2],
    'Emotional Plane': [3, 5, 7],
    'Practical Plane': [8, 1, 6],
    'Thought Plane': [4, 3, 8],
    'Will Plane': [9, 5, 1],
    'Action Plane': [2, 7, 6],
}


def _reduce(n, master=True):
    """Reduce a number to a single digit, preserving master numbers."""
    if master and n in MASTER_NUMBERS:
        return n
    while n > 9:
        n = sum(int(x) for x in str(n))
        if master and n in MASTER_NUMBERS:
            return n
    return n


def parse_date(dob):
    """Parse a DOB accepting YYYY-MM-DD (HTML date input) or DD-MM-YYYY."""
    s = dob.strip().replace('/', '-').replace('.', '-')
    # ISO format from <input type="date">
    if re.match(r'^\d{4}-\d{2}-\d{2}$', s):
        return datetime.strptime(s, '%Y-%m-%d').date()
    if re.match(r'^\d{2}-\d{2}-\d{4}$', s):
        return datetime.strptime(s, '%d-%m-%Y').date()
    # Last-resort attempts for loosely formatted single-digit day/month values.
    for fmt in ('%d-%m-%Y', '%Y-%m-%d', '%m-%d-%Y'):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognised date format: {dob}")


def _chaldean_total(name):
    return sum(CHALDEAN_MAP.get(ch, 0) for ch in name.upper() if ch.isalpha())


def build_report(name, dob, mobile=""):
    """Compute the full numerology report as a serialisable dict."""
    name = (name or "").strip()
    parsed = parse_date(dob)

    driver = _reduce(parsed.day)
    conductor = _reduce(parsed.day + parsed.month + parsed.year)

    # Frequency map of every meaningful digit that lands on the grid.
    freq = {i: 0 for i in range(1, 10)}
    grid_map = {i: [] for i in range(1, 10)}
    digits = [int(x) for x in parsed.strftime('%d%m%Y') if x != '0']
    for n in digits + [driver, conductor]:
        if 1 <= n <= 9:
            freq[n] += 1
            grid_map[n].append(str(n))

    name_total = _chaldean_total(name)
    name_single = _reduce(name_total)

    missing = [n for n in range(1, 10) if freq[n] == 0]
    repeated = [n for n, c in freq.items() if c >= 2]

    # Compatibility score between the name vibration and birth numbers.
    score = 0
    for root in (driver, conductor):
        rel = NUM_RELATIONS.get(root, {})
        if name_single in rel.get('friends', []):
            score += 45
        elif name_single in rel.get('neutral', []):
            score += 25
        else:
            score += 8
    name_digits = [int(x) for x in str(name_total) if x.isdigit()]
    recovered = [x for x in missing if x in name_digits]
    score += min(10, len(recovered) * 2)
    score = min(100, score)

    # Lo Shu grid rows for rendering (empty cells shown as blank).
    grid_rows = []
    for row in LOSHU_LAYOUT:
        cells = []
        for n in row:
            cells.append({'number': n, 'value': ''.join(grid_map[n]), 'present': bool(grid_map[n])})
        grid_rows.append(cells)

    # Plane strengths (how many of a plane's numbers are present).
    planes = []
    for label, nums in PLANES.items():
        present = [n for n in nums if freq[n] > 0]
        planes.append({
            'label': label,
            'numbers': nums,
            'present': present,
            'complete': len(present) == len(nums),
            'strength': round(len(present) / len(nums) * 100),
        })

    # Name-correction guidance.
    name_analysis = _name_analysis(name, driver, conductor, score)

    return {
        'name': name,
        'mobile': mobile,
        'dob_display': parsed.strftime('%d-%m-%Y'),
        'driver': driver,
        'conductor': conductor,
        'name_total': name_total,
        'name_single': name_single,
        'freq': freq,
        'grid_rows': grid_rows,
        'missing': missing,
        'repeated': repeated,
        'score': score,
        'planes': planes,
        'name_analysis': name_analysis,
        'lucky_numbers': sorted({driver, conductor, name_single}),
        'lucky_days': ['Sunday', 'Wednesday', 'Friday'],
        'lucky_colors': ['Aqua Blue', 'White', 'Emerald Green'],
    }


def _name_analysis(name, driver, conductor, score):
    """Return name-correction verdict plus optional improved-spelling ideas."""
    if score >= 85:
        return {
            'perfect': True,
            'score': score,
            'message': (
                f"Your current name vibration is strongly aligned with your Driver "
                f"Number ({driver}), Conductor Number ({conductor}) and native Lo Shu "
                f"frequencies. No correction is required - your present name already "
                f"carries a professionally balanced numerological frequency."
            ),
            'suggestions': [],
        }

    suggestions = []
    friends = NUM_RELATIONS.get(driver, {}).get('friends', [])
    candidates = [
        name + 'h', name + ' Raj', name + ' Dev', name + ' Anand',
        name + ' Kumar', 'Aar' + name, name + ' Sharma', name + ' Sai',
    ]
    seen = set()
    for candidate in candidates:
        single = _reduce(_chaldean_total(candidate))
        if single in friends and candidate not in seen:
            seen.add(candidate)
            # Estimated improved score, capped for realism.
            improved = min(96, 84 + single)
            suggestions.append({
                'name': candidate,
                'number': single,
                'score': improved,
                'reason': (
                    f"This spelling introduces stronger energetic synchronisation "
                    f"with Driver Number {driver} and Destiny Number {conductor}."
                ),
            })
        if len(suggestions) >= 3:
            break

    return {
        'perfect': False,
        'score': score,
        'message': (
            "Your current name is functional, but it does not fully synchronise with "
            "your complete Lo Shu Grid structure and destiny frequencies. A "
            "professionally optimised spelling can significantly improve energetic balance."
        ),
        'suggestions': suggestions,
    }
