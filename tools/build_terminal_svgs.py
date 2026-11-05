"""Aplica o efeito "terminal digitando" nos SVGs de ./assets.

- 01_header.svg: digita `whoami`, a saida aparece linha a linha e a caveirinha
  cruza os bracos em X no meio do ciclo (quadros extras em tools/x_frames/).
- 02..09: ganham uma barra de prompt no topo onde o comando e digitado; o
  conteudo da secao e a "saida" e aparece linha a linha logo depois.

Idempotente: arquivos que ja tem o marcador TYPED-TERMINAL sao ignorados.
Uso: python tools/build_terminal_svgs.py
"""
import base64
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / 'assets'
XFRAMES = Path(__file__).resolve().parent / 'x_frames'
MARK = '<!-- TYPED-TERMINAL -->'

BAR_H = 40
CHAR_W = 10.8  # largura fixa por caractere (textLength) para o clip casar com a fonte
CYCLE = 10.0

COMMANDS = {
    '02_sobre.svg': 'cat sobre.md',
    '03_experiencia.svg': 'git log --oneline experiencia',
    '04_tecnologias.svg': 'ls ~/tecnologias',
    '05_projetos.svg': 'ls -la ~/projetos',
    '06_certificacoes.svg': 'cat certificacoes.txt',
    '07_estatisticas.svg': 'gh api user --stats',
    '08_formacao.svg': 'cat formacao.md',
    '09_footer.svg': 'echo "obrigado pela visita"',
}


def mark(s):
    i = s.index('?>') + 2 if s.startswith('<?xml') else 0
    return s[:i] + chr(10) + MARK + s[i:]


def pct(t, total):
    return round(t / total * 100, 3)


def section(name, command):
    path = ASSETS / name
    s = path.read_text(encoding='utf8')
    if MARK in s:
        print('skip', name)
        return
    m = re.search(r'viewBox="0 0 (\d+) (\d+)" width="\d+" height="\d+"', s)
    w, h = int(m.group(1)), int(m.group(2))
    s = s.replace(m.group(0), f'viewBox="0 0 {w} {h + BAR_H}" width="{w}" height="{h + BAR_H}"', 1)

    n = len(command)
    tw = n * CHAR_W
    prompt = 'visitor@neon-tokyo'
    px = 34
    cmd_x = px + (len(prompt) + 4) * CHAR_W  # ":~$ " = 4 chars
    t_type0 = 0.5
    t_type1 = t_type0 + max(1.0, n * 0.07)
    t_out0 = t_type1 + 0.35
    t_out1 = t_out0 + 1.3
    t_clear = CYCLE - 0.7
    p = lambda t: pct(t, CYCLE)

    css = f'''
    .tclip{{transform-box:fill-box;transform-origin:left center;animation:tclip {CYCLE}s steps({n},end) infinite}}
    .tcur{{animation:tcur {CYCLE}s steps({n},end) infinite}}
    .cur{{animation:blink .9s steps(2,end) infinite}}
    .oclip{{transform-box:fill-box;transform-origin:center top;animation:oclip {CYCLE}s steps(18,end) infinite}}
    @keyframes tclip{{0%,{p(t_type0)}%{{transform:scaleX(0)}}{p(t_type1)}%,{p(t_clear)}%{{transform:scaleX(1)}}{p(t_clear + .01)}%,100%{{transform:scaleX(0)}}}}
    @keyframes tcur{{0%,{p(t_type0)}%{{transform:translateX(0)}}{p(t_type1)}%,{p(t_clear)}%{{transform:translateX({tw}px)}}{p(t_clear + .01)}%,100%{{transform:translateX(0)}}}}
    @keyframes oclip{{0%,{p(t_out0)}%{{transform:scaleY(0)}}{p(t_out1)}%,{p(t_clear)}%{{transform:scaleY(1)}}{p(t_clear + .01)}%,100%{{transform:scaleY(0)}}}}
    '''
    head, rest = s.split(']]></style>', 1)
    body, tail = rest.rsplit('</svg>', 1)
    bar = f'''<defs><clipPath id="tc"><rect class="tclip" x="{cmd_x - 1}" y="8" width="{tw + 2}" height="26"/></clipPath><clipPath id="oc"><rect class="oclip" x="0" y="0" width="{w}" height="{h}"/></clipPath></defs>
    <rect x="0" y="0" width="{w}" height="{BAR_H}" fill="#0b122b"/><rect x="0" y="{BAR_H - 2}" width="{w}" height="2" fill="#53f2fb" opacity=".35"/>
    <text x="{px}" y="27" fill="#84ffcf" font-size="18" font-weight="700" textLength="{len(prompt) * CHAR_W}" lengthAdjust="spacing">{prompt}</text><text x="{px + len(prompt) * CHAR_W}" y="27" fill="#53f2fb" font-size="18" font-weight="700" xml:space="preserve">:~$</text>
    <g clip-path="url(#tc)"><text x="{cmd_x}" y="27" fill="#edf6ff" font-size="18" font-weight="700" textLength="{tw}" lengthAdjust="spacing" xml:space="preserve">{command.replace('&', '&amp;')}</text></g>
    <g class="tcur"><rect class="cur" x="{cmd_x}" y="10" width="9" height="20" fill="#84ffcf"/></g>
    <g transform="translate(0,{BAR_H})"><g clip-path="url(#oc)">'''
    s = f'{head}{css}]]></style>{bar}{body}</g></g></svg>{tail}'
    path.write_text(mark(s), encoding='utf8')
    print('ok', name)


def header():
    name = '01_header.svg'
    path = ASSETS / name
    s = path.read_text(encoding='utf8')
    if MARK in s:
        print('skip', name)
        return
    C = 14.4
    STEP = 0.12
    p = lambda t: pct(t, C)

    # ---- sequencia de quadros: digitando -> X -> digitando ----
    imgs = re.findall(r'xlink:href="(data:image/png;base64,[A-Za-z0-9+/=]+)"', s)
    assert len(imgs) == 16
    for k in ('x00', 'x01', 'x02'):
        b = base64.b64encode((XFRAMES / f'{k}.png').read_bytes()).decode()
        imgs.append('data:image/png;base64,' + b)
    X0, X1, X2 = 16, 17, 18
    seq = [i % 16 for i in range(48)] + [X0] * 2 + [X1] * 2 + [X2] * 34 + [X1] * 2 + [X0] * 2
    seq += [i % 16 for i in range(120 - len(seq))]
    assert len(seq) == 120
    runs = {i: [] for i in range(len(imgs))}
    for pos, f in enumerate(seq):
        if runs[f] and runs[f][-1][1] == pos:
            runs[f][-1][1] = pos + 1
        else:
            runs[f].append([pos, pos + 1])
    kf, rules, tags = [], [], []
    for i, rs in runs.items():
        frames = []
        for a, b in rs:
            frames.append(f'{p(a * STEP)}%{{opacity:1}}{p(b * STEP)}%{{opacity:0}}')
        first = rs[0][0]
        pre = '0%{opacity:0}' if first else ''
        kf.append(f'@keyframes k{i}{{{pre}{"".join(frames)}100%{{opacity:0}}}}')
        rules.append(f'.k{i}{{opacity:0;animation:k{i} {C}s step-end infinite}}')
        tags.append(f'<image class="k{i}" x="0" y="0" width="314" height="314" image-rendering="pixelated" xlink:href="{imgs[i]}"/>')
    # o quadro 0 comeca visivel
    inner = (f'<svg x="754" y="66" width="314" height="314" viewBox="0 0 314 314" overflow="visible" image-rendering="pixelated">'
             f'<style><![CDATA[{"".join(rules)}{"".join(kf)}]]></style>' + '\n'.join(tags) + '</svg>')
    a = s.index('<svg x="754"')
    b = s.index('</svg>', a) + len('</svg>')
    s = s[:a] + inner + s[b:]

    # ---- terminal: whoami digitado + saida linha a linha ----
    cw = 13.2
    typed_x = 59 + 2 * cw
    wd = 'whoami'
    tw = len(wd) * cw
    t0, t1 = 0.6, 1.5
    clear = C - 0.6
    outs = [1.9, 2.3, 2.7, 3.0, 3.2, 3.4, 3.6]
    css = f'''
    .tclip{{transform-box:fill-box;transform-origin:left center;animation:tclip {C}s steps({len(wd)},end) infinite}}
    .tcur{{animation:tcur {C}s steps({len(wd)},end) infinite}}
    .cur{{animation:blink .9s steps(2,end) infinite}}
    @keyframes tclip{{0%,{p(t0)}%{{transform:scaleX(0)}}{p(t1)}%,{p(clear)}%{{transform:scaleX(1)}}{p(clear + .01)}%,100%{{transform:scaleX(0)}}}}
    @keyframes tcur{{0%,{p(t0)}%{{transform:translateX(0)}}{p(t1)}%,{p(clear)}%{{transform:translateX({tw}px)}}{p(clear + .01)}%,100%{{transform:translateX(0)}}}}
    '''
    for i, t in enumerate(outs):
        css += f'.o{i}{{opacity:0;animation:o{i} {C}s step-end infinite}}@keyframes o{i}{{0%{{opacity:0}}{p(t)}%{{opacity:1}}{p(clear)}%{{opacity:0}}100%{{opacity:0}}}}\n    '
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
    s = s.replace('ORIGINAL · 16 FRAMES', 'LIVE CODING · 19 FRAMES')
    path.write_text(mark(s), encoding='utf8')
    print('ok', name)


if __name__ == '__main__':
    header()
    for n, c in COMMANDS.items():
        section(n, c)
