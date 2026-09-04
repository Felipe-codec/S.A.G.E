import pytest
from app.services.imap_service import (
    IMAPService,
    extract_steam_code_from_text,
)


def test_extract_steam_code_from_portuguese_email():
    email_text = """
    Olá Usuário,
    Recentemente recebemos um pedido de acesso à sua conta Steam a partir de um novo navegador.
    Aqui está o seu código de acesso do Steam Guard:
    C78N4
    Se você não tentou iniciar a sessão, proteja sua conta imediatamente.
    """
    code = extract_steam_code_from_text(email_text)
    assert code == "C78N4"


def test_extract_steam_code_from_english_email():
    email_text = """
    Dear Steam User,
    Here is the Steam Guard code you need to login to your account:
    27M9V
    This code will verify that it was really you attempting to log in.
    """
    code = extract_steam_code_from_text(email_text)
    assert code == "27M9V"


def test_extract_steam_code_from_html_template():
    email_html = """
    <html>
      <body>
        <table class="body">
          <tr>
            <td class="title" style="font-size: 24px; font-weight: bold;">
              9BRK3
            </td>
          </tr>
        </table>
      </body>
    </html>
    """
    code = extract_steam_code_from_text(email_html)
    assert code == "9BRK3"


def test_imap_test_connection_invalid_host():
    """Valida que host inválido retorna insucesso sem lançar exceção não tratada."""
    success, message, duration = IMAPService.test_connection(
        host="invalid.nonexistent.domain.test",
        port=993,
        username="user@test.com",
        password="fakepassword",
        use_ssl=True,
        timeout=1,
    )
    assert success is False
    assert duration >= 0
    assert "Erro" in message or "Timeout" in message
