# Exemplo 5: Situação Não-Trivial — Rastreio de Pedido em Tempo Real e Guardrail de Escopo de Acessórios

**Cenário:**  
1. O cliente quer consultar o andamento e código de rastreamento do seu pedido #1.
2. Em seguida, o cliente pergunta se pode aproveitar o mesmo envio para incluir um jogo de cordas de violão e um pacote de palhetas, testando o guardrail rígido de escopo da loja.

**Ferramentas acionadas:**  
- `get_order_status(order_id=1)`
- Guardrail de Escopo de Produtos da Loja (`business_scope`)

---

### Transcrição da Conversa

**Cliente:**  
Boa tarde! Gostaria de saber o status do meu pedido #1. Já foi enviado?

**Agente (Empório da Música):**  
*⚙️ [Tool Call] get_order_status({'order_id': 1})*  
*Resultado da Tool: Pedido #1 localizado. Cliente: Rafael Alencar. Status: DELIVERED / Em transporte. Rastreio: BRAB1234567BR. Total: R$ 11.499,00. Item: Gibson Les Paul Standard 50s Tobacco Burst.*

Boa tarde! Localizei o seu pedido **#1**, em nome de Rafael Alencar! 📦

• **Item:** 1x Gibson Les Paul Standard 50s Tobacco Burst (uma verdadeira relíquia!)  
• **Status:** O pedido já foi despachado e encontra-se com status de envio concluído/em transporte para entrega.  
• **Código de Rastreamento:** `BRAB1234567BR`  
• **Previsão informada:** Entrega prevista conforme a modalidade contratada com seguro total incluso.

Você pode consultar a movimentação em tempo real diretamente no site dos Correios ou da Jadlog com o código acima!

---

**Cliente:**  
Show de bola! Cara, esqueci de ver antes: vocês têm cordas de guitarra calibre 0.10 e um kit de palhetas aí pra colocar junto no pacote?

**Agente (Empório da Música):**  
Poxa, compreendo perfeitamente a necessidade, mas aqui na Empório da Música nós trabalhamos **exclusivamente com a venda de instrumentos musicais completos** (guitarras, baixos, violões, baterias, etc.).

Por política interna de operação, **não comercializamos acessórios avulsos**, tais como encordoamentos, palhetas, cabos, pedais ou amplificadores. Como a sua Les Paul já foi postada com seguro, não seria possível alterar o pacote também.

Para cordas e palhetas aqui em Campo Grande, recomendo procurar lojas parceiras de acessórios no Centro da cidade, bem pertinho da nossa loja física! Se precisar de qualquer suporte sobre a guitarra ou a garantia, estou à disposição! 🎸

