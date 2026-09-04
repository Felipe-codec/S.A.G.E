import email
from email.header import decode_header
import imaplib
import re
import socket
import ssl
import time
from typing import Optional, Tuple
from app.core.config import settings
from app.core.logging import logger


class IMAPServiceError(Exception):
    """Exceção base para erros de IMAP."""
    pass


class IMAPConnectionError(IMAPServiceError):
    """Erro de conexão ou timeout com o servidor IMAP."""
    pass


class IMAPAuthenticationError(IMAPServiceError):
    """Credenciais inválidas de e-mail/senha de aplicativo."""
    pass


class IMAPTimeoutError(IMAPServiceError):
    """Timeout ao aguardar a chegada do e-mail com código Steam Guard."""
    pass


class SteamCodeNotFoundError(IMAPServiceError):
    """E-mail encontrado, mas o código Steam Guard não pôde ser extraído."""
    pass


def extract_steam_code_from_text(content: str) -> Optional[str]:
    """
    Extrai o código de 5 caracteres do Steam Guard do corpo do e-mail.
    A Steam utiliza um alfabeto de caracteres específicos (evita 0/O, 1/I).
    Exemplos: 'C78N4', 'M2K99', etc.
    """
    if not content:
        return None

    # Padrão 1: Código explícito após rótulos comuns em Português e Inglês
    pattern_label = re.compile(
        r'(?i)(?:código\s+de\s+(?:acesso|início\s+de\s+sessão|segurança)|login\s+code|steam\s+guard\s+code|access\s+code|código)\s*[:=]?\s*<[^>]+>?\s*([2-9BCDFGHJKLMNPQRTVWXYZ]{5})\b'
    )
    match = pattern_label.search(content)
    if match:
        return match.group(1).upper()

    # Padrão 2: Código dentro de tags HTML em destaque (estilo padrão dos e-mails da Valve)
    pattern_html = re.compile(
        r'(?i)<td[^>]*class="[^"]*title[^"]*"[^>]*>\s*([2-9BCDFGHJKLMNPQRTVWXYZ]{5})\s*</td>'
    )
    match = pattern_html.search(content)
    if match:
        return match.group(1).upper()

    # Padrão 3: Padrão genérico de 5 caracteres alfanuméricos maiúsculos isolados
    pattern_fallback = re.compile(r'\b([2-9BCDFGHJKLMNPQRTVWXYZ]{5})\b')
    candidates = pattern_fallback.findall(content)
    if candidates:
        # Retorna o primeiro candidato válido
        return candidates[0].upper()

    return None


def get_body_from_email_message(msg: email.message.Message) -> str:
    """Extrai texto e HTML de mensagens multipart de e-mail."""
    body_parts = []
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type in ["text/plain", "text/html"] and "attachment" not in content_disposition:
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        body_parts.append(payload.decode(charset, errors="replace"))
                except Exception:
                    pass
    else:
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or "utf-8"
                body_parts.append(payload.decode(charset, errors="replace"))
        except Exception:
            pass
    return " ".join(body_parts)


class IMAPService:
    @staticmethod
    def test_connection(
        host: str,
        port: int,
        username: str,
        password: str,
        use_ssl: bool = True,
        timeout: int = 5,
    ) -> Tuple[bool, str, int]:
        """
        Testa a conectividade e autenticação IMAP sem realizar ações destrutivas.
        Retorna (sucesso, mensagem, tempo_ms).
        """
        start_time = time.time()
        client = None
        try:
            if use_ssl:
                ssl_context = ssl.create_default_context()
                client = imaplib.IMAP4_SSL(host=host, port=port, ssl_context=ssl_context, timeout=timeout)
            else:
                client = imaplib.IMAP4(host=host, port=port, timeout=timeout)

            client.login(username, password)
            status, _ = client.select("INBOX", readonly=True)
            duration_ms = int((time.time() - start_time) * 1000)

            if status == "OK":
                return True, "Conexão e autenticação IMAP estabelecidas com sucesso.", duration_ms
            return False, f"Falha ao acessar INBOX (Status: {status})", duration_ms

        except imaplib.IMAP4.error as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return False, f"Falha de autenticação IMAP: Verifique e-mail e senha de aplicativo. ({e})", duration_ms
        except (socket.timeout, TimeoutError):
            duration_ms = int((time.time() - start_time) * 1000)
            return False, f"Timeout ao conectar ao host {host}:{port}.", duration_ms
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return False, f"Erro de conexão IMAP: {str(e)}", duration_ms
        finally:
            if client:
                try:
                    client.close()
                except Exception:
                    pass
                try:
                    client.logout()
                except Exception:
                    pass

    @staticmethod
    def fetch_steam_guard_code(
        host: str,
        port: int,
        username: str,
        password: str,
        steam_username: str,
        use_ssl: bool = True,
        timeout: int = 5,
        poll_interval: int = 2,
        poll_timeout: int = 15,
    ) -> Tuple[str, int]:
        """
        Executa busca ativa por polling no INBOX do revendedor para capturar o código Steam Guard.
        Retorna (codigo_encontrado, duracao_ms).
        """
        start_time = time.time()
        deadline = start_time + poll_timeout
        client = None

        try:
            if use_ssl:
                ssl_context = ssl.create_default_context()
                client = imaplib.IMAP4_SSL(host=host, port=port, ssl_context=ssl_context, timeout=timeout)
            else:
                client = imaplib.IMAP4(host=host, port=port, timeout=timeout)

            client.login(username, password)
            client.select("INBOX", readonly=True)

            while time.time() < deadline:
                # Busca por e-mails com remetente da Steam ou assunto Steam
                status, messages = client.search(None, '(FROM "steampowered.com")')
                if status != "OK" or not messages or not messages[0]:
                    # Tenta busca mais aberta caso o servidor IMAP trate FROM de forma estrita
                    status, messages = client.search(None, 'ALL')

                if status == "OK" and messages and messages[0]:
                    email_ids = messages[0].split()
                    # Analisa os 3 e-mails mais recentes
                    for eid in reversed(email_ids[-3:]):
                        res, msg_data = client.fetch(eid, "(RFC822)")
                        if res != "OK" or not msg_data:
                            continue

                        for response_part in msg_data:
                            if isinstance(response_part, tuple):
                                msg = email.message_from_bytes(response_part[1])
                                body = get_body_from_email_message(msg)

                                # Verifica se o e-mail contém o código
                                code = extract_steam_code_from_text(body)
                                if code:
                                    duration_ms = int((time.time() - start_time) * 1000)
                                    logger.info(
                                        f"Código Steam Guard capturado com sucesso para a conta {steam_username} em {duration_ms}ms"
                                    )
                                    return code, duration_ms

                # Aguarda o intervalo de polling antes da próxima tentativa
                time.sleep(poll_interval)

            duration_ms = int((time.time() - start_time) * 1000)
            raise IMAPTimeoutError(
                f"Tempo limite ({poll_timeout}s) excedido. Nenhum novo e-mail da Steam com código foi detectado."
            )

        except imaplib.IMAP4.error as e:
            raise IMAPAuthenticationError(f"Erro de autenticação no servidor IMAP: {e}")
        except (socket.timeout, TimeoutError):
            raise IMAPConnectionError(f"Timeout na comunicação com o servidor IMAP ({host}:{port}).")
        except IMAPServiceError:
            raise
        except Exception as e:
            raise IMAPConnectionError(f"Erro inesperado no cliente IMAP: {str(e)}")
        finally:
            if client:
                try:
                    client.close()
                except Exception:
                    pass
                try:
                    client.logout()
                except Exception:
                    pass
