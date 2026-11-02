"""Ferramentas de consulta de promoções da Empório da Música."""

import sqlite3
from typing import Any, Dict, List, Optional
from emporio_agent.db.database import get_connection


def list_active_promotions(conn: Optional[sqlite3.Connection] = None) -> List[Dict[str, Any]]:
    """Lista todas as promoções e descontos atualmente ativos na loja."""
    close_after = False
    if conn is None:
        conn = get_connection()
        close_after = True

    try:
        sql = """
            SELECT 
                p.promotion_id,
                p.discount_percent,
                p.description AS campaign_name,
                pr.product_id,
                pr.name AS product_name,
                pr.price_brl AS original_price,
                ROUND(pr.price_brl * (1 - p.discount_percent / 100), 2) AS promotional_price
            FROM promotions p
            JOIN products pr ON p.product_id = pr.product_id
            WHERE p.is_active = 1
            ORDER BY p.discount_percent DESC
        """
        cursor = conn.execute(sql)
        return [dict(r) for r in cursor.fetchall()]
    finally:
        if close_after:
            conn.close()

