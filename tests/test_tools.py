"""Testes unitários para as ferramentas de consulta da Empório da Música."""

import os
import unittest
from emporio_agent.tools.catalog import get_product_details, list_categories, search_products
from emporio_agent.tools.orders import get_order_status
from emporio_agent.tools.policies import get_policy_info
from emporio_agent.tools.promotions import list_active_promotions


class TestAgentTools(unittest.TestCase):
    def test_search_violao_under_1000(self):
        """Cenário 1 do edital: violões disponíveis custando até R$ 1000."""
        results = search_products(query="violão", max_price=1000.0, in_stock_only=True)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        for item in results:
            self.assertLessEqual(item["effective_price_brl"], 1000.0)
            self.assertGreater(item["stock_quantity"], 0)

    def test_get_product_takamine_gd20(self):
        """Cenário 3 do edital: consulta de preço do Takamine GD20."""
        product = get_product_details("Takamine GD20")
        self.assertIsNotNone(product)
        self.assertIn("Takamine", product["name"])
        self.assertIn("GD20", product["name"])
        self.assertGreater(product["price_brl"], 0)
        self.assertIn("specs", product)

    def test_get_product_not_found(self):
        product = get_product_details("ProdutoInexistente999XYZ")
        self.assertIsNone(product)

    def test_get_order_status_valid(self):
        """Consulta de pedido existente com retorno de rastreio e itens."""
        order = get_order_status(order_id=1)
        self.assertTrue(order["found"])
        self.assertEqual(order["order_id"], 1)
        self.assertIn("tracking_code", order)
        self.assertGreater(len(order["items"]), 0)

    def test_get_order_status_invalid(self):
        order = get_order_status(order_id=999999)
        self.assertFalse(order["found"])

    def test_policy_arrependimento(self):
        """Cenário 4 do edital: aplicação de política de devolução e arrependimento."""
        policy = get_policy_info("arrependimento")
        self.assertEqual(policy["secao"], "Políticas de Trocas e Devoluções")
        details = policy["detalhes"]["right_of_withdrawal"]
        self.assertIn("7", details["period"])

    def test_policy_frete(self):
        policy = get_policy_info("frete")
        self.assertEqual(policy["secao"], "Política de Frete, Envio e Rastreamento")
        local = policy["detalhes"]["local_metro"]
        self.assertIn("500", local["free_shipping_threshold"])

    def test_policy_acessorios_escopo(self):
        """Verifica que a loja recusa acessórios e orienta redirecionamento."""
        policy = get_policy_info("acessorios")
        self.assertEqual(policy["secao"], "Escopo de Atuação e Produtos Não Comercializados")
        prohibited = policy["detalhes"]["prohibited_items"]
        self.assertIn("cordas", prohibited)
        self.assertIn("palhetas", prohibited)

    def test_list_active_promotions(self):
        promos = list_active_promotions()
        self.assertIsInstance(promos, list)

    def test_list_categories(self):
        cats = list_categories()
        self.assertIsInstance(cats, list)
        self.assertGreater(len(cats), 0)


if __name__ == "__main__":
    unittest.main()

