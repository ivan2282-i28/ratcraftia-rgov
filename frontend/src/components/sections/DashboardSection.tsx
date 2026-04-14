import * as React from "react";
import {
  Button,
  Chip,
  Divider,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import ContentCopyRoundedIcon from "@mui/icons-material/ContentCopyRounded";
import MailRoundedIcon from "@mui/icons-material/MailRounded";
import NotificationsRoundedIcon from "@mui/icons-material/NotificationsRounded";
import SavingsRoundedIcon from "@mui/icons-material/SavingsRounded";
import VerifiedRoundedIcon from "@mui/icons-material/VerifiedRounded";
import type {
  DidTokenResponse,
  NewsRead,
  PushConfigResponse,
  PushStatus,
  UserRead,
} from "../../types";
import { formatDateTime, formatNumber, shortToken } from "../../lib/format";
import { HeroCard, InfoRow, MetricCard, ResponsiveGrid, SectionCard, EmptyState } from "../common";

type AccessForm = {
  newLogin: string;
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
};

export function DashboardSection(props: {
  profile: UserRead;
  did: DidTokenResponse | null;
  news: NewsRead[];
  pushConfig: PushConfigResponse | null;
  pushStatus: PushStatus;
  accessForm: AccessForm;
  setAccessForm: React.Dispatch<React.SetStateAction<AccessForm>>;
  submitting: boolean;
  onCopyDid: () => Promise<void>;
  onChangeLogin: () => void;
  onChangePassword: () => void;
  onEnablePush: () => void;
  onDisablePush: () => void;
  onPreviewPush: () => void;
  onOpenNews: () => void;
}) {
  const pushEnabled =
    props.pushStatus.supported &&
    props.pushStatus.permission === "granted" &&
    props.pushStatus.subscribed;

  return (
    <Stack spacing={2.5}>
      <HeroCard
        title="Единый гражданский портал"
        description="Все основные государственные потоки собраны в одной Material UI оболочке: вход, профиль, сообщения, парламент, законы и Ratubles."
        chips={[
          `${props.news.length} новостей`,
          props.profile.permissions_label,
          `${formatNumber(props.profile.ratubles)} Ratubles`,
        ]}
      />
      <ResponsiveGrid>
        <MetricCard
          title="Ratubles"
          value={formatNumber(props.profile.ratubles)}
          description="Личный баланс"
          icon={<SavingsRoundedIcon />}
          accent="primary"
        />
        <MetricCard
          title="Логин"
          value={props.profile.login}
          description="Активная учётная запись"
          icon={<MailRoundedIcon />}
          accent="secondary"
        />
        <MetricCard
          title="Права доступа"
          value={props.profile.permissions_label}
          description="Роль и полномочия"
          icon={<VerifiedRoundedIcon />}
          accent="neutral"
        />
      </ResponsiveGrid>
      <ResponsiveGrid columns={{ xs: "1fr", lg: "1.25fr 1fr" }}>
        <SectionCard
          title="Личная DID-карта"
          subtitle="Короткоживущий токен можно использовать во внутренних сценариях идентификации."
          action={
            props.did && (
              <Button
                size="small"
                startIcon={<ContentCopyRoundedIcon />}
                onClick={() => void props.onCopyDid()}
              >
                Скопировать токен
              </Button>
            )
          }
        >
          <Stack spacing={1.2}>
            <InfoRow label="ФИО" value={props.profile.full_name} />
            <InfoRow label="Логин" value={props.profile.login} />
            <InfoRow label="УИН" value={props.profile.uin} />
            <InfoRow label="УАН" value={props.profile.uan} />
            <InfoRow label="Истекает" value={formatDateTime(props.did?.expires_at)} />
            <Divider sx={{ my: 1 }} />
            <Typography variant="body2" color="text.secondary">
              {shortToken(props.did?.token ?? "Токен загружается")}
            </Typography>
          </Stack>
        </SectionCard>
        <SectionCard
          title="Push-уведомления"
          subtitle={props.pushStatus.message}
          action={<NotificationsRoundedIcon color="primary" />}
        >
          <Stack spacing={1.25}>
            <Chip
              label={pushEnabled ? "Уведомления активны" : "Уведомления выключены"}
              color={pushEnabled ? "success" : "default"}
              variant={pushEnabled ? "filled" : "outlined"}
            />
            {props.pushConfig ? (
              <Typography variant="body2" color="text.secondary">
                Контакт VAPID: {props.pushConfig.contact_email}
              </Typography>
            ) : (
              <Typography variant="body2" color="text.secondary">
                Сервер push не настроен.
              </Typography>
            )}
            <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
              <Button
                variant="contained"
                disabled={!props.pushConfig || props.submitting}
                onClick={props.onEnablePush}
              >
                Включить
              </Button>
              <Button
                variant="outlined"
                disabled={!props.pushConfig || props.submitting}
                onClick={props.onDisablePush}
              >
                Отключить
              </Button>
              <Button
                variant="text"
                disabled={!props.pushConfig || props.submitting}
                onClick={props.onPreviewPush}
              >
                Тест
              </Button>
            </Stack>
          </Stack>
        </SectionCard>
      </ResponsiveGrid>
      <ResponsiveGrid>
        <SectionCard
          title="Профиль доступа"
          subtitle="Смена логина ограничена одним разом в сутки по часовому поясу сервера."
        >
          <Stack spacing={1.25}>
            <InfoRow
              label="Следующая смена логина"
              value={formatDateTime(props.profile.next_login_change_at)}
            />
            <TextField
              label="Новый логин"
              value={props.accessForm.newLogin}
              onChange={(event) =>
                props.setAccessForm((current) => ({
                  ...current,
                  newLogin: event.target.value,
                }))
              }
            />
            <Button
              variant="contained"
              disabled={!props.accessForm.newLogin.trim() || props.submitting}
              onClick={props.onChangeLogin}
            >
              Сменить логин
            </Button>
            <Divider sx={{ my: 1 }} />
            <TextField
              label="Текущий пароль"
              type="password"
              value={props.accessForm.currentPassword}
              onChange={(event) =>
                props.setAccessForm((current) => ({
                  ...current,
                  currentPassword: event.target.value,
                }))
              }
            />
            <TextField
              label="Новый пароль"
              type="password"
              value={props.accessForm.newPassword}
              onChange={(event) =>
                props.setAccessForm((current) => ({
                  ...current,
                  newPassword: event.target.value,
                }))
              }
            />
            <TextField
              label="Подтвердите новый пароль"
              type="password"
              value={props.accessForm.confirmPassword}
              onChange={(event) =>
                props.setAccessForm((current) => ({
                  ...current,
                  confirmPassword: event.target.value,
                }))
              }
              error={
                Boolean(props.accessForm.confirmPassword) &&
                props.accessForm.newPassword !== props.accessForm.confirmPassword
              }
              helperText={
                Boolean(props.accessForm.confirmPassword) &&
                props.accessForm.newPassword !== props.accessForm.confirmPassword
                  ? "Пароли должны совпадать."
                  : "Минимум 6 символов."
              }
            />
            <Button
              variant="outlined"
              disabled={
                !props.accessForm.currentPassword ||
                !props.accessForm.newPassword ||
                props.accessForm.newPassword !== props.accessForm.confirmPassword ||
                props.submitting
              }
              onClick={props.onChangePassword}
            >
              Обновить пароль
            </Button>
          </Stack>
        </SectionCard>
        <SectionCard
          title="Последние новости"
          subtitle="Короткая лента официальных публикаций."
          action={
            <Button size="small" onClick={props.onOpenNews}>
              Открыть раздел
            </Button>
          }
        >
          <Stack spacing={1.25}>
            {props.news.slice(0, 3).map((item) => (
              <Paper key={item.id} variant="outlined" sx={{ p: 2, borderRadius: 4 }}>
                <Typography variant="h6">{item.title}</Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  {item.author_name} · {formatDateTime(item.created_at)}
                </Typography>
                <Typography variant="body2">
                  {item.body.slice(0, 200)}
                  {item.body.length > 200 ? "…" : ""}
                </Typography>
              </Paper>
            ))}
            {props.news.length === 0 && (
              <EmptyState text="Пока нет опубликованных новостей." />
            )}
          </Stack>
        </SectionCard>
      </ResponsiveGrid>
    </Stack>
  );
}
