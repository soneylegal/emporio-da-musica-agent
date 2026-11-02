"""Módulo unificado de ferramentas (tools) para o agente da Empório da Música."""

from typing import Any, Callable, Dict, List
from emporio_agent.tools.catalog import get_product_details, list_categories, search_products
from emporio_agent.tools.orders import get_order_status
from emporio_agent.tools.policies import get_policy_info
from emporio_agent.tools.promotions import list_active_promotions

# Mapeamento de nome da função para a callable em Python
AVAILABLE_TOOLS: Dict[str, Callable[..., Any]] = {
    "search_products": search_products,
    "get_product_details": get_product_details,
    "list_categories": list_categories,
    "get_order_status": get_order_status,
    "get_policy_info": get_policy_info,
    "list_active_promotions": list_active_promotions,
}

# Declarações de esquemas (JSON Schema) para Function Calling em LLMs
TOOL_SCHEMAS: List[Dict[str, Any]] = [
    {
        "name": "search_products",
        "description": "Busca instrumentos musicais no catálogo por texto, categoria ou faixa de preço.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Termo de busca no nome ou descrição (ex: 'violão', 'yamaha', 'tagima', 'stratocaster').",
                },
                "category": {
                    "type": "string",
                    "description": "Nome da categoria (ex: 'Violões', 'Guitarras', 'Baixos', 'Teclados', 'Baterias', 'Sopro').",
                },
                "min_price": {
                    "type": "number",
                    "description": "Preço mínimo em reais.",
                },
                "max_price": {
                    "type": "number",
                    "description": "Preço máximo em reais (ex: 1000).",
                },
                "in_stock_only": {
                    "type": "boolean",
                    "description": "Se verdadeiro, filtra apenas instrumentos com estoque positivo (padrão true).",
                },
            },
        },
    },
    {
        "name": "get_product_details",
        "description": "Recupera ficha técnica completa, especificações de madeira/cordas/captação, estoque e preço atual de um instrumento específico.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_identifier": {
                    "type": "string",
                    "description": "Nome aproximado ou ID do produto (ex: 'Takamine GD20', '81').",
                },
            },
            "required": ["product_identifier"],
        },
    },
    {
        "name": "get_order_status",
        "description": "Consulta o status de um pedido realizado na loja, código de rastreamento, previsão de entrega e itens comprados.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "integer",
                    "description": "Número identificador do pedido (ex: 1, 2, 3).",
                },
                "customer_contact": {
                    "type": "string",
                    "description": "Telefone ou e-mail do cliente para confirmação cadastral.",
                },
            },
            "required": ["order_id"],
        },
    },
    {
        "name": "get_policy_info",
        "description": "Consulta as políticas oficiais da loja: trocas, devoluções, direito de arrependimento (7 dias), garantia, formas de pagamento, parcelamento, regras de frete e prazos, horário de funcionamento ou escopo de produtos.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Assunto a ser consultado (ex: 'arrependimento', 'devolucao', 'frete', 'horario', 'pagamento', 'acessorios', 'garantia').",
                },
            },
            "required": ["topic"],
        },
    },
    {
        "name": "list_active_promotions",
        "description": "Lista as promoções e descontos especiais que estão ativas no momento na loja.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "list_categories",
        "description": "Lista todas as categorias de instrumentos musicais comercializadas pela loja.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
]

