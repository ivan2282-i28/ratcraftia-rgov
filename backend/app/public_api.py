from __future__ import annotations

from fastapi import Depends, FastAPI, Form, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from .core.security import get_current_user
from .db import get_session
from .models import User
from .schemas import OAuthAuthorizationRequest, OAuthAuthorizationResponse, OAuthTokenResponse, OAuthUserInfoResponse
from .services.oauth import (
    authorize_oauth_application,
    build_frontend_authorize_path,
    deny_oauth_application,
    exchange_oauth_authorization_code,
    get_current_oauth_identity,
    get_public_oauth_app,
    serialize_oauth_userinfo,
)

public_api = FastAPI(
    title="RGOV Public API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    description=(
        "Public OAuth 2.0 endpoints for third-party developers. "
        "Use the authorization-code flow to sign citizens into external apps with RGOV."
    ),
)


@public_api.get(
    "/oauth/authorize",
    summary="Start the OAuth authorization-code flow",
    response_description="Redirects the browser to the RGOV consent screen in the frontend.",
)
def start_oauth_authorization(
    client_id: str = Query(min_length=8, max_length=128),
    redirect_uri: str = Query(min_length=1, max_length=500),
    response_type: str = Query(default="code", pattern="^code$"),
    scope: str = Query(default="profile.basic", max_length=255),
    state: str | None = Query(default=None, max_length=255),
) -> RedirectResponse:
    payload = OAuthAuthorizationRequest(
        client_id=client_id,
        redirect_uri=redirect_uri,
        response_type=response_type,
        scope=scope,
        state=state,
    )
    try:
        return RedirectResponse(
            url=build_frontend_authorize_path(payload),
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@public_api.post("/oauth/token", response_model=OAuthTokenResponse, summary="Exchange an authorization code for an access token")
def oauth_token(
    grant_type: str = Form(...),
    client_id: str = Form(...),
    client_secret: str = Form(...),
    code: str = Form(...),
    redirect_uri: str = Form(...),
    session: Session = Depends(get_session),
) -> OAuthTokenResponse:
    try:
        return exchange_oauth_authorization_code(
            session,
            grant_type=grant_type,
            client_id=client_id,
            client_secret=client_secret,
            code=code,
            redirect_uri=redirect_uri,
        )
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@public_api.get("/userinfo", response_model=OAuthUserInfoResponse, summary="Read RGOV profile data for the current OAuth subject")
def oauth_userinfo(
    identity=Depends(get_current_oauth_identity),
    session: Session = Depends(get_session),
) -> OAuthUserInfoResponse:
    return serialize_oauth_userinfo(session, identity)


@public_api.get("/oauth/apps/{client_id}", include_in_schema=False)
def public_oauth_app_metadata(
    client_id: str,
    session: Session = Depends(get_session),
):
    try:
        return get_public_oauth_app(session, client_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@public_api.post("/oauth/authorize/complete", response_model=OAuthAuthorizationResponse, include_in_schema=False)
def complete_oauth_authorization(
    payload: OAuthAuthorizationRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> OAuthAuthorizationResponse:
    try:
        return authorize_oauth_application(session, user, payload)
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@public_api.post("/oauth/authorize/deny", response_model=OAuthAuthorizationResponse, include_in_schema=False)
def deny_authorization(
    payload: OAuthAuthorizationRequest,
    session: Session = Depends(get_session),
) -> OAuthAuthorizationResponse:
    try:
        return deny_oauth_application(session, payload)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
