"""Cliente desacoplado de LLMs com suporte a Gemini, OpenAI, Groq, Ollama e Mock para testes."""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class LLMClient:
    """Interface unificada para provedores de LLM com suporte a Tool Calling."""

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.provider = (provider or os.getenv("LLM_PROVIDER") or "gemini").lower()
        self.model = model or os.getenv("LLM_MODEL") or self._default_model_for_provider(self.provider)
        self.api_key = api_key or self._get_api_key_for_provider(self.provider)

    def _default_model_for_provider(self, provider: str) -> str:
        defaults = {
            "gemini": "gemini-2.5-flash",
            "openai": "gpt-4o-mini",
            "groq": "llama-3.3-70b-versatile",
            "ollama": "llama3",
            "mock": "mock-musician-v1",
        }
        return defaults.get(provider, "gemini-2.5-flash")

    def _get_api_key_for_provider(self, provider: str) -> Optional[str]:
        if provider == "gemini":
            return os.getenv("GEMINI_API_KEY")
        if provider in ("openai", "groq"):
            return os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")
        return None

    def call(
        self,
        messages: List[Dict[str, Any]],
        tools_schemas: List[Dict[str, Any]],
        system_instruction: str,
    ) -> Dict[str, Any]:
        """Executa uma rodada de geração com o modelo selecionado."""
        if self.provider == "gemini" and self.api_key:
            try:
                return self._call_gemini(messages, tools_schemas, system_instruction)
            except Exception as e:
                logger.warning(f"Falha ao chamar API Gemini ({e}). Alternando para mock.")
                return self._call_mock(messages, tools_schemas, system_instruction)

        elif self.provider in ("openai", "groq") and self.api_key:
            try:
                return self._call_openai(messages, tools_schemas, system_instruction)
            except Exception as e:
                logger.warning(f"Falha ao chamar API OpenAI/Groq ({e}). Alternando para mock.")
                return self._call_mock(messages, tools_schemas, system_instruction)

        elif self.provider == "ollama":
            try:
                return self._call_ollama(messages, tools_schemas, system_instruction)
            except Exception as e:
                logger.warning(f"Falha ao chamar Ollama ({e}). Alternando para mock.")
                return self._call_mock(messages, tools_schemas, system_instruction)

        # Provedor Mock padrão (funciona 100% offline sem chaves de API externas)
        return self._call_mock(messages, tools_schemas, system_instruction)

    def _call_gemini(
        self,
        messages: List[Dict[str, Any]],
        tools_schemas: List[Dict[str, Any]],
        system_instruction: str,
    ) -> Dict[str, Any]:
        """Chamada nativa utilizando a biblioteca google-genai."""
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=self.api_key)

        # Converte schemas de ferramentas para formato Gemini
        gemini_tools = []
        for schema in tools_schemas:
            gemini_tools.append(
                types.Tool(
                    function_declarations=[
                        types.FunctionDeclaration(
                            name=schema["name"],
                            description=schema["description"],
                            parameters=schema.get("parameters"),
                        )
                    ]
                )
            )

        # Monta histórico de conteúdos
        contents = []
        for msg in messages:
            role = msg.get("role")
            if role == "system":
                continue
            gemini_role = "user" if role in ("user", "tool") else "model"
            content = msg.get("content", "")
            contents.append(types.Content(role=gemini_role, parts=[types.Part.from_text(text=str(content))]))

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=gemini_tools if gemini_tools else None,
            temperature=0.2,
        )

        response = client.models.generate_content(
            model=self.model,
            contents=contents,
            config=config,
        )

        # Verifica se o modelo solicitou chamada de ferramenta
        if response.function_calls:
            calls = []
            for fc in response.function_calls:
                calls.append({"name": fc.name, "arguments": dict(fc.args)})
            return {"type": "tool_calls", "tool_calls": calls}

        return {"type": "message", "content": response.text or ""}

    def _call_openai(
        self,
        messages: List[Dict[str, Any]],
        tools_schemas: List[Dict[str, Any]],
        system_instruction: str,
    ) -> Dict[str, Any]:
        """Chamada compatível com OpenAI e Groq."""
        import openai

        base_url = "https://api.groq.com/openai/v1" if self.provider == "groq" else None
        client = openai.OpenAI(api_key=self.api_key, base_url=base_url)

        openai_messages = [{"role": "system", "content": system_instruction}]
        for m in messages:
            openai_messages.append({"role": m["role"], "content": str(m["content"])})

        openai_tools = [
            {"type": "function", "function": s}
            for s in tools_schemas
        ]

        response = client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            tools=openai_tools if openai_tools else None,
            temperature=0.2,
        )

        msg = response.choices[0].message
        if msg.tool_calls:
            calls = []
            for tc in msg.tool_calls:
                calls.append({
                    "name": tc.function.name,
                    "arguments": json.loads(tc.function.arguments),
                })
            return {"type": "tool_calls", "tool_calls": calls}

        return {"type": "message", "content": msg.content or ""}

    def _call_ollama(
        self,
        messages: List[Dict[str, Any]],
        tools_schemas: List[Dict[str, Any]],
        system_instruction: str,
    ) -> Dict[str, Any]:
        """Chamada local Ollama via endpoint OpenAI compatível."""
        import openai

        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        client = openai.OpenAI(base_url=base_url, api_key="ollama")

        openai_messages = [{"role": "system", "content": system_instruction}]
        for m in messages:
            openai_messages.append({"role": m["role"], "content": str(m["content"])})

        response = client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            temperature=0.2,
        )
        return {"type": "message", "content": response.choices[0].message.content or ""}

    def _call_mock(
        self,
        messages: List[Dict[str, Any]],
        tools_schemas: List[Dict[str, Any]],
        system_instruction: str,
    ) -> Dict[str, Any]:
        """Motor mock inteligente para testes automatizados offline e demonstração consistente."""
        last_msg = messages[-1] if messages else {}

        # Se a última mensagem for retorno de ferramenta (role='tool'), sintetiza a resposta final
        if last_msg.get("role") == "tool":
            tool_name = last_msg.get("tool_name", "")
            tool_result = last_msg.get("content", {})
            return self._synthesize_mock_response(tool_name, tool_result, messages)

        # Se a última mensagem veio do usuário, decide se aciona ferramenta ou responde diretamente
        user_text = str(last_msg.get("content", "")).lower()

        # 1. Guardrail de escopo de acessórios
        if any(acc in user_text for acc in ["corda", "palheta", "cabo", "pedal", "amplificador", "case", "bag", "afinador"]):
            return {
                "type": "message",
                "content": (
                    "Olá! Tudo bem? Aqui na Empório da Música nós trabalhamos exclusivamente com a venda dos instrumentos "
                    "musicais em si (violões, guitarras, baixos, teclados, baterias, etc.). Não comercializamos acessórios, "
                    "cordas, palhetas, cabos ou amplificadores. Recomendamos buscar em lojas especializadas de acessórios aqui em Campo Grande!"
                ),
            }

        # 2. Informações institucionais / Endereço / Horário
        if any(k in user_text for k in ["endereco", "endereço", "onde fica", "localiza"]):
            return {
                "type": "tool_calls",
                "tool_calls": [{"name": "get_policy_info", "arguments": {"topic": "endereco"}}],
            }

        if any(k in user_text for k in ["horario", "horário", "aberto", "fecha", "expediente"]):
            return {
                "type": "tool_calls",
                "tool_calls": [{"name": "get_policy_info", "arguments": {"topic": "horario"}}],
            }

        # 3. Políticas de Devolução / Arrependimento / Garantia
        if any(k in user_text for k in ["devolver", "arrepend", "troca", "defeito", "garantia"]):
            return {
                "type": "tool_calls",
                "tool_calls": [{"name": "get_policy_info", "arguments": {"topic": "arrependimento"}}],
            }

        # 4. Status de pedido
        match_order = re.search(r"(?:pedido|order)\s*(?:#|n[ºo]?\s*)?(\d+)", user_text)
        if match_order:
            order_id = int(match_order.group(1))
            return {
                "type": "tool_calls",
                "tool_calls": [{"name": "get_order_status", "arguments": {"order_id": order_id}}],
            }

        # 5. Consulta específica de Takamine GD20
        if "takamine" in user_text or "gd20" in user_text:
            return {
                "type": "tool_calls",
                "tool_calls": [{"name": "get_product_details", "arguments": {"product_identifier": "Takamine GD20"}}],
            }

        # 6. Busca por violões ou faixa de preço
        match_price = re.search(r"(?:at[ée]|abaixo de|menos de)\s*(?:r\$)?\s*(\d+)", user_text)
        max_price = float(match_price.group(1)) if match_price else None

        if "viol" in user_text:
            return {
                "type": "tool_calls",
                "tool_calls": [
                    {
                        "name": "search_products",
                        "arguments": {
                            "query": "violão",
                            "category": "Violões",
                            "max_price": max_price,
                            "in_stock_only": True,
                        },
                    }
                ],
            }

        # Busca genérica de instrumentos
        if any(inst in user_text for inst in ["guitarra", "baixo", "teclado", "bateria", "piano", "ukulele", "flauta"]):
            inst_query = next(i for i in ["guitarra", "baixo", "teclado", "bateria", "piano", "ukulele", "flauta"] if i in user_text)
            return {
                "type": "tool_calls",
                "tool_calls": [
                    {
                        "name": "search_products",
                        "arguments": {"query": inst_query, "max_price": max_price, "in_stock_only": True},
                    }
                ],
            }

        # Saudação geral
        return {
            "type": "message",
            "content": (
                "Olá! Seja muito bem-vindo à Empório da Música! 🎸 Sou o consultor virtual da loja aqui de Campo Grande. "
                "Como posso te ajudar hoje? Posso consultar preços, disponibilidade de instrumentos, status do seu pedido ou tirar dúvidas sobre nossas políticas de entrega e garantia!"
            ),
        }

    def _synthesize_mock_response(
        self,
        tool_name: str,
        result: Any,
        messages: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Gera resposta no tom amigável e musical a partir dos dados recuperados da ferramenta."""
        if tool_name == "search_products":
            items = result if isinstance(result, list) else []
            if not items:
                return {
                    "type": "message",
                    "content": "Poxa, no momento não encontrei opções disponíveis com esses critérios exatos no nosso estoque. Gostaria de dar uma olhada em instrumentos similares em outra faixa de valor?",
                }
            lines = ["Encontrei ótimas opções disponíveis no nosso estoque para você dar uma olhada:"]
            for it in items:
                preco = f"R$ {it.get('effective_price_brl', it.get('price_brl')):.2f}"
                promo_note = f" (Em promoção: {it.get('promo_name')}!)" if it.get("promo_name") else ""
                lines.append(f"• **{it['name']}** — {preco}{promo_note} (Estoque: {it['stock_quantity']} unid.)")
            lines.append("\nTodos com regulagem cuidadosa e opções de pagamento em até 12x sem juros ou 5% de desconto no PIX à vista!")
            return {"type": "message", "content": "\n".join(lines)}

        if tool_name == "get_product_details":
            if not result:
                return {
                    "type": "message",
                    "content": "Não encontrei esse modelo cadastrado em nossa base. Tem certeza do nome ou modelo?",
                }
            p = result
            preco = f"R$ {p.get('effective_price_brl', p.get('price_brl')):.2f}"
            promo = f"\n🔥 **Aproveite: item em promoção ({p.get('promo_name')})!**" if p.get("discount_percent") else ""
            specs_desc = ""
            if isinstance(p.get("specs"), dict):
                specs = p["specs"]
                specs_desc = f"\nFicha técnica: Tampo em {specs.get('top', 'Madeira nobre')}, laterais/fundo em {specs.get('back_sides', 'Nato/Rosewood')} e cordas de {specs.get('strings', 'aço')}."

            return {
                "type": "message",
                "content": (
                    f"O **{p['name']}** está custando **{preco}**.{promo}"
                    f"{specs_desc}\n\nTemos **{p['stock_quantity']} unidades disponíveis** em estoque. "
                    f"Aceitamos parcelamento em até 12x sem juros no cartão ou 5% de desconto à vista via PIX (sobre preço de tabela). "
                    f"Quer garantir o seu ou tem alguma dúvida sobre a entrega aqui em Campo Grande ou para outras cidades?"
                ),
            }

        if tool_name == "get_policy_info":
            secao = result.get("secao", "")
            detalhes = result.get("detalhes", {})

            if "Trocas" in secao or "arrepend" in str(result).lower():
                return {
                    "type": "message",
                    "content": (
                        "Com certeza! Se a sua compra foi realizada online, você tem até **7 (sete) dias corridos** após o recebimento "
                        "do produto para solicitar a devolução por arrependimento, sem precisar de justificativa (conforme o Art. 49 do CDC). "
                        "O produto deve estar na embalagem original, sem sinais de uso e com todos os acessórios/manuais. "
                        "O frete de retorno é por nossa conta e o estorno integral é processado em até 10 dias úteis!"
                    ),
                }

            if "Endereço" in secao or "store_info" in str(result):
                info = detalhes if isinstance(detalhes, dict) else result.get("informacoes_gerais", {}).get("loja", {})
                return {
                    "type": "message",
                    "content": (
                        f"A nossa loja física fica na **{info.get('address', 'Rua 14 de Maio, 3200 — Centro, Campo Grande - MS')}**! 📍\n"
                        f"Nosso telefone fixo é {info.get('phone', '(67) 3341-4444')} e atendemos pelo WhatsApp no {info.get('whatsapp', '(67) 3321-4500')}. "
                        "Será um prazer receber sua visita para tomar um café e testar os instrumentos!"
                    ),
                }

            if "Horário" in secao:
                return {
                    "type": "message",
                    "content": (
                        "Nosso horário de atendimento é:\n"
                        "• **Segunda a Sexta-feira:** das 09:00 às 18:00\n"
                        "• **Sábados:** das 09:00 às 13:00\n"
                        "• **Domingos e Feriados:** Fechado.\n"
                        "Se nos mandar mensagem fora desse horário, responderemos logo na abertura do próximo dia útil!"
                    ),
                }

            if "Escopo" in secao:
                return {
                    "type": "message",
                    "content": (
                        "A Empório da Música atua exclusivamente na venda de instrumentos musicais. "
                        "Não vendemos acessórios como cordas avulsas, palhetas, cabos ou amplificadores. "
                        "Podemos te orientar com prazer em relação aos instrumentos do nosso catálogo!"
                    ),
                }

        if tool_name == "get_order_status":
            if not result.get("found"):
                return {"type": "message", "content": result.get("message", "Pedido não localizado.")}
            items_str = ", ".join([f"{it['quantity']}x {it['product_name']}" for it in result.get("items", [])])
            return {
                "type": "message",
                "content": (
                    f"Localizei seu pedido **#{result['order_id']}** em nome de {result.get('customer_name')}!\n"
                    f"• **Status:** {result['status'].upper()}\n"
                    f"• **Itens:** {items_str}\n"
                    f"• **Código de Rastreamento:** `{result.get('tracking_code', 'Em processamento')}`\n"
                    f"• **Previsão de Entrega:** {result.get('estimated_delivery', 'A calcular')}\n"
                    f"Você pode acompanhar o rastreio diretamente nos Correios ou Jadlog com esse código!"
                ),
            }

        return {"type": "message", "content": f"Informação obtida com sucesso: {result}"}

