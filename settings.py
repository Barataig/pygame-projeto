# -*- coding: utf-8 -*-
"""
settings.py
-----------
Constantes globais do HelpYou: janela, cores, regras de jogo, configuração das
3 fases (STAGE_CONFIGS), taxas de queda (DECAY), textos educativos e os
recortes (RECTS) da spritesheet "itens.png".
"""
import pygame

# ----------------------------------------------------------------------------
# JANELA / ÁREA DE JOGO
# ----------------------------------------------------------------------------
LARGURA, ALTURA = 960, 600
FPS = 60
TITULO = "HelpYou"

ALTURA_HUD = 56          # faixa do HUD no topo
PAREDE = 16              # espessura das paredes
# Retângulo do piso (onde o jogador pode andar)
AREA_JOGO = pygame.Rect(PAREDE, ALTURA_HUD + PAREDE,
                        LARGURA - 2 * PAREDE, ALTURA - ALTURA_HUD - 2 * PAREDE)

# ----------------------------------------------------------------------------
# ESTADOS DO JOGO (máquina de estados)
# ----------------------------------------------------------------------------
ESTADO_MENU = "menu"
ESTADO_INSTRUCOES = "instrucoes"
ESTADO_JOGANDO = "jogando"
ESTADO_PAUSADO = "pausado"
ESTADO_TRANSICAO = "transicao"
ESTADO_VITORIA = "vitoria"
ESTADO_GAME_OVER = "game_over"

# ----------------------------------------------------------------------------
# CORES
# ----------------------------------------------------------------------------
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA = (150, 152, 165)
CINZA_ESCURO = (38, 40, 52)
AMARELO_BRILHO = (255, 230, 60)
VERMELHO = (225, 55, 55)
VERDE = (70, 205, 105)
AZUL = (60, 115, 225)
LARANJA = (240, 140, 40)
COR_HUD = (28, 30, 42)
COR_TEXTO = (240, 240, 245)

# ----------------------------------------------------------------------------
# REGRAS DE JOGO
# ----------------------------------------------------------------------------
VEL_PLAYER = 190.0          # pixels por segundo
TEMPO_PIA = 2.0             # segundos segurando E na pia
TEMPO_VITIMA = 2.5          # segundos segurando E na vítima
PENALIDADE_TEMPO = 10       # segundos perdidos ao usar um distrator
PONTOS_VITIMA = 100         # pontos base por vítima estabilizada
MULT_COMBO = 1.5            # multiplicador do combo
COMBO_MINIMO = 2            # acertos seguidos para ativar o multiplicador
BONUS_POR_SEGUNDO = 5       # bônus por segundo sobrando ao sair pela porta
ALCANCE = 20                # folga (px) ao redor dos objetos para interagir
TAM_ITEM = 32               # tamanho (px) dos sprites de item

# Queda de estabilidade (% por segundo) de cada tipo de vítima
DECAY = {
    "queimadura": 2.0,
    "sangramento": 2.5,
    "fratura": 1.5,
    "tontura": 1.0,
    "engasgo": 2.8,      # novo: muito urgente, sem item (mãos livres)
    "desmaio": 1.3,      # novo: precisa de manta térmica
}

# Token usado quando a etapa exige as MÃOS LIVRES (ex.: manobra de Heimlich)
MAO_VAZIA = "mao_vazia"

# Sequência de itens que cada vítima exige (tratamento simples)
ETAPAS = {
    "queimadura": ["pano_umido"],
    "sangramento": ["pano_limpo"],
    "fratura": ["tala"],
    "tontura": ["agua"],
    "engasgo": [MAO_VAZIA],
    "desmaio": ["manta"],
}

# Tratamento de vítima GRAVE (2 etapas): cada etapa feita reduz a queda pela metade
ETAPAS_GRAVE = {
    "queimadura": ["pano_umido", "pano_limpo"],
    "sangramento": ["pano_limpo", "atadura"],
    "fratura": ["tala", "atadura"],
}

# Tempo (s) segurando E em cada vítima (padrão = TEMPO_VITIMA)
TEMPO_ACAO = {"engasgo": 3.0}

# Agravamento: a cada N segundos (config da fase) uma vítima piora
AGRAVO_MULT = 1.3
AGRAVO_MAX = 2.0

# Itens "mito" (distratores): erro grave
DISTRATORES = ("manteiga", "pasta_dente", "gelo")

NOMES_ITEM = {
    "pano_limpo": "Pano Limpo",
    "pano_umido": "Pano Úmido",
    "gelo": "Gelo",
    "tala": "Tala Rígida",
    "agua": "Água",
    "manteiga": "Manteiga",
    "pasta_dente": "Pasta de Dente",
    "atadura": "Atadura",
    "manta": "Manta Térmica",
}

NOMES_VITIMA = {
    "queimadura": "Queimadura",
    "sangramento": "Sangramento",
    "fratura": "Fratura",
    "tontura": "Tontura",
    "engasgo": "Engasgo",
    "desmaio": "Desmaio",
}

# Nomes curtos para as barras do HUD
HUD_NOMES = {
    "queimadura": "Queimad.",
    "sangramento": "Sangram.",
    "fratura": "Fratura",
    "tontura": "Tontura",
    "engasgo": "Engasgo",
    "desmaio": "Desmaio",
}

# ----------------------------------------------------------------------------
# TEXTOS EDUCATIVOS
# ----------------------------------------------------------------------------
TEXTOS_DISTRATORES = {
    "manteiga": "Manteiga NÃO trata queimadura: segura o calor na pele e pode causar infecção. "
                "O correto é resfriar com pano limpo e úmido.",
    "pasta_dente": "Pasta de dente NÃO trata queimadura: irrita a pele, esconde a lesão e "
                   "favorece infecção. Use pano limpo e úmido.",
    "gelo": "Gelo direto na pele AGRAVA a lesão (queimadura pelo frio). "
            "Use pano limpo e úmido em temperatura ambiente.",
}

DICAS_ERRO = {
    "queimadura": "Queimadura: use um Pano ÚMIDO. Molhe o Pano Limpo na pia (segure E por 2s).",
    "sangramento": "Sangramento: pressione o ferimento com Gaze / Pano Limpo (seco).",
    "fratura": "Fratura: não mova a vítima. Imobilize o local com a Tala Rígida.",
    "tontura": "Tontura: ofereça Água e mantenha a pessoa sentada ou deitada.",
    "engasgo": "Engasgo: use as MÃOS LIVRES (largue o item com Q) e faça a manobra de Heimlich.",
    "desmaio": "Desmaio: deite a pessoa e mantenha-a aquecida com a Manta Térmica.",
}

MSG_ETAPA = {
    "queimadura": "Resfriou! Agora cubra a queimadura com Pano Limpo (sem apertar).",
    "sangramento": "Pressão feita! Agora fixe o curativo com a Atadura.",
    "fratura": "Imobilizada! Agora prenda a tala com a Atadura.",
}

MSG_SUCESSO = {
    "queimadura": "Boa! Resfriar a queimadura com pano úmido alivia a dor e limita o dano.",
    "sangramento": "Boa! Pressionar o ferimento com pano limpo ajuda a controlar o sangramento.",
    "fratura": "Boa! Imobilizar a fratura evita lesões maiores. Nunca tente 'colocar o osso no lugar'.",
    "tontura": "Boa! Água e repouso ajudam em casos de tontura. Ligue 192 se piorar.",
    "engasgo": "Boa! A manobra de Heimlich (compressões no abdome) desobstrui as vias aéreas.",
    "desmaio": "Boa! Deitar e aquecer a pessoa ajuda enquanto o SAMU não chega.",
}

DICAS_GAME_OVER = {
    "queimadura": "Queimadura: resfrie com pano limpo e úmido e ligue 192. "
                  "Nunca use manteiga, pasta de dente ou gelo.",
    "sangramento": "Sangramento: priorize quem perde estabilidade mais rápido. "
                   "Pressione o ferimento com pano limpo e ligue 192.",
    "fratura": "Fratura: não mova a vítima; imobilize com uma tala rígida e chame o 192.",
    "tontura": "Tontura: sente ou deite a pessoa, ofereça água e observe. Chame o 192 se não melhorar.",
    "engasgo": "Engasgo é a emergência mais rápida: vá direto, deixe as mãos livres e faça a manobra de "
               "Heimlich. Comece sempre pelas vítimas que pioram mais rápido.",
    "desmaio": "Desmaio: deite a pessoa de barriga para cima, eleve as pernas, mantenha-a aquecida e chame o 192.",
    "tempo": "O SAMU chegou, mas ainda havia pendências. Planeje o trajeto: pegue o item certo "
             "e atenda primeiro as vítimas que pioram mais rápido.",
}

DICAS_FASE = [
    "Dica: ligue 192 (SAMU) logo no início de qualquer emergência.",
    "Dica: em queimaduras, resfrie com água corrente/pano úmido e limpo por vários minutos.",
    "Dica: em fraturas, imobilize e não force o membro. Priorize chamar socorro.",
    "Dica: no engasgo, a manobra de Heimlich são compressões rápidas para dentro e para cima no abdome.",
    "Dica: em várias vítimas, atenda primeiro quem corre mais risco (triagem).",
]

# ----------------------------------------------------------------------------
# SPRITESHEET "itens.png"
# ----------------------------------------------------------------------------
# A imagem deve ser uma GRADE regular: SHEET_COLUNAS x SHEET_LINHAS células
# do mesmo tamanho (a figura de exemplo tem 8 colunas x 7 linhas).
ARQUIVO_ITENS = "itens.png"
SHEET_COLUNAS = 8
SHEET_LINHAS = 7
SHEET_MARGEM = (0, 0)       # margem (x, y) em pixels ao redor da grade, se houver

# Mapeamento item -> (linha, coluna), contando a partir de 1 (linha 1 = topo)
CELULAS_ITENS = {
    "pano_limpo": (2, 1),    # Gaze
    "gelo": (4, 1),          # Bolsa de gelo
    "tala": (5, 1),          # Tesoura
    "agua": (7, 2),          # Bolsa de soro
    "manteiga": (3, 4),      # Pote de remédio
    "pasta_dente": (3, 1),   # Pomada
    "atadura": (2, 2),       # Rolo de atadura
    "manta": (4, 6),         # Manta térmica (folha prateada)
}


def calcular_rects_itens(largura, altura):
    """Devolve {item: pygame.Rect} com os recortes da spritesheet.

    O tamanho de cada célula é calculado a partir do tamanho real da imagem,
    então funciona com qualquer resolução (desde que seja uma grade regular).
    """
    mx, my = SHEET_MARGEM
    cw = (largura - 2 * mx) // SHEET_COLUNAS
    ch = (altura - 2 * my) // SHEET_LINHAS
    rects = {}
    for nome, (lin, col) in CELULAS_ITENS.items():
        rects[nome] = pygame.Rect(mx + (col - 1) * cw, my + (lin - 1) * ch, cw, ch)
    return rects


# ----------------------------------------------------------------------------
# CONFIGURAÇÃO DAS FASES (cada fase tem vários CÔMODOS separados por paredes)
# ----------------------------------------------------------------------------
ESP_PAREDE = 12      # espessura das paredes internas


def _parede_v(x, vaos, y0=ALTURA_HUD + PAREDE, y1=ALTURA - PAREDE):
    """Parede VERTICAL em x, de y0 a y1, com vãos (portas) [(y_ini, y_fim), ...]."""
    rects, atual = [], y0
    for ini, fim in sorted(vaos):
        if ini > atual:
            rects.append((x, atual, ESP_PAREDE, ini - atual))
        atual = fim
    if atual < y1:
        rects.append((x, atual, ESP_PAREDE, y1 - atual))
    return rects


def _parede_h(y, vaos, x0=PAREDE, x1=LARGURA - PAREDE):
    """Parede HORIZONTAL em y, de x0 a x1, com vãos (portas) [(x_ini, x_fim), ...]."""
    rects, atual = [], x0
    for ini, fim in sorted(vaos):
        if ini > atual:
            rects.append((atual, y, ini - atual, ESP_PAREDE))
        atual = fim
    if atual < x1:
        rects.append((atual, y, x1 - atual, ESP_PAREDE))
    return rects


# Paletas de piso por tipo de cômodo: (cor1, cor2)
PISO_COZINHA = ((226, 218, 200), (210, 202, 184))
PISO_SALA = ((196, 170, 140), (184, 158, 128))
PISO_QUARTO = ((186, 176, 206), (174, 164, 196))
PISO_BANHEIRO = ((190, 220, 226), (176, 208, 216))
PISO_ESCRITORIO = ((170, 180, 196), (158, 168, 186))
PISO_ARQUIVO = ((200, 196, 178), (188, 184, 166))
PISO_RECEPCAO = ((206, 190, 170), (194, 178, 158))

# Campos de cada fase:
#   comodos:    (x, y, w, h, nome, piso)          paredes: (x, y, w, h) sólidas
#   pias:       (x, y, w, h)                      porta:   (x, y, w, h) na parede externa
#   obstaculos: (x, y, w, h, tipo)                jogador: (x, y) centro
#   vitimas:    (tipo, x, y) ou (tipo, x, y, "grave")   itens: (tipo, x, y)
#   dica_item:  mostra o item necessário sobre a vítima (ajuda nas primeiras fases)
#   agrava:     a cada N segundos uma vítima piora (0 = desligado)
STAGE_CONFIGS = [
    {   # ------------------------------------------------------------ FASE 1
        "nome": "Cozinha e Sala",
        "tempo": 75,
        "piso": ((150, 150, 150), (140, 140, 140)),
        "parede": (92, 98, 120),
        "dica_item": True,
        "agrava": 0,
        "comodos": [
            (16, 72, 454, 512, "Cozinha", PISO_COZINHA),
            (482, 72, 462, 512, "Sala", PISO_SALA),
        ],
        "paredes": _parede_v(470, [(290, 370)]),
        "jogador": (100, 330),
        "pias": [(60, 72, 60, 40)],
        "porta": (944, 290, 16, 80),
        "obstaculos": [
            (200, 72, 150, 36, "balcao"),
            (400, 72, 56, 80, "geladeira"),
            (180, 300, 110, 80, "mesa"),
            (560, 430, 200, 60, "sofa"),
            (620, 230, 120, 70, "mesa"),
            (700, 72, 200, 36, "estante"),
            (890, 500, 40, 50, "planta"),
        ],
        "vitimas": [
            ("queimadura", 300, 200),
            ("sangramento", 780, 340),
        ],
        "itens": [
            ("pano_limpo", 150, 190),
            ("pano_limpo", 380, 460),
            ("pano_limpo", 560, 150),
            ("manteiga", 110, 470),
            ("gelo", 540, 340),
        ],
    },
    {   # ------------------------------------------------------------ FASE 2
        "nome": "Casa Térrea",
        "tempo": 90,
        "piso": ((150, 150, 150), (140, 140, 140)),
        "parede": (110, 90, 100),
        "dica_item": True,
        "agrava": 0,
        "comodos": [
            (16, 72, 404, 248, "Cozinha", PISO_COZINHA),
            (16, 332, 404, 252, "Quarto", PISO_QUARTO),
            (432, 72, 512, 512, "Sala", PISO_SALA),
        ],
        "paredes": _parede_v(420, [(160, 240), (440, 520)]) +
                   _parede_h(320, [(150, 230)], x0=16, x1=420),
        "jogador": (120, 270),
        "pias": [(60, 72, 60, 40)],
        "porta": (944, 290, 16, 80),
        "obstaculos": [
            (200, 72, 140, 36, "balcao"),
            (350, 72, 56, 80, "geladeira"),
            (230, 170, 110, 56, "mesa"),
            (40, 420, 130, 100, "cama"),
            (330, 510, 80, 64, "armario"),
            (480, 440, 200, 60, "sofa"),
            (570, 250, 120, 70, "mesa"),
            (700, 72, 200, 36, "estante"),
            (890, 500, 40, 50, "planta"),
        ],
        "vitimas": [
            ("queimadura", 120, 170),
            ("tontura", 250, 540),
            ("sangramento", 800, 330, "grave"),
        ],
        "itens": [
            ("pano_limpo", 300, 270),
            ("pano_limpo", 350, 440),
            ("pano_limpo", 520, 150),
            ("atadura", 220, 400),
            ("atadura", 780, 200),
            ("agua", 100, 550),
            ("manteiga", 380, 250),
            ("gelo", 600, 360),
            ("pasta_dente", 850, 420),
        ],
    },
    {   # ------------------------------------------------------------ FASE 3
        "nome": "Apartamento",
        "tempo": 100,
        "piso": ((150, 150, 150), (140, 140, 140)),
        "parede": (70, 84, 104),
        "dica_item": True,
        "agrava": 30,
        "comodos": [
            (16, 72, 384, 228, "Cozinha", PISO_COZINHA),
            (412, 72, 532, 228, "Sala", PISO_SALA),
            (16, 312, 544, 272, "Quarto", PISO_QUARTO),
            (572, 312, 372, 272, "Banheiro", PISO_BANHEIRO),
        ],
        "paredes": _parede_h(300, [(150, 230), (640, 720)]) +
                   _parede_v(400, [(170, 240)], y0=72, y1=300) +
                   _parede_v(560, [(430, 500)], y0=312, y1=584),
        "jogador": (300, 250),
        "pias": [(60, 72, 60, 40), (800, 316, 60, 40)],
        "porta": (944, 150, 16, 80),
        "obstaculos": [
            (200, 72, 150, 36, "balcao"),
            (120, 170, 110, 50, "mesa"),
            (440, 130, 100, 50, "mesa"),
            (560, 200, 200, 60, "sofa"),
            (700, 72, 200, 36, "estante"),
            (890, 240, 40, 50, "planta"),
            (40, 440, 130, 100, "cama"),
            (250, 330, 70, 44, "arquivo"),
            (400, 520, 120, 56, "armario"),
            (880, 400, 60, 150, "banheira"),
            (600, 520, 100, 56, "armario"),
        ],
        "vitimas": [
            ("queimadura", 270, 140),
            ("sangramento", 620, 150, "grave"),
            ("fratura", 300, 430, "grave"),
            ("engasgo", 700, 440),
        ],
        "itens": [
            ("pano_limpo", 130, 260),
            ("pano_limpo", 480, 250),
            ("pano_limpo", 300, 540),
            ("atadura", 350, 130),
            ("atadura", 850, 160),
            ("tala", 120, 380),
            ("manteiga", 250, 250),
            ("pasta_dente", 640, 400),
            ("gelo", 500, 200),
            ("manteiga", 800, 480),
            ("gelo", 350, 500),
        ],
    },
    {   # ------------------------------------------------------------ FASE 4
        "nome": "Escritório",
        "tempo": 100,
        "piso": ((150, 150, 150), (140, 140, 140)),
        "parede": (74, 80, 108),
        "dica_item": False,
        "agrava": 28,
        "comodos": [
            (16, 72, 314, 258, "Copa", PISO_COZINHA),
            (16, 342, 314, 242, "Arquivo", PISO_ARQUIVO),
            (342, 72, 288, 512, "Recepção", PISO_RECEPCAO),
            (642, 72, 302, 258, "Reunião", PISO_ESCRITORIO),
            (642, 342, 302, 242, "Banheiro", PISO_BANHEIRO),
        ],
        "paredes": _parede_v(330, [(150, 230), (430, 510)]) +
                   _parede_v(630, [(150, 230), (430, 510)]) +
                   _parede_h(330, [(150, 230)], x0=16, x1=330) +
                   _parede_h(330, [(750, 830)], x0=642, x1=944),
        "jogador": (480, 400),
        "pias": [(60, 72, 60, 40), (760, 346, 60, 40)],
        "porta": (944, 130, 16, 80),
        "obstaculos": [
            (140, 72, 120, 36, "balcao"),
            (264, 72, 56, 80, "geladeira"),
            (120, 200, 110, 56, "mesa"),
            (40, 350, 60, 90, "arquivo"),
            (110, 350, 60, 90, "arquivo"),
            (200, 470, 110, 60, "mesa"),
            (440, 250, 150, 60, "mesa"),
            (360, 480, 200, 60, "sofa"),
            (560, 90, 40, 50, "planta"),
            (700, 160, 200, 70, "mesa"),
            (780, 72, 150, 36, "estante"),
            (880, 520, 60, 50, "armario"),
        ],
        "vitimas": [
            ("queimadura", 70, 200),
            ("sangramento", 480, 150, "grave"),
            ("fratura", 100, 520, "grave"),
            ("desmaio", 780, 260),
            ("engasgo", 800, 470),
        ],
        "itens": [
            ("pano_limpo", 200, 150),
            ("pano_limpo", 400, 150),
            ("pano_limpo", 480, 420),
            ("atadura", 250, 300),
            ("atadura", 200, 400),
            ("tala", 260, 420),
            ("manta", 670, 300),
            ("manteiga", 150, 280),
            ("gelo", 400, 330),
            ("pasta_dente", 700, 420),
            ("manteiga", 900, 400),
            ("gelo", 160, 560),
        ],
    },
    {   # ------------------------------------------------------------ FASE 5
        "nome": "Casa Grande",
        "tempo": 110,
        "piso": ((150, 150, 150), (140, 140, 140)),
        "parede": (84, 70, 90),
        "dica_item": False,
        "agrava": 26,
        "comodos": [
            (16, 72, 304, 248, "Cozinha", PISO_COZINHA),
            (332, 72, 298, 248, "Sala", PISO_SALA),
            (642, 72, 302, 248, "Quarto 1", PISO_QUARTO),
            (16, 332, 304, 252, "Banheiro", PISO_BANHEIRO),
            (332, 332, 298, 252, "Escritório", PISO_ESCRITORIO),
            (642, 332, 302, 252, "Quarto 2", PISO_QUARTO),
        ],
        "paredes": _parede_v(320, [(150, 230), (430, 510)]) +
                   _parede_v(630, [(150, 230), (430, 510)]) +
                   _parede_h(320, [(120, 200), (430, 510), (740, 820)]),
        "jogador": (480, 380),
        "pias": [(60, 72, 60, 40), (60, 336, 60, 40)],
        "porta": (944, 100, 16, 80),
        "obstaculos": [
            (140, 72, 120, 36, "balcao"),
            (264, 72, 50, 80, "geladeira"),
            (130, 200, 110, 50, "mesa"),
            (360, 250, 180, 55, "sofa"),
            (450, 72, 150, 36, "estante"),
            (760, 80, 130, 100, "cama"),
            (660, 260, 100, 50, "armario"),
            (200, 510, 110, 64, "banheira"),
            (400, 420, 140, 60, "mesa"),
            (560, 500, 50, 70, "arquivo"),
            (680, 460, 140, 100, "cama"),
            (880, 340, 56, 100, "armario"),
        ],
        "vitimas": [
            ("queimadura", 80, 215, "grave"),
            ("sangramento", 500, 150, "grave"),
            ("tontura", 860, 220),
            ("fratura", 100, 430, "grave"),
            ("engasgo", 480, 540),
            ("desmaio", 760, 400),
        ],
        "itens": [
            ("pano_limpo", 180, 150),
            ("pano_limpo", 420, 150),
            ("pano_limpo", 780, 300),
            ("pano_limpo", 200, 420),
            ("atadura", 250, 300),
            ("atadura", 560, 300),
            ("tala", 260, 380),
            ("agua", 700, 150),
            ("manta", 560, 420),
            ("manteiga", 150, 300),
            ("gelo", 600, 200),
            ("pasta_dente", 700, 380),
            ("manteiga", 150, 540),
            ("gelo", 900, 520),
        ],
    },
]
