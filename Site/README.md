# Tracking de cliques (GTM)

Todos os links e botões clicáveis das 3 páginas receberam uma `class` exclusiva para tracking, sem alterar estilo (inline styles mantidos) ou estrutura do HTML.

## Convenção de nome

```
btn-{página}-{local}-{papel}
```

- **página**: `index`, `newsletter`, `thankyou`
- **local**: onde o elemento está (`nav`, `hero`, `form`, `logo`, `back-home`...)
- **papel**: o que ele representa (`primary`, `secondary`, `cta`, `submit`)

Elementos como o logo entraram no escopo (para medir cliques de retorno à home), mas não precisam de trigger dedicado se não forem relevantes para você.

## Classes por página

### index.html
| Classe | Elemento | Por que rastrear |
|---|---|---|
| `btn-index-logo` | Logo no header | Mede quantos cliques voltam pra home a partir de outra seção |
| `btn-index-nav-recursos` | Nav "Recursos" | Interesse em explorar a oferta antes de converter |
| `btn-index-nav-solucoes` | Nav "Soluções" → `newsletter.html` | Principal ponte entre site e newsletter — indica origem do lead |
| `btn-index-nav-cta` | Nav "Começar agora" | CTA de topo, meça se converte mais que os do hero |
| `btn-index-hero-primary` | Hero "Quero conhecer" | CTA principal — compare taxa de clique vs. o secundário |
| `btn-index-hero-secondary` | Hero "Saiba mais" | CTA de baixo compromisso — sinal de interesse ainda não pronto pra converter |
| `btn-index-form-submit` | Botão "Enviar" (contato) | Evento de conversão do formulário de contato |

### newsletter.html
| Classe | Elemento | Por que rastrear |
|---|---|---|
| `btn-newsletter-logo` | Logo no header | Cliques de saída da página de oferta |
| `btn-newsletter-nav-recursos` | Nav "Recursos" | Volume de quem quer mais contexto antes de assinar |
| `btn-newsletter-nav-inicio` | Nav "Início" | Taxa de abandono da oferta de volta pro site |
| `btn-newsletter-nav-cta` | Nav "Se inscrever" | CTA de topo — compare com o do hero/rodapé |
| `btn-newsletter-hero-primary` | Hero "Quero me inscrever" | Intenção de assinatura direto do topo |
| `btn-newsletter-hero-secondary` | Hero "Saiba mais" | Quem precisa ver benefícios antes de decidir |
| `btn-newsletter-form-submit` | Botão "Enviar" (inscrição) | **Evento de conversão principal** — o lead da newsletter |

### thank-you.html
| Classe | Elemento | Por que rastrear |
|---|---|---|
| `btn-thankyou-logo` | Logo no header | Engajamento pós-conversão |
| `btn-thankyou-back-home` | "Voltar ao início" | Mede se o lead recém-convertido continua navegando no site |

## Como configurar no GTM

1. Crie uma tag **Click - All Elements**.
2. Em **Trigger**, use **Click Classes** → `contains` → a classe desejada (ou `matches CSS selector` para várias de uma vez, ex: `[class^="btn-newsletter"]` pega todos os cliques da página de newsletter).
3. Recomendo criar **um trigger por classe** para eventos de conversão (`btn-newsletter-form-submit`, `btn-index-form-submit`) e um trigger genérico por prefixo de página para os demais, se quiser menos ruído no relatório.
