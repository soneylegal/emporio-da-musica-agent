"""Orquestrador do ciclo de vida do agente com gerenciamento de memória e chamadas de ferramentas."""

import logging
from typing import Any, Dict, List, Optional
from emporio_agent.agent.llm_client import LLMClient
from emporio_agent.agent.prompts import SYSTEM_PROMPT
from emporio_agent.tools import AVAILABLE_TOOLS, TOOL_SCHEMAS

logger = logging.getLogger(__name__)


class EmporioAgent:
    """Agente de atendimento da Empório da Música."""

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        system_prompt: str = SYSTEM_PROMPT,
        max_tool_iterations: int = 5,
    ):
        self.llm_client = llm_client or LLMClient()
        self.system_prompt = system_prompt
        self.max_tool_iterations = max_tool_iterations
        self.messages: List[Dict[str, Any]] = []
        self.last_traces: List[Dict[str, Any]] = []

    def reset_history(self) -> None:
        """Reinicia o histórico da conversa."""
        self.messages.clear()
        self.last_traces.clear()

    def process_message(self, user_message: str) -> str:
        """Processa uma mensagem enviada pelo usuário, executando chamadas de ferramentas necessárias."""
        self.messages.append({"role": "user", "content": user_message})
        self.last_traces.clear()

        iterations = 0
        while iterations < self.max_tool_iterations:
            iterations += 1

            response = self.llm_client.call(
                messages=self.messages,
                tools_schemas=TOOL_SCHEMAS,
                system_instruction=self.system_prompt,
            )

            # Caso o modelo tenha gerado texto direto
            if response.get("type") == "message":
                reply = response.get("content", "")
                self.messages.append({"role": "assistant", "content": reply})
                return reply

            # Caso o modelo tenha solicitado chamada de ferramenta (Tool Call)
            if response.get("type") == "tool_calls":
                tool_calls = response.get("tool_calls", [])
                # Registra a chamada de ferramenta feita pelo assistente
                self.messages.append({"role": "assistant", "tool_calls": tool_calls})

                for call in tool_calls:
                    fn_name = call.get("name")
                    fn_args = call.get("arguments", {})
                    fn = AVAILABLE_TOOLS.get(fn_name)

                    if not fn:
                        tool_result = {"error": f"Ferramenta '{fn_name}' não existe."}
                    else:
                        try:
                            tool_result = fn(**fn_args)
                        except Exception as e:
                            logger.error(f"Erro ao executar ferramenta {fn_name}: {e}")
                            tool_result = {"error": str(e)}

                    trace = {
                        "tool_name": fn_name,
                        "arguments": fn_args,
                        "result": tool_result,
                    }
                    self.last_traces.append(trace)

                    # Registra a chamada e o resultado no histórico de mensagens
                    self.messages.append({
                        "role": "tool",
                        "tool_name": fn_name,
                        "content": tool_result,
                    })

        fallback_reply = "Desculpe, tive uma dificuldade temporária ao processar as informações. Como posso ajudar com outra dúvida?"
        self.messages.append({"role": "assistant", "content": fallback_reply})
        return fallback_reply

