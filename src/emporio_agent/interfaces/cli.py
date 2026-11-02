"""Interface de linha de comando (CLI) interativa para o agente da Empório da Música."""

import os
import sys
from emporio_agent.agent.llm_client import LLMClient
from emporio_agent.agent.orchestrator import EmporioAgent

try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    console = Console()
    HAS_RICH = True
except ImportError:
    console = None
    HAS_RICH = False


def print_banner():
    title = "🎸 EMPÓRIO DA MÚSICA — ASSISTENTE DE ATENDIMENTO 🎸"
    subtitle = "Sua música começa aqui | Campo Grande - MS | Digite 'sair' para encerrar ou 'limpar' para reiniciar"
    if HAS_RICH:
        console.print(Panel(f"[bold green]{title}[/bold green]\n[dim]{subtitle}[/dim]", border_style="blue"))
    else:
        print("=" * 65)
        print(title)
        print(subtitle)
        print("=" * 65)


def run_cli():
    """Inicia o loop interativo da CLI."""
    print_banner()

    agent = EmporioAgent()

    if HAS_RICH:
        console.print(f"[dim]Provedor ativo: [bold]{agent.llm_client.provider.upper()}[/bold] (Modelo: {agent.llm_client.model})[/dim]\n")
    else:
        print(f"Provedor ativo: {agent.llm_client.provider.upper()} (Modelo: {agent.llm_client.model})\n")

    while True:
        try:
            user_input = input("Você: ").strip()
            if not user_input:
                continue

            if user_input.lower() in ("sair", "exit", "quit"):
                print("\nEncerrando atendimento. Até logo e boas notas musicais! 🎶\n")
                break

            if user_input.lower() in ("limpar", "clear", "reset"):
                agent.reset_history()
                if HAS_RICH:
                    console.print("[yellow]Histórico de conversa reiniciado.[/yellow]\n")
                else:
                    print("Histórico de conversa reiniciado.\n")
                continue

            # Processamento da mensagem
            response = agent.process_message(user_input)

            # Exibe ferramentas acionadas se houver
            if agent.last_traces:
                for trace in agent.last_traces:
                    trace_info = f"⚙️ [Tool Call] {trace['tool_name']}({trace['arguments']})"
                    if HAS_RICH:
                        console.print(f"[dim cyan]{trace_info}[/dim cyan]")
                    else:
                        print(trace_info)

            # Resposta do assistente
            if HAS_RICH:
                console.print("\n[bold green]Empório da Música:[/bold green]")
                console.print(Markdown(response))
                console.print()
            else:
                print(f"\nEmpório da Música: {response}\n")

        except (KeyboardInterrupt, EOFError):
            print("\nAtendimento encerrado pelo usuário.")
            break
        except Exception as e:
            if HAS_RICH:
                console.print(f"[bold red]Ocorreu um erro no processamento: {e}[/bold red]\n")
            else:
                print(f"Erro: {e}\n")


if __name__ == "__main__":
    run_cli()

