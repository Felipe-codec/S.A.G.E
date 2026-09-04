import pytest
from cryptography.fernet import Fernet, InvalidToken
from app.core.crypto import CryptoManager, decrypt_secret, encrypt_secret


def test_encrypt_and_decrypt():
    """Valida o ciclo de criptografia e descriptografia em memória."""
    plain_password = "MinhaSenhaSuperSecreta123!@#"
    cipher = encrypt_secret(plain_password)

    assert cipher != plain_password
    assert len(cipher) > 20

    decrypted = decrypt_secret(cipher)
    assert decrypted == plain_password


def test_key_rotation():
    """Valida suporte a rotação de chaves criptográficas sem perda de dados."""
    old_key = Fernet.generate_key().decode()
    new_key = Fernet.generate_key().decode()

    # Criptografa com a chave antiga
    old_manager = CryptoManager(old_key)
    secret = "SenhaImapAntiga123"
    cipher_old = old_manager.encrypt(secret)

    # Novo manager com rotação (chave primária nova, chave secundária antiga)
    rotation_manager = CryptoManager(new_key, fallback_keys=[old_key])

    # Consegue descriptografar cipher gerado pela chave antiga
    assert rotation_manager.decrypt(cipher_old) == secret

    # Rotaciona para nova chave
    re_encrypted = rotation_manager.rotate(cipher_old)
    assert re_encrypted != cipher_old

    # Novo ciphertext pode ser descriptografado apenas com a nova chave
    single_new_manager = CryptoManager(new_key)
    assert single_new_manager.decrypt(re_encrypted) == secret


def test_invalid_cipher_raises_error():
    """Verifica que dados corrompidos ou com chaves incorretas lançam erro."""
    other_key = Fernet.generate_key().decode()
    other_manager = CryptoManager(other_key)
    with pytest.raises(InvalidToken):
        other_manager.decrypt("gAAAAABmCorruptedDataStringThatIsNotValidToken12345678==")
