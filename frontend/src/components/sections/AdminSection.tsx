import * as React from "react";
import {
  Alert,
  Button,
  Chip,
  MenuItem,
  Paper,
  Stack,
  Tab,
  Tabs,
  TextField,
  Typography,
} from "@mui/material";
import PersonAddAltRoundedIcon from "@mui/icons-material/PersonAddAltRounded";
import type { AdminLogRead, DeveloperAppRead, OrganizationRead, UserRead } from "../../types";
import { formatDateTime, formatNumber } from "../../lib/format";
import { EmptyState, HeroCard, ResponsiveGrid, SectionCard } from "../common";

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

export function AdminSection(props: {
  visible: boolean;
  adminTab: number;
  setAdminTab: React.Dispatch<React.SetStateAction<number>>;
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
  organizationForm: OrganizationForm;
  setOrganizationForm: React.Dispatch<React.SetStateAction<OrganizationForm>>;
  permissionPresets: Array<{ label: string; value: string }>;
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
}) {
  const [oauthReviewNotes, setOauthReviewNotes] = React.useState<Record<number, string>>({});

  return (
    <Stack spacing={2.5}>
      <HeroCard
        title="Управление"
        description="Пользователи, организации, кадровые операции, одобрение внешних OAuth-приложений и административный журнал."
        chips={[
          `${props.users.length} пользователей`,
          `${props.organizations.length} организаций`,
          `${props.oauthApps.length} OAuth apps`,
          `${props.adminLogs.length} записей журнала`,
        ]}
      />
      {!props.visible ? (
        <SectionCard title="Недостаточно прав">
          <EmptyState text="Для раздела управления требуются административные или исполнительные разрешения." />
        </SectionCard>
      ) : (
        <SectionCard
          title="Административная консоль"
          subtitle="Разделы скрыты, если соответствующих прав у вашей учётной записи нет."
        >
          <Tabs
            value={props.adminTab}
            onChange={(_, value) => props.setAdminTab(value)}
            sx={{ mb: 2 }}
          >
            <Tab label="Пользователи" />
            <Tab label="Организации" />
            <Tab label="Журнал" />
            <Tab label="OAuth apps" />
          </Tabs>
          {props.adminTab === 0 && (
            <ResponsiveGrid columns={{ xs: "1fr", xl: "400px minmax(0, 1fr)" }}>
              <SectionCard
                title="Создать пользователя"
                subtitle="Быстрая регистрация новой учётной записи гражданина или сотрудника."
              >
                <Stack spacing={1.25}>
                  <TextField
                    label="УИН"
                    disabled={!props.canCreateUsers}
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
                    disabled={!props.canCreateUsers}
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
                    disabled={!props.canCreateUsers}
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
                    disabled={!props.canCreateUsers}
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
                    disabled={!props.canCreateUsers}
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
                    disabled={!props.canCreateUsers}
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
                    disabled={!props.canCreateUsers}
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
                    disabled={!props.canCreateUsers}
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
                    disabled={!props.canCreateUsers}
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
                    disabled={!props.canCreateUsers}
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
                      !props.canCreateUsers ||
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
                subtitle="Редактирование личности, назначение в организацию и права доступа."
              >
                <Stack spacing={1.25}>
                  <TextField
                    select
                    label="Выберите пользователя"
                    value={props.selectedUserId}
                    disabled={!props.canReadUsers}
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
                        {props.selectedUser.organization
                          ? ` · ${props.selectedUser.organization.name}`
                          : ""}
                      </Typography>
                      <TextField
                        label="УИН"
                        disabled={!props.canUpdateUsers}
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
                        disabled={!props.canUpdateUsers}
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
                        disabled={!props.canUpdateUsers}
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
                        disabled={!props.canUpdateUsers}
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
                        disabled={!props.canUpdateUsers}
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
                        disabled={!props.canUpdateUsers || props.submitting}
                        onClick={props.onUpdateUser}
                      >
                        Сохранить личные данные
                      </Button>
                      <TextField
                        label="Permissions"
                        disabled={!props.canWritePermissions}
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
                        disabled={!props.canWritePermissions || props.submitting}
                        onClick={props.onUpdatePermissions}
                      >
                        Сохранить permissions
                      </Button>
                      <TextField
                        select
                        label="Организация"
                        disabled={!props.canManagePersonnel}
                        value={props.userEditForm.orgSlug}
                        onChange={(event) =>
                          props.setUserEditForm((current) => ({
                            ...current,
                            orgSlug: event.target.value,
                          }))
                        }
                      >
                        {props.organizations.map((organization) => (
                          <MenuItem key={organization.id} value={organization.slug}>
                            {organization.name}
                          </MenuItem>
                        ))}
                      </TextField>
                      <TextField
                        label="Должность"
                        disabled={!props.canManagePersonnel}
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
                            !props.canManagePersonnel ||
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
                          disabled={!props.canManagePersonnel || props.submitting}
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
          )}
          {props.adminTab === 1 && (
            <ResponsiveGrid columns={{ xs: "1fr", xl: "400px minmax(0, 1fr)" }}>
              <SectionCard
                title="Создать организацию"
                subtitle="Добавьте новую государственную структуру для кадровых операций."
              >
                <Stack spacing={1.25}>
                  <TextField
                    label="Название"
                    disabled={!props.canCreateOrganizations}
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
                    disabled={!props.canCreateOrganizations}
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
                    disabled={!props.canCreateOrganizations}
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
                      !props.canCreateOrganizations ||
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
                      <Stack
                        direction={{ xs: "column", sm: "row" }}
                        justifyContent="space-between"
                        spacing={1}
                      >
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
                  {props.organizations.length === 0 && (
                    <EmptyState text="Организации пока не созданы." />
                  )}
                </Stack>
              </SectionCard>
            </ResponsiveGrid>
          )}
          {props.adminTab === 2 && (
            <SectionCard
              title="Административный журнал"
              subtitle="Хронология ключевых действий в системе."
            >
              {props.canReadAdminLogs ? (
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
                  {props.adminLogs.length === 0 && (
                    <EmptyState text="Записей журнала пока нет." />
                  )}
                </Stack>
              ) : (
                <EmptyState text="У вашей учётной записи нет права на просмотр журналов." />
              )}
            </SectionCard>
          )}
          {props.adminTab === 3 && (
            <SectionCard
              title="OAuth-приложения"
              subtitle="Каждое внешнее приложение должно быть отдельно одобрено, отклонено или отозвано."
            >
              {props.canReadOAuthApps ? (
                <Stack spacing={1.25}>
                  {props.oauthApps.map((application) => (
                    <Paper key={application.id} variant="outlined" sx={{ p: 1.75, borderRadius: 4 }}>
                      <Stack spacing={1}>
                        <Stack
                          direction={{ xs: "column", md: "row" }}
                          justifyContent="space-between"
                          spacing={1}
                        >
                          <Stack spacing={0.35}>
                            <Typography variant="subtitle1">{application.name}</Typography>
                            <Typography variant="body2" color="text.secondary">
                              {application.owner_name ?? "Неизвестный владелец"} · {application.client_id}
                            </Typography>
                          </Stack>
                          <Chip
                            label={application.status}
                            color={
                              application.status === "approved"
                                ? "success"
                                : application.status === "rejected"
                                  ? "error"
                                  : application.status === "revoked"
                                    ? "warning"
                                    : "default"
                            }
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
                          disabled={!props.canReviewOAuthApps}
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
                            disabled={!props.canReviewOAuthApps || props.submitting}
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
                            disabled={!props.canReviewOAuthApps || props.submitting}
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
                            disabled={!props.canReviewOAuthApps || props.submitting}
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
                  {props.oauthApps.length === 0 && (
                    <EmptyState text="OAuth-приложения пока не зарегистрированы." />
                  )}
                </Stack>
              ) : (
                <EmptyState text="У вашей учётной записи нет права на просмотр OAuth-приложений." />
              )}
            </SectionCard>
          )}
        </SectionCard>
      )}
    </Stack>
  );
}
