"""Ferramentas de consulta de catálogo e produtos da Empório da Música."""

import json
import sqlite3
from typing import Any, Dict, List, Optional
from emporio_agent.db.database import get_connection


def search_products(
    query: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock_only: bool = True,
    limit: int = 5,
    conn: Optional[sqlite3.Connection] = None,
) -> List[Dict[str, Any]]:
    """Busca produtos no catálogo da loja por termo textual, categoria e faixa de preço.
    
    Args:
        query: Termo de busca no nome ou descrição do instrumento (ex: 'violão', 'yamaha', 'tagima').
        category: Nome ou parte do nome da categoria (ex: 'Violões', 'Guitarras', 'Teclados').
        min_price: Preço mínimo em reais.
        max_price: Preço máximo em reais.
        in_stock_only: Se True, retorna apenas itens com estoque maior que zero.
        limit: Quantidade máxima de resultados (padrão 5).
        conn: Conexão opcional com SQLite.
    """
    close_after = False
    if conn is None:
        conn = get_connection()
        close_after = True

    try:
        sql = """
            SELECT 
                p.product_id,
                p.name,
                c.name AS category_name,
                p.price_brl,
                p.stock_quantity,
                p.status,
                p.description,
                pr.discount_percent,
                pr.description AS promo_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
            LEFT JOIN promotions pr ON p.product_id = pr.product_id AND pr.is_active = 1
            WHERE p.status = 'active'
        """
        params: List[Any] = []

        if in_stock_only:
            sql += " AND p.stock_quantity > 0"

        if query:
            clean_query = f"%{query.strip().lower()}%"
            sql += " AND (LOWER(p.name) LIKE ? OR LOWER(p.description) LIKE ?)"
            params.extend([clean_query, clean_query])

        if category:
            clean_cat = f"%{category.strip().lower()}%"
            sql += " AND LOWER(c.name) LIKE ?"
            params.append(clean_cat)

        if min_price is not None:
            sql += " AND p.price_brl >= ?"
            params.append(float(min_price))

        if max_price is not None:
            sql += " AND p.price_brl <= ?"
            params.append(float(max_price))

        sql += " ORDER BY p.price_brl ASC LIMIT ?"
        params.append(int(limit))

        cursor = conn.execute(sql, params)
        results = []
        for row in cursor.fetchall():
            item = dict(row)
            # Calcula valor promocional caso haja promoção ativa
            if item.get("discount_percent"):
                discount = item["discount_percent"]
                item["effective_price_brl"] = round(item["price_brl"] * (1 - discount / 100), 2)
            else:
                item["effective_price_brl"] = item["price_brl"]
            results.append(item)

        return results
    finally:
        if close_after:
            conn.close()


def get_product_details(
    product_identifier: str,
    conn: Optional[sqlite3.Connection] = None,
) -> Optional[Dict[str, Any]]:
    """Recupera a ficha técnica detalhada e estoque de um instrumento específico.
    
    Args:
        product_identifier: ID numérico do produto ou nome aproximado (ex: 'Takamine GD20', '81').
    """
    close_after = False
    if conn is None:
        conn = get_connection()
        close_after = True

    try:
        sql = """
            SELECT 
                p.product_id,
                p.name,
                c.name AS category_name,
                p.price_brl,
                p.stock_quantity,
                p.status,
                p.description,
                p.specs,
                pr.discount_percent,
                pr.description AS promo_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
            LEFT JOIN promotions pr ON p.product_id = pr.product_id AND pr.is_active = 1
        """
        params: List[Any] = []

        is_id = product_identifier.isdigit()
        if is_id:
            sql += " WHERE p.product_id = ?"
            params.append(int(product_identifier))
        else:
            clean_name = f"%{product_identifier.strip().lower()}%"
            sql += " WHERE LOWER(p.name) LIKE ?"
            params.append(clean_name)

        sql += " LIMIT 1"
        cursor = conn.execute(sql, params)
        row = cursor.fetchone()
        if not row:
            return None

        data = dict(row)
        # Parse das especificações JSON se presentes
        if data.get("specs"):
            try:
                data["specs"] = json.loads(data["specs"])
            except Exception:
                pass

        if data.get("discount_percent"):
            discount = data["discount_percent"]
            data["effective_price_brl"] = round(data["price_brl"] * (1 - discount / 100), 2)
        else:
            data["effective_price_brl"] = data["price_brl"]

        return data
    finally:
        if close_after:
            conn.close()


def list_categories(conn: Optional[sqlite3.Connection] = None) -> List[Dict[str, Any]]:
    """Lista todas as categorias de instrumentos musicais disponíveis na loja."""
    close_after = False
    if conn is None:
        conn = get_connection()
        close_after = True

    try:
        cursor = conn.execute("SELECT category_id, name, description FROM categories ORDER BY name ASC")
        return [dict(r) for r in cursor.fetchall()]
    finally:
        if close_after:
            conn.close()

