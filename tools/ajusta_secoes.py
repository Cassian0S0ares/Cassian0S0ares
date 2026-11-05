"""Traduz os textos restantes para portugues e aumenta o respiro no topo
das secoes (02..09) e do cabecalho. Idempotente (marcador PAD-TOP).
Uso: python tools/ajusta_secoes.py"""
import re
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / 'assets'
TOP = 24
MARK = '<!-- PAD-TOP -->'

TRADUCOES = [
    ('[ RUNNING ]', '[ EXECUTANDO ]'),
    ('[ NEON_CODING.exe ]', '[ PROGRAMANDO.exe ]'),
    ('DEVELOPER STATUS', 'STATUS DO DEV'),
    ('IDENTITY / PROFILE', 'IDENTIDADE / PERFIL'),
    ('BIOGRAPHY  /  01', 'BIOGRAFIA  /  01'),
    ('CURRENT PROCESS  /  ACTIVE', 'PROCESSOS ATUAIS  /  ATIVO'),
    ('WORK HISTORY / TIMELINE', 'HISTÓRICO / LINHA DO TEMPO'),
    ('CAREER NODE', 'CARREIRA'),
    ('BUILD  ·  DEPLOY  ·  IMPROVE', 'CONSTRUIR  ·  PUBLICAR  ·  MELHORAR'),
    ('SKILL MATRIX / INSTALLED', 'MATRIZ DE HABILIDADES / INSTALADO'),
    ('>MODULE ', '>MÓDULO '),
    ('[ RUNNING IN PRODUCTION ]', '[ EM PRODUÇÃO ]'),
    ('STACK INVENTORY', 'INVENTÁRIO DA STACK'),
    ('PROJECT FILES / 03', 'ARQUIVOS DE PROJETO / 03'),
    ('>PROJECT / ', '>PROJETO / '),
    ('~/projects/  →  3 ENTRIES FOUND', '~/projetos/  →  3 ITENS ENCONTRADOS'),
    ('CREDENTIAL DATABASE', 'BANCO DE CREDENCIAIS'),
    ('CERTIFICATE / ', 'CERTIFICADO / '),
    ('[ KNOWLEDGE UNLOCKED ]', '[ CONHECIMENTO DESBLOQUEADO ]'),
    ('>LIVE DATA<', '>DADOS AO VIVO<'),
    ('ACADEMIC RECORD', 'HISTÓRICO ACADÊMICO'),
    ('DEGREE / ', 'FORMAÇÃO / '),
    ('SYSTEM OFFLINE', 'SISTEMA OFFLINE'),
]

for f in sorted(ASSETS.glob('0*_v2.svg')):
    s = f.read_text(encoding='utf8')
    for a, b in TRADUCOES:
        s = s.replace(a, b)
    if MARK not in s and not f.name.startswith('01_'):
        m = re.search(r'viewBox="0 0 (\d+) (\d+)" width="\d+" height="\d+"', s)
        w, h = int(m.group(1)), int(m.group(2))
        nh = h + TOP
        s = s.replace(m.group(0), f'viewBox="0 0 {w} {nh}" width="{w}" height="{nh}"', 1)
        s = s.replace(f'<rect x="0" y="0" width="{w}" height="{h}"', f'<rect x="0" y="0" width="{w}" height="{nh}"', 1)
        s = re.sub(rf'(<path d="M\d+ 0L\d+ ){h}"', rf'\g<1>{nh}"', s)
        top = f'<rect x="0" y="0" width="{w}" height="5" rx="0" fill="#ff62c7" />'
        bot_old = f'<rect x="0" y="{h - 5}" width="{w}" height="5"'
        i = s.find(bot_old)
        if i >= 0:
            s = s.replace(bot_old, f'<rect x="0" y="{nh - 5}" width="{w}" height="5"', 1)
            j = s.index('/>', i) + 2
            s = s[:j] + f'<g transform="translate(0,{TOP})">' + s[j:]
            s = s[:s.rindex('</svg>')] + '</g></svg>'
        else:
            print('sem barra inferior em', f.name)
        s = s.replace('?>', '?>\n' + MARK, 1)
    f.write_text(s, encoding='utf8')
    print('ok', f.name)
