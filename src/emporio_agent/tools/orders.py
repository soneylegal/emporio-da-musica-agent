"""Ferramentas de consulta de status de pedidos e rastreamento da Empório da Música."""

import sqlite3
from typing import Any, Dict, List, Optional
from emporio_agent.db.database import get_connection


def get_order_status(
    order_id: int,
    customer_contact: Optional[str] = None,
    conn: Optional[sqlite3.Connection] = None,
) -> Dict[str, Any]:
    """Consulta o status detalhado de um pedido pelo número de identificação.
    
    Args:
        order_id: Número identificador do pedido (ex: 1, 2, 3).
        customer_contact: Telefone ou e-mail opcional para validação de segurança do cliente.
        conn: Conexão opcional com SQLite.
    """
    close_after = False
    if conn is None:
        conn = get_connection()
        close_after = True

    try:
        sql = """
            SELECT 
                o.order_id,
                o.order_date,
                o.status,
                o.total_brl,
                o.payment_method,
                o.tracking_code,
                o.estimated_delivery,
                o.notes,
                c.customer_id,
                c.name AS customer_name,
                c.phone AS customer_phone,
                c.email AS customer_email,
                c.city AS customer_city
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.order_id = ?
        """
        cursor = conn.execute(sql, [order_id])
        row = cursor.fetchone()

        if not row:
            return {
                "found": False,
                "message": f"Pedido #{order_id} não encontrado na base de dados. Verifique o número digitado."
            }

        order_data = dict(row)

        # Se contato foi fornecido, verifica compatibilidade básica
        if customer_contact:
            contact_clean = "".join(filter(str.isalnum, customer_contact.lower()))
            phone_clean = "".join(filter(str.isalnum, (order_data.get("customer_phone") or "").lower()))
            email_clean = (order_data.get("customer_email") or "").lower()

            if contact_clean not in phone_clean and contact_clean not in email_clean:
                return {
                    "found": False,
                    "message": f"Os dados de contato fornecidos não coincidem com o cadastro do pedido #{order_id}."
                }

        # Busca os itens que compõem o pedido
        items_sql = """
            SELECT 
                oi.quantity,
                p.product_id,
                p.name AS product_name,
                p.price_brl
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = ?
        """
        items_cursor = conn.execute(items_sql, [order_id])
        items: List[Dict[str, Any]] = [dict(r) for r in items_cursor.fetchall()]

        return {
            "found": True,
            "order_id": order_data["order_id"],
            "status": order_data["status"],
            "order_date": order_data["order_date"],
            "total_brl": order_data["total_brl"],
            "payment_method": order_data["payment_method"],
            "tracking_code": order_data["tracking_code"],
            "estimated_delivery": order_data["estimated_delivery"],
            "customer_name": order_data["customer_name"],
            "customer_city": order_data["customer_city"],
            "items": items,
        }
    finally:
        if close_after:
            conn.close()

