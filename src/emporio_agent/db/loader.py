"""Carregador de dados dos arquivos CSV para o banco SQLite da Empório da Música."""

import csv
import logging
import os
import sys
from pathlib import Path
from typing import Optional

from emporio_agent.db.database import get_connection, init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"


def get_data_dir() -> Path:
    custom_dir = os.getenv("DATA_DIR")
    if custom_dir:
        return Path(custom_dir).resolve()
    return DEFAULT_DATA_DIR


def load_categories(conn, data_dir: Path) -> int:
    csv_path = data_dir / "categories.csv"
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [
            (int(r["category_id"]), r["name"].strip(), r.get("description", "").strip())
            for r in reader
        ]
    conn.executemany(
        "INSERT OR REPLACE INTO categories (category_id, name, description) VALUES (?, ?, ?);",
        rows,
    )
    return len(rows)


def load_customers(conn, data_dir: Path) -> int:
    csv_path = data_dir / "customers.csv"
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [
            (
                int(r["customer_id"]),
                r["name"].strip(),
                r.get("phone", "").strip(),
                r.get("email", "").strip(),
                r.get("city", "").strip(),
            )
            for r in reader
        ]
    conn.executemany(
        "INSERT OR REPLACE INTO customers (customer_id, name, phone, email, city) VALUES (?, ?, ?, ?, ?);",
        rows,
    )
    return len(rows)


def load_products(conn, data_dir: Path) -> int:
    csv_path = data_dir / "products.csv"
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        for r in reader:
            rows.append(
                (
                    int(r["product_id"]),
                    float(r["price_brl"]),
                    r["name"].strip(),
                    int(r["category_id"]) if r.get("category_id") else None,
                    r.get("description", "").strip(),
                    int(r.get("stock_quantity", 0)),
                    r.get("status", "active").strip(),
                    r.get("specs", "").strip(),
                    r.get("created_at", "").strip(),
                )
            )
    conn.executemany(
        """INSERT OR REPLACE INTO products 
           (product_id, price_brl, name, category_id, description, stock_quantity, status, specs, created_at) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);""",
        rows,
    )
    return len(rows)


def load_orders(conn, data_dir: Path) -> int:
    csv_path = data_dir / "orders.csv"
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        for r in reader:
            rows.append(
                (
                    int(r["order_id"]),
                    int(r["customer_id"]) if r.get("customer_id") else None,
                    r.get("order_date", "").strip(),
                    r.get("status", "").strip(),
                    float(r["total_brl"]) if r.get("total_brl") else 0.0,
                    r.get("payment_method", "").strip(),
                    r.get("tracking_code", "").strip(),
                    r.get("estimated_delivery", "").strip(),
                    r.get("notes", "").strip(),
                )
            )
    conn.executemany(
        """INSERT OR REPLACE INTO orders 
           (order_id, customer_id, order_date, status, total_brl, payment_method, tracking_code, estimated_delivery, notes) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);""",
        rows,
    )
    return len(rows)


def load_order_items(conn, data_dir: Path) -> int:
    csv_path = data_dir / "order_items.csv"
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [
            (
                int(r["order_id"]),
                int(r.get("quantity", 1)),
                int(r["product_id"]),
            )
            for r in reader
        ]
    conn.executemany(
        "INSERT INTO order_items (order_id, quantity, product_id) VALUES (?, ?, ?);",
        rows,
    )
    return len(rows)


def load_promotions(conn, data_dir: Path) -> int:
    csv_path = data_dir / "promotions.csv"
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [
            (
                int(r["promotion_id"]),
                int(r["product_id"]),
                float(r["discount_percent"]),
                r.get("description", "").strip(),
                int(r.get("is_active", 0)),
            )
            for r in reader
        ]
    conn.executemany(
        """INSERT OR REPLACE INTO promotions 
           (promotion_id, product_id, discount_percent, description, is_active) 
           VALUES (?, ?, ?, ?, ?);""",
        rows,
    )
    return len(rows)


def seed_database(data_dir: Optional[Path] = None, db_path: Optional[Path] = None) -> None:
    data_dir = data_dir or get_data_dir()
    logger.info(f"Iniciando schema do banco em: {db_path or 'padrão'}")
    init_db(db_path)

    conn = get_connection(db_path)
    try:
        with conn:
            # Limpa tabelas antes de recarregar
            conn.execute("DELETE FROM order_items;")
            conn.execute("DELETE FROM orders;")
            conn.execute("DELETE FROM promotions;")
            conn.execute("DELETE FROM products;")
            conn.execute("DELETE FROM customers;")
            conn.execute("DELETE FROM categories;")

            num_cat = load_categories(conn, data_dir)
            num_cust = load_customers(conn, data_dir)
            num_prod = load_products(conn, data_dir)
            num_ord = load_orders(conn, data_dir)
            num_items = load_order_items(conn, data_dir)
            num_promo = load_promotions(conn, data_dir)

            logger.info(
                f"Banco populado com sucesso: {num_cat} categorias, {num_cust} clientes, "
                f"{num_prod} produtos, {num_ord} pedidos, {num_items} itens de pedidos, {num_promo} promoções."
            )
    finally:
        conn.close()


if __name__ == "__main__":
    seed_database()

