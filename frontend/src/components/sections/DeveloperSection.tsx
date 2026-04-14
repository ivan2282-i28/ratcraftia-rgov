import * as React from "react";
import {
  Alert,
  Button,
  Checkbox,
  Chip,
  FormControlLabel,
  Link,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import KeyRoundedIcon from "@mui/icons-material/KeyRounded";
import LaunchRoundedIcon from "@mui/icons-material/LaunchRounded";
import VerifiedRoundedIcon from "@mui/icons-material/VerifiedRounded";
import WarningAmberRoundedIcon from "@mui/icons-material/WarningAmberRounded";
import type {
  DeveloperAppRead,
  DeveloperScopeRead,
  PublicOAuthAppRead,
} from "../../types";
import { formatDateTime } from "../../lib/format";
import { EmptyState, HeroCard, ResponsiveGrid, SectionCard } from "../common";

type DeveloperAppForm = {
  name: string;
  slug: string;
  description: string;
  websiteUrl: string;
  redirectUris: string;
  allowedScopes: string[];
};

type LatestSecretState = {
  label: string;
  clientId: string;
  clientSecret: string;
  rotatedAt: string;
} | null;

type OAuthRequestState = {
  clientId: string;
  redirectUri: string;
  responseType: "code";
  scope: string;
  scopes: string[];
  state?: string;
} | null;

function appStatusLabel(status: DeveloperAppRead["status"] | PublicOAuthAppRead["status"]) {
  switch (status) {
    case "approved":
      return "Одобрено";
    case "rejected":
      return "Отклонено";
    case "revoked":
      return "Отозвано";
    default:
      return "На модерации";
  }
}

function appStatusColor(status: DeveloperAppRead["status"] | PublicOAuthAppRead["status"]) {
  switch (status) {
    case "approved":
      return "success";
    case "rejected":
      return "error";
    case "revoked":
      return "warning";
    default:
      return "default";
  }
}

export function DeveloperSection(props: {
  developerApps: DeveloperAppRead[];
  oauthScopes: DeveloperScopeRead[];
  createAppForm: DeveloperAppForm;
  setCreateAppForm: React.Dispatch<React.SetStateAction<DeveloperAppForm>>;
  latestSecret: LatestSecretState;
  oauthRequest: OAuthRequestState;
  oauthRequestApp: PublicOAuthAppRead | null;
  oauthRequestLoading: boolean;
  oauthRequestError: string | null;
  submitting: boolean;
  onCreateApp: () => void;
  onRotateSecret: (appId: number) => void;
  onApproveOAuthRequest: () => void;
  onDenyOAuthRequest: () => void;
}) {
  const origin = typeof window === "undefined" ? "" : window.location.origin;
  const docsUrl = `${origin}/api/public/docs`;
  const authorizeUrl = `${origin}/api/public/oauth/authorize`;
  const tokenUrl = `${origin}/api/public/oauth/token`;
  const userinfoUrl = `${origin}/api/public/userinfo`;

  return (
    <Stack spacing={2.5}>
      <HeroCard
        title="Разработчикам"
        description="Регистрируйте внешние приложения, проходите административное одобрение и подключайте OAuth-вход через RGOV."
        chips={[
          `${props.developerApps.length} приложений`,
          `${props.oauthScopes.length} доступных scope`,
          "Public docs /api/public/docs",
        ]}
      />

      {props.oauthRequest && (
        <SectionCard
          title="OAuth-разрешение"
          subtitle="Эта карточка открывается, когда внешнее приложение отправляет пользователя в RGOV для авторизации."
        >
          <Stack spacing={1.5}>
            {props.oauthRequestLoading && <Alert severity="info">Проверяем параметры OAuth-приложения.</Alert>}
            {props.oauthRequestError && <Alert severity="error">{props.oauthRequestError}</Alert>}
            {props.oauthRequestApp && (
              <>
                <Stack direction={{ xs: "column", md: "row" }} spacing={1} alignItems={{ md: "center" }}>
                  <Typography variant="h6">{props.oauthRequestApp.name}</Typography>
                  <Chip
                    icon={
                      props.oauthRequestApp.status === "approved" ? (
                        <VerifiedRoundedIcon />
                      ) : (
                        <WarningAmberRoundedIcon />
                      )
                    }
                    color={appStatusColor(props.oauthRequestApp.status)}
                    label={appStatusLabel(props.oauthRequestApp.status)}
                    variant="outlined"
                  />
                </Stack>
                <Typography variant="body2" color="text.secondary">
                  Владелец: {props.oauthRequestApp.owner_name}
                </Typography>
                <Typography variant="body2">
                  {props.oauthRequestApp.description || "Описание приложения не указано."}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Redirect URI: {props.oauthRequest.redirectUri}
                </Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                  {props.oauthRequest.scopes.map((scope) => (
                    <Chip key={scope} label={scope} />
                  ))}
                </Stack>
                {props.oauthRequestApp.status !== "approved" && (
                  <Alert severity="warning">
                    Пока администратор RGOV не одобрит приложение, выдать ему доступ нельзя.
                  </Alert>
                )}
                <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
                  <Button
                    variant="contained"
                    disabled={
                      props.submitting ||
                      props.oauthRequestLoading ||
                      !props.oauthRequestApp ||
                      props.oauthRequestApp.status !== "approved"
                    }
                    onClick={props.onApproveOAuthRequest}
                  >
                    Разрешить доступ
                  </Button>
                  <Button
                    variant="text"
                    color="error"
                    disabled={props.submitting || props.oauthRequestLoading}
                    onClick={props.onDenyOAuthRequest}
                  >
                    Отклонить
                  </Button>
                </Stack>
              </>
            )}
          </Stack>
        </SectionCard>
      )}

      {props.latestSecret && (
        <Alert severity="success" icon={<KeyRoundedIcon />}>
          <Stack spacing={0.75}>
            <Typography variant="subtitle2">{props.latestSecret.label}</Typography>
            <Typography variant="body2">Client ID: {props.latestSecret.clientId}</Typography>
            <Typography variant="body2" sx={{ wordBreak: "break-all" }}>
              Client secret: {props.latestSecret.clientSecret}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Секрет показан один раз. Сохраните его у себя в менеджере секретов. {formatDateTime(props.latestSecret.rotatedAt)}
            </Typography>
          </Stack>
        </Alert>
      )}

      <ResponsiveGrid columns={{ xs: "1fr", xl: "420px minmax(0, 1fr)" }}>
        <SectionCard
          title="Регистрация приложения"
          subtitle="После создания приложение попадает на одобрение администратору RGOV."
        >
          <Stack spacing={1.25}>
            <TextField
              label="Название"
              value={props.createAppForm.name}
              onChange={(event) =>
                props.setCreateAppForm((current) => ({
                  ...current,
                  name: event.target.value,
                }))
              }
            />
            <TextField
              label="Slug"
              helperText="Латиница, цифры и дефисы."
              value={props.createAppForm.slug}
              onChange={(event) =>
                props.setCreateAppForm((current) => ({
                  ...current,
                  slug: event.target.value,
                }))
              }
            />
            <TextField
              label="Website URL"
              placeholder="https://app.example.com"
              value={props.createAppForm.websiteUrl}
              onChange={(event) =>
                props.setCreateAppForm((current) => ({
                  ...current,
                  websiteUrl: event.target.value,
                }))
              }
            />
            <TextField
              label="Описание"
              multiline
              minRows={3}
              value={props.createAppForm.description}
              onChange={(event) =>
                props.setCreateAppForm((current) => ({
                  ...current,
                  description: event.target.value,
                }))
              }
            />
            <TextField
              label="Redirect URIs"
              multiline
              minRows={4}
              placeholder={"https://app.example.com/callback\nhttp://localhost:3000/callback"}
              value={props.createAppForm.redirectUris}
              onChange={(event) =>
                props.setCreateAppForm((current) => ({
                  ...current,
                  redirectUris: event.target.value,
                }))
              }
              helperText="Один URI на строку."
            />
            <Stack spacing={0.5}>
              <Typography variant="subtitle2">Разрешённые scope</Typography>
              {props.oauthScopes.map((scope) => {
                const checked = props.createAppForm.allowedScopes.includes(scope.scope);
                const disableUncheck =
                  scope.scope === "profile.basic" &&
                  checked &&
                  props.createAppForm.allowedScopes.length === 1;
                return (
                  <FormControlLabel
                    key={scope.scope}
                    control={
                      <Checkbox
                        checked={checked}
                        disabled={disableUncheck}
                        onChange={(_, nextChecked) =>
                          props.setCreateAppForm((current) => ({
                            ...current,
                            allowedScopes: nextChecked
                              ? [...current.allowedScopes, scope.scope]
                              : current.allowedScopes.filter((item) => item !== scope.scope),
                          }))
                        }
                      />
                    }
                    label={`${scope.scope} — ${scope.description}`}
                  />
                );
              })}
            </Stack>
            <Button
              variant="contained"
              disabled={
                props.submitting ||
                !props.createAppForm.name.trim() ||
                !props.createAppForm.slug.trim() ||
                !props.createAppForm.redirectUris.trim()
              }
              onClick={props.onCreateApp}
            >
              Создать приложение
            </Button>
          </Stack>
        </SectionCard>

        <Stack spacing={2.5}>
          <SectionCard
            title="Интеграция"
            subtitle="Публичная OAuth/OpenAPI документация доступна без входа."
            action={
              <Link href={docsUrl} target="_blank" rel="noreferrer" underline="hover">
                <Stack direction="row" spacing={0.5} alignItems="center">
                  <LaunchRoundedIcon fontSize="small" />
                  <span>Docs</span>
                </Stack>
              </Link>
            }
          >
            <Stack spacing={1.25}>
              <Paper variant="outlined" sx={{ p: 1.5, borderRadius: 4 }}>
                <Typography variant="subtitle2">1. Отправьте пользователя в authorize endpoint</Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.75, wordBreak: "break-all" }}>
                  {authorizeUrl}?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_CALLBACK&response_type=code&scope=profile.basic&state=opaque
                </Typography>
              </Paper>
              <Paper variant="outlined" sx={{ p: 1.5, borderRadius: 4 }}>
                <Typography variant="subtitle2">2. Обменяйте code на access token</Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.75, wordBreak: "break-all" }}>
                  POST {tokenUrl}
                </Typography>
              </Paper>
              <Paper variant="outlined" sx={{ p: 1.5, borderRadius: 4 }}>
                <Typography variant="subtitle2">3. Запросите профиль пользователя</Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.75, wordBreak: "break-all" }}>
                  GET {userinfoUrl}
                </Typography>
              </Paper>
            </Stack>
          </SectionCard>

          <SectionCard
            title="Мои приложения"
            subtitle="Статус модерации, client_id и зарегистрированные callback-адреса."
          >
            <Stack spacing={1.25}>
              {props.developerApps.map((application) => (
                <Paper key={application.id} variant="outlined" sx={{ p: 1.75, borderRadius: 4 }}>
                  <Stack spacing={1}>
                    <Stack direction={{ xs: "column", sm: "row" }} spacing={1} justifyContent="space-between">
                      <Stack spacing={0.4}>
                        <Typography variant="subtitle1">{application.name}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {application.slug} · {application.client_id}
                        </Typography>
                      </Stack>
                      <Chip
                        label={appStatusLabel(application.status)}
                        color={appStatusColor(application.status)}
                        variant="outlined"
                      />
                    </Stack>
                    <Typography variant="body2">
                      {application.description || "Описание не указано."}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Scope: {application.allowed_scopes.join(", ")}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Redirect URIs: {application.redirect_uris.join(" · ")}
                    </Typography>
                    {application.review_note && (
                      <Alert severity={application.status === "approved" ? "success" : "info"}>
                        {application.review_note}
                      </Alert>
                    )}
                    <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
                      <Button
                        variant="outlined"
                        onClick={() => props.onRotateSecret(application.id)}
                        disabled={props.submitting}
                      >
                        Повернуть секрет
                      </Button>
                      {application.website_url && (
                        <Link href={application.website_url} target="_blank" rel="noreferrer" underline="hover">
                          <Button variant="text">Открыть сайт</Button>
                        </Link>
                      )}
                    </Stack>
                  </Stack>
                </Paper>
              ))}
              {props.developerApps.length === 0 && (
                <EmptyState text="У вас пока нет зарегистрированных OAuth-приложений." />
              )}
            </Stack>
          </SectionCard>
        </Stack>
      </ResponsiveGrid>
    </Stack>
  );
}
