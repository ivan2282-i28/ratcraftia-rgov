import type {
  AdminLogRead,
  BillRead,
  DeveloperAppCreateResponse,
  DeveloperAppRead,
  DeveloperAppSecretResponse,
  DeveloperScopeRead,
  DidTokenResponse,
  LawRead,
  MailRead,
  MessageResponse,
  NewsRead,
  OAuthAuthorizationResponse,
  OrganizationRead,
  ParliamentElectionRead,
  ParliamentSummaryRead,
  PublicOAuthAppRead,
  PushConfigResponse,
  RatublesDirectoryEntryRead,
  RatublesTransactionRead,
  ReferendumOutcomeRead,
  ReferendumRead,
  TokenResponse,
  UserRead,
} from "../types";

export const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "/api";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}

type RequestOptions = {
  body?: unknown;
  requiresAuth?: boolean;
  method?: "GET" | "POST" | "PATCH" | "DELETE";
};

export class ApiClient {
  private token: string | null = null;
  private overwriteMode = false;

  setToken(token: string | null) {
    this.token = token;
  }

  setOverwriteMode(enabled: boolean) {
    this.overwriteMode = enabled;
  }

  private async request<T>(
    path: string,
    { body, method = "GET", requiresAuth = true }: RequestOptions = {},
  ): Promise<T> {
    const headers: Record<string, string> = {
      Accept: "application/json",
    };

    const init: RequestInit = { method, headers };

    if (body !== undefined) {
      headers["Content-Type"] = "application/json";
      init.body = JSON.stringify(body);
    }

    if (requiresAuth) {
      if (!this.token) {
        throw new ApiError("Сессия не активна.", 401);
      }
      headers.Authorization = `Bearer ${this.token}`;
      if (this.overwriteMode) {
        headers["X-RGOV-Overwrite-Mode"] = "true";
      }
    }

    const response = await fetch(`${apiBaseUrl}${path}`, init);
    const contentType = response.headers.get("content-type") ?? "";
    const isJson = contentType.includes("application/json");
    const payload = isJson ? await response.json() : null;

    if (!response.ok) {
      const detail =
        payload && typeof payload === "object" && "detail" in payload
          ? String(payload.detail)
          : `Ошибка ${response.status}`;
      throw new ApiError(detail, response.status);
    }

    return payload as T;
  }

  login(identifier: string, secret: string) {
    return this.request<TokenResponse>("/auth/login", {
      method: "POST",
      body: { identifier, secret },
      requiresAuth: false,
    });
  }

  me() {
    return this.request<UserRead>("/auth/me");
  }

  didToken() {
    return this.request<DidTokenResponse>("/did/me/token");
  }

  changeLogin(newLogin: string) {
    return this.request<UserRead>("/auth/change-login", {
      method: "POST",
      body: { new_login: newLogin },
    });
  }

  changePassword(currentPassword: string, newPassword: string) {
    return this.request<MessageResponse>("/auth/change-password", {
      method: "POST",
      body: {
        current_password: currentPassword,
        new_password: newPassword,
      },
    });
  }

  getPushConfig() {
    return this.request<PushConfigResponse>("/notifications/config");
  }

  getInbox() {
    return this.request<MailRead[]>("/mail/messages?box=inbox");
  }

  getSent() {
    return this.request<MailRead[]>("/mail/messages?box=sent");
  }

  sendMail(to: string, subject: string, text: string) {
    return this.request<MailRead>("/mail/messages", {
      method: "POST",
      body: { to, subject, text },
    });
  }

  getNews() {
    return this.request<NewsRead[]>("/news", { requiresAuth: false });
  }

  postNews(title: string, body: string) {
    return this.request<NewsRead>("/news", {
      method: "POST",
      body: { title, body },
    });
  }

  deleteNews(newsId: number) {
    return this.request<MessageResponse>(`/news/${newsId}`, {
      method: "DELETE",
    });
  }

  getLaws() {
    return this.request<LawRead[]>("/laws", { requiresAuth: false });
  }

  getBills() {
    return this.request<BillRead[]>("/parliament/bills", { requiresAuth: false });
  }

  getParliamentSummary() {
    return this.request<ParliamentSummaryRead>("/parliament/summary", {
      requiresAuth: false,
    });
  }

  getParliamentElections() {
    return this.request<ParliamentElectionRead[]>("/parliament/elections", {
      requiresAuth: false,
    });
  }

  nominateParliamentCandidate(electionId: number, partyName: string) {
    return this.request<ParliamentElectionRead>(
      `/parliament/elections/${electionId}/candidates`,
      {
        method: "POST",
        body: { party_name: partyName },
      },
    );
  }

  signParliamentCandidate(electionId: number, candidateId: number) {
    return this.request<ParliamentElectionRead>(
      `/parliament/elections/${electionId}/candidates/${candidateId}/sign`,
      {
        method: "POST",
      },
    );
  }

  voteParliamentCandidate(
    electionId: number,
    candidateId: number,
    vote: "yes" | "no",
  ) {
    return this.request<ParliamentElectionRead>(
      `/parliament/elections/${electionId}/candidates/${candidateId}/vote`,
      {
        method: "POST",
        body: { vote },
      },
    );
  }

  createBill(payload: {
    title: string;
    summary: string;
    proposedText: string;
    lawId?: number | null;
  }) {
    return this.request<BillRead>("/parliament/bills", {
      method: "POST",
      body: {
        title: payload.title,
        summary: payload.summary,
        proposed_text: payload.proposedText,
        law_id: payload.lawId ?? null,
        target_level: "law",
      },
    });
  }

  voteBill(billId: number, vote: "yes" | "no") {
    return this.request<BillRead>(`/parliament/bills/${billId}/vote`, {
      method: "POST",
      body: { vote },
    });
  }

  publishBill(billId: number) {
    return this.request<LawRead>(`/parliament/bills/${billId}/publish`, {
      method: "POST",
    });
  }

  getReferenda() {
    return this.request<ReferendumRead[]>("/referenda", { requiresAuth: false });
  }

  createReferendum(payload: {
    title: string;
    description: string;
    proposedText: string;
    targetLevel: string;
    matterType: string;
    subjectIdentifier?: string;
    lawId?: number | null;
  }) {
    return this.request<ReferendumRead>("/referenda", {
      method: "POST",
      body: {
        title: payload.title,
        description: payload.description,
        proposed_text: payload.proposedText,
        law_id: payload.lawId ?? null,
        target_level: payload.targetLevel,
        matter_type: payload.matterType,
        subject_identifier: payload.subjectIdentifier || null,
        closes_in_days: 4,
      },
    });
  }

  signReferendum(referendumId: number) {
    return this.request<ReferendumRead>(`/referenda/${referendumId}/sign`, {
      method: "POST",
    });
  }

  voteReferendum(referendumId: number, vote: "yes" | "no") {
    return this.request<ReferendumRead>(`/referenda/${referendumId}/vote`, {
      method: "POST",
      body: { vote },
    });
  }

  publishReferendum(referendumId: number) {
    return this.request<ReferendumOutcomeRead>(
      `/referenda/${referendumId}/publish`,
      {
        method: "POST",
      },
    );
  }

  getRatublesDirectory() {
    return this.request<RatublesDirectoryEntryRead[]>("/ratubles/directory");
  }

  getRatublesTransactions() {
    return this.request<RatublesTransactionRead[]>("/ratubles/transactions");
  }

  getRatublesLedger() {
    return this.request<RatublesTransactionRead[]>("/ratubles/ledger");
  }

  transferRatubles(payload: {
    recipientId: number;
    recipientKind: "user" | "organization";
    amount: number;
    reason: string;
  }) {
    return this.request<RatublesTransactionRead>("/ratubles/transfer", {
      method: "POST",
      body: {
        recipient_id: payload.recipientId,
        recipient_kind: payload.recipientKind,
        amount: payload.amount,
        reason: payload.reason,
      },
    });
  }

  mintRatubles(payload: {
    recipientId: number;
    recipientKind: "user" | "organization";
    amount: number;
    reason: string;
  }) {
    return this.request<RatublesTransactionRead>("/ratubles/mint", {
      method: "POST",
      body: {
        recipient_id: payload.recipientId,
        recipient_kind: payload.recipientKind,
        amount: payload.amount,
        reason: payload.reason,
      },
    });
  }

  getUsers() {
    return this.request<UserRead[]>("/admin/users");
  }

  createUser(payload: {
    uin: string;
    uan: string;
    login: string;
    password: string;
    firstName: string;
    lastName: string;
    patronymic: string;
    permissions: string[];
    orgSlug?: string;
    positionTitle: string;
  }) {
    return this.request<UserRead>("/admin/users", {
      method: "POST",
      body: {
        uin: payload.uin,
        uan: payload.uan,
        login: payload.login,
        password: payload.password,
        first_name: payload.firstName,
        last_name: payload.lastName,
        patronymic: payload.patronymic,
        permissions: payload.permissions,
        org_slug: payload.orgSlug || null,
        position_title: payload.positionTitle,
      },
    });
  }

  updateUser(payload: {
    userId: number;
    uin: string;
    uan: string;
    firstName: string;
    lastName: string;
    patronymic: string;
  }) {
    return this.request<UserRead>(`/admin/users/${payload.userId}`, {
      method: "PATCH",
      body: {
        uin: payload.uin,
        uan: payload.uan,
        first_name: payload.firstName,
        last_name: payload.lastName,
        patronymic: payload.patronymic,
      },
    });
  }

  changeUserPermissions(userId: number, permissions: string[]) {
    return this.request<UserRead>(`/admin/users/${userId}/permissions`, {
      method: "POST",
      body: { permissions },
    });
  }

  hireUser(userId: number, orgSlug: string, positionTitle: string) {
    return this.request<UserRead>(`/admin/users/${userId}/hire`, {
      method: "POST",
      body: { org_slug: orgSlug, position_title: positionTitle },
    });
  }

  fireUser(userId: number) {
    return this.request<UserRead>(`/admin/users/${userId}/fire`, {
      method: "POST",
    });
  }

  getOrganizations() {
    return this.request<OrganizationRead[]>("/admin/organizations");
  }

  overwriteLaw(
    lawId: number,
    payload: {
      title: string;
      slug: string;
      level: string;
      currentText: string;
      status: string;
      adoptedVia: string;
      reason: string;
    },
  ) {
    return this.request<LawRead>(`/admin/laws/${lawId}/overwrite`, {
      method: "POST",
      body: {
        title: payload.title,
        slug: payload.slug,
        level: payload.level,
        current_text: payload.currentText,
        status: payload.status,
        adopted_via: payload.adoptedVia,
        reason: payload.reason,
      },
    });
  }

  createOrganization(payload: {
    name: string;
    slug: string;
    description: string;
  }) {
    return this.request<OrganizationRead>("/admin/organizations", {
      method: "POST",
      body: {
        name: payload.name,
        slug: payload.slug,
        description: payload.description,
        kind: "government",
      },
    });
  }

  getAdminLogs() {
    return this.request<AdminLogRead[]>("/admin/logs");
  }

  getAdminOAuthApps() {
    return this.request<DeveloperAppRead[]>("/admin/oauth/apps");
  }

  reviewAdminOAuthApp(
    appId: number,
    payload: { status: "approved" | "rejected" | "revoked"; reviewNote: string },
  ) {
    return this.request<DeveloperAppRead>(`/admin/oauth/apps/${appId}/review`, {
      method: "POST",
      body: {
        status: payload.status,
        review_note: payload.reviewNote,
      },
    });
  }

  getDeveloperScopes() {
    return this.request<DeveloperScopeRead[]>("/developer/scopes", {
      requiresAuth: false,
    });
  }

  getDeveloperApps() {
    return this.request<DeveloperAppRead[]>("/developer/apps");
  }

  createDeveloperApp(payload: {
    name: string;
    slug: string;
    description: string;
    websiteUrl: string;
    redirectUris: string[];
    allowedScopes: string[];
  }) {
    return this.request<DeveloperAppCreateResponse>("/developer/apps", {
      method: "POST",
      body: {
        name: payload.name,
        slug: payload.slug,
        description: payload.description,
        website_url: payload.websiteUrl,
        redirect_uris: payload.redirectUris,
        allowed_scopes: payload.allowedScopes,
      },
    });
  }

  rotateDeveloperAppSecret(appId: number) {
    return this.request<DeveloperAppSecretResponse>(
      `/developer/apps/${appId}/rotate-secret`,
      {
        method: "POST",
      },
    );
  }

  getPublicOAuthApp(clientId: string) {
    return this.request<PublicOAuthAppRead>(`/public/oauth/apps/${clientId}`, {
      requiresAuth: false,
    });
  }

  completeOAuthAuthorization(payload: {
    clientId: string;
    redirectUri: string;
    responseType: "code";
    scope: string;
    state?: string;
  }) {
    return this.request<OAuthAuthorizationResponse>("/public/oauth/authorize/complete", {
      method: "POST",
      body: {
        client_id: payload.clientId,
        redirect_uri: payload.redirectUri,
        response_type: payload.responseType,
        scope: payload.scope,
        state: payload.state ?? null,
      },
    });
  }

  denyOAuthAuthorization(payload: {
    clientId: string;
    redirectUri: string;
    responseType: "code";
    scope: string;
    state?: string;
  }) {
    return this.request<OAuthAuthorizationResponse>("/public/oauth/authorize/deny", {
      method: "POST",
      body: {
        client_id: payload.clientId,
        redirect_uri: payload.redirectUri,
        response_type: payload.responseType,
        scope: payload.scope,
        state: payload.state ?? null,
      },
      requiresAuth: false,
    });
  }
}
