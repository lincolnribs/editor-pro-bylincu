# talking-head (pessoa falando para a câmera)

**Etapas:** todas. Base técnica completa.

- **Preparar:** transcrever todos os takes de fala; separar fala × b-roll pela folha.
- **Plano:** decupagem por frase (o último take completo costuma ser o melhor; nunca cortar no meio da frase; nome da marca nunca cortado). Gancho = a frase mais forte, com movimento em 1–2 s. Texto onde soma, desenhado pelo sentido de cada frase (`../plano/direcao.md`): gancho, número, contraste e virada com desenhos diferentes; legenda discreta só onde não há lettering (se o cliente usa legenda). B-roll nos argumentos. Faixa de texto fora do rosto.
- **Montar:** `ep.py voz --lista takes.txt -o base.mp4 --cortar-silencios --respiro 0.14 --escala 1080x1920` → base + `base.cortes.json`; retranscrever a base e conferir que nenhuma palavra sumiu nem sobrou sílaba solta. Punch-in alternado ligado (`base.punchIn`).
- **Para ficar excelente:** destaque de uma palavra por lettering na cor da marca; CTA ou marca nos últimos 2 s; efeito sobre a pessoa (texto atrás da cabeça, flash só nela) pelo complemento `effects`.
- **Só montar os takes** ("corta os erros e os silêncios", sem motion): mesma decupagem, sem lettering, b-roll nem SFX; punch-in continua.
