# -*- coding: utf-8 -*-
"""
entities.py
-----------
Classes das entidades do HelpYou: Player, Victim, Item, Station (Pia) e Door.
Também contém desenhar_brilho(): o brilho amarelo pulsante (onda senoidal)
usado em tudo que é interativo.
"""
import math
import random
import pygame

from settings import (AREA_JOGO, VEL_PLAYER, DECAY, VERDE, VERMELHO, AMARELO_BRILHO,
                      LARANJA, BRANCO, ETAPAS, ETAPAS_GRAVE, MAO_VAZIA)


# ----------------------------------------------------------------------------
# BRILHO PULSANTE
# ----------------------------------------------------------------------------
def desenhar_brilho(tela, rect, t, raio_extra=8):
    """Desenha um brilho amarelo cujo raio/alfa pulsam com uma onda senoidal."""
    onda = (math.sin(t * 4.0) + 1.0) / 2.0              # 0..1
    raio = int(max(rect.w, rect.h) / 2 + raio_extra + 5 * onda)
    alfa = int(55 + 110 * onda)
    s = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
    pygame.draw.circle(s, (*AMARELO_BRILHO, alfa), (raio, raio), raio)
    pygame.draw.circle(s, (255, 246, 160, min(255, alfa + 40)), (raio, raio), int(raio * 0.62))
    tela.blit(s, (rect.centerx - raio, rect.centery - raio))


def _sombra(tela, cx, cy, w=26, h=10):
    """Sombra elíptica sob personagens/itens."""
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0, 0, 0, 70), (0, 0, w, h))
    tela.blit(s, (cx - w // 2, cy - h // 2))


# ----------------------------------------------------------------------------
# PLAYER
# ----------------------------------------------------------------------------
class Player:
    """Jogador (socorrista de camisa azul). Carrega no máximo 1 item."""

    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)          # centro (float, movimento suave)
        self.rect = pygame.Rect(0, 0, 20, 20)    # hitbox
        self.rect.center = (round(x), round(y))
        self.direcao = "baixo"
        self.item = None                         # slot de mão = 1 item
        self.anim = 0.0
        self.movendo = False

    def mover(self, dt, teclas, solidos):
        """Move com colisão por eixo contra a lista de retângulos 'solidos'."""
        dx = int(teclas[pygame.K_d] or teclas[pygame.K_RIGHT]) - int(teclas[pygame.K_a] or teclas[pygame.K_LEFT])
        dy = int(teclas[pygame.K_s] or teclas[pygame.K_DOWN]) - int(teclas[pygame.K_w] or teclas[pygame.K_UP])
        vet = pygame.Vector2(dx, dy)
        self.movendo = vet.length_squared() > 0
        if not self.movendo:
            self.anim = 0.0
            return
        vet = vet.normalize()
        if abs(vet.x) >= abs(vet.y):
            self.direcao = "direita" if vet.x > 0 else "esquerda"
        else:
            self.direcao = "baixo" if vet.y > 0 else "cima"
        self.anim += dt * 9.0

        metade = self.rect.w // 2
        # --- eixo X ---
        self.pos.x += vet.x * VEL_PLAYER * dt
        self.pos.x = max(AREA_JOGO.left + metade, min(AREA_JOGO.right - metade, self.pos.x))
        self.rect.centerx = round(self.pos.x)
        for s in solidos:
            if self.rect.colliderect(s):
                if vet.x > 0:
                    self.rect.right = s.left
                elif vet.x < 0:
                    self.rect.left = s.right
                self.pos.x = self.rect.centerx
        # --- eixo Y ---
        self.pos.y += vet.y * VEL_PLAYER * dt
        self.pos.y = max(AREA_JOGO.top + metade, min(AREA_JOGO.bottom - metade, self.pos.y))
        self.rect.centery = round(self.pos.y)
        for s in solidos:
            if self.rect.colliderect(s):
                if vet.y > 0:
                    self.rect.bottom = s.top
                elif vet.y < 0:
                    self.rect.top = s.bottom
                self.pos.y = self.rect.centery

    def desenhar(self, tela, frames, minis):
        """Desenha o player e o item que ele está segurando."""
        passo = int(self.anim) % 2 if self.movendo else 0
        _sombra(tela, self.rect.centerx, self.rect.bottom - 1)
        tela.blit(frames[(self.direcao, passo)],
                  (self.rect.centerx - 16, self.rect.centery - 20))
        if self.item is not None:
            mini = minis[self.item]
            tela.blit(mini, (self.rect.centerx + 5, self.rect.centery - 6))


# ----------------------------------------------------------------------------
# VÍTIMA
# ----------------------------------------------------------------------------
class Victim:
    """Vítima com barra de estabilidade que cai com o tempo.

    Pode exigir VÁRIAS ETAPAS (itens em sequência). Cada etapa concluída reduz a
    velocidade de queda; um agravamento aumenta a velocidade de queda.
    """

    def __init__(self, tipo, x, y, grave=False):
        self.tipo = tipo
        self.grave = grave
        self.rect = pygame.Rect(0, 0, 28, 28)
        self.rect.center = (x, y)
        self.estab = 100.0
        self.estabilizada = False
        self.fase = random.random() * 6.28
        # Sequência de itens exigida (grave = 2 etapas, quando existir)
        if grave and tipo in ETAPAS_GRAVE:
            self.etapas = list(ETAPAS_GRAVE[tipo])
        else:
            self.etapas = list(ETAPAS[tipo])
        self.etapa = 0
        self.mult_decay = 1.0        # multiplicador da queda (etapas reduzem, agravos aumentam)
        self.alerta = 0.0            # tempo restante do ícone "!" de agravamento

    @property
    def solido(self):
        """Fratura NÃO pode ser empurrada: colisão sólida para o player."""
        return self.tipo == "fratura"

    @property
    def necessario(self):
        """Item (ou MAO_VAZIA) exigido na etapa atual."""
        return self.etapas[min(self.etapa, len(self.etapas) - 1)]

    def atualizar(self, dt):
        if self.alerta > 0:
            self.alerta = max(0.0, self.alerta - dt)
        if not self.estabilizada:
            self.estab = max(0.0, self.estab - DECAY[self.tipo] * self.mult_decay * dt)

    def desenhar(self, tela, sprite, icone, icone_ok, t, dica=None, icone_alerta=None):
        """'dica' = Surface do item necessário (mostrada só nas primeiras fases)."""
        cx, cy = self.rect.center
        _sombra(tela, cx, self.rect.bottom - 1)
        tela.blit(sprite, (cx - 16, cy - 20))
        # Ícone flutuante (balança com seno)
        flut = math.sin(t * 3.0 + self.fase) * 3
        ic = icone_ok if self.estabilizada else icone
        tela.blit(ic, (cx - 14, cy - 54 + flut))
        # Balão com o item necessário (dica das primeiras fases)
        if dica is not None and not self.estabilizada:
            bal = pygame.Rect(cx + 14, cy - 56 + int(flut), 28, 28)
            pygame.draw.rect(tela, (245, 245, 250), bal, border_radius=7)
            pygame.draw.rect(tela, (60, 70, 110), bal, 2, border_radius=7)
            tela.blit(dica, dica.get_rect(center=bal.center))
        # Alerta de agravamento
        if self.alerta > 0 and icone_alerta is not None and int(t * 6) % 2 == 0:
            tela.blit(icone_alerta, (cx - 44, cy - 52 + flut))
        # Mini barra de estabilidade
        pygame.draw.rect(tela, (20, 20, 28), (cx - 19, cy + 17, 38, 7), border_radius=2)
        if self.estabilizada:
            cor = VERDE
        elif self.estab > 50:
            cor = (240, 200, 60)
        else:
            cor = VERMELHO
        larg = int(36 * self.estab / 100.0)
        if larg > 0:
            pygame.draw.rect(tela, cor, (cx - 18, cy + 18, larg, 5), border_radius=2)
        # Pontinhos das etapas (vítimas com tratamento em 2 passos)
        n = len(self.etapas)
        if n > 1:
            for i in range(n):
                px = cx - (n - 1) * 5 + i * 10
                feito = self.estabilizada or i < self.etapa
                pygame.draw.circle(tela, VERDE if feito else (40, 44, 60), (px, cy + 30), 4)
                pygame.draw.circle(tela, BRANCO, (px, cy + 30), 4, 1)


# ----------------------------------------------------------------------------
# ITEM
# ----------------------------------------------------------------------------
class Item:
    """Item no chão que pode ser coletado."""

    def __init__(self, tipo, x, y):
        self.tipo = tipo
        self.rect = pygame.Rect(0, 0, 28, 28)
        self.rect.center = (x, y)
        self.fase = random.random() * 6.28

    def desenhar(self, tela, sprite, t):
        flut = math.sin(t * 3.0 + self.fase) * 2
        _sombra(tela, self.rect.centerx, self.rect.centery + 13, 22, 8)
        tela.blit(sprite, (self.rect.centerx - 16, self.rect.centery - 16 + flut))


# ----------------------------------------------------------------------------
# PIA (STATION)
# ----------------------------------------------------------------------------
class Station:
    """Pia: Pano Limpo + Pia (segurar E por 2,0s) = Pano Úmido."""

    def __init__(self, rect):
        self.rect = pygame.Rect(rect)

    def desenhar(self, tela, ativa=False):
        r = self.rect
        pygame.draw.rect(tela, (0, 0, 0), r.move(3, 4), border_radius=5)
        pygame.draw.rect(tela, (190, 200, 212), r, border_radius=5)
        pygame.draw.rect(tela, (235, 240, 248), (r.x, r.y, r.w, 7), border_radius=5)
        bacia = r.inflate(-16, -16)
        bacia.y += 3
        pygame.draw.rect(tela, (86, 128, 172), bacia, border_radius=7)
        pygame.draw.rect(tela, (60, 98, 140), bacia, 2, border_radius=7)
        # Torneira
        pygame.draw.rect(tela, (150, 155, 168), (r.centerx - 3, r.y + 3, 6, 12), border_radius=2)
        pygame.draw.rect(tela, (150, 155, 168), (r.centerx - 8, r.y + 3, 16, 4), border_radius=2)
        if ativa:  # fio d'água enquanto o pano é umedecido
            pygame.draw.rect(tela, (150, 210, 255), (r.centerx - 1, r.y + 15, 3, 12))


# ----------------------------------------------------------------------------
# PORTA
# ----------------------------------------------------------------------------
class Door:
    """Porta verde de saída: só abre quando todas as vítimas estão estabilizadas."""

    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.aberta = False

    @property
    def gatilho(self):
        """Área em que o player precisa encostar para sair."""
        return self.rect.inflate(30, 0)

    def desenhar(self, tela, t):
        r = self.rect
        if self.aberta:
            onda = (math.sin(t * 5.0) + 1) / 2
            cor = (60 + int(40 * onda), 220, 100)
            borda = (20, 120, 60)
        else:
            cor = (58, 96, 72)
            borda = (30, 50, 40)
        pygame.draw.rect(tela, borda, r.inflate(6, 6), border_radius=3)
        pygame.draw.rect(tela, cor, r, border_radius=3)
        pygame.draw.rect(tela, borda, (r.x + 3, r.y + 6, r.w - 6, r.h - 12), 1)
        if not self.aberta:
            # cadeado
            pygame.draw.rect(tela, (200, 200, 90), (r.centerx - 4, r.centery - 3, 8, 7))
            pygame.draw.arc(tela, (200, 200, 90), (r.centerx - 4, r.centery - 9, 8, 10), 0, math.pi, 2)
        else:
            # seta indicando saída
            pygame.draw.polygon(tela, BRANCO, [(r.centerx - 4, r.centery - 6),
                                               (r.centerx + 4, r.centery),
                                               (r.centerx - 4, r.centery + 6)])
