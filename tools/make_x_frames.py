"""Gera os quadros extras da caveirinha: bracos subindo e cruzando em X.
Uso: python make_x_frames.py <dir com f00..f15.png> <dir de saida>"""
import sys
from PIL import Image, ImageDraw

src, out = sys.argv[1], sys.argv[2]
S = 4  # supersampling
OUT = (18, 12, 40, 255)
SLEEVE = (84, 70, 156, 255)
SLEEVE_HI = (112, 96, 190, 255)
HAND = (231, 220, 239, 255)

def erase_hands(im):
    # apaga as maos do teclado cobrindo com a cor do moletom
    d = ImageDraw.Draw(im)
    fill = (34, 27, 67, 255)
    for cx in (140, 179):
        d.ellipse((cx - 19, 205, cx + 19, 229), fill=fill)
    return im

def arm(d, p0, p1, w):
    s = lambda p: (p[0] * S, p[1] * S)
    d.line([s(p0), s(p1)], fill=OUT, width=(w + 5) * S)
    d.line([s(p0), s(p1)], fill=SLEEVE, width=w * S)
    off = (-1, -1)
    d.line([s((p0[0] + off[0], p0[1] + off[1])), s((p1[0] + off[0], p1[1] + off[1]))], fill=SLEEVE_HI, width=2 * S)

def hand(d, c, r):
    x, y = c[0] * S, c[1] * S
    d.ellipse((x - (r + 2) * S, y - (r + 2) * S, x + (r + 2) * S, y + (r + 2) * S), fill=OUT)
    d.ellipse((x - r * S, y - r * S, x + r * S, y + r * S), fill=HAND)

def pose(base, hands_l, hands_r, elbow_l, elbow_r, shoulder_l, shoulder_r):
    im = erase_hands(Image.open(base).convert('RGBA'))
    big = im.resize((im.width * S, im.height * S), Image.NEAREST)
    d = ImageDraw.Draw(big)
    for sh, el, h in ((shoulder_l, elbow_l, hands_l), (shoulder_r, elbow_r, hands_r)):
        arm(d, sh, el, 12)
        arm(d, el, h, 11)
    for h in (hands_l, hands_r):
        hand(d, h, 9)
    over = big.resize(im.size, Image.LANCZOS)
    res = im.copy()
    res.alpha_composite(over)
    return res

# ombros (de onde saem os bracos) e maos
SH_L, SH_R = (122, 190), (196, 190)
frames = {
    # maos sobem do teclado
    'x00': pose(f'{src}/f00.png', (130, 198), (188, 198), (114, 212), (204, 212), SH_L, SH_R),
    # bracos cruzando
    'x01': pose(f'{src}/f03.png', (160, 184), (160, 184), (128, 214), (192, 214), SH_L, SH_R),
    # X completo: cada mao no ombro oposto
    'x02': pose(f'{src}/f03.png', (190, 176), (128, 176), (140, 216), (178, 216), SH_L, SH_R),
}
for k, im in frames.items():
    im.save(f'{out}/{k}.png')
