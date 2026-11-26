# -*- coding: utf-8 -*-
"""
sprites.py
----------
Sprites do HelpYou:
  * Player e vítimas: desenhados por código (pixel art 32x32, via Surface + draw).
  * Ícones flutuantes das vítimas (chama, gota, osso, tontura).
  * Itens: recortados de "itens.png" (load_spritesheet) com FALLBACK procedural
    caso a imagem não exista ou esteja inválida.

Técnica de pixel art: desenhamos em uma grade lógica de 16x16, adicionamos
contorno de 1px e ampliamos 2x (sem suavização) => 32x32.
"""
import math
import pygame

from settings import (ARQUIVO_ITENS, CELULAS_ITENS, TAM_ITEM, calcular_rects_itens)

CONTORNO = (22, 24, 34, 255)


# ----------------------------------------------------------------------------
# UTILITÁRIOS DE DESENHO
# ----------------------------------------------------------------------------
def _r(surf, cor, x, y, w=1, h=1):
    """Preenche um retângulo (em pixels lógicos) sem misturar alfa."""
    surf.fill(cor, (x, y, w, h))


def _contorno(base, escala=2):
    """Adiciona contorno de 1px à arte lógica e amplia com 'nearest'."""
    mascara = pygame.mask.from_surface(base)
    sil = pygame.Surface(base.get_size(), pygame.SRCALPHA)
    mascara.to_surface(sil, setcolor=CONTORNO, unsetcolor=(0, 0, 0, 0))
    saida = pygame.Surface(base.get_size(), pygame.SRCALPHA)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        saida.blit(sil, (dx, dy))
    saida.blit(base, (0, 0))
    tam = (base.get_width() * escala, base.get_height() * escala)
    return pygame.transform.scale(saida, tam)


def _escurecer(cor, q=35):
    return (max(0, cor[0] - q), max(0, cor[1] - q), max(0, cor[2] - q))


# ----------------------------------------------------------------------------
# PESSOA BASE (usada pelo player e pelas vítimas)
# ----------------------------------------------------------------------------
def _pessoa(camisa, cabelo, pele, calca, direcao="baixo", passo=0):
    """Desenha uma pessoa em 16x16 olhando para 'direcao' (baixo/cima/esquerda/direita)."""
    s = pygame.Surface((16, 16), pygame.SRCALPHA)
    sapato = (45, 32, 30)
    olho = (30, 30, 40)
    lado = direcao in ("esquerda", "direita")

    # Pernas (duas posições para animar a caminhada)
    if lado:
        pernas = [(6, 12, 2, 2), (8, 12, 2, 2)] if passo == 0 else [(5, 12, 2, 2), (9, 12, 2, 1)]
    else:
        pernas = [(5, 12, 2, 2), (9, 12, 2, 2)] if passo == 0 else [(5, 12, 2, 1), (9, 12, 2, 2)]
    for (x, y, w, h) in pernas:
        _r(s, calca, x, y, w, h)
        _r(s, sapato, x, y + h - 1, w, 1)
    _r(s, calca, 5, 10, 6, 2)

    # Tronco e braços
    if lado:
        _r(s, camisa, 5, 6, 6, 4)
        _r(s, _escurecer(camisa), 7, 7, 2, 3)
        _r(s, pele, 7, 9, 2, 1)
    else:
        _r(s, camisa, 4, 6, 8, 4)
        _r(s, camisa, 3, 6, 1, 3)
        _r(s, camisa, 12, 6, 1, 3)
        _r(s, pele, 3, 9)
        _r(s, pele, 12, 9)

    # Cabeça
    if direcao == "baixo":
        _r(s, cabelo, 5, 1, 6, 2)
        _r(s, pele, 5, 3, 6, 3)
        _r(s, olho, 6, 4)
        _r(s, olho, 9, 4)
    elif direcao == "cima":
        _r(s, cabelo, 5, 1, 6, 5)
    elif direcao == "esquerda":
        _r(s, cabelo, 5, 1, 6, 2)
        _r(s, cabelo, 8, 3, 3, 3)
        _r(s, pele, 5, 3, 3, 3)
        _r(s, olho, 6, 4)
    else:  # direita
        _r(s, cabelo, 5, 1, 6, 2)
        _r(s, cabelo, 5, 3, 3, 3)
        _r(s, pele, 8, 3, 3, 3)
        _r(s, olho, 9, 4)
    return s


def criar_frames_player():
    """Gera os frames do player: {(direcao, passo): Surface 32x32}. Camisa AZUL."""
    frames = {}
    for d in ("baixo", "cima", "esquerda", "direita"):
        for passo in (0, 1):
            base = _pessoa(camisa=(50, 110, 225), cabelo=(90, 55, 30),
                           pele=(240, 195, 150), calca=(45, 50, 72),
                           direcao=d, passo=passo)
            frames[(d, passo)] = _contorno(base)
    return frames


# ----------------------------------------------------------------------------
# VÍTIMAS
# ----------------------------------------------------------------------------
def criar_sprite_vitima(tipo):
    """Sprite 32x32 de uma vítima, com marcas visuais do ferimento."""
    estilos = {
        "queimadura": ((150, 150, 168), (40, 30, 30), (236, 182, 140), (62, 62, 84)),
        "sangramento": ((70, 150, 92), (60, 40, 25), (230, 180, 140), (70, 60, 50)),
        "fratura": ((214, 172, 62), (30, 30, 35), (214, 160, 120), (60, 70, 90)),
        "tontura": ((140, 104, 182), (130, 80, 40), (238, 226, 205), (50, 55, 70)),
        "engasgo": ((205, 95, 95), (30, 30, 35), (170, 195, 235), (60, 60, 82)),
        "desmaio": ((232, 232, 240), (120, 70, 40), (236, 226, 214), (90, 90, 112)),
    }
    camisa, cabelo, pele, calca = estilos[tipo]
    s = _pessoa(camisa, cabelo, pele, calca, "baixo", 0)

    if tipo == "queimadura":
        _r(s, (235, 95, 40), 3, 9)
        _r(s, (235, 95, 40), 12, 9)
        _r(s, (220, 70, 40), 4, 6, 2, 2)
        _r(s, (255, 150, 60), 10, 7)
        _r(s, (225, 75, 45), 9, 3, 1, 2)
    elif tipo == "sangramento":
        sangue = (205, 20, 35)
        _r(s, sangue, 6, 7, 3, 2)
        _r(s, sangue, 7, 9, 1, 2)
        _r(s, sangue, 10, 12, 1, 2)
    elif tipo == "fratura":
        _r(s, (236, 236, 236), 5, 11, 2, 3)      # tala improvisada na perna
        _r(s, (150, 150, 165), 5, 12, 2, 1)
        _r(s, (236, 236, 236), 12, 6, 1, 4)      # braço imobilizado
        _r(s, (225, 60, 60), 4, 13)
    elif tipo == "tontura":
        _r(s, (30, 30, 40), 6, 3)
        _r(s, (30, 30, 40), 9, 3)
        _r(s, (150, 50, 60), 7, 5, 2, 1)
    elif tipo == "engasgo":
        _r(s, (236, 190, 150), 5, 6, 2, 1)       # mãos na garganta
        _r(s, (236, 190, 150), 9, 6, 2, 1)
        _r(s, (40, 20, 30), 7, 5, 2, 1)          # boca aberta
        _r(s, (255, 255, 255), 6, 4)
        _r(s, (255, 255, 255), 9, 4)
    elif tipo == "desmaio":
        _r(s, (236, 226, 214), 6, 4, 2, 1)       # olhos fechados
        _r(s, (236, 226, 214), 9, 4, 2, 1)
        _r(s, (80, 60, 70), 6, 4, 2, 1)
        _r(s, (80, 60, 70), 9, 4, 2, 1)
        _r(s, (210, 210, 224), 3, 7, 1, 2)
        _r(s, (210, 210, 224), 12, 7, 1, 2)
    return _contorno(s)


# ----------------------------------------------------------------------------
# ÍCONES FLUTUANTES DAS VÍTIMAS
# ----------------------------------------------------------------------------
def _icone(desenho):
    """Recebe uma Surface 12x12, centraliza em 14x14, contorna e amplia 2x (=> 28x28)."""
    base = pygame.Surface((14, 14), pygame.SRCALPHA)
    base.blit(desenho, (1, 1))
    return _contorno(base)


def criar_icones():
    """Devolve {tipo_vitima: Surface 28x28} + 'ok' (check verde)."""
    icones = {}

    # Chama (queimadura)
    s = pygame.Surface((12, 12), pygame.SRCALPHA)
    pygame.draw.polygon(s, (240, 100, 20), [(6, 0), (9, 4), (10, 8), (8, 11), (4, 11), (2, 8), (3, 4), (5, 5)])
    pygame.draw.polygon(s, (255, 215, 60), [(6, 5), (8, 8), (7, 10), (5, 10), (4, 8)])
    icones["queimadura"] = _icone(s)

    # Gota de sangue (sangramento)
    s = pygame.Surface((12, 12), pygame.SRCALPHA)
    pygame.draw.circle(s, (205, 20, 35), (6, 8), 3)
    pygame.draw.polygon(s, (205, 20, 35), [(6, 1), (3, 7), (9, 7)])
    _r(s, (255, 160, 160), 5, 7)
    icones["sangramento"] = _icone(s)

    # Osso (fratura)
    s = pygame.Surface((12, 12), pygame.SRCALPHA)
    osso = (242, 242, 232)
    _r(s, osso, 2, 5, 8, 2)
    for (x, y) in ((1, 3), (1, 7), (9, 3), (9, 7)):
        _r(s, osso, x, y, 2, 2)
    _r(s, (200, 200, 190), 3, 6, 6, 1)
    icones["fratura"] = _icone(s)

    # Espiral (tontura)
    s = pygame.Surface((12, 12), pygame.SRCALPHA)
    pts = []
    for i in range(0, 40):
        ang = i * 0.5
        r = 0.4 + 0.12 * i
        pts.append((int(round(5.5 + r * math.cos(ang))), int(round(5.5 + r * math.sin(ang)))))
    pygame.draw.lines(s, (255, 210, 50), False, pts, 1)
    icones["tontura"] = _icone(s)

    # Rosto sem ar (engasgo)
    s = pygame.Surface((12, 12), pygame.SRCALPHA)
    pygame.draw.circle(s, (120, 180, 255), (6, 6), 5)
    pygame.draw.circle(s, (20, 30, 60), (6, 8), 2)
    _r(s, (20, 30, 60), 4, 4)
    _r(s, (20, 30, 60), 8, 4)
    icones["engasgo"] = _icone(s)

    # Estrelas girando (desmaio)
    s = pygame.Surface((12, 12), pygame.SRCALPHA)
    pygame.draw.circle(s, (140, 110, 200), (6, 6), 5)
    pygame.draw.lines(s, (255, 255, 255), False, [(3, 4), (8, 4), (3, 8), (8, 8)], 1)
    icones["desmaio"] = _icone(s)

    # Mão aberta (etapa que exige MÃOS LIVRES)
    s = pygame.Surface((12, 12), pygame.SRCALPHA)
    pele = (240, 195, 150)
    _r(s, pele, 3, 5, 6, 5)
    for x in (3, 5, 7):
        _r(s, pele, x, 2, 1, 4)
    _r(s, pele, 9, 5, 1, 3)
    _r(s, pele, 1, 6, 2, 1)
    icones["mao_vazia"] = _icone(s)

    # Alerta de agravamento
    s = pygame.Surface((12, 12), pygame.SRCALPHA)
    pygame.draw.circle(s, (225, 40, 40), (6, 6), 5)
    _r(s, (255, 255, 255), 5, 2, 2, 5)
    _r(s, (255, 255, 255), 5, 8, 2, 2)
    icones["alerta"] = _icone(s)

    # Check verde (vítima estabilizada)
    s = pygame.Surface((12, 12), pygame.SRCALPHA)
    pygame.draw.lines(s, (70, 215, 110), False, [(2, 6), (5, 9), (10, 2)], 2)
    icones["ok"] = _icone(s)
    return icones


# ----------------------------------------------------------------------------
# ITENS: FALLBACK PROCEDURAL
# ----------------------------------------------------------------------------
def criar_item_fallback(nome):
    """Desenha um item em pixel art (usado quando 'itens.png' não está disponível)."""
    s = pygame.Surface((16, 16), pygame.SRCALPHA)
    if nome == "pano_limpo":
        _r(s, (242, 242, 246), 3, 4, 10, 8)
        _r(s, (205, 205, 215), 3, 8, 10, 1)
        _r(s, (205, 205, 215), 8, 4, 1, 8)
    elif nome == "pano_umido":
        _r(s, (160, 205, 255), 3, 4, 10, 8)
        _r(s, (120, 170, 235), 3, 8, 10, 1)
        _r(s, (60, 110, 210), 5, 6)
        _r(s, (60, 110, 210), 10, 10)
        _r(s, (60, 110, 210), 7, 10)
    elif nome == "gelo":
        _r(s, (170, 228, 252), 3, 4, 10, 9)
        _r(s, (235, 250, 255), 4, 5, 3, 1)
        _r(s, (235, 250, 255), 4, 6, 1, 2)
        _r(s, (255, 255, 255), 7, 8, 3, 1)
        _r(s, (255, 255, 255), 8, 7, 1, 3)
    elif nome == "tala":
        _r(s, (204, 164, 104), 2, 6, 12, 4)
        _r(s, (160, 120, 70), 2, 9, 12, 1)
        _r(s, (240, 240, 240), 5, 5, 1, 6)
        _r(s, (240, 240, 240), 10, 5, 1, 6)
    elif nome == "agua":
        _r(s, (125, 195, 245), 4, 3, 8, 10)
        _r(s, (190, 230, 255), 5, 4, 2, 5)
        _r(s, (160, 160, 170), 7, 1, 2, 2)
        _r(s, (160, 160, 170), 8, 13, 1, 2)
    elif nome == "manteiga":
        _r(s, (255, 226, 100), 3, 6, 10, 6)
        _r(s, (255, 242, 165), 3, 5, 10, 2)
        _r(s, (225, 190, 70), 3, 11, 10, 1)
    elif nome == "pasta_dente":
        _r(s, (240, 244, 250), 3, 6, 9, 4)
        _r(s, (70, 180, 120), 3, 7, 9, 1)
        _r(s, (60, 110, 220), 12, 6, 2, 4)
        _r(s, (200, 205, 215), 3, 9, 1, 1)
    elif nome == "atadura":
        _r(s, (236, 226, 200), 3, 4, 10, 8)
        _r(s, (200, 190, 160), 3, 7, 10, 1)
        _r(s, (200, 190, 160), 3, 9, 10, 1)
        _r(s, (255, 250, 235), 3, 4, 10, 1)
    elif nome == "manta":
        _r(s, (200, 205, 215), 2, 4, 12, 9)
        _r(s, (235, 238, 245), 3, 5, 5, 3)
        _r(s, (150, 155, 170), 8, 9, 5, 1)
        _r(s, (150, 155, 170), 4, 11, 6, 1)
    return _contorno(s)


# ----------------------------------------------------------------------------
# SPRITESHEET "itens.png"
# ----------------------------------------------------------------------------
def _remover_fundo(surf):
    """Torna transparente o fundo claro/transparente conectado às bordas (flood fill).

    Assim o branco DENTRO dos itens (ex.: gaze) é preservado.
    """
    w, h = surf.get_size()
    visitado = [[False] * w for _ in range(h)]
    pilha = []
    for x in range(w):
        pilha.append((x, 0))
        pilha.append((x, h - 1))
    for y in range(h):
        pilha.append((0, y))
        pilha.append((w - 1, y))
    while pilha:
        x, y = pilha.pop()
        if x < 0 or y < 0 or x >= w or y >= h or visitado[y][x]:
            continue
        visitado[y][x] = True
        c = surf.get_at((x, y))
        if c.a < 20 or (c.r >= 232 and c.g >= 232 and c.b >= 232):
            surf.set_at((x, y), (0, 0, 0, 0))
            pilha.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))


def _preparar_recorte(recorte):
    """Limpa fundo, corta no conteúdo e redimensiona para TAM_ITEM x TAM_ITEM."""
    w, h = recorte.get_size()
    mx, my = int(w * 0.06), int(h * 0.06)
    interno = recorte.subsurface(pygame.Rect(mx, my, w - 2 * mx, h - 2 * my)).copy()
    _remover_fundo(interno)
    caixa = interno.get_bounding_rect()
    if caixa.width < 2 or caixa.height < 2:
        return None
    interno = interno.subsurface(caixa).copy()
    esc = min(TAM_ITEM / caixa.width, TAM_ITEM / caixa.height)
    nw, nh = max(1, int(caixa.width * esc)), max(1, int(caixa.height * esc))
    reduzido = pygame.transform.smoothscale(interno, (nw, nh))
    saida = pygame.Surface((TAM_ITEM, TAM_ITEM), pygame.SRCALPHA)
    saida.blit(reduzido, ((TAM_ITEM - nw) // 2, (TAM_ITEM - nh) // 2))
    return saida


def load_spritesheet(caminho=ARQUIVO_ITENS):
    """Carrega 'itens.png' e recorta cada item com pygame.Rect.

    Retorna {nome_item: Surface 32x32}. Se o arquivo não existir (ou der erro),
    usa o fallback procedural, então o jogo NUNCA quebra por causa da imagem.
    O 'pano_umido' é sempre derivado do 'pano_limpo' (tingido de azul).
    """
    sprites = {}
    try:
        folha = pygame.image.load(caminho).convert_alpha()
    except (pygame.error, FileNotFoundError, OSError):
        folha = None
        print("[HelpYou] '%s' não encontrado: usando sprites procedurais." % caminho)

    if folha is not None:
        rects = calcular_rects_itens(folha.get_width(), folha.get_height())
        for nome, rect in rects.items():
            try:
                recorte = folha.subsurface(rect).copy()
                pronto = _preparar_recorte(recorte)
                if pronto is not None:
                    sprites[nome] = pronto
            except (ValueError, pygame.error):
                pass  # recorte fora da imagem -> cai no fallback
        print("[HelpYou] '%s' carregado (%d itens recortados)." % (caminho, len(sprites)))

    # Completa o que faltar com fallback procedural
    for nome in CELULAS_ITENS:
        if nome not in sprites:
            sprites[nome] = criar_item_fallback(nome)

    # Pano úmido: derivado do pano limpo
    umido = sprites["pano_limpo"].copy()
    umido.fill((140, 185, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
    for (x, y) in ((10, 20), (16, 24), (22, 19)):
        pygame.draw.circle(umido, (40, 100, 215), (x, y), 2)
    sprites["pano_umido"] = umido
    return sprites
