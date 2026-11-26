# -*- coding: utf-8 -*-
"""
game.py
-------
Classe Jogo: máquina de estados (Menu -> Instruções -> Fases -> Transição ->
Vitória / Game Over), HUD, coleta/preparo de itens, colisões, spawns por fase,
pontuação/combo e sons gerados por código (array + pygame.mixer).
"""
import math
import array
import random
import pygame

from settings import *
import sprites as spr
from entities import Player, Victim, Item, Station, Door, desenhar_brilho


# ----------------------------------------------------------------------------
# FUNÇÕES AUXILIARES
# ----------------------------------------------------------------------------
def quebrar_texto(fonte, texto, largura):
    """Quebra 'texto' em linhas que caibam em 'largura' pixels."""
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = (atual + " " + palavra).strip()
        if fonte.size(teste)[0] <= largura:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas


def desenhar_estrela(surf, centro, raio, cor, borda=(70, 55, 0)):
    """Desenha uma estrela de 5 pontas (avaliação da fase)."""
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        r = raio if i % 2 == 0 else raio * 0.45
        pts.append((centro[0] + r * math.cos(ang), centro[1] + r * math.sin(ang)))
    pygame.draw.polygon(surf, cor, pts)
    pygame.draw.polygon(surf, borda, pts, 2)


def nome_etapa(item):
    """Nome amigável de uma etapa (item ou mãos livres)."""
    if item == MAO_VAZIA:
        return "Mãos livres (Heimlich)"
    if item == "pano_umido":
        return "Pano Úmido (Pano Limpo + Pia)"
    return NOMES_ITEM[item]


def desenhar_obstaculo(surf, rect, tipo):
    """Desenha um móvel simples (obstáculo sólido) no fundo da fase."""
    cores = {
        "sofa": (165, 72, 84), "mesa": (160, 115, 70), "armario": (132, 100, 70),
        "geladeira": (214, 220, 230), "estante": (115, 80, 55), "planta": (62, 150, 82),
        "arquivo": (135, 140, 152), "balcao": (190, 180, 160),
        "cama": (150, 120, 190), "banheira": (226, 236, 244),
    }
    cor = cores.get(tipo, (150, 150, 150))
    escura = tuple(max(0, c - 45) for c in cor)
    clara = tuple(min(255, c + 35) for c in cor)
    # sombra
    sombra = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    sombra.fill((0, 0, 0, 60))
    surf.blit(sombra, (rect.x + 4, rect.y + 6))
    if tipo == "planta":
        pygame.draw.rect(surf, (150, 95, 60), (rect.x + rect.w // 4, rect.bottom - 16,
                                                rect.w // 2, 16), border_radius=3)
        pygame.draw.circle(surf, cor, (rect.centerx, rect.centery - 6), rect.w // 2)
        pygame.draw.circle(surf, clara, (rect.centerx - 5, rect.centery - 10), rect.w // 5)
        return
    pygame.draw.rect(surf, cor, rect, border_radius=4)
    pygame.draw.rect(surf, clara, (rect.x, rect.y, rect.w, 8), border_radius=4)
    pygame.draw.rect(surf, escura, rect, 2, border_radius=4)
    if tipo == "sofa":
        for i in range(3):
            w = (rect.w - 16) // 3
            pygame.draw.rect(surf, clara, (rect.x + 8 + i * w, rect.y + 12, w - 3, rect.h - 20),
                             border_radius=5)
    elif tipo == "geladeira":
        pygame.draw.line(surf, escura, (rect.x, rect.centery), (rect.right - 1, rect.centery), 2)
        pygame.draw.rect(surf, escura, (rect.right - 10, rect.y + 16, 3, 14))
    elif tipo in ("estante", "armario"):
        for i in range(1, 4):
            x = rect.x + i * rect.w // 4
            pygame.draw.line(surf, escura, (x, rect.y + 8), (x, rect.bottom - 3), 1)
    elif tipo == "arquivo":
        for i in range(3):
            y = rect.y + 8 + i * (rect.h - 10) // 3
            pygame.draw.line(surf, escura, (rect.x + 3, y), (rect.right - 4, y), 2)
    elif tipo == "cama":
        pygame.draw.rect(surf, (245, 245, 250), (rect.x + 10, rect.y + 12, rect.w - 20, 24),
                         border_radius=7)
        pygame.draw.rect(surf, clara, (rect.x + 4, rect.y + 44, rect.w - 8, rect.h - 48),
                         border_radius=5)
    elif tipo == "banheira":
        pygame.draw.rect(surf, (150, 200, 235), rect.inflate(-16, -16), border_radius=10)
        pygame.draw.rect(surf, escura, rect.inflate(-16, -16), 2, border_radius=10)


# ----------------------------------------------------------------------------
# CLASSE PRINCIPAL
# ----------------------------------------------------------------------------
class Jogo:
    def __init__(self, tela):
        self.tela = tela
        self.rodando = True
        self.t = 0.0

        # Fontes (fonte padrão do pygame: sempre disponível, com acentos)
        self.f_titulo = pygame.font.Font(None, 120)
        self.f_grande = pygame.font.Font(None, 56)
        self.f_media = pygame.font.Font(None, 34)
        self.f_normal = pygame.font.Font(None, 27)
        self.f_peq = pygame.font.Font(None, 21)
        self.f_hud_v = pygame.font.Font(None, 34)
        self.f_hud_l = pygame.font.Font(None, 17)

        # Sprites
        self.sprites_item = spr.load_spritesheet()
        self.frames_player = spr.criar_frames_player()
        self.sprites_vitima = {t: spr.criar_sprite_vitima(t) for t in DECAY}
        self.icones = spr.criar_icones()
        self.minis = {k: pygame.transform.smoothscale(v, (22, 22))
                      for k, v in self.sprites_item.items()}

        # Sons
        self.sons = self._criar_sons()

        # Estado geral
        self.estado = ESTADO_MENU
        self.fase_idx = 0
        self.pontos = 0
        self.pontos_inicio_fase = 0
        self.causa = "tempo"
        self.resumo = {}
        self.pag_instr = 0
        self.estrelas_fases = []       # estrelas (1-3) de cada fase concluída
        self._reset_fase_vars()

        self.fundo_menu = self._gerar_fundo_degrade((24, 28, 52), (70, 40, 70))

    # ------------------------------------------------------------------ sons
    def _amostras(self, freq, dur, vol=0.35, forma="seno", freq_fim=None):
        """Gera amostras 16-bit (array) de um tom, com envelope de volume."""
        taxa, _, canais = pygame.mixer.get_init()
        n = int(taxa * dur)
        dados = array.array("h")
        fase = 0.0
        ataque = max(1.0, 0.01 * taxa)
        for i in range(n):
            prog = i / n
            f = freq if freq_fim is None else freq + (freq_fim - freq) * prog
            fase += 2 * math.pi * f / taxa
            onda = math.sin(fase)
            if forma == "quadrada":
                onda = 1.0 if onda >= 0 else -1.0
            env = min(1.0, i / ataque) * (1.0 - prog)
            amostra = int(32767 * vol * onda * env)
            for _ in range(canais):
                dados.append(amostra)
        return dados

    def _criar_sons(self):
        """Cria os efeitos sonoros. Se não houver áudio, o jogo segue mudo."""
        sons = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(22050, -16, 1, 512)
            sons["ok"] = pygame.mixer.Sound(buffer=self._amostras(1320, 0.16, 0.30))       # bipe agudo
            sons["erro"] = pygame.mixer.Sound(buffer=self._amostras(150, 0.38, 0.40,
                                                                    "quadrada", 95))      # bipe grave
            sons["pegar"] = pygame.mixer.Sound(buffer=self._amostras(660, 0.07, 0.25))
            sons["alerta"] = pygame.mixer.Sound(buffer=self._amostras(520, 0.25, 0.30, "quadrada", 380))
            porta = self._amostras(660, 0.10, 0.30)
            porta.extend(self._amostras(880, 0.10, 0.30))
            porta.extend(self._amostras(1320, 0.18, 0.30))
            sons["porta"] = pygame.mixer.Sound(buffer=porta)
        except Exception as exc:  # sem dispositivo de áudio, etc.
            print("[HelpYou] Áudio indisponível (%s). Jogo seguirá sem som." % exc)
            sons = {}
        return sons

    def tocar(self, nome):
        som = self.sons.get(nome)
        if som:
            som.play()

    # ------------------------------------------------------------ preparação
    def _reset_fase_vars(self):
        self.cfg = None
        self.tempo = 0.0
        self.player = None
        self.vitimas, self.itens, self.obstaculos = [], [], []
        self.paredes = []
        self.pias = []
        self.timer_agrava = 0.0
        self.duracao_atual = TEMPO_VITIMA
        self.porta = None
        self.fundo = None
        self.combo = 0
        self.flash = 0.0
        self.msg = None            # (texto, cor, tempo_restante)
        self.popups = []           # [texto, x, y, vida, cor]
        self.progresso = 0.0
        self.alvo_atual = None
        self.travado = False
        self.pia_ativa = False

    def novo_jogo(self):
        self.pontos = 0
        self.fase_idx = 0
        self.estrelas_fases = []
        self.iniciar_fase(0)

    def iniciar_fase(self, idx):
        """Monta a fase 'idx': spawn de player, vítimas, itens, pia, porta e fundo."""
        self._reset_fase_vars()
        self.fase_idx = idx
        self.pontos_inicio_fase = self.pontos
        cfg = STAGE_CONFIGS[idx]
        self.cfg = cfg
        self.tempo = float(cfg["tempo"])
        self.player = Player(*cfg["jogador"])
        self.vitimas = [Victim(v[0], v[1], v[2], len(v) > 3 and v[3] == "grave")
                        for v in cfg["vitimas"]]
        self.itens = [Item(t, x, y) for (t, x, y) in cfg["itens"]]
        self.pias = [Station(p) for p in cfg["pias"]]
        self.porta = Door(cfg["porta"])
        self.obstaculos = [pygame.Rect(o[0], o[1], o[2], o[3]) for o in cfg["obstaculos"]]
        self.paredes = [pygame.Rect(p) for p in cfg["paredes"]]
        self.timer_agrava = float(cfg.get("agrava", 0))
        self.fundo = self._montar_fundo(cfg)
        self.estado = ESTADO_JOGANDO
        extra = " Cuidado: as vítimas podem piorar!" if cfg.get("agrava") else ""
        self.mostrar_msg("Fase %d/%d: %s. Ajude as vítimas antes do SAMU chegar!%s"
                         % (idx + 1, len(STAGE_CONFIGS), cfg["nome"], extra), AZUL, 4.0)

    def _montar_fundo(self, cfg):
        """Pré-renderiza cômodos (pisos), paredes internas e móveis (estáticos na fase)."""
        bg = pygame.Surface((LARGURA, ALTURA))
        bg.fill(cfg["parede"])
        # Piso base (soleiras/portas entre os cômodos)
        c1, c2 = cfg["piso"]
        for j, y in enumerate(range(AREA_JOGO.top, AREA_JOGO.bottom, 32)):
            for i, x in enumerate(range(AREA_JOGO.left, AREA_JOGO.right, 32)):
                pygame.draw.rect(bg, c1 if (i + j) % 2 == 0 else c2, (x, y, 32, 32))
        # Piso de cada cômodo (xadrez com a paleta do cômodo)
        for (x, y, w, h, nome, piso) in cfg["comodos"]:
            r = pygame.Rect(x, y, w, h)
            for yy in range(r.top, r.bottom, 32):
                for xx in range(r.left, r.right, 32):
                    tile = pygame.Rect(xx, yy, 32, 32).clip(r)
                    k = ((xx - r.left) // 32 + (yy - r.top) // 32) % 2
                    pygame.draw.rect(bg, piso[k], tile)
        # Contorno interno das paredes externas
        escura = tuple(max(0, c - 30) for c in cfg["parede"])
        pygame.draw.rect(bg, escura, AREA_JOGO.inflate(4, 4), 3)
        # Paredes internas
        clara = tuple(min(255, c + 28) for c in cfg["parede"])
        for p in cfg["paredes"]:
            r = pygame.Rect(p)
            sombra = pygame.Surface(r.size, pygame.SRCALPHA)
            sombra.fill((0, 0, 0, 70))
            bg.blit(sombra, (r.x + 4, r.y + 5))
            pygame.draw.rect(bg, clara, r)
            pygame.draw.rect(bg, escura, r, 2)
        # Móveis
        for o in cfg["obstaculos"]:
            desenhar_obstaculo(bg, pygame.Rect(o[0], o[1], o[2], o[3]), o[4])
        # Nome dos cômodos
        for (x, y, w, h, nome, piso) in cfg["comodos"]:
            txt = self.f_hud_l.render(nome.upper(), True, tuple(max(0, c - 95) for c in piso[0]))
            bg.blit(txt, (x + 10, y + h - 22))
        return bg

    def _gerar_fundo_degrade(self, c_topo, c_base):
        s = pygame.Surface((LARGURA, ALTURA))
        for y in range(ALTURA):
            k = y / ALTURA
            cor = tuple(int(c_topo[i] + (c_base[i] - c_topo[i]) * k) for i in range(3))
            pygame.draw.line(s, cor, (0, y), (LARGURA, y))
        return s

    # ---------------------------------------------------------------- eventos
    def tratar_evento(self, ev):
        if ev.type == pygame.QUIT:
            self.rodando = False
            return
        if ev.type != pygame.KEYDOWN:
            return
        k = ev.key
        confirma = k in (pygame.K_RETURN, pygame.K_KP_ENTER)
        est = self.estado

        if est == ESTADO_MENU:
            if confirma:
                self.pag_instr = 0
                self.estado = ESTADO_INSTRUCOES
            elif k == pygame.K_ESCAPE:
                self.rodando = False
        elif est == ESTADO_INSTRUCOES:
            if confirma:
                if self.pag_instr == 0:
                    self.pag_instr = 1
                else:
                    self.novo_jogo()
            elif k == pygame.K_ESCAPE:
                if self.pag_instr == 1:
                    self.pag_instr = 0
                else:
                    self.estado = ESTADO_MENU
        elif est == ESTADO_JOGANDO:
            if k == pygame.K_ESCAPE:
                self.estado = ESTADO_PAUSADO
            elif k == pygame.K_q:
                self.largar_item()
            elif k in (pygame.K_e, pygame.K_SPACE):
                self.ao_apertar_acao()
        elif est == ESTADO_PAUSADO:
            if k == pygame.K_ESCAPE or confirma:
                self.estado = ESTADO_JOGANDO
            elif k == pygame.K_m:
                self.estado = ESTADO_MENU
        elif est == ESTADO_TRANSICAO:
            if confirma:
                self.iniciar_fase(self.fase_idx + 1)
        elif est == ESTADO_VITORIA:
            if confirma or k == pygame.K_ESCAPE:
                self.estado = ESTADO_MENU
        elif est == ESTADO_GAME_OVER:
            if confirma:
                self.pontos = self.pontos_inicio_fase
                self.iniciar_fase(self.fase_idx)
            elif k == pygame.K_ESCAPE:
                self.estado = ESTADO_MENU

    # ------------------------------------------------------------ interações
    def mostrar_msg(self, texto, cor=VERMELHO, dur=4.5):
        self.msg = [texto, cor, dur]

    def alvos_em_alcance(self):
        """Lista de (tipo, objeto, distancia) ao alcance do player."""
        p = pygame.Vector2(self.player.rect.center)
        lista = []
        for it in self.itens:
            if it.rect.inflate(2 * ALCANCE, 2 * ALCANCE).collidepoint(p):
                lista.append(("item", it, p.distance_to(it.rect.center)))
        for pia in self.pias:
            if pia.rect.inflate(2 * ALCANCE, 2 * ALCANCE).collidepoint(p):
                lista.append(("pia", pia, p.distance_to(pia.rect.center)))
        for v in self.vitimas:
            if not v.estabilizada and v.rect.inflate(2 * ALCANCE, 2 * ALCANCE).collidepoint(p):
                lista.append(("vitima", v, p.distance_to(v.rect.center)))
        return lista

    def _escolher_estacao(self, estacoes):
        """Entre pias/vítimas ao alcance, prefere a que aceita o que está na mão."""
        item = self.player.item

        def serve(a):
            if a[0] == "pia":
                return item == "pano_limpo"
            nec = a[1].necessario
            return (nec == MAO_VAZIA and item is None) or (item is not None and item == nec)

        validas = [a for a in estacoes if serve(a)]
        return min(validas or estacoes, key=lambda a: a[2])

    def alvo_principal(self):
        """Alvo mostrado no rótulo [E] Ação (prioriza item se a mão está vazia)."""
        alvos = self.alvos_em_alcance()
        if not alvos:
            return None
        # Mão vazia: prioriza pegar item, EXCETO se há vítima ao alcance pedindo mãos livres
        # (senão o item largado no chão seria pego de novo ao apertar E para o Heimlich)
        pede_maos = any(a[0] == "vitima" and a[1].necessario == MAO_VAZIA for a in alvos)
        if self.player.item is None and not pede_maos:
            itens = [a for a in alvos if a[0] == "item"]
            if itens:
                return min(itens, key=lambda a: a[2])
        estacoes = [a for a in alvos if a[0] != "item"]
        if estacoes:
            return self._escolher_estacao(estacoes)
        return min(alvos, key=lambda a: a[2])

    def ao_apertar_acao(self):
        """Ao APERTAR E/Espaço: coleta itens (instantâneo) ou dá dicas."""
        alvo = self.alvo_principal()
        if alvo is None:
            return
        tipo, obj, _ = alvo
        if tipo == "item":
            if self.player.item is None:
                self.player.item = obj.tipo
                self.itens.remove(obj)
                self.travado = True      # evita iniciar "segurar" com a mesma pressão
                self.tocar("pegar")
            else:
                self.mostrar_msg("Mão ocupada! Largue o item atual com [Q].", AZUL, 2.5)
        elif tipo == "pia":
            if self.player.item == "pano_limpo":
                pass                     # o progresso é tratado enquanto segura
            elif self.player.item == "pano_umido":
                self.mostrar_msg("Este pano já está úmido. Leve-o até uma queimadura.", AZUL, 2.5)
            else:
                self.mostrar_msg("Segure um Pano Limpo e mantenha [E] na pia para umedecer.", AZUL, 3.0)
        elif tipo == "vitima":
            if obj.necessario == MAO_VAZIA:
                if self.player.item is not None:
                    self.mostrar_msg("Engasgo! Largue o item com [Q]: a manobra exige as mãos livres.",
                                     AZUL, 3.0)
            elif self.player.item is None:
                self.mostrar_msg("Pegue um item antes de ajudar a vítima.", AZUL, 2.5)

    def largar_item(self):
        """Q: larga o item da mão no chão (ao lado do player)."""
        if self.player.item is None:
            return
        dx = {"direita": 24, "esquerda": -24}.get(self.player.direcao, 0)
        dy = {"baixo": 24, "cima": -24}.get(self.player.direcao, 0)
        x = self.player.rect.centerx + dx
        y = self.player.rect.centery + dy
        x = max(AREA_JOGO.left + 16, min(AREA_JOGO.right - 16, x))
        y = max(AREA_JOGO.top + 16, min(AREA_JOGO.bottom - 16, y))
        self.itens.append(Item(self.player.item, x, y))
        self.player.item = None
        self.travado = True

    def concluir_acao(self, tipo, obj):
        if tipo == "pia":
            self.player.item = "pano_umido"
            self.tocar("ok")
            self.mostrar_msg("Pano Úmido pronto! Use em queimaduras.", VERDE, 2.5)
        else:
            self.aplicar_item_na_vitima(obj)

    def aplicar_item_na_vitima(self, v):
        item = self.player.item
        nec = v.necessario
        correto = (nec == MAO_VAZIA and item is None) or (item is not None and item == nec)
        if correto:
            # ---- ETAPA CORRETA ----
            self.player.item = None
            v.etapa += 1
            if v.etapa < len(v.etapas):
                # Tratamento em várias etapas: ainda não terminou
                v.mult_decay = max(0.25, v.mult_decay * 0.5)
                v.estab = min(100.0, v.estab + 12.0)
                self.popups.append(["Etapa %d/%d" % (v.etapa, len(v.etapas)), v.rect.centerx,
                                    v.rect.centery - 60, 1.3, AMARELO_BRILHO])
                self.tocar("ok")
                self.mostrar_msg(MSG_ETAPA.get(v.tipo, "Continue o tratamento!"), AZUL, 4.0)
                return
            # ---- VÍTIMA ESTABILIZADA ----
            v.estabilizada = True
            self.combo += 1
            mult = MULT_COMBO if self.combo >= COMBO_MINIMO else 1.0
            ganho = int(PONTOS_VITIMA * mult)
            self.pontos += ganho
            self.popups.append(["+%d" % ganho, v.rect.centerx, v.rect.centery - 60, 1.2, VERDE])
            self.tocar("ok")
            self.mostrar_msg(MSG_SUCESSO[v.tipo], VERDE, 4.0)
            if all(x.estabilizada for x in self.vitimas):
                self.porta.aberta = True
                self.tocar("porta")
                self.mostrar_msg("Todas estabilizadas! Corra até a PORTA VERDE antes do SAMU chegar.",
                                 VERDE, 5.0)
        elif item in DISTRATORES:
            # ---- ERRO GRAVE (mito) ----
            self.player.item = None
            self.tempo -= PENALIDADE_TEMPO
            self.combo = 0
            self.flash = 0.6
            self.tocar("erro")
            self.popups.append(["-%ds" % PENALIDADE_TEMPO, v.rect.centerx, v.rect.centery - 60, 1.4, VERMELHO])
            self.mostrar_msg(TEXTOS_DISTRATORES[item], VERMELHO, 6.0)
            if self.tempo <= 0:
                self.tempo = 0
                self.game_over("tempo")
        else:
            # ---- ITEM ERRADO (não é mito, mas não serve) ----
            self.combo = 0
            self.flash = 0.4
            self.tocar("erro")
            texto = DICAS_ERRO[v.tipo]
            if len(v.etapas) > 1:
                texto += " (Etapa %d/%d)" % (v.etapa + 1, len(v.etapas))
            self.mostrar_msg(texto, VERMELHO, 5.0)

    def game_over(self, causa):
        self.causa = causa
        self.estado = ESTADO_GAME_OVER
        self.tocar("erro")

    def fase_concluida(self):
        bonus = int(self.tempo) * BONUS_POR_SEGUNDO
        self.pontos += bonus
        frac = self.tempo / float(self.cfg["tempo"])
        estrelas = 3 if frac >= 0.4 else (2 if frac >= 0.2 else 1)
        self.estrelas_fases = self.estrelas_fases[:self.fase_idx] + [estrelas]
        self.resumo = {"bonus": bonus, "tempo": int(self.tempo), "estrelas": estrelas}
        self.tocar("porta")
        if self.fase_idx >= len(STAGE_CONFIGS) - 1:
            self.estado = ESTADO_VITORIA
        else:
            self.estado = ESTADO_TRANSICAO

    # -------------------------------------------------------------- atualizar
    def atualizar(self, dt):
        self.t += dt
        if self.estado == ESTADO_JOGANDO:
            self._atualizar_jogo(dt)

    def _atualizar_jogo(self, dt):
        teclas = pygame.key.get_pressed()

        # Colisão: móveis, pia e vítimas sólidas (fratura)
        solidos = list(self.obstaculos) + list(self.paredes) + [p.rect for p in self.pias] + \
                  [v.rect for v in self.vitimas if v.solido]
        self.player.mover(dt, teclas, solidos)

        # Estabilidade das vítimas
        for v in self.vitimas:
            v.atualizar(dt)
            if v.estab <= 0 and not v.estabilizada:
                self.game_over(v.tipo)
                return

        # Tempo do SAMU
        self.tempo -= dt
        if self.tempo <= 0:
            self.tempo = 0
            self.game_over("tempo")
            return

        # ---- Segurar E/Espaço (pia 2,0s / vítima 2,5s) ----
        segurando = teclas[pygame.K_e] or teclas[pygame.K_SPACE]
        if not segurando:
            self.travado = False
        valido, duracao, tipo, obj = False, 0.0, None, None
        if segurando and not self.travado:
            # prioriza pia/vítima ao alcance, independente de itens no chão
            estacoes = [a for a in self.alvos_em_alcance() if a[0] != "item"]
            if estacoes:
                tipo, obj, _ = self._escolher_estacao(estacoes)
                if tipo == "pia" and self.player.item == "pano_limpo":
                    valido, duracao = True, TEMPO_PIA
                elif tipo == "vitima":
                    if obj.necessario == MAO_VAZIA:
                        valido = self.player.item is None      # manobra: mãos livres
                    else:
                        valido = self.player.item is not None
                    duracao = TEMPO_ACAO.get(obj.tipo, TEMPO_VITIMA)
        self.pia_ativa = False
        if valido:
            if obj is not self.alvo_atual:
                self.alvo_atual = obj
                self.progresso = 0.0
            self.progresso += dt
            self.duracao_atual = duracao
            self.pia_ativa = (tipo == "pia")
            if self.progresso >= duracao:
                self.progresso = 0.0
                self.alvo_atual = None
                self.travado = True           # exige soltar a tecla antes da próxima ação
                self.concluir_acao(tipo, obj)
                if self.estado != ESTADO_JOGANDO:
                    return
        else:
            self.progresso = 0.0
            self.alvo_atual = None

        # ---- Agravamento: de tempos em tempos uma vítima piora ----
        if self.timer_agrava > 0 and not self.porta.aberta:
            self.timer_agrava -= dt
            if self.timer_agrava <= 0:
                self.timer_agrava = float(self.cfg["agrava"])
                vivos = [v for v in self.vitimas if not v.estabilizada]
                if vivos:
                    v = random.choice(vivos)
                    v.mult_decay = min(AGRAVO_MAX, v.mult_decay * AGRAVO_MULT)
                    v.alerta = 3.0
                    self.tocar("alerta")
                    self.mostrar_msg("%s piorou! A estabilidade dela cai mais rápido."
                                     % NOMES_VITIMA[v.tipo], LARANJA, 3.5)

        # ---- Porta de saída ----
        if self.porta.aberta and self.player.rect.colliderect(self.porta.gatilho):
            self.fase_concluida()
            return

        # ---- Efeitos visuais ----
        self.flash = max(0.0, self.flash - dt)
        if self.msg:
            self.msg[2] -= dt
            if self.msg[2] <= 0:
                self.msg = None
        for p in self.popups:
            p[2] -= 40 * dt
            p[3] -= dt
        self.popups = [p for p in self.popups if p[3] > 0]

    # ----------------------------------------------------------------- desenho
    def texto(self, s, fonte, cor, pos, centro=False, sombra=True):
        img = fonte.render(s, True, cor)
        r = img.get_rect()
        if centro:
            r.center = pos
        else:
            r.topleft = pos
        if sombra:
            sh = fonte.render(s, True, (0, 0, 0))
            self.tela.blit(sh, r.move(2, 2))
        self.tela.blit(img, r)
        return r

    def desenhar(self):
        est = self.estado
        if est == ESTADO_MENU:
            self._desenhar_menu()
        elif est == ESTADO_INSTRUCOES:
            self._desenhar_instrucoes()
        elif est in (ESTADO_JOGANDO, ESTADO_PAUSADO):
            self._desenhar_jogo()
            if est == ESTADO_PAUSADO:
                self._desenhar_pausa()
        elif est == ESTADO_TRANSICAO:
            self._desenhar_transicao()
        elif est == ESTADO_VITORIA:
            self._desenhar_vitoria()
        elif est == ESTADO_GAME_OVER:
            self._desenhar_game_over()

    def _painel(self, rect, cor=(14, 16, 28, 215), borda=(120, 130, 170)):
        s = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(s, cor, s.get_rect(), border_radius=14)
        pygame.draw.rect(s, borda, s.get_rect(), 2, border_radius=14)
        self.tela.blit(s, rect.topleft)

    # ---- Menu ----
    def _desenhar_menu(self):
        self.tela.blit(self.fundo_menu, (0, 0))
        onda = (math.sin(self.t * 2.5) + 1) / 2
        cor = (255, int(200 + 40 * onda), int(80 + 60 * onda))
        self.texto(TITULO, self.f_titulo, cor, (LARGURA // 2, 120), centro=True)
        self.texto("Primeiros socorros: ajude as vítimas antes do SAMU chegar!",
                   self.f_media, COR_TEXTO, (LARGURA // 2, 195), centro=True)
        # Elenco: socorrista + 6 tipos de vítima
        tipos = list(DECAY.keys())
        self.tela.blit(pygame.transform.scale(self.frames_player[("baixo", 0)], (88, 88)),
                       (LARGURA // 2 - 3 * 112 - 44, 280))
        for i, tp in enumerate(tipos):
            cx = LARGURA // 2 + (i - 2) * 112
            self.tela.blit(pygame.transform.scale(self.sprites_vitima[tp], (88, 88)), (cx - 44, 280))
            ic = self.icones[tp]
            self.tela.blit(ic, (cx - 14, 236 + math.sin(self.t * 3 + i) * 4))
        if int(self.t * 2) % 2 == 0:
            self.texto("ENTER - Jogar", self.f_grande, BRANCO, (LARGURA // 2, 440), centro=True)
        self.texto("ESC - Sair", self.f_normal, CINZA, (LARGURA // 2, 495), centro=True)
        self.texto("Python 3.11 + Pygame 2.6.1", self.f_peq, CINZA, (LARGURA // 2, 570), centro=True)

    # ---- Instruções (2 páginas) ----
    def _desenhar_instrucoes(self):
        self.tela.blit(self.fundo_menu, (0, 0))
        self._painel(pygame.Rect(30, 20, 900, 560))
        self.texto("COMO JOGAR  (%d/2)" % (self.pag_instr + 1), self.f_grande, (255, 215, 90),
                   (LARGURA // 2, 55), centro=True)
        y = 95
        if self.pag_instr == 0:
            blocos = [
                ("CONTROLES", (255, 215, 90), [
                    "WASD / Setas: mover   |   E ou Espaço: coletar / segurar   |   Q: largar   |   ESC: pausar",
                    "Segure H durante o jogo para ver o GUIA RÁPIDO de tratamentos.",
                ]),
                ("COMO SALVAR", (255, 215, 90), [
                    "Você carrega 1 item por vez. Pegue o item certo e segure E por 2,5s perto da vítima.",
                    "Pano Limpo + Pia = Pano Úmido (segure E por 2,0s na pia).",
                    "Vítimas GRAVES têm 2 etapas (ex.: Pano Limpo e depois Atadura). Cada etapa feita reduz a queda.",
                    "Engasgo exige as MÃOS LIVRES: largue o item (Q) e segure E por 3s (manobra de Heimlich).",
                ]),
                ("CÔMODOS E PERIGOS", (255, 215, 90), [
                    "As casas têm vários cômodos ligados por portas. Planeje o trajeto: pias, itens e vítimas",
                    "ficam espalhados. Nas fases finais, de tempos em tempos uma vítima PIORA (cai mais rápido).",
                    "Manteiga, Pasta de Dente e Gelo são mitos perigosos: -10s, combo zerado e flash vermelho.",
                ]),
                ("PONTOS", (255, 215, 90), [
                    "+100 por vítima; acertos seguidos ativam o multiplicador x1,5 (erro zera o combo).",
                    "Sobrar tempo ao sair pela PORTA VERDE dá bônus e até 3 estrelas por fase. São 5 fases.",
                ]),
            ]
            for titulo, cor, linhas in blocos:
                self.texto(titulo, self.f_normal, cor, (60, y), sombra=False)
                y += 26
                for ln in linhas:
                    for sub in quebrar_texto(self.f_peq, ln, 830):
                        self.texto(sub, self.f_peq, COR_TEXTO, (74, y), sombra=False)
                        y += 21
                y += 8
        else:
            self.texto("Cada vítima exige um tratamento (queda de estabilidade por segundo):",
                       self.f_peq, COR_TEXTO, (60, y), sombra=False)
            y += 30
            linhas = [
                ("queimadura", "Queimadura (-2,0%/s): Pano ÚMIDO. Grave: depois Pano Limpo"),
                ("sangramento", "Sangramento (-2,5%/s): Gaze / Pano Limpo. Grave: depois Atadura"),
                ("fratura", "Fratura (-1,5%/s): Tala Rígida (sólida). Grave: depois Atadura"),
                ("tontura", "Tontura (-1,0%/s): Água"),
                ("engasgo", "Engasgo (-2,8%/s): MÃOS LIVRES, segure E por 3s (Heimlich)"),
                ("desmaio", "Desmaio (-1,3%/s): Manta Térmica"),
            ]
            for tp, desc in linhas:
                self.tela.blit(self.icones[tp], (60, y - 6))
                nec = ETAPAS[tp][0]
                if nec == MAO_VAZIA:
                    self.tela.blit(self.icones["mao_vazia"], (100, y - 6))
                else:
                    self.tela.blit(self.sprites_item[nec], (98, y - 8))
                self.texto(desc, self.f_normal, COR_TEXTO, (146, y), sombra=False)
                y += 46
            y += 6
            x = 60
            for it in DISTRATORES:
                self.tela.blit(self.sprites_item[it], (x, y - 6))
                x += 40
            self.texto("Mitos perigosos: Manteiga, Pasta de Dente e Gelo (-10s).", self.f_normal,
                       (255, 130, 120), (190, y + 2), sombra=False)
            y += 44
            self.texto("Se uma barra chegar a 0% ou o SAMU chegar antes de você sair, é Game Over.",
                       self.f_peq, COR_TEXTO, (60, y), sombra=False)
        if int(self.t * 2) % 2 == 0:
            rot = "ENTER - Próxima página" if self.pag_instr == 0 else "ENTER - Começar"
            self.texto(rot + "    |    ESC - Voltar", self.f_media, BRANCO,
                       (LARGURA // 2, 548), centro=True)

    # ---- Jogo ----
    def _desenhar_jogo(self):
        tela = self.tela
        t = self.t
        tela.blit(self.fundo, (0, 0))

        # Brilho pulsante nos interativos
        for it in self.itens:
            desenhar_brilho(tela, it.rect, t)
        for pia in self.pias:
            desenhar_brilho(tela, pia.rect, t, 4)
        for v in self.vitimas:
            if not v.estabilizada:
                desenhar_brilho(tela, v.rect, t)
        if self.porta.aberta:
            desenhar_brilho(tela, self.porta.rect, t, 10)

        self.porta.desenhar(tela, t)
        for pia in self.pias:
            pia.desenhar(tela, self.pia_ativa and self.alvo_atual is pia)
        for it in self.itens:
            it.desenhar(tela, self.sprites_item[it.tipo], t)

        # Vítimas e player ordenados por profundidade (y)
        ents = [("v", v) for v in self.vitimas] + [("p", self.player)]
        ents.sort(key=lambda e: e[1].rect.bottom)
        mostrar_dica = self.cfg.get("dica_item", False)
        for tipo, e in ents:
            if tipo == "v":
                dica = None
                if mostrar_dica:
                    dica = self.icones["mao_vazia"] if e.necessario == MAO_VAZIA \
                        else self.minis[e.necessario]
                e.desenhar(tela, self.sprites_vitima[e.tipo], self.icones[e.tipo],
                           self.icones["ok"], t, dica, self.icones["alerta"])
            else:
                e.desenhar(tela, self.frames_player, self.minis)

        # Rótulo [E] Ação ao aproximar
        if self.estado == ESTADO_JOGANDO:
            alvo = self.alvo_principal()
            if alvo:
                tipo, obj, _ = alvo
                if tipo == "vitima":
                    pos = (obj.rect.centerx, obj.rect.centery - 80)
                elif tipo == "pia":
                    pos = (obj.rect.centerx, obj.rect.bottom + 14)
                else:
                    pos = (obj.rect.centerx, obj.rect.top - 18)
                self._rotulo("[E] Ação", pos)
                self._dica_contextual(tipo, obj)

        # Barra de progresso (segurando E)
        if self.progresso > 0 and self.alvo_atual is not None:
            frac = min(1.0, self.progresso / self.duracao_atual)
            bx, by = self.player.rect.centerx - 30, self.player.rect.centery - 52
            pygame.draw.rect(tela, (20, 20, 28), (bx - 2, by - 2, 64, 12), border_radius=4)
            pygame.draw.rect(tela, AMARELO_BRILHO, (bx, by, int(60 * frac), 8), border_radius=3)

        # Popups de pontos
        for txt, x, y, vida, cor in self.popups:
            self.texto(txt, self.f_media, cor, (x, y), centro=True)

        # Flash vermelho de erro
        if self.flash > 0:
            s = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            s.fill((230, 30, 30, int(130 * min(1.0, self.flash / 0.4))))
            tela.blit(s, (0, 0))

        self._desenhar_hud()
        self._desenhar_mensagem()
        if self.estado == ESTADO_JOGANDO and pygame.key.get_pressed()[pygame.K_h]:
            self._desenhar_guia()

    def _rotulo(self, texto, pos):
        img = self.f_peq.render(texto, True, (30, 24, 0))
        r = img.get_rect(center=pos).inflate(14, 8)
        pygame.draw.rect(self.tela, AMARELO_BRILHO, r, border_radius=8)
        pygame.draw.rect(self.tela, (120, 90, 0), r, 2, border_radius=8)
        self.tela.blit(img, img.get_rect(center=pos))

    def _dica_contextual(self, tipo, obj):
        p = self.player
        if tipo == "item":
            txt = ("Pressione E: pegar " + NOMES_ITEM[obj.tipo]) if p.item is None \
                else "Mão ocupada: Q para largar o item atual"
        elif tipo == "pia":
            txt = "Segure E por 2s com um Pano Limpo na mão para umedecer" \
                if p.item == "pano_limpo" else "Pia: leve um Pano Limpo aqui para umedecer"
        else:
            etapa = ""
            if len(obj.etapas) > 1:
                etapa = ", etapa %d/%d" % (obj.etapa + 1, len(obj.etapas))
            if obj.necessario == MAO_VAZIA:
                txt = "Segure E por 3s: manobra de Heimlich (%s)" % NOMES_VITIMA[obj.tipo] \
                    if p.item is None else "Engasgo: largue o item com Q para usar as mãos livres"
            elif p.item:
                txt = "Segure E por 2,5s para aplicar o item (%s%s)" % (NOMES_VITIMA[obj.tipo], etapa)
            else:
                txt = "Pegue um item e volte para ajudar (%s%s)" % (NOMES_VITIMA[obj.tipo], etapa)
        s = pygame.Surface((LARGURA - 2 * PAREDE, 26), pygame.SRCALPHA)
        s.fill((10, 12, 22, 190))
        self.tela.blit(s, (PAREDE, ALTURA - PAREDE - 26))
        self.texto(txt, self.f_peq, COR_TEXTO, (LARGURA // 2, ALTURA - PAREDE - 13),
                   centro=True, sombra=False)

    def _desenhar_guia(self):
        """Guia rápido (segure H): tratamento de cada tipo de vítima."""
        rect = pygame.Rect(0, 0, 820, 40 + 28 * len(DECAY))
        rect.center = (LARGURA // 2, ALTURA // 2 + 20)
        self._painel(rect, (10, 12, 26, 240), AMARELO_BRILHO)
        self.texto("GUIA RÁPIDO (segure H)", self.f_media, AMARELO_BRILHO,
                   (rect.centerx, rect.y + 22), centro=True, sombra=False)
        y = rect.y + 48
        for tp in DECAY:
            base = " + ".join(nome_etapa(e) for e in ETAPAS[tp])
            txt = "%s: %s" % (NOMES_VITIMA[tp], base)
            if tp in ETAPAS_GRAVE:
                txt += "   |   grave: " + " > ".join(nome_etapa(e).split(" (")[0] for e in ETAPAS_GRAVE[tp])
            self.texto(txt, self.f_peq, COR_TEXTO, (rect.x + 20, y), sombra=False)
            y += 28

    def _desenhar_hud(self):
        tela = self.tela
        pygame.draw.rect(tela, COR_HUD, (0, 0, LARGURA, ALTURA_HUD))
        pygame.draw.line(tela, (80, 86, 120), (0, ALTURA_HUD - 1), (LARGURA, ALTURA_HUD - 1), 2)

        # Tempo SAMU
        seg = int(math.ceil(self.tempo))
        cor_t = VERMELHO if seg <= 15 and int(self.t * 4) % 2 == 0 else COR_TEXTO
        self.texto("SAMU CHEGA EM", self.f_hud_l, CINZA, (12, 8), sombra=False)
        self.texto("%ds" % seg, self.f_hud_v, cor_t, (12, 24), sombra=False)
        # Pontos
        self.texto("PONTOS", self.f_hud_l, CINZA, (150, 8), sombra=False)
        self.texto(str(self.pontos), self.f_hud_v, COR_TEXTO, (150, 24), sombra=False)
        # Combo
        mult = MULT_COMBO if self.combo >= COMBO_MINIMO else 1.0
        self.texto("COMBO", self.f_hud_l, CINZA, (270, 8), sombra=False)
        txt_c = "%d (x%.1f)" % (self.combo, mult)
        self.texto(txt_c.replace(".", ","), self.f_hud_v,
                   AMARELO_BRILHO if mult > 1 else COR_TEXTO, (270, 24), sombra=False)
        # Item na mão
        self.texto("MÃO", self.f_hud_l, CINZA, (392, 8), sombra=False)
        pygame.draw.rect(tela, (50, 54, 78), (392, 22, 34, 30), border_radius=5)
        pygame.draw.rect(tela, (120, 130, 170), (392, 22, 34, 30), 2, border_radius=5)
        if self.player.item:
            tela.blit(self.minis[self.player.item], (398, 26))
            nome = NOMES_ITEM[self.player.item]
            self.texto(nome, self.f_peq, COR_TEXTO, (432, 30), sombra=False)
        else:
            self.texto("vazia", self.f_peq, CINZA, (432, 30), sombra=False)
        # Barras de estabilidade (até 6 vítimas)
        n = max(1, len(self.vitimas))
        larg_b = min(84, (944 - 566) // n - 6)
        for i, v in enumerate(self.vitimas):
            x = 566 + i * (larg_b + 6)
            self.texto(HUD_NOMES[v.tipo], self.f_hud_l, CINZA, (x, 8), sombra=False)
            pygame.draw.rect(tela, (14, 14, 22), (x, 24, larg_b, 18), border_radius=4)
            if v.estabilizada:
                cor = VERDE
            elif v.estab > 50:
                cor = (240, 200, 60)
            elif v.estab > 25:
                cor = LARANJA
            else:
                cor = VERMELHO
            larg = int((larg_b - 4) * v.estab / 100.0)
            if larg > 0:
                pygame.draw.rect(tela, cor, (x + 2, 26, larg, 14), border_radius=3)
            if v.estabilizada:
                rot = "OK"
            else:
                rot = "%d%%" % int(v.estab)
                if len(v.etapas) > 1:
                    rot += " %d/%d" % (v.etapa, len(v.etapas))
            self.texto(rot, self.f_hud_l, BRANCO, (x + larg_b // 2, 33), centro=True)
        # Nome da fase na parede superior
        self.texto("Fase %d/%d - %s        [H] guia rápido" % (self.fase_idx + 1, len(STAGE_CONFIGS),
                                                             self.cfg["nome"]),
                   self.f_hud_l, COR_TEXTO, (20, ALTURA_HUD + 2), sombra=False)

    def _desenhar_mensagem(self):
        if not self.msg:
            return
        texto, cor, _ = self.msg
        linhas = quebrar_texto(self.f_normal, texto, 740)
        alt = 18 + 26 * len(linhas)
        rect = pygame.Rect(0, 0, 780, alt)
        rect.midtop = (LARGURA // 2, ALTURA_HUD + PAREDE + 8)
        self._painel(rect, (12, 14, 24, 225), cor)
        for i, ln in enumerate(linhas):
            self.texto(ln, self.f_normal, COR_TEXTO, (rect.centerx, rect.y + 22 + i * 26),
                       centro=True, sombra=False)

    # ---- Outras telas ----
    def _estrelas(self, n, centro, raio=26, total=3):
        """Desenha 'total' estrelas, 'n' delas acesas."""
        x0 = centro[0] - (total - 1) * (raio + 6)
        for i in range(total):
            cor = (255, 210, 50) if i < n else (70, 70, 85)
            desenhar_estrela(self.tela, (x0 + i * (2 * raio + 12), centro[1]), raio, cor)

    def _desenhar_pausa(self):
        s = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        s.fill((0, 0, 0, 170))
        self.tela.blit(s, (0, 0))
        self.texto("PAUSADO", self.f_titulo, BRANCO, (LARGURA // 2, 220), centro=True)
        self.texto("ESC ou ENTER - Continuar", self.f_media, COR_TEXTO, (LARGURA // 2, 320), centro=True)
        self.texto("M - Voltar ao menu", self.f_media, CINZA, (LARGURA // 2, 365), centro=True)

    def _desenhar_transicao(self):
        self.tela.blit(self.fundo_menu, (0, 0))
        self._painel(pygame.Rect(130, 70, 700, 460))
        self.texto("FASE %d CONCLUÍDA!" % (self.fase_idx + 1), self.f_grande, VERDE,
                   (LARGURA // 2, 115), centro=True)
        self._estrelas(self.resumo["estrelas"], (LARGURA // 2, 180))
        self.texto("Bônus de tempo (%ds x %d): +%d" % (self.resumo["tempo"], BONUS_POR_SEGUNDO,
                                                       self.resumo["bonus"]),
                   self.f_media, COR_TEXTO, (LARGURA // 2, 245), centro=True)
        self.texto("Pontuação: %d" % self.pontos, self.f_grande, AMARELO_BRILHO,
                   (LARGURA // 2, 300), centro=True)
        dica = DICAS_FASE[min(self.fase_idx, len(DICAS_FASE) - 1)]
        for i, ln in enumerate(quebrar_texto(self.f_normal, dica, 600)):
            self.texto(ln, self.f_normal, COR_TEXTO, (LARGURA // 2, 360 + i * 28), centro=True)
        prox = STAGE_CONFIGS[self.fase_idx + 1]
        self.texto("Próxima: %s (%ds, %d vítimas)" % (prox["nome"], prox["tempo"], len(prox["vitimas"])),
                   self.f_media, CINZA, (LARGURA // 2, 440), centro=True)
        if int(self.t * 2) % 2 == 0:
            self.texto("ENTER - Continuar", self.f_media, BRANCO, (LARGURA // 2, 490), centro=True)

    def _desenhar_vitoria(self):
        self.tela.blit(self.fundo_menu, (0, 0))
        self._painel(pygame.Rect(110, 50, 740, 500))
        self.texto("VITÓRIA!", self.f_titulo, VERDE, (LARGURA // 2, 110), centro=True)
        self.texto("Você ajudou todas as vítimas até o SAMU chegar!", self.f_media, COR_TEXTO,
                   (LARGURA // 2, 180), centro=True)
        # Estrelas por fase
        total = 0
        for i, est in enumerate(self.estrelas_fases):
            cx = LARGURA // 2 + (i - (len(self.estrelas_fases) - 1) / 2.0) * 130
            self._estrelas(est, (int(cx), 262), raio=11)
            self.texto("Fase %d" % (i + 1), self.f_peq, CINZA, (int(cx), 292), centro=True)
            total += est
        self.texto("Estrelas: %d de %d" % (total, 3 * len(STAGE_CONFIGS)), self.f_media,
                   (255, 210, 50), (LARGURA // 2, 335), centro=True)
        self.texto("Pontuação final: %d" % self.pontos, self.f_grande, AMARELO_BRILHO,
                   (LARGURA // 2, 395), centro=True)
        self.texto("Lembre-se: na vida real, ligue 192 (SAMU) primeiro.", self.f_normal, COR_TEXTO,
                   (LARGURA // 2, 455), centro=True)
        if int(self.t * 2) % 2 == 0:
            self.texto("ENTER - Menu", self.f_media, BRANCO, (LARGURA // 2, 505), centro=True)

    def _desenhar_game_over(self):
        self.tela.blit(self.fundo_menu, (0, 0))
        self._painel(pygame.Rect(110, 80, 740, 440), borda=VERMELHO)
        self.texto("GAME OVER", self.f_titulo, VERMELHO, (LARGURA // 2, 150), centro=True)
        if self.causa == "tempo":
            motivo = "O tempo do SAMU acabou!"
        else:
            motivo = "Uma vítima de %s chegou a 0%%!" % NOMES_VITIMA[self.causa].lower()
        self.texto(motivo, self.f_media, COR_TEXTO, (LARGURA // 2, 225), centro=True)
        self.texto("DICA:", self.f_media, AMARELO_BRILHO, (LARGURA // 2, 285), centro=True)
        for i, ln in enumerate(quebrar_texto(self.f_normal, DICAS_GAME_OVER[self.causa], 620)):
            self.texto(ln, self.f_normal, COR_TEXTO, (LARGURA // 2, 322 + i * 28), centro=True)
        self.texto("Pontuação: %d" % self.pontos_inicio_fase, self.f_normal, CINZA,
                   (LARGURA // 2, 420), centro=True)
        if int(self.t * 2) % 2 == 0:
            self.texto("ENTER - Tentar a fase de novo", self.f_media, BRANCO,
                       (LARGURA // 2, 462), centro=True)
        self.texto("ESC - Menu", self.f_peq, CINZA, (LARGURA // 2, 495), centro=True)
