# Exemplo 2: Informações Institucionais, Endereço e Horários

**Cenário:** Cliente pergunta onde fica localizada a loja e os horários de funcionamento.  
**Ferramentas acionadas:** `get_policy_info(topic='endereco')` e `get_policy_info(topic='horario')`  

---

### Transcrição da Conversa

**Cliente:**  
Qual o endereço da loja e até que horas vocês ficam abertos no sábado?

**Agente (Empório da Música):**  
*⚙️ [Tool Call] get_policy_info({'topic': 'endereco'})*  
*⚙️ [Tool Call] get_policy_info({'topic': 'horario'})*  

A nossa loja física fica na **Rua 14 de Maio, 3200 — Centro, Campo Grande - MS** (CEP 79202-333)! 📍

Quanto aos nossos horários de funcionamento:
• **Segunda a Sexta-feira:** das 09:00 às 18:00  
• **Sábado:** das 09:00 às 13:00  
• **Domingos e Feriados:** Fechado  

Nosso telefone fixo é o **(67) 3341-4444** e nosso WhatsApp oficial de atendimento é o **(67) 3321-4500**.

Será um prazer receber sua visita para tomar um café com a gente e testar os instrumentos pessoalmente! Precisa de orientações de como chegar?

