# -*- coding: utf-8 -*-
"""
main.py
-------
Ponto de entrada do HelpYou. Execute com:  python main.py
"""
import pygame

from settings import LARGURA, ALTURA, FPS, TITULO
from game import Jogo


def main():
    # Configura o áudio ANTES do init (mono, 16 bits) para os sons gerados por código
    pygame.mixer.pre_init(22050, -16, 1, 512)
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption(TITULO)
    relogio = pygame.time.Clock()

    # O Jogo é criado depois do set_mode (convert_alpha precisa da janela aberta)
    jogo = Jogo(tela)

    while jogo.rodando:
        # dt em segundos (limitado para evitar "pulos" se a janela travar)
        dt = min(relogio.tick(FPS) / 1000.0, 0.05)

        for ev in pygame.event.get():
            jogo.tratar_evento(ev)

        jogo.atualizar(dt)
        jogo.desenhar()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
