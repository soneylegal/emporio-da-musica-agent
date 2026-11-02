"""Testes de ponta a ponta para o orquestrador do agente da Empório da Música."""

import unittest
from emporio_agent.agent.llm_client import LLMClient
from emporio_agent.agent.orchestrator import EmporioAgent


class TestEmporioAgent(unittest.TestCase):
    def setUp(self):
        # Utiliza o cliente mock para garantir testes determinísticos offline
        client = LLMClient(provider="mock")
        self.agent = EmporioAgent(llm_client=client)

    def test_scenario_violoes_ate_1000(self):
        """Cenário 1 do edital: consulta sobre catálogo de violões até R$1000."""
        response = self.agent.process_message("Quais opções de violões disponíveis custando até R$1000?")
        self.assertIn("R$", response)
        self.assertTrue(any(v in response for v in ["Yamaha", "Tagima", "opções disponíveis"]))
        self.assertTrue(len(self.agent.last_traces) > 0)
        self.assertEqual(self.agent.last_traces[0]["tool_name"], "search_products")

    def test_scenario_store_address(self):
        """Cenário 2 do edital: informações gerais e endereço da loja."""
        response = self.agent.process_message("Qual o endereço da loja?")
        self.assertIn("14 de Maio", response)
        self.assertIn("Campo Grande", response)
        self.assertEqual(self.agent.last_traces[0]["tool_name"], "get_policy_info")

    def test_scenario_price_takamine_gd20(self):
        """Cenário 3 do edital: consulta de preço do Takamine GD20."""
        response = self.agent.process_message("Quanto custa o Takamine GD20?")
        self.assertIn("Takamine", response)
        self.assertIn("R$", response)
        self.assertEqual(self.agent.last_traces[0]["tool_name"], "get_product_details")

    def test_scenario_return_policy(self):
        """Cenário 4 do edital: aplicação de políticas de devolução e arrependimento."""
        response = self.agent.process_message("Me arrependi da minha compra, posso devolver meu pedido?")
        self.assertIn("7", response)
        self.assertIn("dias", response)
        self.assertEqual(self.agent.last_traces[0]["tool_name"], "get_policy_info")

    def test_scenario_accessories_out_of_scope(self):
        """Guardrail de escopo: pergunta sobre cabos e palhetas."""
        response = self.agent.process_message("Vocês vendem encordoamento de cordas e palhetas?")
        self.assertTrue(any(w in response.lower() for w in ["exclusivamente", "não comercializamos", "acessórios"]))

    def test_scenario_order_status(self):
        """Consulta não trivial: status do pedido 1."""
        response = self.agent.process_message("Gostaria de ver o andamento do meu pedido #1")
        self.assertIn("1", response)
        self.assertTrue(len(self.agent.last_traces) > 0)
        self.assertEqual(self.agent.last_traces[0]["tool_name"], "get_order_status")


if __name__ == "__main__":
    unittest.main()

