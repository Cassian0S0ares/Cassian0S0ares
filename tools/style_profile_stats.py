"""Enquadra os SVGs gerados sem alterar métricas, gráficos ou animações."""
from pathlib import Path
import argparse
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'profile-summary-card-output/tokyonight'
TARGET = ROOT / 'assets'
PALETTE = {'#1a1b27': '#101936', '#70a5fd': '#53f2fb', '#bf91f3': '#ad93ff', '#38bdae': '#84ffcf'}


def embed(path, x, y, width, height):
    source = path.read_text()
    source = re.sub(r'<\?xml[^>]*\?>', '', source)
    source = re.sub(r'<!DOCTYPE[^>]*>', '', source)
    for old, new in PALETTE.items():
        source = source.replace(old, new)
    source = source.replace('<svg ', f'<svg x="{x}" y="{y}" ', 1)
    source = re.sub(r'(<svg\b[^>]*\bwidth=")[^"]*', rf'\g<1>{width}', source, count=1)
    source = re.sub(r'(<svg\b[^>]*\bheight=")[^"]*', rf'\g<1>{height}', source, count=1)
    # Scope the upstream universal font selector to the embedded card.
    source = source.replace('* {', '.gpsc-root {')
    return source


def frame(title, subtitle, height, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1100" height="{height}" viewBox="0 0 1100 {height}" role="img" aria-label="{title}">
<title>{title}</title><desc>{subtitle}</desc>
<defs><pattern id="stats-grid" width="44" height="44" patternUnits="userSpaceOnUse"><path d="M44 0H0V44" fill="none" stroke="#152448" stroke-opacity=".45"/></pattern></defs>
<rect width="1100" height="{height}" fill="#060a19"/><rect width="1100" height="{height}" fill="url(#stats-grid)"/>
<rect x="30" y="20" width="1040" height="{height-40}" rx="2" fill="#101936" stroke="#30466d" stroke-width="2"/>
<path d="M30 36V20h16M1054 20h16v16M30 {height-36}v16h16M1054 {height-20}h16v-16" fill="none" stroke="#53f2fb" stroke-width="3"/>
<rect x="32" y="22" width="1036" height="34" fill="#182447"/>
<text x="50" y="44" fill="#53f2fb" font-family="Consolas,DejaVu Sans Mono,monospace" font-size="14" font-weight="700" letter-spacing="1.5">{title}</text>
{body}<path d="M0 {height-2}H1100" stroke="#53f2fb" stroke-width="4"/></svg>'''


def write(name, svg):
    ET.fromstring(svg)
    (TARGET / name).write_text(svg + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--snake', type=Path)
    args = parser.parse_args()
    if args.snake:
        # Keep the original SVG timeline and paths inside the decorative frame.
        svg = frame('CONTRIBUIÇÕES / SNAKE', 'Histórico de contribuições animado', 310,
                    embed(args.snake, 50, 72, 1000, 210))
        ET.fromstring(svg)
        args.snake.write_text(svg + '\n')
        return
    write('stats_activity.svg', frame('ATIVIDADE / LINGUAGENS', 'Estatísticas e linguagens atualizadas diariamente', 380,
          embed(SOURCE / '3-stats.svg', 50, 66, 490, 288) +
          embed(SOURCE / '2-most-commit-language.svg', 560, 66, 490, 288)))
    write('stats_details.svg', frame('HISTÓRICO / CONTRIBUIÇÕES', 'Resumo de atividade do GitHub atualizado diariamente', 380,
          embed(SOURCE / '0-profile-details.svg', 50, 68, 1000, 286)))


if __name__ == '__main__':
    main()
