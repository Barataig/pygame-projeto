# HelpYou

Jogo 2D top-down de primeiros socorros (Python 3.11 + Pygame 2.6.1).
Estabilize as vítimas com o item certo e saia pela porta verde antes do SAMU chegar.

## Como rodar

1. Coloque os 5 arquivos `.py` (`settings.py`, `sprites.py`, `entities.py`, `game.py`, `main.py`) na mesma pasta.
2. (Opcional) Coloque também a imagem `itens.png` nessa pasta.
3. Instale o Pygame e execute:

```
pip install pygame==2.6.1
python main.py
```

Sem `itens.png` o jogo funciona normalmente, usando sprites desenhados por código.
Não há outras dependências além de `pygame` e da biblioteca padrão (`math`, `random`, `array`).

## Controles

| Tecla | Ação |
|---|---|
| WASD / Setas | Mover |
| E / Espaço | Coletar item (toque) ou segurar (pia 2,0s / vítima 2,5s) |
| Q | Largar o item da mão |
| H (segurar) | Guia rápido de tratamentos |
| ESC | Pausar (no menu: sair) |
| Enter | Confirmar |

## Regras

- A mão carrega 1 item. **Pano Limpo + Pia = Pano Úmido** (segure E por 2,0s na pia).
- **5 fases com vários cômodos** ligados por portas (paredes sólidas): Cozinha e Sala (75s), Casa Térrea (90s), Apartamento (100s), Escritório (100s) e Casa Grande (110s). As pias, os itens e as vítimas ficam espalhados: planeje o trajeto.
- Vítimas (queda de estabilidade por segundo):

| Vítima | Queda | Tratamento (grave = 2 etapas) |
|---|---|---|
| Queimadura | -2,0%/s | Pano Úmido. Grave: depois Pano Limpo |
| Sangramento | -2,5%/s | Gaze / Pano Limpo. Grave: depois Atadura |
| Fratura | -1,5%/s | Tala Rígida (sólida, não pode ser empurrada). Grave: depois Atadura |
| Tontura | -1,0%/s | Água |
| Engasgo | -2,8%/s | MÃOS LIVRES (largue o item com Q): segure E por 3s (Heimlich) |
| Desmaio | -1,3%/s | Manta Térmica |

- Vítima grave: cada etapa concluída reduz a queda pela metade e devolve um pouco de estabilidade.
- **Agravamento** (fases 3 a 5): de tempos em tempos uma vítima piora e a barra dela cai mais rápido (aparece um "!" vermelho).
- Nas fases 1 a 3 aparece sobre a vítima o item que ela precisa; nas fases 4 e 5 não. Segure **H** a qualquer momento para ver o guia rápido.
- Distratores (Manteiga, Pasta de Dente, Gelo): -10s, flash vermelho, combo zerado e texto educativo.
- Item errado que não é distrator: combo zerado e dica na tela.
- +100 pontos por vítima; com 2 acertos seguidos o multiplicador x1,5 é ativado. Erro zera o combo.
- Estabilidade em 0% ou tempo em 0 = Game Over (com dica). A porta verde abre quando todas as vítimas estão estabilizadas. Sobrar tempo ao sair dá bônus e até 3 estrelas por fase.

## Como deve ser o `itens.png`

- Uma **grade regular** de células iguais: **8 colunas x 7 linhas** (como na imagem de itens médicos usada no projeto).
- Fundo branco ou transparente. O jogo remove o fundo conectado às bordas de cada célula (o branco interno dos itens é preservado), recorta no conteúdo e redimensiona para 32x32.
- O tamanho de cada célula é calculado a partir do tamanho real da imagem (`largura / 8`, `altura / 7`), então qualquer resolução funciona.

Mapeamento usado (linha, coluna, contando a partir de 1; fica em `CELULAS_ITENS` no `settings.py`):

| Item do jogo | Sprite | Linha | Coluna |
|---|---|---|---|
| Pano Limpo | Gaze | 2 | 1 |
| Gelo | Bolsa de gelo | 4 | 1 |
| Tala Rígida | Tesoura | 5 | 1 |
| Água | Bolsa de soro | 7 | 2 |
| Manteiga | Pote de remédio | 3 | 4 |
| Pasta de Dente | Pomada | 3 | 1 |
| Atadura | Rolo de atadura | 2 | 2 |
| Manta Térmica | Folha prateada | 4 | 6 |

O Pano Úmido é gerado automaticamente a partir do Pano Limpo (tingido de azul, com gotas).

Para ajustar um recorte, edite `CELULAS_ITENS` (célula de cada item) ou `SHEET_COLUNAS`, `SHEET_LINHAS` e `SHEET_MARGEM` no `settings.py`. A função `calcular_rects_itens()` gera os `pygame.Rect` usados no recorte.

## Estrutura

| Arquivo | Conteúdo |
|---|---|
| `settings.py` | Constantes, fases (`STAGE_CONFIGS`), `DECAY`, textos educativos, recortes da spritesheet |
| `sprites.py` | Player/vítimas/ícones procedurais, `load_spritesheet()` com fallback |
| `entities.py` | `Player`, `Victim`, `Item`, `Station` (pia), `Door` |
| `game.py` | Máquina de estados, HUD, lógica, pontuação, sons |
| `main.py` | Loop principal (60 FPS) |
