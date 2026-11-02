# Exemplo 1: Consulta de Catálogo por Faixa de Preço

**Cenário:** Cliente busca violões disponíveis em estoque com limite orçamentário de R$ 1.000,00.  
**Ferramenta acionada:** `search_products(query='violão', category='Violões', max_price=1000.0, in_stock_only=True)`  

---

### Transcrição da Conversa

**Cliente:**  
Olá! Quais opções de violões disponíveis custando até R$1000 vocês têm aí na loja?

**Agente (Empório da Música):**  
*⚙️ [Tool Call] search_products({'query': 'violão', 'category': 'Violões', 'max_price': 1000.0, 'in_stock_only': True})*  
*Resultado da Tool: 5 itens encontrados em estoque.*

Encontrei ótimas opções disponíveis no nosso estoque para você dar uma olhada:

• **Yamaha C40 Nylon Natural** — R$ 599.90 (Estoque: 12 unid.)  
• **Yamaha C70 Nylon Natural** — R$ 849.00 (Estoque: 8 unid.)  
• **Tagima Memphis AC-39 Nylon Natural** — R$ 429.90 (Estoque: 15 unid.)  
• **Tagima Memphis AC-39 Nylon Preto** — R$ 429.90 (Estoque: 10 unid.)  
• **Tagima Dallas Aço Eletroacústico Sunburst** — R$ 949.90 (Estoque: 6 unid.)  

Todos com regulagem cuidadosa e opções de pagamento em até 12x sem juros no cartão ou com 5% de desconto à vista via PIX (sobre o preço de tabela)!

Você tem preferência por cordas de aço ou nylon? Se quiser, posso te passar mais detalhes de algum deles! 🎶

