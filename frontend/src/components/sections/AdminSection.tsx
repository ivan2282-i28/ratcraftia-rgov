import * as React from "react";
import {
  Alert,
  Button,
  Chip,
  FormControlLabel,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  MenuItem,
  Paper,
  Stack,
  Switch,
  TextField,
  Typography,
} from "@mui/material";
import GavelRoundedIcon from "@mui/icons-material/GavelRounded";
import PersonAddAltRoundedIcon from "@mui/icons-material/PersonAddAltRounded";
import GroupsRoundedIcon from "@mui/icons-material/GroupsRounded";
import ApartmentRoundedIcon from "@mui/icons-material/ApartmentRounded";
import HistoryRoundedIcon from "@mui/icons-material/HistoryRounded";
import VpnKeyRoundedIcon from "@mui/icons-material/VpnKeyRounded";
import ChevronRightRoundedIcon from "@mui/icons-material/ChevronRightRounded";
import ShieldRoundedIcon from "@mui/icons-material/ShieldRounded";
import type { AdminLogRead, DeveloperAppRead, LawRead, OrganizationRead, UserRead } from "../../types";
import { formatDateTime, formatNumber } from "../../lib/format";
import { EmptyState, HeroCard, ResponsiveGrid, SectionCard } from "../common";

type AdminTreeNode =
  | "laws"
  | "constitution"
  | "users"
  | "organizations"
  | "oauth_apps"
  | "logs";

type CreateUserForm = {
  uin: string;
  uan: string;
  login: string;
  password: string;
  firstName: string;
  lastName: string;
  patronymic: string;
  permissions: string;
  orgSlug: string;
  positionTitle: string;
};

type UserEditForm = {
  uin: string;
  uan: string;
  firstName: string;
  lastName: string;
  patronymic: string;
  permissions: string;
  orgSlug: string;
  positionTitle: string;
};

type OrganizationForm = {
  name: string;
  slug: string;
  description: string;
};

type LawEditForm = {
  title: string;
  slug: string;
  level: string;
  status: string;
  adoptedVia: string;
  currentText: string;
  reason: string;
};

function TreeNodeButton(props: {
  label: string;
  selected: boolean;
  icon: React.ReactNode;
  depth?: number;
  onClick: () => void;
}) {
  return (
    <ListItemButton
      selected={props.selected}
      onClick={props.onClick}
      sx={{
        pl: 2 + (props.depth ?? 0) * 2,
        borderRadius: 3,
        mb: 0.5,
      }}
    >
      <ListItemIcon sx={{ minWidth: 38 }}>{props.icon}</ListItemIcon>
      <ListItemText primary={props.label} />
      <ChevronRightRoundedIcon fontSize="small" />
    </ListItemButton>
  );
}

function appStatusColor(status: DeveloperAppRead["status"]) {
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

export function AdminSection(props: {
  visible: boolean;
  activeNode: AdminTreeNode;
  setActiveNode: React.Dispatch<React.SetStateAction<AdminTreeNode>>;
  laws: LawRead[];
  users: UserRead[];
  organizations: OrganizationRead[];
  adminLogs: AdminLogRead[];
  oauthApps: DeveloperAppRead[];
  createUserForm: CreateUserForm;
  setCreateUserForm: React.Dispatch<React.SetStateAction<CreateUserForm>>;
  selectedUserId: number | "";
  setSelectedUserId: React.Dispatch<React.SetStateAction<number | "">>;
  selectedUser: UserRead | null;
  userEditForm: UserEditForm;
  setUserEditForm: React.Dispatch<React.SetStateAction<UserEditForm>>;
  selectedLawId: number | "";
  setSelectedLawId: React.Dispatch<React.SetStateAction<number | "">>;
  selectedLaw: LawRead | null;
  lawEditForm: LawEditForm;
  setLawEditForm: React.Dispatch<React.SetStateAction<LawEditForm>>;
  organizationForm: OrganizationForm;
  setOrganizationForm: React.Dispatch<React.SetStateAction<OrganizationForm>>;
  permissionPresets: Array<{ label: string; value: string }>;
  canUseOverwriteMode: boolean;
  overwriteMode: boolean;
  setOverwriteMode: React.Dispatch<React.SetStateAction<boolean>>;
  canReadUsers: boolean;
  canCreateUsers: boolean;
  canUpdateUsers: boolean;
  canWritePermissions: boolean;
  canManagePersonnel: boolean;
  canCreateOrganizations: boolean;
  canReadAdminLogs: boolean;
  canReadOAuthApps: boolean;
  canReviewOAuthApps: boolean;
  submitting: boolean;
  onCreateUser: () => void;
  onUpdateUser: () => void;
  onUpdatePermissions: () => void;
  onHire: () => void;
  onFire: () => void;
  onCreateOrganization: () => void;
  onReviewOAuthApp: (
    appId: number,
    status: "approved" | "rejected" | "revoked",
    reviewNote: string,
  ) => void;
  onOverwriteLaw: () => void;
}) {
  const [oauthReviewNotes, setOauthReviewNotes] = React.useState<Record<number, string>>({});
  const constitutionLaw =
    props.laws.find((law) => law.level === "constitution") ?? null;
  const rootOverride = props.canUseOverwriteMode && props.overwriteMode;

  const openNode = (node: AdminTreeNode) => {
    props.setActiveNode(node);
    if (node === "constitution" && constitutionLaw) {
      props.setSelectedLawId(constitutionLaw.id);
    }
  };

  const lawsContent = (
    <SectionCard
      title={props.activeNode === "constitution" ? "Конституция" : "Законы"}
      subtitle="Официально опубликованные акты RGOV. В overwrite mode можно менять их напрямую."
    >
      <ResponsiveGrid columns={{ xs: "1fr", xl: "320px minmax(0, 1fr)" }}>
        <Stack spacing={1.25}>
          {props.laws.map((law) => (
            <Paper
              key={law.id}
              variant="outlined"
              sx={{
                p: 1.5,
                borderRadius: 4,
                cursor: "pointer",
                borderColor: law.id === props.selectedLawId ? "primary.main" : undefined,
              }}
              onClick={() => {
                props.setSelectedLawId(law.id);
                props.setActiveNode(law.level === "constitution" ? "constitution" : "laws");
              }}
            >
              <Stack spacing={0.45}>
                <Stack direction={{ xs: "column", sm: "row" }} justifyContent="space-between" spacing={1}>
                  <Typography variant="subtitle1">{law.title}</Typography>
                  <Chip label={`${law.level} · v${law.version}`} size="small" variant="outlined" />
                </Stack>
                <Typography variant="body2" color="text.secondary">
                  {law.slug}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Обновлено {formatDateTime(law.updated_at)}
                </Typography>
              </Stack>
            </Paper>
          ))}
          {props.laws.length === 0 && <EmptyState text="Законы пока не опубликованы." />}
        </Stack>
        {props.selectedLaw ? (
          <Stack spacing={1.25}>
            <TextField
              label="Название"
              value={props.lawEditForm.title}
              onChange={(event) =>
                props.setLawEditForm((current) => ({ ...current, title: event.target.value }))
              }
            />
            <TextField
              label="Slug"
              value={props.lawEditForm.slug}
              onChange={(event) =>
                props.setLawEditForm((current) => ({ ...current, slug: event.target.value }))
              }
            />
            <TextField
              select
              label="Уровень"
              value={props.lawEditForm.level}
              onChange={(event) =>
                props.setLawEditForm((current) => ({ ...current, level: event.target.value }))
              }
            >
              <MenuItem value="constitution">Конституция</MenuItem>
              <MenuItem value="law">Закон</MenuItem>
              <MenuItem value="resolution">Резолюция</MenuItem>
            </TextField>
            <TextField
              label="Статус"
              value={props.lawEditForm.status}
              onChange={(event) =>
                props.setLawEditForm((current) => ({ ...current, status: event.target.value }))
              }
            />
            <TextField
              label="Adopted via"
              value={props.lawEditForm.adoptedVia}
              onChange={(event) =>
                props.setLawEditForm((current) => ({ ...current, adoptedVia: event.target.value }))
              }
            />
            <TextField
              label="Причина перезаписи"
              value={props.lawEditForm.reason}
              onChange={(event) =>
                props.setLawEditForm((current) => ({ ...current, reason: event.target.value }))
              }
              helperText="Попадёт в административный журнал."
            />
            <TextField
              label="Текст акта"
              multiline
              minRows={14}
              value={props.lawEditForm.currentText}
              onChange={(event) =>
                props.setLawEditForm((current) => ({ ...current, currentText: event.target.value }))
              }
            />
            {!props.canUseOverwriteMode ? (
              <Alert severity="info">
                Для прямого редактирования законов нужен permission `root`.
              </Alert>
            ) : !props.overwriteMode ? (
              <Alert severity="warning">
                Включите `Overwrite mode`, чтобы изменять законы и Конституцию без парламентских или референдумных процедур.
              </Alert>
            ) : (
              <Alert severity="warning">
                Overwrite mode обходит обычные политики RGOV. Используйте его только для осознанной root-операции.
              </Alert>
            )}
            <Button
              variant="contained"
              color="warning"
              disabled={
                props.submitting ||
                !props.canUseOverwriteMode ||
                !props.overwriteMode ||
                !props.lawEditForm.title.trim() ||
                !props.lawEditForm.slug.trim() ||
                !props.lawEditForm.currentText.trim()
              }
              onClick={props.onOverwriteLaw}
            >
              Перезаписать закон
            </Button>
          </Stack>
        ) : (
          <EmptyState text="Выберите закон в дереве Ratcraftia." />
        )}
      </ResponsiveGrid>
    </SectionCard>
  );

  const usersContent = (
    <ResponsiveGrid columns={{ xs: "1fr", xl: "400px minmax(0, 1fr)" }}>
      <SectionCard
        title="Создать пользователя"
        subtitle="Быстрая регистрация новой учётной записи гражданина или сотрудника."
      >
        <Stack spacing={1.25}>
          <TextField
            label="УИН"
            disabled={!props.canCreateUsers && !rootOverride}
            value={props.createUserForm.uin}
            onChange={(event) =>
              props.setCreateUserForm((current) => ({
                ...current,
                uin: event.target.value,
              }))
            }
          />
          <TextField
            label="УАН"
            disabled={!props.canCreateUsers && !rootOverride}
            value={props.createUserForm.uan}
            onChange={(event) =>
              props.setCreateUserForm((current) => ({
                ...current,
                uan: event.target.value,
              }))
            }
          />
          <TextField
            label="Логин"
            disabled={!props.canCreateUsers && !rootOverride}
            value={props.createUserForm.login}
            onChange={(event) =>
              props.setCreateUserForm((current) => ({
                ...current,
                login: event.target.value,
              }))
            }
          />
          <TextField
            label="Пароль"
            type="password"
            disabled={!props.canCreateUsers && !rootOverride}
            value={props.createUserForm.password}
            onChange={(event) =>
              props.setCreateUserForm((current) => ({
                ...current,
                password: event.target.value,
              }))
            }
          />
          <TextField
            label="Имя"
            disabled={!props.canCreateUsers && !rootOverride}
            value={props.createUserForm.firstName}
            onChange={(event) =>
              props.setCreateUserForm((current) => ({
                ...current,
                firstName: event.target.value,
              }))
            }
          />
          <TextField
            label="Фамилия"
            disabled={!props.canCreateUsers && !rootOverride}
            value={props.createUserForm.lastName}
            onChange={(event) =>
              props.setCreateUserForm((current) => ({
                ...current,
                lastName: event.target.value,
              }))
            }
          />
          <TextField
            label="Отчество"
            disabled={!props.canCreateUsers && !rootOverride}
            value={props.createUserForm.patronymic}
            onChange={(event) =>
              props.setCreateUserForm((current) => ({
                ...current,
                patronymic: event.target.value,
              }))
            }
          />
          <TextField
            select
            label="Организация"
            disabled={!props.canCreateUsers && !rootOverride}
            value={props.createUserForm.orgSlug}
            onChange={(event) =>
              props.setCreateUserForm((current) => ({
                ...current,
                orgSlug: event.target.value,
              }))
            }
          >
            <MenuItem value="">Без назначения</MenuItem>
            {props.organizations.map((organization) => (
              <MenuItem key={organization.id} value={organization.slug}>
                {organization.name}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            label="Должность"
            disabled={!props.canCreateUsers && !rootOverride}
            value={props.createUserForm.positionTitle}
            onChange={(event) =>
              props.setCreateUserForm((current) => ({
                ...current,
                positionTitle: event.target.value,
              }))
            }
          />
          <TextField
            label="Permissions"
            disabled={!props.canCreateUsers && !rootOverride}
            value={props.createUserForm.permissions}
            onChange={(event) =>
              props.setCreateUserForm((current) => ({
                ...current,
                permissions: event.target.value,
              }))
            }
            helperText="Укажите значения через запятую или выберите пресет ниже."
          />
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            {props.permissionPresets.map((preset) => (
              <Chip
                key={preset.label}
                label={preset.label}
                onClick={() =>
                  props.setCreateUserForm((current) => ({
                    ...current,
                    permissions: preset.value,
                  }))
                }
                variant="outlined"
              />
            ))}
          </Stack>
          <Button
            variant="contained"
            startIcon={<PersonAddAltRoundedIcon />}
            disabled={
              (!props.canCreateUsers && !rootOverride) ||
              !props.createUserForm.uin.trim() ||
              !props.createUserForm.uan.trim() ||
              !props.createUserForm.login.trim() ||
              !props.createUserForm.password.trim() ||
              !props.createUserForm.firstName.trim() ||
              !props.createUserForm.lastName.trim() ||
              props.submitting
            }
            onClick={props.onCreateUser}
          >
            Создать учётную запись
          </Button>
        </Stack>
      </SectionCard>
      <SectionCard
        title="Управление персоналом"
        subtitle="Редактирование личности, кадрового статуса и прав доступа."
      >
        <Stack spacing={1.25}>
          <TextField
            select
            label="Выберите пользователя"
            value={props.selectedUserId}
            disabled={!props.canReadUsers && !rootOverride}
            onChange={(event) => props.setSelectedUserId(Number(event.target.value))}
          >
            {props.users.map((user) => (
              <MenuItem key={user.id} value={user.id}>
                {user.full_name} · {user.login}
              </MenuItem>
            ))}
          </TextField>
          {props.selectedUser ? (
            <>
              <Typography variant="body2" color="text.secondary">
                {props.selectedUser.permissions_label}
                {props.selectedUser.organization ? ` · ${props.selectedUser.organization.name}` : ""}
              </Typography>
              <TextField
                label="УИН"
                disabled={!props.canUpdateUsers && !rootOverride}
                value={props.userEditForm.uin}
                onChange={(event) =>
                  props.setUserEditForm((current) => ({
                    ...current,
                    uin: event.target.value,
                  }))
                }
              />
              <TextField
                label="УАН"
                disabled={!props.canUpdateUsers && !rootOverride}
                value={props.userEditForm.uan}
                onChange={(event) =>
                  props.setUserEditForm((current) => ({
                    ...current,
                    uan: event.target.value,
                  }))
                }
              />
              <TextField
                label="Имя"
                disabled={!props.canUpdateUsers && !rootOverride}
                value={props.userEditForm.firstName}
                onChange={(event) =>
                  props.setUserEditForm((current) => ({
                    ...current,
                    firstName: event.target.value,
                  }))
                }
              />
              <TextField
                label="Фамилия"
                disabled={!props.canUpdateUsers && !rootOverride}
                value={props.userEditForm.lastName}
                onChange={(event) =>
                  props.setUserEditForm((current) => ({
                    ...current,
                    lastName: event.target.value,
                  }))
                }
              />
              <TextField
                label="Отчество"
                disabled={!props.canUpdateUsers && !rootOverride}
                value={props.userEditForm.patronymic}
                onChange={(event) =>
                  props.setUserEditForm((current) => ({
                    ...current,
                    patronymic: event.target.value,
                  }))
                }
              />
              <Button
                variant="outlined"
                disabled={(!props.canUpdateUsers && !rootOverride) || props.submitting}
                onClick={props.onUpdateUser}
              >
                Сохранить личные данные
              </Button>
              <TextField
                label="Permissions"
                disabled={!props.canWritePermissions && !rootOverride}
                value={props.userEditForm.permissions}
                onChange={(event) =>
                  props.setUserEditForm((current) => ({
                    ...current,
                    permissions: event.target.value,
                  }))
                }
              />
              <Button
                variant="outlined"
                disabled={(!props.canWritePermissions && !rootOverride) || props.submitting}
                onClick={props.onUpdatePermissions}
              >
                Сохранить permissions
              </Button>
              <TextField
                select
                label="Организация"
                disabled={!props.canManagePersonnel && !rootOverride}
                value={props.userEditForm.orgSlug}
                onChange={(event) =>
                  props.setUserEditForm((current) => ({
                    ...current,
                    orgSlug: event.target.value,
                  }))
                }
              >
                <MenuItem value="">Без назначения</MenuItem>
                {props.organizations.map((organization) => (
                  <MenuItem key={organization.id} value={organization.slug}>
                    {organization.name}
                  </MenuItem>
                ))}
              </TextField>
              <TextField
                label="Должность"
                disabled={!props.canManagePersonnel && !rootOverride}
                value={props.userEditForm.positionTitle}
                onChange={(event) =>
                  props.setUserEditForm((current) => ({
                    ...current,
                    positionTitle: event.target.value,
                  }))
                }
              />
              <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
                <Button
                  variant="contained"
                  disabled={
                    (!props.canManagePersonnel && !rootOverride) ||
                    !props.userEditForm.orgSlug ||
                    !props.userEditForm.positionTitle.trim() ||
                    props.submitting
                  }
                  onClick={props.onHire}
                >
                  Назначить
                </Button>
                <Button
                  variant="text"
                  color="error"
                  disabled={(!props.canManagePersonnel && !rootOverride) || props.submitting}
                  onClick={props.onFire}
                >
                  Уволить
                </Button>
              </Stack>
            </>
          ) : (
            <EmptyState text="Пользователь не выбран." />
          )}
        </Stack>
      </SectionCard>
    </ResponsiveGrid>
  );

  const organizationsContent = (
    <ResponsiveGrid columns={{ xs: "1fr", xl: "400px minmax(0, 1fr)" }}>
      <SectionCard
        title="Создать организацию"
        subtitle="Добавьте новую государственную структуру для кадровых операций."
      >
        <Stack spacing={1.25}>
          <TextField
            label="Название"
            disabled={!props.canCreateOrganizations && !rootOverride}
            value={props.organizationForm.name}
            onChange={(event) =>
              props.setOrganizationForm((current) => ({
                ...current,
                name: event.target.value,
              }))
            }
          />
          <TextField
            label="Slug"
            disabled={!props.canCreateOrganizations && !rootOverride}
            value={props.organizationForm.slug}
            onChange={(event) =>
              props.setOrganizationForm((current) => ({
                ...current,
                slug: event.target.value,
              }))
            }
          />
          <TextField
            label="Описание"
            multiline
            minRows={4}
            disabled={!props.canCreateOrganizations && !rootOverride}
            value={props.organizationForm.description}
            onChange={(event) =>
              props.setOrganizationForm((current) => ({
                ...current,
                description: event.target.value,
              }))
            }
          />
          <Button
            variant="contained"
            disabled={
              (!props.canCreateOrganizations && !rootOverride) ||
              !props.organizationForm.name.trim() ||
              !props.organizationForm.slug.trim() ||
              props.submitting
            }
            onClick={props.onCreateOrganization}
          >
            Создать организацию
          </Button>
        </Stack>
      </SectionCard>
      <SectionCard
        title="Список организаций"
        subtitle="Баланс Ratubles и краткое описание каждой структуры."
      >
        <Stack spacing={1.25}>
          {props.organizations.map((organization) => (
            <Paper key={organization.id} variant="outlined" sx={{ p: 1.75, borderRadius: 4 }}>
              <Stack direction={{ xs: "column", sm: "row" }} justifyContent="space-between" spacing={1}>
                <Stack spacing={0.4}>
                  <Typography variant="subtitle1">{organization.name}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {organization.slug} · {organization.kind}
                  </Typography>
                </Stack>
                <Chip label={`${formatNumber(organization.ratubles)} RAT`} />
              </Stack>
              <Typography variant="body2" sx={{ mt: 1 }}>
                {organization.description || "Описание не указано."}
              </Typography>
            </Paper>
          ))}
          {props.organizations.length === 0 && <EmptyState text="Организации пока не созданы." />}
        </Stack>
      </SectionCard>
    </ResponsiveGrid>
  );

  const logsContent = (
    <SectionCard
      title="Административный журнал"
      subtitle="Хронология ключевых действий в системе."
    >
      {props.canReadAdminLogs || rootOverride ? (
        <Stack spacing={1.25}>
          {props.adminLogs.map((entry) => (
            <Paper key={entry.id} variant="outlined" sx={{ p: 1.75, borderRadius: 4 }}>
              <Typography variant="subtitle1">{entry.summary}</Typography>
              <Typography variant="body2" color="text.secondary">
                {entry.actor_name}
                {entry.target_name ? ` → ${entry.target_name}` : ""}
                {" · "}
                {entry.action}
              </Typography>
              {entry.reason && (
                <Typography variant="body2" sx={{ mt: 1 }}>
                  {entry.reason}
                </Typography>
              )}
              <Typography variant="caption" color="text.secondary">
                {formatDateTime(entry.created_at)}
              </Typography>
            </Paper>
          ))}
          {props.adminLogs.length === 0 && <EmptyState text="Записей журнала пока нет." />}
        </Stack>
      ) : (
        <EmptyState text="У вашей учётной записи нет права на просмотр журналов." />
      )}
    </SectionCard>
  );

  const oauthAppsContent = (
    <SectionCard
      title="OAuth-приложения"
      subtitle="Каждое внешнее приложение должно быть отдельно одобрено, отклонено или отозвано."
    >
      {props.canReadOAuthApps || rootOverride ? (
        <Stack spacing={1.25}>
          {props.oauthApps.map((application) => (
            <Paper key={application.id} variant="outlined" sx={{ p: 1.75, borderRadius: 4 }}>
              <Stack spacing={1}>
                <Stack direction={{ xs: "column", md: "row" }} justifyContent="space-between" spacing={1}>
                  <Stack spacing={0.35}>
                    <Typography variant="subtitle1">{application.name}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {application.owner_name ?? "Неизвестный владелец"} · {application.client_id}
                    </Typography>
                  </Stack>
                  <Chip
                    label={application.status}
                    color={appStatusColor(application.status)}
                    variant="outlined"
                  />
                </Stack>
                <Typography variant="body2">
                  {application.description || "Описание приложения не указано."}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Redirect URIs: {application.redirect_uris.join(" · ")}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Scope: {application.allowed_scopes.join(", ")}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Создано {formatDateTime(application.created_at)}
                  {application.approved_at ? ` · Одобрено ${formatDateTime(application.approved_at)}` : ""}
                </Typography>
                {application.review_note && (
                  <Alert severity={application.status === "approved" ? "success" : "info"}>
                    {application.review_note}
                  </Alert>
                )}
                <TextField
                  label="Заметка администратора"
                  multiline
                  minRows={2}
                  disabled={!props.canReviewOAuthApps && !rootOverride}
                  value={oauthReviewNotes[application.id] ?? application.review_note}
                  onChange={(event) =>
                    setOauthReviewNotes((current) => ({
                      ...current,
                      [application.id]: event.target.value,
                    }))
                  }
                />
                <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
                  <Button
                    variant="contained"
                    disabled={(!props.canReviewOAuthApps && !rootOverride) || props.submitting}
                    onClick={() =>
                      props.onReviewOAuthApp(
                        application.id,
                        "approved",
                        oauthReviewNotes[application.id] ?? application.review_note,
                      )
                    }
                  >
                    Одобрить
                  </Button>
                  <Button
                    variant="outlined"
                    color="warning"
                    disabled={(!props.canReviewOAuthApps && !rootOverride) || props.submitting}
                    onClick={() =>
                      props.onReviewOAuthApp(
                        application.id,
                        "rejected",
                        oauthReviewNotes[application.id] ?? application.review_note,
                      )
                    }
                  >
                    Отклонить
                  </Button>
                  <Button
                    variant="text"
                    color="error"
                    disabled={(!props.canReviewOAuthApps && !rootOverride) || props.submitting}
                    onClick={() =>
                      props.onReviewOAuthApp(
                        application.id,
                        "revoked",
                        oauthReviewNotes[application.id] ?? application.review_note,
                      )
                    }
                  >
                    Отозвать
                  </Button>
                </Stack>
              </Stack>
            </Paper>
          ))}
          {props.oauthApps.length === 0 && <EmptyState text="OAuth-приложения пока не зарегистрированы." />}
        </Stack>
      ) : (
        <EmptyState text="У вашей учётной записи нет права на просмотр OAuth-приложений." />
      )}
    </SectionCard>
  );

  let content: React.ReactNode = lawsContent;
  if (props.activeNode === "users") {
    content = usersContent;
  } else if (props.activeNode === "organizations") {
    content = organizationsContent;
  } else if (props.activeNode === "oauth_apps") {
    content = oauthAppsContent;
  } else if (props.activeNode === "logs") {
    content = logsContent;
  }

  return (
    <Stack spacing={2.5}>
      <HeroCard
        title="Ratcraftia"
        description="Дерево управления RGOV: законы, пользователи, организации, OAuth и журнал в одном навигаторе."
        chips={[
          `${props.laws.length} законов`,
          `${props.users.length} пользователей`,
          `${props.organizations.length} организаций`,
          props.overwriteMode ? "Overwrite mode: on" : "Overwrite mode: off",
        ]}
      />
      {!props.visible ? (
        <SectionCard title="Недостаточно прав">
          <EmptyState text="Для раздела управления требуются административные, исполнительные или root-разрешения." />
        </SectionCard>
      ) : (
        <ResponsiveGrid columns={{ xs: "1fr", xl: "320px minmax(0, 1fr)" }}>
          <SectionCard
            title="Дерево Ratcraftia"
            subtitle="Выберите ветку портала и работайте с нужным контуром напрямую."
          >
            <Stack spacing={2}>
              <Paper variant="outlined" sx={{ p: 1.5, borderRadius: 4 }}>
                <Stack direction="row" spacing={1} alignItems="center">
                  <ShieldRoundedIcon color="primary" />
                  <Typography variant="subtitle1">Ratcraftia</Typography>
                </Stack>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.75 }}>
                  Законы, пользователи, организации и контрольные журналы собраны в одно дерево управления.
                </Typography>
              </Paper>

              <List disablePadding>
                <TreeNodeButton
                  label="Законы"
                  selected={props.activeNode === "laws"}
                  icon={<GavelRoundedIcon />}
                  onClick={() => openNode("laws")}
                />
                {constitutionLaw && (
                  <TreeNodeButton
                    label="Конституция"
                    depth={1}
                    selected={props.activeNode === "constitution"}
                    icon={<ChevronRightRoundedIcon />}
                    onClick={() => openNode("constitution")}
                  />
                )}
                <TreeNodeButton
                  label="Пользователи"
                  selected={props.activeNode === "users"}
                  icon={<GroupsRoundedIcon />}
                  onClick={() => openNode("users")}
                />
                <TreeNodeButton
                  label="Организации"
                  selected={props.activeNode === "organizations"}
                  icon={<ApartmentRoundedIcon />}
                  onClick={() => openNode("organizations")}
                />
                <TreeNodeButton
                  label="OAuth apps"
                  selected={props.activeNode === "oauth_apps"}
                  icon={<VpnKeyRoundedIcon />}
                  onClick={() => openNode("oauth_apps")}
                />
                <TreeNodeButton
                  label="Журнал"
                  selected={props.activeNode === "logs"}
                  icon={<HistoryRoundedIcon />}
                  onClick={() => openNode("logs")}
                />
              </List>

              {props.canUseOverwriteMode ? (
                <Paper variant="outlined" sx={{ p: 1.5, borderRadius: 4 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={props.overwriteMode}
                        onChange={(_, nextChecked) => props.setOverwriteMode(nextChecked)}
                      />
                    }
                    label="Overwrite mode"
                  />
                  <Typography variant="body2" color="text.secondary">
                    Требует permission `root` и включает прямую перезапись законов, Конституции и административных сущностей в обход обычных политик RGOV.
                  </Typography>
                </Paper>
              ) : (
                <Alert severity="info">
                  Overwrite mode доступен только для учётных записей с permission `root`.
                </Alert>
              )}
            </Stack>
          </SectionCard>

          {content}
        </ResponsiveGrid>
      )}
    </Stack>
  );
}
