"""Linjeikoner (24×24, 1.5 px linje) för vägval, tjänster och genvägar. Ritade för koncernsajterna."""

_P = {
    "blixt": '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
    "hus": '<path d="M3 11 12 3l9 8"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>',
    "kontor": '<rect x="4" y="3" width="16" height="18"/><path d="M8 7h2M14 7h2M8 11h2M14 11h2M8 15h2M14 15h2M10 21v-3h4v3"/>',
    "skold": '<path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6z"/><path d="m9 12 2 2 4-4"/>',
    "robot": '<rect x="5" y="8" width="14" height="11" rx="2"/><path d="M12 8V4M9 13h.01M15 13h.01M9 16h6M3 12v3M21 12v3"/><circle cx="12" cy="3.5" r="1"/>',
    "kran": '<path d="M5 21V4h2v17M3 21h8M7 5h13l-3 3H7M15 8v6"/><rect x="13.5" y="14" width="3" height="3"/>',
    "vag": '<path d="M8 3 4 21M16 3l4 18M12 4v3M12 10v3M12 16v3"/>',
    "bro": '<path d="M2 15h20M4 15v5M20 15v5M2 15c4-7 16-7 20 0M8 11v4M12 10v5M16 11v4"/>',
    "ror": '<path d="M3 8h8a3 3 0 0 1 3 3v10M3 12h8v9M17 21v-4M21 21v-4M14 17h7"/>',
    "lov": '<path d="M5 19c0-8 6-14 15-14 0 9-6 15-14 15"/><path d="M5 19 13 11"/>',
    "skog": '<path d="m8 3-5 8h3l-3 5h10l-3-5h3z"/><path d="M8 16v5M17 7l-3 5h2l-3 4h8l-3-4h2z"/><path d="M17 16v5"/>',
    "sol": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "graf": '<path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 6-7"/><path d="M16 7h4v4"/>',
    "sok": '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
    "folk": '<circle cx="9" cy="8" r="3"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><circle cx="17" cy="9" r="2.5"/><path d="M15.5 14.2A5 5 0 0 1 21 19"/>',
    "kugge": '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M2 12h3M19 12h3M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1"/><circle cx="12" cy="12" r="7"/>',
    "karta": '<path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2z"/><path d="M9 4v14M15 6v14"/>',
    "nyckel": '<circle cx="8" cy="15" r="4"/><path d="m11 12 9-9M17 6l3 3M14 9l2 2"/>',
    "vatten": '<path d="M12 3s7 7.5 7 12a7 7 0 0 1-14 0c0-4.5 7-12 7-12z"/><path d="M9 15a3 3 0 0 0 3 3"/>',
    "skola": '<path d="m2 9 10-5 10 5-10 5z"/><path d="M6 11v5c0 1.7 2.7 3 6 3s6-1.3 6-3v-5M22 9v6"/>',
    "vard": '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M12 7v10M7 12h10"/>',
    "ritning": '<rect x="3" y="4" width="18" height="16"/><path d="M3 9h6v11M9 13h12M15 4v9"/>',
    "hjalm": '<path d="M3 17h18M4 17a8 8 0 0 1 16 0"/><path d="M10 9V6h4v3M8 17v-4M16 17v-4"/>',
    "fabrik": '<path d="M3 21V10l6 4v-4l6 4V5h4v16z"/><path d="M7 18h2M12 18h2"/>',
    "laddning": '<rect x="4" y="3" width="10" height="18" rx="1"/><path d="m10 8-2 4h3l-2 4M14 9h3a2 2 0 0 1 2 2v5a1 1 0 0 0 2 0V8l-2-2"/>',
    "vind": '<path d="M12 12v9M12 12 6 4M12 12l8-1M12 12l-3 7"/><circle cx="12" cy="12" r="1.5"/>',
    "lada": '<path d="M3 8 12 3l9 5v13H3z"/><path d="M8 21v-7h8v7M8 14l8 7M16 14l-8 7"/>',
    "dokument": '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 12h6M9 16h6"/>',
    "megafon": '<path d="M3 10v4h4l7 5V5L7 10z"/><path d="M17 9a4 4 0 0 1 0 6M7 14l1 6h3l-1-5"/>',
    "portfolj": '<rect x="3" y="7" width="18" height="13" rx="1.5"/><path d="M9 7V4h6v3M3 13h18"/>',
    "pil": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "upp": '<path d="M12 19V5M6 11l6-6 6 6"/>',
    "glob": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.5 3.8 5.5 3.8 9s-1.3 6.5-3.8 9c-2.5-2.5-3.8-5.5-3.8-9S9.5 5.5 12 3z"/>',
    "telefon": '<path d="M21 16.5v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 1.1 3.8 2 2 0 0 1 3.1 1.6h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L7.1 9.5a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/>',
    "kamera": '<path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/>',
    "hjarta": '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>',
    "trad": '<path d="M12 21v-6M12 15c-4 0-6-2.5-6-5.5S8.5 4 12 3c3.5 1 6 3.5 6 6.5S16 15 12 15z"/><path d="M9 21h6"/>',
    "sax": '<circle cx="6" cy="17" r="3"/><circle cx="18" cy="17" r="3"/><path d="M8.2 15 18 3M15.8 15 6 3"/>',
    "tass": '<circle cx="7" cy="9" r="1.8"/><circle cx="11" cy="6" r="1.8"/><circle cx="15" cy="6" r="1.8"/><circle cx="18.5" cy="9.5" r="1.8"/><path d="M8 17c0-3 2-5.5 4.5-5.5S17 14 17 17c0 2-1.5 3-3 3-1 0-1.5-.6-2-.6s-1 .6-2 .6c-1.5 0-2-1.2-2-3z"/>',
    "ringar": '<circle cx="9" cy="14" r="5"/><circle cx="15" cy="14" r="5"/><path d="m10 5 2-2 2 2"/>',
    "eld": '<path d="M12 21a6 6 0 0 0 6-6c0-4-3-6-4-10-2 2-3 4-3 6-1-1-2-2-2-3-2 2-3 4-3 7a6 6 0 0 0 6 6z"/>',
    "hiss": '<rect x="5" y="3" width="14" height="18"/><path d="M12 3v18M8.5 9l1.5-2 1.5 2M12.5 15l1.5 2 1.5-2"/>',
    "pensel": '<path d="M14 3h6v6l-9 9-6-6z"/><path d="M5 12l-2 6 3 3 6-2"/>',
    "bat": '<path d="M3 16h18l-3 4H6z"/><path d="M12 3v13M12 4l6 10h-6M12 6 7 14h5"/>',
    "bil": '<path d="M4 16v-4l2-5h12l2 5v4z"/><path d="M4 12h16"/><circle cx="7.5" cy="16.5" r="1.5"/><circle cx="16.5" cy="16.5" r="1.5"/>',
    "kalender": '<rect x="3" y="5" width="18" height="16"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    "stjarna": '<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>',
    "las": '<rect x="5" y="11" width="14" height="10" rx="1"/><path d="M8 11V7a4 4 0 0 1 8 0v4M12 15v2"/>',
    "verktyg": '<path d="M14.7 6.3a4 4 0 0 0 5 5L12 19l-3-3 7.7-7.7z"/><path d="M9 16 4 21M3 3l6 6"/>',
    "hamare": '<path d="m14 4 6 6-3 3-6-6z"/><path d="M11 7 3 15l3 3 8-8"/>',
    "lampa": '<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-4 10.5c1 1 1 2.5 1 3.5h6c0-1 0-2.5 1-3.5A6 6 0 0 0 12 3z"/>',
    "sten": '<path d="M4 18 7 8l6-3 6 5 1 8z"/><path d="m7 8 4 4 9-2M11 12l-3 6"/>',
    "kors": '<path d="M12 3v18M7 8h10"/>',
    "hem": '<path d="M3 11 12 3l9 8v10h-6v-6H9v6H3z"/>',
}


def ikon(namn, cls="ik"):
    d = _P.get(namn) or _P["pil"]
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{d}</svg>')


NAMN = sorted(_P)
