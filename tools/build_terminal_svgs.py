"""Aplica o efeito "terminal digitando" no cabecalho (assets/01_header_v2.svg).

`whoami` e digitado uma unica vez, a saida aparece linha a linha e o terminal
fica parado no final (sem reiniciar). A caveirinha segue com os 16 quadros
originais. As demais secoes ficam como o original, sem efeito.

Idempotente: arquivo que ja tem o marcador TYPED-TERMINAL e ignorado.
Uso: python tools/build_terminal_svgs.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / 'assets'
MARK = '<!-- TYPED-TERMINAL -->'



def mark(s):
    i = s.index('?>') + 2 if s.startswith('<?xml') else 0
    return s[:i] + chr(10) + MARK + s[i:]


def pct(t, total):
    return round(t / total * 100, 3)


def header():
    name = '01_header_v2.svg'
    path = ASSETS / name
    s = path.read_text(encoding='utf8')
    if MARK in s:
        print('skip', name)
        return
    C = 4.0
    p = lambda t: pct(t, C)

    # ---- terminal: whoami digitado + saida linha a linha ----
    cw = 13.2
    typed_x = 59 + 2 * cw
    wd = 'whoami'
    tw = len(wd) * cw
    t0, t1 = 0.6, 1.5
    outs = [1.9, 2.3, 2.7, 3.0, 3.2, 3.4, 3.6]
    css = f'''
    .tclip{{transform-box:fill-box;transform-origin:left center;animation:tclip {C}s steps({len(wd)},end) 1 forwards}}
    .tcur{{animation:tcur {C}s steps({len(wd)},end) 1 forwards}}
    .cur{{animation:blink .9s steps(2,end) infinite}}
    @keyframes tclip{{0%,{p(t0)}%{{transform:scaleX(0)}}{p(t1)}%,100%{{transform:scaleX(1)}}}}
    @keyframes tcur{{0%,{p(t0)}%{{transform:translateX(0)}}{p(t1)}%,100%{{transform:translateX({tw}px)}}}}
    '''
    for i, t in enumerate(outs):
        css += f'.o{i}{{opacity:0;animation:o{i} {C}s step-end 1 forwards}}@keyframes o{i}{{0%{{opacity:0}}{p(t)}%,100%{{opacity:1}}}}' + chr(10) + '    '
    head, rest = s.split(']]></style>', 1)
    s = head + css + ']]></style>' + rest

    old = re.search(r'<text x="59" y="112"[^>]*>&gt; whoami</text>', s).group(0)
    new = (f'<defs><clipPath id="tc"><rect class="tclip" x="{typed_x - 1}" y="90" width="{tw + 2}" height="30"/></clipPath></defs>'
           f'<text x="59" y="112" fill="#84ffcf" font-size="22" font-weight="700">&gt;</text>'
           f'<g clip-path="url(#tc)"><text x="{typed_x}" y="112" fill="#84ffcf" font-size="22" font-weight="700" textLength="{tw}" lengthAdjust="spacing">{wd}</text></g>'
           f'<g class="tcur"><rect class="cur" x="{typed_x}" y="94" width="11" height="22" fill="#84ffcf"/></g>')
    s = s.replace(old, new, 1)

    def wrap(pattern, idx):
        nonlocal s
        mm = re.search(pattern, s)
        assert mm, pattern
        s = s.replace(mm.group(0), f'<g class="o{idx}">{mm.group(0)}</g>', 1)

    wrap(r'<text x="54" y="193"[^>]*>CASSIANO</text>', 0)
    wrap(r'<text x="54" y="274"[^>]*>SOARES</text>', 1)
    wrap(r'<text x="61" y="314"[^>]*>FULL STACK[^<]*</text>', 2)
    for idx, x in zip((3, 4, 5, 6), (61, 179, 299, 403)):
        wrap(rf'<rect x="{x}" y="334"[^>]*/><text[^>]*>[A-Z]+</text>', idx)
    s = re.sub(r'<text x="528" y="354"[^>]*>ORIGINAL[^<]*</text>', '', s)
    path.write_text(mark(s), encoding='utf8')
    print('ok', name)


if __name__ == '__main__':
    header()
