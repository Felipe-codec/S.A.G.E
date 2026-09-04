from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.crypto import decrypt_secret
from app.core.logging import logger
from app.core.security import hash_token, mask_ip_address, mask_steam_code
from app.db.session import get_db
from app.models.code_request import CodeRequest
from app.models.imap_config import ImapConfig
from app.models.redemption_session import RedemptionSession
from app.models.redemption_token import RedemptionToken
from app.models.steam_account import SteamAccount
from app.schemas.redemption import CodeRequestPayload, CodeResponse, RedemptionInfoResponse
from app.services.imap_service import (
    IMAPAuthenticationError,
    IMAPConnectionError,
    IMAPService,
    IMAPTimeoutError,
    SteamCodeNotFoundError,
)
from app.services.rate_limit_service import get_rate_limit_service

router = APIRouter(prefix="/resgate", tags=["Public Redemption"])


@router.get("/{raw_token}/info", response_model=RedemptionInfoResponse)
def get_redemption_info(raw_token: str, db: Session = Depends(get_db)):
    """
    Retorna metadados do token para a tela pública do comprador.
    Valida vigência, expiração e usos restantes.
    """
    token_hashed = hash_token(raw_token)
    token_record = (
        db.query(RedemptionToken)
        .filter(RedemptionToken.token_hash == token_hashed)
        .first()
    )

    if not token_record or not token_record.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link de resgate inválido ou revogado.",
        )

    now = datetime.now(timezone.utc)
    if token_record.expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Este link de resgate expirou. Solicite um novo link ao vendedor.",
        )

    if token_record.current_uses >= token_record.max_uses:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="O limite de resgates para este link já foi atingido.",
        )

    account = db.query(SteamAccount).filter(SteamAccount.id == token_record.steam_account_id).first()
    if not account or not account.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta Steam associada não está disponível.",
        )

    remaining_uses = token_record.max_uses - token_record.current_uses

    return RedemptionInfoResponse(
        valid=True,
        steam_username=account.username,
        display_name=account.display_name,
        expires_at=token_record.expires_at,
        remaining_uses=remaining_uses,
    )


@router.post("/{raw_token}/code", response_model=CodeResponse)
def request_steam_code(
    raw_token: str,
    payload: CodeRequestPayload,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Endpoint de alta demanda para obtenção do código Steam Guard em tempo real.
    Aplica rate limiting estrito por IP e por token para evitar abuso e bloqueio no IMAP.
    """
    client_ip = request.client.host if request.client else "unknown"
    masked_ip = mask_ip_address(client_ip)

    # 1. Rate Limiting específico para resgate de código (ex: 5 reqs/min por IP/token)
    rate_limiter = get_rate_limit_service()
    rate_limit_key = f"redemption:{client_ip}:{raw_token[:8]}"
    is_limited, retry_after = rate_limiter.check_rate_limit(rate_limit_key, max_requests=5, window_seconds=60)
    if is_limited:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Muitas solicitações seguidas. Aguarde {retry_after} segundos antes de tentar novamente.",
            headers={"Retry-After": str(retry_after)},
        )

    # 2. Validação do Token
    token_hashed = hash_token(raw_token)
    token_record = (
        db.query(RedemptionToken)
        .filter(RedemptionToken.token_hash == token_hashed)
        .first()
    )

    if not token_record or not token_record.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link de resgate inválido ou expirado.",
        )

    now = datetime.now(timezone.utc)
    if token_record.expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Este link de resgate expirou.",
        )

    if token_record.current_uses >= token_record.max_uses:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="O limite de resgates para este token foi esgotado.",
        )

    # 3. Busca a conta Steam e as configurações IMAP do vendedor
    account = db.query(SteamAccount).filter(SteamAccount.id == token_record.steam_account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conta Steam não encontrada."
        )

    imap_config = db.query(ImapConfig).filter(ImapConfig.seller_id == token_record.seller_id).first()
    if not imap_config:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="O revendedor ainda não configurou o serviço de e-mail IMAP.",
        )

    # 4. Descriptografa a senha IMAP em memória no momento do uso
    try:
        decrypted_imap_password = decrypt_secret(imap_config.encrypted_password)
    except Exception as e:
        logger.error(f"Erro ao descriptografar senha IMAP para seller {token_record.seller_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Falha ao processar credenciais de resgate.",
        )

    # 5. Executa a busca segura no servidor IMAP
    start_time = datetime.now(timezone.utc)
    code_found = None
    duration_ms = 0
    request_status = "PENDING"
    error_msg = None

    try:
        code_found, duration_ms = IMAPService.fetch_steam_guard_code(
            host=imap_config.host,
            port=imap_config.port,
            username=imap_config.username,
            password=decrypted_imap_password,
            steam_username=account.username,
            use_ssl=imap_config.use_ssl,
            timeout=settings.IMAP_TIMEOUT,
            poll_interval=settings.CODE_POLL_INTERVAL,
            poll_timeout=settings.CODE_POLL_TIMEOUT,
        )
        request_status = "SUCCESS"

        # Incrementa contador de uso do token
        token_record.current_uses += 1

    except IMAPTimeoutError as e:
        request_status = "TIMEOUT"
        error_msg = str(e)
        logger.warning(f"Timeout buscando código Steam para {account.username} (IP: {masked_ip})")
    except IMAPAuthenticationError as e:
        request_status = "IMAP_ERROR"
        error_msg = f"Falha de autenticação IMAP: {e}"
        logger.error(f"Erro de autenticação IMAP no seller {token_record.seller_id}")
    except (IMAPConnectionError, Exception) as e:
        request_status = "IMAP_ERROR"
        error_msg = f"Erro de conexão IMAP: {e}"
        logger.error(f"Falha de conexão IMAP: {e}")

    # 6. Registra a auditoria da solicitação no banco (código é sempre mascarado no log e no banco!)
    masked_code = mask_steam_code(code_found) if code_found else None
    audit_record = CodeRequest(
        steam_account_id=account.id,
        token_id=token_record.id,
        requested_at=start_time,
        status=request_status,
        code_found_masked=masked_code,
        search_duration_ms=duration_ms,
        error_message=error_msg,
    )
    db.add(audit_record)
    db.commit()

    # 7. Retorna a resposta ao usuário
    if request_status == "SUCCESS" and code_found:
        return CodeResponse(
            success=True,
            code=code_found,
            message="Código Steam Guard localizado com sucesso!",
            expires_in_seconds=60,
            search_duration_ms=duration_ms,
        )
    elif request_status == "TIMEOUT":
        return CodeResponse(
            success=False,
            code=None,
            message="O código ainda não chegou no e-mail. Tente fazer login na Steam novamente e clique no botão para atualizar.",
            expires_in_seconds=0,
            search_duration_ms=duration_ms,
        )
    else:
        return CodeResponse(
            success=False,
            code=None,
            message="Não foi possível sincronizar com a caixa de e-mail no momento. Tente novamente em instantes.",
            expires_in_seconds=0,
            search_duration_ms=duration_ms,
        )
