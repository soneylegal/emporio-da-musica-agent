"""Interface Web interativa (Streamlit) para o agente da Empório da Música."""

import os
import streamlit as st
from emporio_agent.agent.llm_client import LLMClient
from emporio_agent.agent.orchestrator import EmporioAgent

st.set_page_config(
    page_title="Empório da Música — Atendimento Virtual",
    page_icon="🎸",
    layout="wide",
)


def get_agent(provider: str, model: str, api_key: str) -> EmporioAgent:
    client = LLMClient(provider=provider, model=model, api_key=api_key or None)
    return EmporioAgent(llm_client=client)


def main():
    st.title("🎸 Empório da Música — Atendimento ao Cliente")
    st.caption("Protótipo de Agente Inteligente com Tool Calling e RAG de Políticas")

    # Sidebar com configurações
    with st.sidebar:
        st.header("⚙️ Configurações do Agente")
        provider = st.selectbox(
            "Provedor do Modelo:",
            ["mock", "gemini", "openai", "groq", "ollama"],
            index=0,
            help="Selecione 'mock' para testes offline sem consumo de API ou 'gemini'/'openai' para uso com chaves reais.",
        )

        default_model = "gemini-2.5-flash" if provider == "gemini" else "gpt-4o-mini" if provider in ("openai", "groq") else "mock-musician-v1"
        model = st.text_input("Modelo:", value=default_model)

        api_key = ""
        if provider in ("gemini", "openai", "groq"):
            api_key = st.text_input(
                f"API Key ({provider.capitalize()}):",
                type="password",
                value=os.getenv(f"{provider.upper()}_API_KEY", ""),
            )

        st.divider()
        st.subheader("💡 Perguntas Rápidas do Desafio")
        quick_questions = [
            "Quais opções de violões disponíveis custando até R$1000?",
            "Qual o endereço da loja?",
            "Quanto custa o Takamine GD20?",
            "Me arrependi da minha compra, posso devolver meu pedido?",
            "Vocês vendem encordoamento de cordas e palhetas?",
            "Gostaria de ver o andamento do meu pedido #1",
        ]
        for q in quick_questions:
            if st.button(q, key=f"btn_{q[:15]}"):
                st.session_state["pending_input"] = q

        if st.button("🗑️ Limpar Conversa", type="secondary"):
            st.session_state["messages"] = []
            st.session_state["traces"] = []
            st.rerun()

    # Inicializa sessão
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": (
                    "Olá! Seja bem-vindo à **Empório da Música**! 🎸\n\n"
                    "Sou o consultor virtual da nossa loja em Campo Grande. Posso te ajudar a consultar instrumentos em estoque, "
                    "verificar preços, tirar dúvidas sobre frete e devoluções ou consultar o status de um pedido. Como posso te ajudar?"
                ),
            }
        ]
    if "traces" not in st.session_state:
        st.session_state["traces"] = []

    # Renderiza mensagens anteriores
    for idx, msg in enumerate(st.session_state["messages"]):
        with st.chat_message(msg["role"], avatar="🎸" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])
            # Se houver trace correspondente a esta resposta
            if msg["role"] == "assistant" and idx < len(st.session_state["traces"]) and st.session_state["traces"][idx]:
                with st.expander("🔍 Detalhes da Execução de Ferramentas (Tool Calls)"):
                    for t in st.session_state["traces"][idx]:
                        st.json(t)

    # Trata entrada pendente vinda dos botões da sidebar
    user_input = None
    if "pending_input" in st.session_state and st.session_state["pending_input"]:
        user_input = st.session_state.pop("pending_input")

    # Campo de digitação de chat
    chat_prompt = st.chat_input("Digite sua mensagem para a Empório da Música...")
    if chat_prompt:
        user_input = chat_prompt

    if user_input:
        # Exibe mensagem do usuário
        st.session_state["messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        # Processamento pelo agente
        agent = get_agent(provider=provider, model=model, api_key=api_key)

        with st.spinner("Consultando dados e políticas da loja..."):
            reply = agent.process_message(user_input)
            traces = list(agent.last_traces)

        st.session_state["messages"].append({"role": "assistant", "content": reply})
        st.session_state["traces"].append(traces)

        with st.chat_message("assistant", avatar="🎸"):
            st.markdown(reply)
            if traces:
                with st.expander("🔍 Detalhes da Execução de Ferramentas (Tool Calls)"):
                    for t in traces:
                        st.json(t)


if __name__ == "__main__":
    main()

