import unittest
import werkzeug
from app import app
from flask_jwt_extended import decode_token

# Ajuste para prevenir erro com Werkzeug
if not hasattr(werkzeug, "__version__"):
    werkzeug.__version__ = "fixed-version"


class TesteSimplesAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.client = app.test_client()

    def test_raiz_retorna_mensagem(self):
        """Verifica se a rota principal responde corretamente."""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)

        data = resp.get_json()
        self.assertIn("message", data)
        self.assertTrue("API is running" in data["message"])

    def test_gerar_token_e_validar(self):
        """Garante que o login gera um token JWT válido e decodificável."""
        resp = self.client.post("/login")
        self.assertEqual(resp.status_code, 200)

        payload = resp.get_json()
        token = payload.get("access_token")

        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)

        # Decodifica o token para validar a identidade
        with self.app.app_context():
            resultado = decode_token(token)
            self.assertEqual(resultado.get("sub"), "user")

    def test_acesso_protegido_com_token(self):
        """Testa se é possível acessar /protected utilizando um token."""
        # Primeiro pega o token
        login = self.client.post("/login")
        token = login.get_json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}
        resp = self.client.get("/protected", headers=headers)

        self.assertEqual(resp.status_code, 200)

        corpo = resp.get_json()
        self.assertEqual(corpo.get("message"), "Protected route")


if __name__ == "__main__":
    unittest.main()
