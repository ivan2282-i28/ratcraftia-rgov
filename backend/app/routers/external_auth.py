from __future__ import annotations

from html import escape

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session

from ..core.security import bearer_scheme
from ..db import get_session
from ..schemas import (
    ExternalAuthApplicationRequest,
    ExternalAuthApplicationSecretResponse,
    ExternalAuthApplicationStatusResponse,
    ExternalAuthProfileResponse,
    OAuthTokenResponse,
)
from ..services.external_auth import (
    append_query_params,
    authenticate_user_for_oauth,
    build_oauth_error_redirect,
    create_external_auth_application,
    exchange_authorization_code,
    get_external_auth_application_status,
    get_external_auth_context,
    issue_authorization_code,
    serialize_external_auth_profile,
    validate_oauth_application,
)


router = APIRouter(prefix="/api/oauth", tags=["oauth"])


def _render_authorize_page(
    *,
    app_name: str,
    app_description: str,
    client_id: str,
    redirect_uri: str,
    state: str,
    error: str = "",
    identifier: str = "",
) -> HTMLResponse:
    error_block = ""
    if error:
        error_block = f"""
        <div style="margin-bottom:16px;padding:12px 14px;border-radius:14px;background:#ffe2dc;color:#7c1f12;">
          {escape(error)}
        </div>
        """
    html = f"""
    <!doctype html>
    <html lang="ru">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>RGOV OAuth</title>
      </head>
      <body style="margin:0;font-family:Arial,sans-serif;background:linear-gradient(135deg,#f3ecdf,#d6e4e2);color:#18211f;">
        <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px;">
          <div style="width:100%;max-width:520px;background:#fff;border-radius:28px;padding:28px;box-shadow:0 24px 60px rgba(24,33,31,0.12);">
            <div style="font-size:32px;font-weight:700;">RGOV OAuth 2.0</div>
            <div style="margin-top:8px;font-size:18px;color:#53615d;">Внешнее приложение запрашивает доступ к вашему профилю.</div>
            <div style="margin-top:22px;padding:16px;border-radius:18px;background:#f3f5f4;">
              <div style="font-weight:700;">{escape(app_name)}</div>
              <div style="margin-top:6px;color:#53615d;">{escape(app_description or 'Описание не указано.')}</div>
              <div style="margin-top:10px;font-size:14px;color:#53615d;">Client ID: {escape(client_id)}</div>
              <div style="margin-top:4px;font-size:14px;color:#53615d;">Redirect URI: {escape(redirect_uri)}</div>
            </div>
            <div style="margin-top:18px;padding:14px;border-radius:18px;background:#f7efe3;color:#5d4631;line-height:1.5;">
              После подтверждения приложение получит OAuth-код, а затем сможет обменять его на токен доступа к вашему базовому профилю RGOV.
            </div>
            <form method="post" action="/api/oauth/authorize" style="margin-top:20px;">
              <input type="hidden" name="response_type" value="code">
              <input type="hidden" name="client_id" value="{escape(client_id)}">
              <input type="hidden" name="redirect_uri" value="{escape(redirect_uri)}">
              <input type="hidden" name="state" value="{escape(state)}">
              {error_block}
              <label style="display:block;font-weight:600;margin-bottom:8px;">Логин или УИН</label>
              <input name="identifier" value="{escape(identifier)}" style="width:100%;box-sizing:border-box;padding:14px 16px;border:1px solid #cfd9d6;border-radius:16px;margin-bottom:14px;" placeholder="Например: root или 1.26.563372">
              <label style="display:block;font-weight:600;margin-bottom:8px;">Пароль или УАН</label>
              <input type="password" name="secret" style="width:100%;box-sizing:border-box;padding:14px 16px;border:1px solid #cfd9d6;border-radius:16px;margin-bottom:16px;" placeholder="Введите пароль или УАН">
              <div style="display:flex;gap:12px;flex-wrap:wrap;">
                <button type="submit" name="decision" value="approve" style="border:none;background:#2f6f63;color:#fff;padding:14px 18px;border-radius:16px;font-weight:700;cursor:pointer;">Разрешить доступ</button>
                <button type="submit" name="decision" value="deny" style="border:1px solid #c7d1ce;background:#fff;color:#20302c;padding:14px 18px;border-radius:16px;font-weight:700;cursor:pointer;">Отказать</button>
              </div>
            </form>
          </div>
        </div>
      </body>
    </html>
    """
    return HTMLResponse(html)


@router.post("/apps/request", response_model=ExternalAuthApplicationSecretResponse, status_code=status.HTTP_201_CREATED)
def request_application(
    payload: ExternalAuthApplicationRequest,
    session: Session = Depends(get_session),
) -> ExternalAuthApplicationSecretResponse:
    return create_external_auth_application(session, payload)


@router.get("/apps/{client_id}/status", response_model=ExternalAuthApplicationStatusResponse)
def application_status(
    client_id: str,
    session: Session = Depends(get_session),
) -> ExternalAuthApplicationStatusResponse:
    return get_external_auth_application_status(session, client_id)


@router.get("/authorize")
def authorize(
    response_type: str,
    client_id: str,
    redirect_uri: str,
    state: str = "",
    session: Session = Depends(get_session),
):
    try:
        application = validate_oauth_application(session, client_id, redirect_uri)
    except HTTPException as error:
        return HTMLResponse(str(error.detail), status_code=error.status_code)

    if response_type != "code":
        return RedirectResponse(
            build_oauth_error_redirect(
                redirect_uri,
                error="unsupported_response_type",
                error_description="Поддерживается только response_type=code.",
                state=state,
            ),
            status_code=status.HTTP_302_FOUND,
        )
    if not application.is_approved or not application.is_active:
        return RedirectResponse(
            build_oauth_error_redirect(
                redirect_uri,
                error="unauthorized_client",
                error_description="Приложение ещё не одобрено администратором RGOV.",
                state=state,
            ),
            status_code=status.HTTP_302_FOUND,
        )
    return _render_authorize_page(
        app_name=application.name,
        app_description=application.description,
        client_id=application.client_id,
        redirect_uri=application.redirect_uri,
        state=state,
    )


@router.post("/authorize")
def authorize_submit(
    response_type: str = Form(...),
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    state: str = Form(default=""),
    identifier: str = Form(default=""),
    secret: str = Form(default=""),
    decision: str = Form(default="approve"),
    session: Session = Depends(get_session),
):
    try:
        application = validate_oauth_application(session, client_id, redirect_uri)
    except HTTPException as error:
        return HTMLResponse(str(error.detail), status_code=error.status_code)

    if response_type != "code":
        return RedirectResponse(
            build_oauth_error_redirect(
                redirect_uri,
                error="unsupported_response_type",
                error_description="Поддерживается только response_type=code.",
                state=state,
            ),
            status_code=status.HTTP_302_FOUND,
        )
    if not application.is_approved or not application.is_active:
        return RedirectResponse(
            build_oauth_error_redirect(
                redirect_uri,
                error="unauthorized_client",
                error_description="Приложение ещё не одобрено администратором RGOV.",
                state=state,
            ),
            status_code=status.HTTP_302_FOUND,
        )
    if decision != "approve":
        return RedirectResponse(
            build_oauth_error_redirect(
                redirect_uri,
                error="access_denied",
                error_description="Пользователь отказал в доступе.",
                state=state,
            ),
            status_code=status.HTTP_302_FOUND,
        )

    try:
        user = authenticate_user_for_oauth(session, identifier, secret)
    except HTTPException as error:
        return _render_authorize_page(
            app_name=application.name,
            app_description=application.description,
            client_id=application.client_id,
            redirect_uri=application.redirect_uri,
            state=state,
            error=str(error.detail),
            identifier=identifier,
        )

    code = issue_authorization_code(session, application, user, redirect_uri)
    return RedirectResponse(
        append_query_params(
            redirect_uri,
            {"code": code, "state": state},
        ),
        status_code=status.HTTP_302_FOUND,
    )


@router.post("/token", response_model=OAuthTokenResponse)
def create_token(
    grant_type: str = Form(...),
    code: str = Form(...),
    redirect_uri: str = Form(...),
    client_id: str = Form(...),
    client_secret: str = Form(...),
    session: Session = Depends(get_session),
) -> OAuthTokenResponse:
    return exchange_authorization_code(
        session,
        grant_type=grant_type,
        code=code,
        redirect_uri=redirect_uri,
        client_id=client_id,
        client_secret=client_secret,
    )


@router.get("/me", response_model=ExternalAuthProfileResponse)
def external_profile(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> ExternalAuthProfileResponse:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется внешний токен авторизации.",
        )
    user, _ = get_external_auth_context(session, credentials.credentials)
    return serialize_external_auth_profile(session, user)
