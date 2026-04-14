import * as React from "react";
import {
  Alert,
  AppBar,
  Avatar,
  Badge,
  Box,
  Card,
  CardContent,
  Chip,
  Container,
  Divider,
  Drawer,
  IconButton,
  LinearProgress,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Snackbar,
  Stack,
  Toolbar,
  Tooltip,
  Typography,
  useMediaQuery,
} from "@mui/material";
import { alpha, useTheme } from "@mui/material/styles";
import AdminPanelSettingsRoundedIcon from "@mui/icons-material/AdminPanelSettingsRounded";
import CampaignRoundedIcon from "@mui/icons-material/CampaignRounded";
import CodeRoundedIcon from "@mui/icons-material/CodeRounded";
import DarkModeRoundedIcon from "@mui/icons-material/DarkModeRounded";
import DashboardRoundedIcon from "@mui/icons-material/DashboardRounded";
import GavelRoundedIcon from "@mui/icons-material/GavelRounded";
import HowToVoteRoundedIcon from "@mui/icons-material/HowToVoteRounded";
import LightModeRoundedIcon from "@mui/icons-material/LightModeRounded";
import LogoutRoundedIcon from "@mui/icons-material/LogoutRounded";
import MailRoundedIcon from "@mui/icons-material/MailRounded";
import MenuRoundedIcon from "@mui/icons-material/MenuRounded";
import RefreshRoundedIcon from "@mui/icons-material/RefreshRounded";
import SavingsRoundedIcon from "@mui/icons-material/SavingsRounded";
import VerifiedRoundedIcon from "@mui/icons-material/VerifiedRounded";
import AccountBalanceRoundedIcon from "@mui/icons-material/AccountBalanceRounded";
import type {
  AdminLogRead,
  BillRead,
  DeveloperAppRead,
  DeveloperScopeRead,
  DidTokenResponse,
  LawRead,
  MailRead,
  NewsRead,
  OrganizationRead,
  ParliamentElectionRead,
  ParliamentSummaryRead,
  PublicOAuthAppRead,
  PushConfigResponse,
  PushStatus,
  RatublesDirectoryEntryRead,
  RatublesTransactionRead,
  ReferendumRead,
  UserRead,
} from "./types";
import { ApiClient, ApiError, apiBaseUrl } from "./lib/api";
import { formatNumber, initials } from "./lib/format";
import { hasPermission, permissions } from "./lib/permissions";
import {
  disablePush,
  enablePush,
  getPushStatus,
  previewPush,
  syncPushSubscription,
} from "./lib/push";
import { LoginScreen } from "./components/LoginScreen";
import { DashboardSection } from "./components/sections/DashboardSection";
import { MailSection } from "./components/sections/MailSection";
import { RatublesSection } from "./components/sections/RatublesSection";
import { ParliamentSection } from "./components/sections/ParliamentSection";
import { ReferendaSection } from "./components/sections/ReferendaSection";
import { LawsSection } from "./components/sections/LawsSection";
import { NewsSection } from "./components/sections/NewsSection";
import { AdminSection } from "./components/sections/AdminSection";
import { DeveloperSection } from "./components/sections/DeveloperSection";

type PortalSection =
  | "dashboard"
  | "mail"
  | "ratubles"
  | "parliament"
  | "referenda"
  | "laws"
  | "news"
  | "developers"
  | "admin";

type SnackbarState = {
  open: boolean;
  message: string;
  severity: "success" | "error" | "info";
};

type SessionState = {
  token: string | null;
  profile: UserRead | null;
};

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

type AdminTreeNode =
  | "laws"
  | "constitution"
  | "users"
  | "organizations"
  | "oauth_apps"
  | "logs";

type LawEditForm = {
  title: string;
  slug: string;
  level: string;
  status: string;
  adoptedVia: string;
  currentText: string;
  reason: string;
};

type PortalData = {
  did: DidTokenResponse | null;
  inbox: MailRead[];
  sent: MailRead[];
  news: NewsRead[];
  laws: LawRead[];
  bills: BillRead[];
  parliamentSummary: ParliamentSummaryRead | null;
  elections: ParliamentElectionRead[];
  referenda: ReferendumRead[];
  directory: RatublesDirectoryEntryRead[];
  transactions: RatublesTransactionRead[];
  ledger: RatublesTransactionRead[];
  users: UserRead[];
  organizations: OrganizationRead[];
  adminLogs: AdminLogRead[];
  developerApps: DeveloperAppRead[];
  oauthScopes: DeveloperScopeRead[];
  adminOAuthApps: DeveloperAppRead[];
  pushConfig: PushConfigResponse | null;
  pushStatus: PushStatus;
};

const drawerWidth = 300;

const matterTypeOptions = [
  { value: "constitution_amendment", label: "Поправка к конституции" },
  { value: "law_change", label: "Изменение закона" },
  { value: "government_question", label: "Государственный вопрос" },
  { value: "deputy_recall", label: "Отзыв депутата" },
  { value: "official_recall", label: "Отзыв должностного лица" },
];

const targetLevelOptions = [
  { value: "constitution", label: "Конституция" },
  { value: "law", label: "Закон" },
  { value: "resolution", label: "Резолюция" },
];

const permissionPresets = [
  { label: "Базовый доступ", value: "" },
  { label: "Управление новостями", value: permissions.newsManage },
  {
    label: "Исполнительный доступ",
    value: [
      permissions.newsManage,
      permissions.orgsCreate,
      permissions.orgsRead,
      permissions.personnelManage,
      permissions.referendaManage,
      permissions.usersRead,
    ].join(", "),
  },
  {
    label: "Парламентский доступ",
    value: [permissions.billsManage, permissions.referendaManage].join(", "),
  },
  {
    label: "Административный доступ",
    value: [
      permissions.adminLogsRead,
      permissions.billsManage,
      permissions.newsManage,
      permissions.orgsCreate,
      permissions.orgsRead,
      permissions.oauthAppsRead,
      permissions.oauthAppsReview,
      permissions.personnelManage,
      permissions.ratublesMint,
      permissions.referendaManage,
      permissions.usersCreate,
      permissions.usersPermissionsWrite,
      permissions.usersRead,
      permissions.usersUpdate,
    ].join(", "),
  },
  { label: "Root / Overwrite", value: [permissions.root, "*"].join(", ") },
  { label: "Полный доступ", value: "*" },
];

const emptyPushStatus: PushStatus = {
  supported: false,
  permission: "default",
  subscribed: false,
  message: "Push-уведомления пока не настроены.",
};

const emptyPortalData: PortalData = {
  did: null,
  inbox: [],
  sent: [],
  news: [],
  laws: [],
  bills: [],
  parliamentSummary: null,
  elections: [],
  referenda: [],
  directory: [],
  transactions: [],
  ledger: [],
  users: [],
  organizations: [],
  adminLogs: [],
  developerApps: [],
  oauthScopes: [],
  adminOAuthApps: [],
  pushConfig: null,
  pushStatus: emptyPushStatus,
};

function readStoredSession(): SessionState {
  try {
    const raw = window.localStorage.getItem("rgov-session");
    if (!raw) {
      return { token: null, profile: null };
    }
    return JSON.parse(raw) as SessionState;
  } catch {
    return { token: null, profile: null };
  }
}

function optionalRequest<T>(promise: Promise<T>, fallback: T) {
  return promise.catch((error: unknown) => {
    if (error instanceof ApiError && [403, 404].includes(error.status)) {
      return fallback;
    }
    throw error;
  });
}

function parseSection(pathname: string, hash: string): PortalSection {
  if (pathname === "/oauth/authorize") {
    return "developers";
  }
  const candidate = hash.replace("#", "") as PortalSection;
  return [
    "dashboard",
    "mail",
    "ratubles",
    "parliament",
    "referenda",
    "laws",
    "news",
    "developers",
    "admin",
  ].includes(candidate)
    ? candidate
    : "dashboard";
}

function parsePermissionsInput(value: string) {
  const normalized = value
    .split(",")
    .map((item) => item.trim().toLowerCase())
    .filter(Boolean);

  if (normalized.includes("*")) {
    return normalized.includes(permissions.root) ? [permissions.root, "*"] : ["*"];
  }
  return Array.from(new Set(normalized));
}

function parseDirectoryValue(value: string) {
  const [kind, rawId] = value.split(":");
  return {
    kind: kind as "user" | "organization",
    id: Number(rawId),
  };
}

function parseOAuthScopeString(value: string) {
  return value
    .split(" ")
    .map((item) => item.trim())
    .filter(Boolean);
}

function readOAuthRequest(pathname: string, search: string): OAuthRequestState {
  if (pathname !== "/oauth/authorize") {
    return null;
  }

  const params = new URLSearchParams(search);
  const clientId = params.get("client_id")?.trim() ?? "";
  const redirectUri = params.get("redirect_uri")?.trim() ?? "";
  if (!clientId || !redirectUri) {
    return null;
  }

  const responseType = (params.get("response_type")?.trim() || "code") as "code";
  const scope = params.get("scope")?.trim() || "profile.basic";
  const state = params.get("state")?.trim() || undefined;

  return {
    clientId,
    redirectUri,
    responseType,
    scope,
    scopes: parseOAuthScopeString(scope),
    state,
  };
}

function currentElection(
  summary: ParliamentSummaryRead | null,
  elections: ParliamentElectionRead[],
) {
  return summary?.active_election ?? elections[0] ?? null;
}

function getErrorMessage(error: unknown) {
  if (error instanceof ApiError) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Произошла непредвиденная ошибка.";
}

function readStoredOverwriteMode() {
  try {
    return window.localStorage.getItem("rgov-overwrite-mode") === "true";
  } catch {
    return false;
  }
}

type AppProps = {
  colorMode: "light" | "dark";
  onToggleColorMode: () => void;
};

export function App({ colorMode, onToggleColorMode }: AppProps) {
  const theme = useTheme();
  const isDesktop = useMediaQuery(theme.breakpoints.up("lg"));
  const api = React.useRef(new ApiClient()).current;
  const [session, setSession] = React.useState<SessionState>(() => readStoredSession());
  const [portalData, setPortalData] = React.useState<PortalData>(emptyPortalData);
  const [section, setSection] = React.useState<PortalSection>(() =>
    parseSection(window.location.pathname, window.location.hash),
  );
  const [oauthRequest, setOAuthRequest] = React.useState<OAuthRequestState>(() =>
    readOAuthRequest(window.location.pathname, window.location.search),
  );
  const [oauthRequestApp, setOAuthRequestApp] = React.useState<PublicOAuthAppRead | null>(null);
  const [oauthRequestLoading, setOAuthRequestLoading] = React.useState(false);
  const [oauthRequestError, setOAuthRequestError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [submitting, setSubmitting] = React.useState(false);
  const [mobileDrawerOpen, setMobileDrawerOpen] = React.useState(false);
  const [mailboxTab, setMailboxTab] = React.useState<"inbox" | "sent">("inbox");
  const [adminTreeNode, setAdminTreeNode] = React.useState<AdminTreeNode>("laws");
  const [overwriteMode, setOverwriteMode] = React.useState(() => readStoredOverwriteMode());
  const [lawSearch, setLawSearch] = React.useState("");
  const deferredLawSearch = React.useDeferredValue(lawSearch);
  const [snackbar, setSnackbar] = React.useState<SnackbarState>({
    open: false,
    message: "",
    severity: "info",
  });

  const [loginForm, setLoginForm] = React.useState({ identifier: "", secret: "" });
  const [accessForm, setAccessForm] = React.useState({
    newLogin: "",
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });
  const [mailForm, setMailForm] = React.useState({ to: "", subject: "", text: "" });
  const [transferForm, setTransferForm] = React.useState({
    recipient: "",
    amount: "",
    reason: "",
  });
  const [mintForm, setMintForm] = React.useState({
    recipient: "",
    amount: "",
    reason: "",
  });
  const [billForm, setBillForm] = React.useState({
    title: "",
    summary: "",
    proposedText: "",
    lawId: "",
  });
  const [referendumForm, setReferendumForm] = React.useState({
    title: "",
    description: "",
    proposedText: "",
    lawId: "",
    targetLevel: "constitution",
    matterType: "constitution_amendment",
    subjectIdentifier: "",
  });
  const [candidatePartyName, setCandidatePartyName] = React.useState("");
  const [newsForm, setNewsForm] = React.useState({ title: "", body: "" });
  const [organizationForm, setOrganizationForm] = React.useState({
    name: "",
    slug: "",
    description: "",
  });
  const [developerAppForm, setDeveloperAppForm] = React.useState<DeveloperAppForm>({
    name: "",
    slug: "",
    description: "",
    websiteUrl: "",
    redirectUris: "",
    allowedScopes: ["profile.basic"],
  });
  const [latestSecret, setLatestSecret] = React.useState<LatestSecretState>(null);
  const [createUserForm, setCreateUserForm] = React.useState({
    uin: "",
    uan: "",
    login: "",
    password: "",
    firstName: "",
    lastName: "",
    patronymic: "",
    permissions: "",
    orgSlug: "",
    positionTitle: "",
  });
  const [selectedUserId, setSelectedUserId] = React.useState<number | "">("");
  const [userEditForm, setUserEditForm] = React.useState({
    uin: "",
    uan: "",
    firstName: "",
    lastName: "",
    patronymic: "",
    permissions: "",
    orgSlug: "",
    positionTitle: "",
  });
  const [selectedLawId, setSelectedLawId] = React.useState<number | "">("");
  const [lawEditForm, setLawEditForm] = React.useState<LawEditForm>({
    title: "",
    slug: "",
    level: "law",
    status: "active",
    adoptedVia: "overwrite",
    currentText: "",
    reason: "",
  });

  const requestCounterRef = React.useRef(0);
  api.setToken(session.token);
  api.setOverwriteMode(overwriteMode);

  React.useEffect(() => {
    const handleLocationChange = () => {
      setSection(parseSection(window.location.pathname, window.location.hash));
      setOAuthRequest(readOAuthRequest(window.location.pathname, window.location.search));
    };
    window.addEventListener("hashchange", handleLocationChange);
    window.addEventListener("popstate", handleLocationChange);
    return () => {
      window.removeEventListener("hashchange", handleLocationChange);
      window.removeEventListener("popstate", handleLocationChange);
    };
  }, []);

  React.useEffect(() => {
    if (!session.token) {
      window.localStorage.removeItem("rgov-session");
      return;
    }
    window.localStorage.setItem("rgov-session", JSON.stringify(session));
  }, [session]);

  React.useEffect(() => {
    window.localStorage.setItem("rgov-overwrite-mode", overwriteMode ? "true" : "false");
  }, [overwriteMode]);

  React.useEffect(() => {
    const selectedUser = portalData.users.find((user) => user.id === selectedUserId);
    if (!selectedUser) {
      if (portalData.users.length > 0) {
        setSelectedUserId(portalData.users[0].id);
      }
      return;
    }
    setUserEditForm({
      uin: selectedUser.uin,
      uan: selectedUser.uan,
      firstName: selectedUser.first_name,
      lastName: selectedUser.last_name,
      patronymic: selectedUser.patronymic,
      permissions: selectedUser.permissions.join(", "),
      orgSlug: selectedUser.organization?.slug ?? "",
      positionTitle: selectedUser.position_title,
    });
  }, [portalData.users, selectedUserId]);

  React.useEffect(() => {
    const selectedLaw = portalData.laws.find((law) => law.id === selectedLawId);
    if (!selectedLaw) {
      const constitutionLaw = portalData.laws.find((law) => law.level === "constitution");
      if (constitutionLaw) {
        setSelectedLawId(constitutionLaw.id);
      } else if (portalData.laws.length > 0) {
        setSelectedLawId(portalData.laws[0].id);
      }
      return;
    }
    setLawEditForm({
      title: selectedLaw.title,
      slug: selectedLaw.slug,
      level: selectedLaw.level,
      status: selectedLaw.status,
      adoptedVia: selectedLaw.adopted_via,
      currentText: selectedLaw.current_text,
      reason: "",
    });
  }, [portalData.laws, selectedLawId]);

  React.useEffect(() => {
    if (transferForm.recipient || portalData.directory.length === 0) {
      return;
    }
    const candidate = portalData.directory.find(
      (entry) => entry.kind !== "user" || entry.id !== session.profile?.id,
    );
    if (candidate) {
      setTransferForm((current) => ({
        ...current,
        recipient: `${candidate.kind}:${candidate.id}`,
      }));
    }
  }, [portalData.directory, session.profile?.id, transferForm.recipient]);

  React.useEffect(() => {
    if (mintForm.recipient || portalData.directory.length === 0) {
      return;
    }
    const candidate = portalData.directory[0];
    setMintForm((current) => ({
      ...current,
      recipient: `${candidate.kind}:${candidate.id}`,
    }));
  }, [mintForm.recipient, portalData.directory]);

  React.useEffect(() => {
    let cancelled = false;

    async function loadOauthRequestApp() {
      if (!oauthRequest) {
        setOAuthRequestApp(null);
        setOAuthRequestError(null);
        setOAuthRequestLoading(false);
        return;
      }

      setOAuthRequestLoading(true);
      setOAuthRequestError(null);

      try {
        const application = await api.getPublicOAuthApp(oauthRequest.clientId);
        if (!cancelled) {
          setOAuthRequestApp(application);
        }
      } catch (error) {
        if (!cancelled) {
          setOAuthRequestApp(null);
          setOAuthRequestError(getErrorMessage(error));
        }
      } finally {
        if (!cancelled) {
          setOAuthRequestLoading(false);
        }
      }
    }

    void loadOauthRequestApp();

    return () => {
      cancelled = true;
    };
  }, [api, oauthRequest]);

  const openSnackbar = React.useEffectEvent(
    (message: string, severity: SnackbarState["severity"] = "info") => {
      setSnackbar({ open: true, message, severity });
    },
  );

  const logout = React.useEffectEvent(() => {
    setSession({ token: null, profile: null });
    setPortalData(emptyPortalData);
    setLatestSecret(null);
    setOAuthRequestApp(null);
    setOAuthRequestError(null);
    if (window.location.pathname === "/oauth/authorize") {
      window.history.replaceState({}, "", "/");
      setOAuthRequest(null);
    }
    window.location.hash = "dashboard";
    openSnackbar("Сеанс завершён.", "info");
  });

  async function loadPortalData(background = false) {
    if (!session.token) {
      return;
    }
    const requestId = requestCounterRef.current + 1;
    requestCounterRef.current = requestId;
    background ? setSubmitting(true) : setLoading(true);

    try {
      const [
        profile,
        did,
        inbox,
        sent,
        news,
        laws,
        bills,
        parliamentSummary,
        elections,
        referenda,
        directory,
        transactions,
        pushConfig,
        users,
        organizations,
        ledger,
        adminLogs,
        developerApps,
        oauthScopes,
        adminOAuthApps,
      ] = await Promise.all([
        api.me(),
        api.didToken(),
        api.getInbox(),
        api.getSent(),
        api.getNews(),
        api.getLaws(),
        api.getBills(),
        api.getParliamentSummary(),
        api.getParliamentElections(),
        api.getReferenda(),
        api.getRatublesDirectory(),
        api.getRatublesTransactions(),
        optionalRequest(api.getPushConfig(), null),
        optionalRequest(api.getUsers(), []),
        optionalRequest(api.getOrganizations(), []),
        optionalRequest(api.getRatublesLedger(), []),
        optionalRequest(api.getAdminLogs(), []),
        api.getDeveloperApps(),
        api.getDeveloperScopes(),
        optionalRequest(api.getAdminOAuthApps(), []),
      ]);

      let pushStatus = await getPushStatus();
      if (
        pushConfig &&
        pushStatus.supported &&
        pushStatus.permission === "granted" &&
        session.token
      ) {
        try {
          pushStatus = await syncPushSubscription({
            publicKey: pushConfig.public_vapid_key,
            apiBaseUrl,
            token: session.token,
          });
        } catch {
          pushStatus = await getPushStatus();
        }
      }

      if (requestId !== requestCounterRef.current) {
        return;
      }

      React.startTransition(() => {
        setSession((current) => ({ token: current.token, profile }));
        setPortalData({
          did,
          inbox,
          sent,
          news,
          laws,
          bills,
          parliamentSummary,
          elections,
          referenda,
          directory,
          transactions,
          ledger,
          users,
          organizations,
          adminLogs,
          developerApps,
          oauthScopes,
          adminOAuthApps,
          pushConfig,
          pushStatus,
        });
      });
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        logout();
        return;
      }
      openSnackbar(getErrorMessage(error), "error");
    } finally {
      if (requestId === requestCounterRef.current) {
        setLoading(false);
        setSubmitting(false);
      }
    }
  }

  React.useEffect(() => {
    if (session.token) {
      void loadPortalData();
    }
  }, [session.token]);

  React.useEffect(() => {
    if (session.token) {
      void loadPortalData(true);
    }
  }, [overwriteMode, session.token]);

  async function runAction(
    task: () => Promise<void>,
    successMessage?: string,
    refresh = true,
  ) {
    setSubmitting(true);
    try {
      await task();
      if (successMessage) {
        openSnackbar(successMessage, "success");
      }
      if (refresh) {
        await loadPortalData(true);
      }
    } catch (error) {
      openSnackbar(getErrorMessage(error), "error");
    } finally {
      setSubmitting(false);
    }
  }

  const selectedUser =
    portalData.users.find((user) => user.id === selectedUserId) ?? null;
  const selectedLaw =
    portalData.laws.find((law) => law.id === selectedLawId) ?? null;
  const activeElection = currentElection(
    portalData.parliamentSummary,
    portalData.elections,
  );

  const canUseOverwriteMode = hasPermission(session.profile, permissions.root);
  const canManageNews = hasPermission(session.profile, permissions.newsManage);
  const canManageBills = hasPermission(session.profile, permissions.billsManage);
  const canManageReferenda = hasPermission(
    session.profile,
    permissions.referendaManage,
  );
  const canMintRatubles = hasPermission(
    session.profile,
    permissions.ratublesMint,
  );
  const canReadUsers = hasPermission(session.profile, permissions.usersRead);
  const canCreateUsers = hasPermission(session.profile, permissions.usersCreate);
  const canUpdateUsers = hasPermission(session.profile, permissions.usersUpdate);
  const canWritePermissions = hasPermission(
    session.profile,
    permissions.usersPermissionsWrite,
  );
  const canManagePersonnel = hasPermission(
    session.profile,
    permissions.personnelManage,
  );
  const canCreateOrganizations = hasPermission(
    session.profile,
    permissions.orgsCreate,
  );
  const canReadAdminLogs = hasPermission(
    session.profile,
    permissions.adminLogsRead,
  );
  const canReadOAuthApps = hasPermission(
    session.profile,
    permissions.oauthAppsRead,
  );
  const canReviewOAuthApps = hasPermission(
    session.profile,
    permissions.oauthAppsReview,
  );

  const adminVisible =
    canUseOverwriteMode ||
    canReadUsers ||
    canCreateUsers ||
    canUpdateUsers ||
    canWritePermissions ||
    canManagePersonnel ||
    canCreateOrganizations ||
    canReadAdminLogs ||
    canReadOAuthApps ||
    canReviewOAuthApps;

  React.useEffect(() => {
    if (!canUseOverwriteMode && overwriteMode) {
      setOverwriteMode(false);
    }
  }, [canUseOverwriteMode, overwriteMode]);

  const filteredLaws = portalData.laws.filter((law) =>
    [law.title, law.slug, law.level, law.adopted_via, law.current_text]
      .join(" ")
      .toLowerCase()
      .includes(deferredLawSearch.trim().toLowerCase()),
  );

  const navigationItems = [
    { key: "dashboard" as const, label: "Обзор", icon: <DashboardRoundedIcon /> },
    {
      key: "mail" as const,
      label: "GovMail",
      icon: <MailRoundedIcon />,
      badge: portalData.inbox.filter((item) => !item.read_at).length,
    },
    { key: "ratubles" as const, label: "Ratubles", icon: <SavingsRoundedIcon /> },
    {
      key: "parliament" as const,
      label: "Парламент",
      icon: <AccountBalanceRoundedIcon />,
    },
    {
      key: "referenda" as const,
      label: "Референдумы",
      icon: <HowToVoteRoundedIcon />,
    },
    { key: "laws" as const, label: "Законы", icon: <GavelRoundedIcon /> },
    { key: "news" as const, label: "Новости", icon: <CampaignRoundedIcon /> },
    {
      key: "developers" as const,
      label: "Разработчикам",
      icon: <CodeRoundedIcon />,
    },
    {
      key: "admin" as const,
      label: "Управление",
      icon: <AdminPanelSettingsRoundedIcon />,
      hidden: !adminVisible,
    },
  ];

  const handleSectionChange = (nextSection: PortalSection) => {
    if (window.location.pathname === "/oauth/authorize") {
      window.history.replaceState({}, "", "/");
      setOAuthRequest(null);
      setOAuthRequestApp(null);
      setOAuthRequestError(null);
    }
    window.location.hash = nextSection;
    setSection(nextSection);
    setMobileDrawerOpen(false);
  };

  if (!session.token || !session.profile) {
    return (
      <>
        <LoginScreen
          colorMode={colorMode}
          loading={loading || submitting}
          form={loginForm}
          onChange={setLoginForm}
          onSubmit={async () => {
            setLoading(true);
            try {
              const result = await api.login(loginForm.identifier.trim(), loginForm.secret);
              setSession({ token: result.access_token, profile: result.profile });
              setLoginForm({ identifier: "", secret: "" });
              openSnackbar("Вход выполнен.", "success");
            } catch (error) {
              openSnackbar(getErrorMessage(error), "error");
            } finally {
              setLoading(false);
            }
          }}
          onToggleColorMode={onToggleColorMode}
        />
        <AppSnackbar snackbar={snackbar} onClose={() => setSnackbar((current) => ({ ...current, open: false }))} />
      </>
    );
  }

  return (
    <>
      <Box
        sx={{
          minHeight: "100vh",
          backgroundImage: `linear-gradient(180deg, ${theme.palette.background.default}, ${alpha(
            theme.palette.primary.main,
            theme.palette.mode === "light" ? 0.04 : 0.08,
          )})`,
          backgroundColor: theme.palette.background.default,
        }}
      >
        <AppBar
          color="transparent"
          elevation={0}
          position="sticky"
          sx={{
            backdropFilter: "blur(18px)",
            backgroundColor: alpha(theme.palette.background.default, 0.8),
          }}
        >
          {(loading || submitting) && <LinearProgress color="secondary" />}
          <Toolbar sx={{ gap: 1.5 }}>
            {!isDesktop && (
              <IconButton onClick={() => setMobileDrawerOpen(true)}>
                <MenuRoundedIcon />
              </IconButton>
            )}
            <Stack sx={{ minWidth: 0, flex: 1 }}>
              <Typography variant="h6">RGOV</Typography>
              <Typography variant="body2" color="text.secondary" noWrap>
                {navigationItems.find((item) => item.key === section)?.label}
              </Typography>
            </Stack>
            <Chip
              icon={<VerifiedRoundedIcon />}
              label={`УИН ${session.profile.uin}`}
              variant="outlined"
              sx={{ display: { xs: "none", sm: "inline-flex" } }}
            />
            <Tooltip title="Обновить данные">
              <span>
                <IconButton onClick={() => void loadPortalData(true)} disabled={loading || submitting}>
                  <RefreshRoundedIcon />
                </IconButton>
              </span>
            </Tooltip>
            <Tooltip title={colorMode === "light" ? "Тёмная тема" : "Светлая тема"}>
              <IconButton onClick={onToggleColorMode}>
                {colorMode === "light" ? <DarkModeRoundedIcon /> : <LightModeRoundedIcon />}
              </IconButton>
            </Tooltip>
            <Tooltip title="Выйти">
              <IconButton onClick={() => logout()}>
                <LogoutRoundedIcon />
              </IconButton>
            </Tooltip>
            <Avatar src={session.profile.photo_url ?? undefined}>
              {initials(session.profile.full_name)}
            </Avatar>
          </Toolbar>
        </AppBar>

        <Box sx={{ display: "flex" }}>
          <NavigationDrawer
            isDesktop={isDesktop}
            open={mobileDrawerOpen}
            onClose={() => setMobileDrawerOpen(false)}
            profile={session.profile}
            items={navigationItems}
            section={section}
            onSelect={handleSectionChange}
          />
          <Container maxWidth={false} sx={{ width: "100%", py: { xs: 2, md: 3 }, px: { xs: 2, md: 3 } }}>
            {section === "dashboard" && (
              <DashboardSection
                profile={session.profile}
                did={portalData.did}
                news={portalData.news}
                pushConfig={portalData.pushConfig}
                pushStatus={portalData.pushStatus}
                accessForm={accessForm}
                setAccessForm={setAccessForm}
                submitting={submitting}
                onCopyDid={async () => {
                  if (portalData.did?.token) {
                    await navigator.clipboard.writeText(portalData.did.token);
                    openSnackbar("DID-токен скопирован.", "success");
                  }
                }}
                onChangeLogin={() =>
                  void runAction(async () => {
                    await api.changeLogin(accessForm.newLogin.trim());
                    setAccessForm((current) => ({ ...current, newLogin: "" }));
                  }, "Логин обновлён.")
                }
                onChangePassword={() =>
                  void runAction(async () => {
                    await api.changePassword(
                      accessForm.currentPassword,
                      accessForm.newPassword,
                    );
                    setAccessForm((current) => ({
                      ...current,
                      currentPassword: "",
                      newPassword: "",
                      confirmPassword: "",
                    }));
                  }, "Пароль обновлён.")
                }
                onEnablePush={() =>
                  void runAction(
                    async () => {
                      if (!session.token || !portalData.pushConfig) {
                        return;
                      }
                      const status = await enablePush({
                        publicKey: portalData.pushConfig.public_vapid_key,
                        apiBaseUrl,
                        token: session.token,
                      });
                      setPortalData((current) => ({ ...current, pushStatus: status }));
                    },
                    "Push-уведомления включены.",
                    false,
                  )
                }
                onDisablePush={() =>
                  void runAction(
                    async () => {
                      if (!session.token) {
                        return;
                      }
                      const status = await disablePush({ apiBaseUrl, token: session.token });
                      setPortalData((current) => ({ ...current, pushStatus: status }));
                    },
                    "Push-уведомления отключены.",
                    false,
                  )
                }
                onPreviewPush={() =>
                  void runAction(async () => {
                    await previewPush();
                  }, "Тестовое уведомление отправлено.", false)
                }
                onOpenNews={() => handleSectionChange("news")}
              />
            )}
            {section === "mail" && (
              <MailSection
                inbox={portalData.inbox}
                sent={portalData.sent}
                mailboxTab={mailboxTab}
                setMailboxTab={setMailboxTab}
                mailForm={mailForm}
                setMailForm={setMailForm}
                submitting={submitting}
                onSend={() =>
                  void runAction(async () => {
                    await api.sendMail(mailForm.to.trim(), mailForm.subject.trim(), mailForm.text.trim());
                    setMailForm({ to: "", subject: "", text: "" });
                    setMailboxTab("sent");
                  }, "Письмо отправлено.")
                }
              />
            )}
            {section === "ratubles" && (
              <RatublesSection
                profile={session.profile}
                directory={portalData.directory}
                transactions={portalData.transactions}
                ledger={portalData.ledger}
                transferForm={transferForm}
                setTransferForm={setTransferForm}
                mintForm={mintForm}
                setMintForm={setMintForm}
                canMintRatubles={canMintRatubles}
                submitting={submitting}
                onTransfer={() =>
                  void runAction(async () => {
                    const recipient = parseDirectoryValue(transferForm.recipient);
                    await api.transferRatubles({
                      recipientId: recipient.id,
                      recipientKind: recipient.kind,
                      amount: Number(transferForm.amount),
                      reason: transferForm.reason.trim(),
                    });
                    setTransferForm((current) => ({ ...current, amount: "", reason: "" }));
                  }, "Перевод выполнен.")
                }
                onMint={() =>
                  void runAction(async () => {
                    const recipient = parseDirectoryValue(mintForm.recipient);
                    await api.mintRatubles({
                      recipientId: recipient.id,
                      recipientKind: recipient.kind,
                      amount: Number(mintForm.amount),
                      reason: mintForm.reason.trim(),
                    });
                    setMintForm((current) => ({ ...current, amount: "", reason: "" }));
                  }, "Эмиссия выполнена.")
                }
              />
            )}
            {section === "parliament" && (
              <ParliamentSection
                parliamentSummary={portalData.parliamentSummary}
                activeElection={activeElection}
                bills={portalData.bills}
                billForm={billForm}
                setBillForm={setBillForm}
                candidatePartyName={candidatePartyName}
                setCandidatePartyName={setCandidatePartyName}
                canManageBills={canManageBills}
                submitting={submitting}
                onNominate={() =>
                  void runAction(async () => {
                    if (activeElection) {
                      await api.nominateParliamentCandidate(activeElection.id, candidatePartyName.trim());
                      setCandidatePartyName("");
                    }
                  }, "Кандидатура подана.")
                }
                onSignCandidate={(candidateId) =>
                  void runAction(async () => {
                    if (activeElection) {
                      await api.signParliamentCandidate(activeElection.id, candidateId);
                    }
                  }, "Подпись учтена.")
                }
                onVoteCandidate={(candidateId, vote) =>
                  void runAction(async () => {
                    if (activeElection) {
                      await api.voteParliamentCandidate(activeElection.id, candidateId, vote);
                    }
                  }, vote === "yes" ? "Голос за кандидата учтён." : "Голос против кандидата учтён.")
                }
                onCreateBill={() =>
                  void runAction(async () => {
                    await api.createBill({
                      title: billForm.title.trim(),
                      summary: billForm.summary.trim(),
                      proposedText: billForm.proposedText.trim(),
                      lawId: billForm.lawId ? Number(billForm.lawId) : null,
                    });
                    setBillForm({ title: "", summary: "", proposedText: "", lawId: "" });
                  }, "Законопроект создан.")
                }
                onVoteBill={(billId, vote) =>
                  void runAction(async () => {
                    await api.voteBill(billId, vote);
                  }, vote === "yes" ? "Голос за законопроект учтён." : "Голос против законопроекта учтён.")
                }
                onPublishBill={(billId) =>
                  void runAction(async () => {
                    await api.publishBill(billId);
                  }, "Закон опубликован.")
                }
              />
            )}
            {section === "referenda" && (
              <ReferendaSection
                referenda={portalData.referenda}
                referendumForm={referendumForm}
                setReferendumForm={setReferendumForm}
                canManageReferenda={canManageReferenda}
                submitting={submitting}
                matterTypeOptions={matterTypeOptions}
                targetLevelOptions={targetLevelOptions}
                onCreate={() =>
                  void runAction(async () => {
                    await api.createReferendum({
                      title: referendumForm.title.trim(),
                      description: referendumForm.description.trim(),
                      proposedText: referendumForm.proposedText.trim(),
                      targetLevel: referendumForm.targetLevel,
                      matterType: referendumForm.matterType,
                      subjectIdentifier: referendumForm.subjectIdentifier.trim() || undefined,
                      lawId: referendumForm.lawId ? Number(referendumForm.lawId) : null,
                    });
                    setReferendumForm({
                      title: "",
                      description: "",
                      proposedText: "",
                      lawId: "",
                      targetLevel: "constitution",
                      matterType: "constitution_amendment",
                      subjectIdentifier: "",
                    });
                  }, "Инициатива референдума создана.")
                }
                onSign={(referendumId) =>
                  void runAction(async () => {
                    await api.signReferendum(referendumId);
                  }, "Подпись за инициативу учтена.")
                }
                onVote={(referendumId, vote) =>
                  void runAction(async () => {
                    await api.voteReferendum(referendumId, vote);
                  }, vote === "yes" ? "Голос за референдум учтён." : "Голос против референдума учтён.")
                }
                onPublish={(referendumId) =>
                  void runAction(async () => {
                    await api.publishReferendum(referendumId);
                  }, "Итог референдума опубликован.")
                }
              />
            )}
            {section === "laws" && (
              <LawsSection laws={filteredLaws} search={lawSearch} setSearch={setLawSearch} />
            )}
            {section === "news" && (
              <NewsSection
                news={portalData.news}
                newsForm={newsForm}
                setNewsForm={setNewsForm}
                canManageNews={canManageNews}
                submitting={submitting}
                onCreate={() =>
                  void runAction(async () => {
                    await api.postNews(newsForm.title.trim(), newsForm.body.trim());
                    setNewsForm({ title: "", body: "" });
                  }, "Новость опубликована.")
                }
                onDelete={(newsId) =>
                  void runAction(async () => {
                    await api.deleteNews(newsId);
                  }, "Новость удалена.")
                }
              />
            )}
            {section === "developers" && (
              <DeveloperSection
                developerApps={portalData.developerApps}
                oauthScopes={portalData.oauthScopes}
                createAppForm={developerAppForm}
                setCreateAppForm={setDeveloperAppForm}
                latestSecret={latestSecret}
                oauthRequest={oauthRequest}
                oauthRequestApp={oauthRequestApp}
                oauthRequestLoading={oauthRequestLoading}
                oauthRequestError={oauthRequestError}
                submitting={submitting}
                onCreateApp={() =>
                  void runAction(async () => {
                    const created = await api.createDeveloperApp({
                      name: developerAppForm.name.trim(),
                      slug: developerAppForm.slug.trim(),
                      description: developerAppForm.description.trim(),
                      websiteUrl: developerAppForm.websiteUrl.trim(),
                      redirectUris: developerAppForm.redirectUris
                        .split("\n")
                        .map((item) => item.trim())
                        .filter(Boolean),
                      allowedScopes: developerAppForm.allowedScopes,
                    });
                    setLatestSecret({
                      label: `Секрет для ${created.name}`,
                      clientId: created.client_id,
                      clientSecret: created.client_secret,
                      rotatedAt: created.created_at,
                    });
                    setDeveloperAppForm({
                      name: "",
                      slug: "",
                      description: "",
                      websiteUrl: "",
                      redirectUris: "",
                      allowedScopes: ["profile.basic"],
                    });
                  }, "OAuth-приложение зарегистрировано и отправлено на модерацию.")
                }
                onRotateSecret={(appId) =>
                  void runAction(async () => {
                    const app = portalData.developerApps.find((candidate) => candidate.id === appId);
                    const rotated = await api.rotateDeveloperAppSecret(appId);
                    setLatestSecret({
                      label: `Новый секрет для ${app?.name ?? rotated.client_id}`,
                      clientId: rotated.client_id,
                      clientSecret: rotated.client_secret,
                      rotatedAt: rotated.rotated_at,
                    });
                  }, "Client secret обновлён.")
                }
                onApproveOAuthRequest={() =>
                  void runAction(async () => {
                    if (!oauthRequest) {
                      return;
                    }
                    const result = await api.completeOAuthAuthorization({
                      clientId: oauthRequest.clientId,
                      redirectUri: oauthRequest.redirectUri,
                      responseType: oauthRequest.responseType,
                      scope: oauthRequest.scope,
                      state: oauthRequest.state,
                    });
                    window.location.href = result.redirect_to;
                  }, undefined, false)
                }
                onDenyOAuthRequest={() =>
                  void runAction(async () => {
                    if (!oauthRequest) {
                      return;
                    }
                    const result = await api.denyOAuthAuthorization({
                      clientId: oauthRequest.clientId,
                      redirectUri: oauthRequest.redirectUri,
                      responseType: oauthRequest.responseType,
                      scope: oauthRequest.scope,
                      state: oauthRequest.state,
                    });
                    window.location.href = result.redirect_to;
                  }, undefined, false)
                }
              />
            )}
            {section === "admin" && (
              <AdminSection
                visible={adminVisible}
                activeNode={adminTreeNode}
                setActiveNode={setAdminTreeNode}
                laws={portalData.laws}
                users={portalData.users}
                organizations={portalData.organizations}
                adminLogs={portalData.adminLogs}
                oauthApps={portalData.adminOAuthApps}
                createUserForm={createUserForm}
                setCreateUserForm={setCreateUserForm}
                selectedUserId={selectedUserId}
                setSelectedUserId={setSelectedUserId}
                selectedUser={selectedUser}
                userEditForm={userEditForm}
                setUserEditForm={setUserEditForm}
                selectedLawId={selectedLawId}
                setSelectedLawId={setSelectedLawId}
                selectedLaw={selectedLaw}
                lawEditForm={lawEditForm}
                setLawEditForm={setLawEditForm}
                organizationForm={organizationForm}
                setOrganizationForm={setOrganizationForm}
                permissionPresets={permissionPresets}
                canUseOverwriteMode={canUseOverwriteMode}
                overwriteMode={overwriteMode}
                setOverwriteMode={setOverwriteMode}
                canReadUsers={canReadUsers}
                canCreateUsers={canCreateUsers}
                canUpdateUsers={canUpdateUsers}
                canWritePermissions={canWritePermissions}
                canManagePersonnel={canManagePersonnel}
                canCreateOrganizations={canCreateOrganizations}
                canReadAdminLogs={canReadAdminLogs}
                canReadOAuthApps={canReadOAuthApps}
                canReviewOAuthApps={canReviewOAuthApps}
                submitting={submitting}
                onCreateUser={() =>
                  void runAction(async () => {
                    await api.createUser({
                      uin: createUserForm.uin.trim(),
                      uan: createUserForm.uan.trim(),
                      login: createUserForm.login.trim(),
                      password: createUserForm.password,
                      firstName: createUserForm.firstName.trim(),
                      lastName: createUserForm.lastName.trim(),
                      patronymic: createUserForm.patronymic.trim(),
                      permissions: parsePermissionsInput(createUserForm.permissions),
                      orgSlug: createUserForm.orgSlug.trim() || undefined,
                      positionTitle: createUserForm.positionTitle.trim(),
                    });
                    setCreateUserForm({
                      uin: "",
                      uan: "",
                      login: "",
                      password: "",
                      firstName: "",
                      lastName: "",
                      patronymic: "",
                      permissions: "",
                      orgSlug: "",
                      positionTitle: "",
                    });
                  }, "Пользователь создан.")
                }
                onUpdateUser={() =>
                  void runAction(async () => {
                    if (!selectedUser) {
                      return;
                    }
                    await api.updateUser({
                      userId: selectedUser.id,
                      uin: userEditForm.uin.trim(),
                      uan: userEditForm.uan.trim(),
                      firstName: userEditForm.firstName.trim(),
                      lastName: userEditForm.lastName.trim(),
                      patronymic: userEditForm.patronymic.trim(),
                    });
                  }, "Данные пользователя обновлены.")
                }
                onUpdatePermissions={() =>
                  void runAction(async () => {
                    if (!selectedUser) {
                      return;
                    }
                    await api.changeUserPermissions(
                      selectedUser.id,
                      parsePermissionsInput(userEditForm.permissions),
                    );
                  }, "Права доступа обновлены.")
                }
                onHire={() =>
                  void runAction(async () => {
                    if (!selectedUser) {
                      return;
                    }
                    await api.hireUser(
                      selectedUser.id,
                      userEditForm.orgSlug,
                      userEditForm.positionTitle.trim(),
                    );
                  }, "Назначение выполнено.")
                }
                onFire={() =>
                  void runAction(async () => {
                    if (!selectedUser) {
                      return;
                    }
                    await api.fireUser(selectedUser.id);
                  }, "Пользователь освобождён от должности.")
                }
                onCreateOrganization={() =>
                  void runAction(async () => {
                    await api.createOrganization({
                      name: organizationForm.name.trim(),
                      slug: organizationForm.slug.trim(),
                      description: organizationForm.description.trim(),
                    });
                    setOrganizationForm({ name: "", slug: "", description: "" });
                  }, "Организация создана.")
                }
                onReviewOAuthApp={(appId, status, reviewNote) =>
                  void runAction(async () => {
                    await api.reviewAdminOAuthApp(appId, { status, reviewNote });
                  }, "Статус OAuth-приложения обновлён.")
                }
                onOverwriteLaw={() =>
                  void runAction(async () => {
                    if (!selectedLaw) {
                      return;
                    }
                    await api.overwriteLaw(selectedLaw.id, {
                      title: lawEditForm.title.trim(),
                      slug: lawEditForm.slug.trim(),
                      level: lawEditForm.level.trim(),
                      status: lawEditForm.status.trim(),
                      adoptedVia: lawEditForm.adoptedVia.trim(),
                      currentText: lawEditForm.currentText,
                      reason: lawEditForm.reason.trim(),
                    });
                  }, "Закон перезаписан в overwrite mode.")
                }
              />
            )}
          </Container>
        </Box>
      </Box>
      <AppSnackbar snackbar={snackbar} onClose={() => setSnackbar((current) => ({ ...current, open: false }))} />
    </>
  );
}

function NavigationDrawer(props: {
  isDesktop: boolean;
  open: boolean;
  onClose: () => void;
  profile: UserRead;
  items: Array<{
    key: PortalSection;
    label: string;
    icon: React.ReactNode;
    badge?: number;
    hidden?: boolean;
  }>;
  section: PortalSection;
  onSelect: (nextSection: PortalSection) => void;
}) {
  const theme = useTheme();

  const content = (
    <Box sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <Box sx={{ px: 3, py: 3 }}>
        <Box component="img" src="/ratcraftia-mark.svg" alt="RGOV" sx={{ width: "100%", maxWidth: 180 }} />
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1.5 }}>
          Единый портал Ratcraftia: профиль, законы, парламент, референдумы и Ratubles.
        </Typography>
      </Box>
      <Divider />
      <List sx={{ px: 1.5, py: 2 }}>
        {props.items.filter((item) => !item.hidden).map((item) => (
          <ListItem key={item.key} disablePadding sx={{ mb: 0.75 }}>
            <ListItemButton selected={item.key === props.section} onClick={() => props.onSelect(item.key)}>
              <ListItemIcon sx={{ minWidth: 42 }}>
                {typeof item.badge === "number" && item.badge > 0 ? (
                  <Badge badgeContent={item.badge} color="secondary">
                    {item.icon}
                  </Badge>
                ) : (
                  item.icon
                )}
              </ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Box sx={{ mt: "auto", p: 2 }}>
        <Card
          sx={{
            bgcolor: alpha(
              props.profile.permissions.includes("*")
                ? "#006a67"
                : "#4b635f",
              0.1,
            ),
            borderColor: alpha(theme.palette.primary.main, 0.16),
          }}
        >
          <CardContent>
            <Typography sx={{ fontWeight: 700 }}>{props.profile.full_name}</Typography>
            <Typography variant="body2" color="text.secondary">
              {props.profile.permissions_label}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Баланс: {formatNumber(props.profile.ratubles)} Ratubles
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );

  if (props.isDesktop) {
    return (
      <Drawer
        open
        variant="permanent"
        PaperProps={{
          sx: {
            width: drawerWidth,
            position: "sticky",
            top: 0,
            height: "100vh",
          },
        }}
      >
        {content}
      </Drawer>
    );
  }

  return (
    <Drawer
      open={props.open}
      onClose={props.onClose}
      ModalProps={{ keepMounted: true }}
      PaperProps={{ sx: { width: drawerWidth } }}
    >
      {content}
    </Drawer>
  );
}

function AppSnackbar(props: {
  snackbar: SnackbarState;
  onClose: () => void;
}) {
  return (
    <Snackbar open={props.snackbar.open} autoHideDuration={4000} onClose={props.onClose}>
      <Alert severity={props.snackbar.severity} variant="filled" onClose={props.onClose}>
        {props.snackbar.message}
      </Alert>
    </Snackbar>
  );
}
