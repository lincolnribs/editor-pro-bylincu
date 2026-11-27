# Complementos (plugin opcional `editor-pro-motion`)

Só entram quando o vídeo pede e o usuário escolhe. Nunca carregar um complemento sem passar pelo menu.

## Menu (na etapa plano, depois de entender o vídeo)
1. Confira se o plugin está instalado (as skills `motionmaxxing`, `pixel2motion`, `effects` aparecem na lista de skills). Se não estiver, diga em uma linha que existe e como instalar (`/plugin install editor-pro-motion@bylincu`), e siga sem ele.
2. Mostre **só os que combinam com este vídeo**, numerados, cada um com o que faz e em que cena entra. Ex.:
   ```
   Complementos que combinam com este vídeo:
   1. motionmaxxing — abertura em plano contínuo, sem corte, câmera estilo After Effects (c01, 0–3 s)
   2. pixel2motion — logo do cliente se desenhando no fecho (c09)
   Escolha por número ou "nenhum".
   ```
3. Grave a escolha: `ep.py set <pasta> complementos '["motionmaxxing"]'` (ou `[]`). Sem escolha, nada de complemento.

| Complemento | Quando oferecer | O que entrega |
|---|---|---|
| `motionmaxxing` | O plano tem uma tela de motion pedida (abertura, explicação de produto, "plano contínuo") | Um MP4 em plano contínuo, sem corte, com câmera estilo After Effects |
| `pixel2motion` | Fecho com a logo do cliente e só existe PNG/JPG; ícones animados | `logo.svg` limpo + coreografia (`motion_spec.md`) |
| `effects` | Talking head com momento de destaque: flash só na pessoa antes do fundo mudar, palavra gigante atrás da cabeça | Trecho da base com o efeito, mesmo áudio e mesma duração |

## Ponte para o motor (na etapa montar)
As regras do Editor Pro valem por cima das do complemento: identidade do cliente, margens, rosto livre, curva 65/65, sem dado não confirmado. O som é sempre da etapa som (renderizar o complemento sem áudio).

- **motionmaxxing:** é o único motor de motion. Trabalhe em `_CLAUDE/motion/<cena>/`, com 1080x1920 e 30 fps (`render.mjs ... --width 1080 --height 1920 --fps 30`, sem `--audio`). Use cores e fontes do perfil do cliente, não as do complemento. O MP4 vai para `_CLAUDE/edicao/media/motion/<cena>.mp4` e entra no roteiro como `clipes` (sem fala) ou `broll` (por cima da fala), com transição na entrada e na saída. Um plano só: nada de corte dentro dele.
- **pixel2motion:** use o `logo.svg` e a coreografia do `motion_spec.md` para escrever a peça `LogoAnimado` em `src/extras.tsx` (mesmas curvas e tempos, em múltiplos de U), e use-a no `fecho` ou em `pecas`. Assim tudo fica no motor, sem vídeo com transparência. Guarde o SVG e a peça no kit do cliente.
- **effects:** rode sobre a base já limpa (`_CLAUDE/edicao/media/base.mp4`), só na janela do efeito (1,5–4 s), e salve como `base-fx.mp4`. A duração e o áudio não mudam: troque `base.arquivo` no roteiro. No Windows o Python dele é `.venv\Scripts\python.exe`. Confira no quadro que o efeito não cobre o rosto nem o texto.

Fora do menu, se o usuário pedir um complemento pelo nome, use-o seguindo esta ponte.
