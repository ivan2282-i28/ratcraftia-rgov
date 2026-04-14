export interface OrganizationRead {
  id: number;
  name: string;
  slug: string;
  kind: string;
  description: string;
  ratubles: number;
}

export interface UserRead {
  id: number;
  uin: string;
  uan: string;
  login: string;
  first_name: string;
  last_name: string;
  patronymic: string;
  full_name: string;
  permissions: string[];
  permissions_label: string;
  is_active: boolean;
  ratubles: number;
  position_title: string;
  organization: OrganizationRead | null;
  photo_url: string | null;
  aliases: string[];
  next_login_change_at: string | null;
  is_deputy: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  profile: UserRead;
}

export interface DidTokenResponse {
  token: string;
  expires_at: string;
  payload: Record<string, string>;
}

export interface MailRead {
  id: number;
  from_address: string;
  to_address: string;
  subject: string;
  text: string;
  sender_name: string;
  recipient_name: string;
  created_at: string;
  read_at: string | null;
}

export interface NewsRead {
  id: number;
  title: string;
  body: string;
  author_name: string;
  created_at: string;
}

export interface LawRead {
  id: number;
  title: string;
  slug: string;
  level: string;
  version: number;
  status: string;
  adopted_via: string;
  current_text: string;
  updated_at: string;
}

export interface BillRead {
  id: number;
  title: string;
  summary: string;
  proposed_text: string;
  law_id: number | null;
  target_level: string;
  status: string;
  proposer_name: string;
  created_at: string;
  yes_votes: number;
  no_votes: number;
  total_votes: number;
  quorum_required: number;
  quorum_reached: boolean;
}

export interface ParliamentCandidateRead {
  id: number;
  user_id: number;
  full_name: string;
  party_name: string;
  status: string;
  signatures: number;
  required_signatures: number;
  votes: number;
}

export interface ParliamentElectionRead {
  id: number;
  title: string;
  kind: string;
  status: string;
  seat_count: number;
  opens_at: string;
  closes_at: string;
  created_at: string;
  total_ballots: number;
  candidate_count: number;
  registered_candidate_count: number;
  candidates: ParliamentCandidateRead[];
}

export interface DeputyRead {
  user_id: number;
  full_name: string;
  seat_number: number;
  starts_at: string;
  ends_at: string;
}

export interface ParliamentSummaryRead {
  seat_count: number;
  quorum: number;
  vacancies: number;
  deputies: DeputyRead[];
  active_election: ParliamentElectionRead | null;
}

export interface ReferendumRead {
  id: number;
  title: string;
  description: string;
  proposed_text: string;
  law_id: number | null;
  target_level: string;
  matter_type: string;
  status: string;
  proposer_name: string;
  subject_user_id: number | null;
  subject_name: string | null;
  opens_at: string;
  closes_at: string;
  created_at: string;
  signature_count: number;
  required_signatures: number;
  yes_votes: number;
  no_votes: number;
  total_votes: number;
  required_quorum: number;
  quorum_reached: boolean;
}

export interface ReferendumOutcomeRead {
  referendum: ReferendumRead;
  law: LawRead | null;
  detail: string;
}

export interface RatublesDirectoryEntryRead {
  id: number;
  kind: "user" | "organization";
  code: string;
  full_name: string;
  subtitle: string;
}

export interface RatublesTransactionRead {
  id: number;
  kind: string;
  direction: string;
  amount: number;
  reason: string;
  sender_kind: string | null;
  sender_name: string | null;
  sender_code: string | null;
  sender_uin: string | null;
  recipient_kind: string;
  recipient_name: string | null;
  recipient_code: string | null;
  recipient_uin: string | null;
  actor_name: string | null;
  created_at: string;
}

export interface AdminLogRead {
  id: number;
  action: string;
  summary: string;
  reason: string;
  actor_name: string;
  target_name: string | null;
  created_at: string;
}

export interface PushConfigResponse {
  public_vapid_key: string;
  contact_email: string;
}

export interface MessageResponse {
  detail: string;
}

export interface PushStatus {
  supported: boolean;
  permission: NotificationPermission | "default";
  subscribed: boolean;
  message: string;
}
