"""Ferramenta de recuperação de regras e políticas internas da Empório da Música."""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_POLICIES_PATH = Path(__file__).resolve().parent.parent.parent.parent / "data" / "policies.json"


def get_policies_path() -> Path:
    custom_path = os.getenv("POLICIES_FILE")
    if custom_path:
        return Path(custom_path).resolve()
    return DEFAULT_POLICIES_PATH


def load_policies() -> Dict[str, Any]:
    path = get_policies_path()
    if not path.exists():
        return {}
    with open(path, mode="r", encoding="utf-8") as f:
        return json.load(f)


def get_policy_info(topic: str) -> Dict[str, Any]:
    """Recupera cláusulas específicas do manual de políticas da Empório da Música.
    
    Args:
        topic: Assunto da dúvida (ex: 'devolucao', 'troca', 'arrependimento', 'horario', 
               'pagamento', 'parcelamento', 'frete', 'entrega', 'garantia', 'escopo', 'endereco').
    """
    policies = load_policies()
    topic_clean = topic.strip().lower()

    # Mapeamento semântico de palavras-chave para seções do manual
    if any(k in topic_clean for k in ["horari", "funcion", "abert", "fechad", "expediente", "domingo", "sabado", "sábado"]):
        return {
            "secao": "Horário de Funcionamento",
            "detalhes": policies.get("opening_hours", {})
        }

    if any(k in topic_clean for k in ["troc", "devol", "arrepend", "defeit", "estorno"]):
        return {
            "secao": "Políticas de Trocas e Devoluções",
            "detalhes": policies.get("returns_and_exchanges", {})
        }

    if any(k in topic_clean for k in ["pagament", "pix", "cartao", "cartão", "parcel", "boleto", "juros", "desconto pix"]):
        return {
            "secao": "Formas de Pagamento e Condições de Parcelamento",
            "detalhes": policies.get("payment_methods", {})
        }

    if any(k in topic_clean for k in ["fret", "entreg", "sedex", "pac", "jadlog", "rastre", "prazo"]):
        return {
            "secao": "Política de Frete, Envio e Rastreamento",
            "detalhes": policies.get("shipping_and_delivery", {})
        }

    if any(k in topic_clean for k in ["garanti"]):
        return {
            "secao": "Garantia Legal e de Fabricante",
            "detalhes": policies.get("warranty", {})
        }

    if any(k in topic_clean for k in ["acessori", "acessóri", "corda", "palheta", "cabo", "pedal", "amplificador", "escopo", "case", "bag", "afinador"]):
        return {
            "secao": "Escopo de Atuação e Produtos Não Comercializados",
            "detalhes": policies.get("business_scope", {})
        }

    if any(k in topic_clean for k in ["enderec", "endereç", "localiza", "contato", "telefone", "whatsapp", "onde fica", "sobre"]):
        return {
            "secao": "Dados Institucionais e Endereço",
            "detalhes": policies.get("store_info", {})
        }

    if any(k in topic_clean for k in ["promo", "black friday", "desconto", "queima"]):
        return {
            "secao": "Regras de Promoções e Campanhas",
            "detalhes": policies.get("promotions_policy", {})
        }

    # Se não houver correspondência direta, retorna visão geral das políticas mais frequentes
    return {
        "secao": "Visão Geral de Políticas",
        "informacoes_gerais": {
            "loja": policies.get("store_info", {}),
            "horarios": policies.get("opening_hours", {}),
            "escopo": policies.get("business_scope", {}),
            "pagamento": policies.get("payment_methods", {}),
            "trocas": policies.get("returns_and_exchanges", {}),
            "frete": policies.get("shipping_and_delivery", {})
        }
    }
