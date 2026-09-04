from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_seller
from app.core.crypto import decrypt_secret, encrypt_secret
from app.db.session import get_db
from app.models.imap_config import ImapConfig
from app.models.seller import Seller
from app.schemas.imap_config import ImapConfigCreate, ImapConfigOut, ImapTestRequest, ImapTestResponse
from app.services.imap_service import IMAPService

router = APIRouter(prefix="/api/v1/imap-configs", tags=["IMAP Config"])


@router.post("", response_model=ImapConfigOut)
def save_imap_config(
    payload: ImapConfigCreate,
    current_seller: Seller = Depends(get_current_seller),
    db: Session = Depends(get_db),
):
    """
    Cadastra ou atualiza as configurações do servidor IMAP do revendedor.
    A senha é criptografada com a chave simétrica Fernet antes de persistir no PostgreSQL.
    """
    config = db.query(ImapConfig).filter(ImapConfig.seller_id == current_seller.id).first()

    encrypted_pwd = encrypt_secret(payload.password)

    if config:
        config.host = payload.host
        config.port = payload.port
        config.username = payload.username
        config.encrypted_password = encrypted_pwd
        config.use_ssl = payload.use_ssl
    else:
        config = ImapConfig(
            seller_id=current_seller.id,
            host=payload.host,
            port=payload.port,
            username=payload.username,
            encrypted_password=encrypted_pwd,
            use_ssl=payload.use_ssl,
        )
        db.add(config)

    db.commit()
    db.refresh(config)
    return config


@router.get("", response_model=ImapConfigOut)
def get_imap_config(
    current_seller: Seller = Depends(get_current_seller),
    db: Session = Depends(get_db),
):
    """Retorna as configurações IMAP do revendedor (sem a senha)."""
    config = db.query(ImapConfig).filter(ImapConfig.seller_id == current_seller.id).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma configuração IMAP cadastrada para este revendedor.",
        )
    return config


@router.post("/test", response_model=ImapTestResponse)
def test_imap_connection(
    payload: ImapTestRequest,
    current_seller: Seller = Depends(get_current_seller),
    db: Session = Depends(get_db),
):
    """
    Testa a conectividade com o servidor IMAP do revendedor com isolamento total de erros.
    Se nenhuma senha for informada no body, utiliza a senha salva e descriptografa em memória.
    """
    password_to_test = payload.password
    if not password_to_test:
        config = db.query(ImapConfig).filter(ImapConfig.seller_id == current_seller.id).first()
        if not config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhuma senha salva encontrada. Forneça a senha no payload.",
            )
        try:
            password_to_test = decrypt_secret(config.encrypted_password)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao descriptografar credenciais salvas.",
            )

    success, message, response_time = IMAPService.test_connection(
        host=payload.host,
        port=payload.port,
        username=payload.username,
        password=password_to_test,
        use_ssl=payload.use_ssl,
        timeout=5,
    )

    return ImapTestResponse(
        success=success,
        message=message,
        response_time_ms=response_time,
    )
