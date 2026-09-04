import base64
from typing import List, Optional
from cryptography.fernet import Fernet, MultiFernet, InvalidToken
from app.core.config import settings


class CryptoManager:
    """
    Gerenciador de criptografia simétrica utilizando Fernet (AES-128-CBC + HMAC-SHA256).
    Suporta rotação de chaves sem downtime através de MultiFernet.
    """

    def __init__(self, primary_key: str, fallback_keys: Optional[List[str]] = None):
        keys = [primary_key]
        if fallback_keys:
            keys.extend(fallback_keys)

        fernet_instances = []
        for k in keys:
            k_bytes = k.strip().encode("utf-8")
            # Valida se a chave tem tamanho compatível com Fernet (32 bytes base64 = 44 chars)
            try:
                fernet_instances.append(Fernet(k_bytes))
            except Exception as e:
                raise ValueError(f"Chave de criptografia Fernet inválida: {e}")

        self.multi_fernet = MultiFernet(fernet_instances)
        self.primary_fernet = fernet_instances[0]

    def encrypt(self, plain_text: str) -> str:
        """Criptografa um texto em memória e retorna a string criptografada em base64."""
        if not plain_text:
            return ""
        encrypted_bytes = self.primary_fernet.encrypt(plain_text.encode("utf-8"))
        return encrypted_bytes.decode("utf-8")

    def decrypt(self, cipher_text: str) -> str:
        """Descriptografa o texto em memória. Lança InvalidToken caso a chave não corresponda."""
        if not cipher_text:
            return ""
        decrypted_bytes = self.multi_fernet.decrypt(cipher_text.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")

    def rotate(self, cipher_text: str) -> str:
        """Re-encripta um texto criptografado com a chave primária atual (rotação de chave)."""
        if not cipher_text:
            return ""
        re_encrypted = self.multi_fernet.rotate(cipher_text.encode("utf-8"))
        return re_encrypted.decode("utf-8")


# Instância global de criptografia configurada com a chave mestra
crypto_manager = CryptoManager(settings.MASTER_ENCRYPTION_KEY)


def encrypt_secret(plain_text: str) -> str:
    return crypto_manager.encrypt(plain_text)


def decrypt_secret(cipher_text: str) -> str:
    return crypto_manager.decrypt(cipher_text)
