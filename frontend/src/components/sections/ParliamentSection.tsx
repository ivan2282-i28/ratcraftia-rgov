import * as React from "react";
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Button,
  Chip,
  Divider,
  MenuItem,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import ExpandMoreRoundedIcon from "@mui/icons-material/ExpandMoreRounded";
import AccountBalanceRoundedIcon from "@mui/icons-material/AccountBalanceRounded";
import HowToRegRoundedIcon from "@mui/icons-material/HowToRegRounded";
import VerifiedRoundedIcon from "@mui/icons-material/VerifiedRounded";
import type { BillRead, ParliamentElectionRead, ParliamentSummaryRead } from "../../types";
import { formatDate, formatDateTime, sentenceCase } from "../../lib/format";
import { EmptyState, HeroCard, MetricCard, ResponsiveGrid, SectionCard } from "../common";

type BillForm = {
  title: string;
  summary: string;
  proposedText: string;
  lawId: string;
};

export function ParliamentSection(props: {
  parliamentSummary: ParliamentSummaryRead | null;
  activeElection: ParliamentElectionRead | null;
  bills: BillRead[];
  billForm: BillForm;
  setBillForm: React.Dispatch<React.SetStateAction<BillForm>>;
  candidatePartyName: string;
  setCandidatePartyName: React.Dispatch<React.SetStateAction<string>>;
  canManageBills: boolean;
  submitting: boolean;
  onNominate: () => void;
  onSignCandidate: (candidateId: number) => void;
  onVoteCandidate: (candidateId: number, vote: "yes" | "no") => void;
  onCreateBill: () => void;
  onVoteBill: (billId: number, vote: "yes" | "no") => void;
  onPublishBill: (billId: number) => void;
}) {
  const election = props.activeElection;

  return (
    <Stack spacing={2.5}>
      <HeroCard
        title="Парламент"
        description="Обзор мандатов, активных выборов и законотворческого потока в одном месте."
        chips={[
          `${props.parliamentSummary?.seat_count ?? 0} мест`,
          `${props.bills.length} законопроектов`,
          `${props.activeElection?.candidate_count ?? 0} кандидатов`,
        ]}
      />
      <ResponsiveGrid>
        <MetricCard
          title="Действующие депутаты"
          value={String(props.parliamentSummary?.deputies.length ?? 0)}
          description="Активные мандаты"
          icon={<AccountBalanceRoundedIcon />}
          accent="primary"
        />
        <MetricCard
          title="Кворум"
          value={String(props.parliamentSummary?.quorum ?? 0)}
          description="Минимум для решений"
          icon={<VerifiedRoundedIcon />}
          accent="neutral"
        />
        <MetricCard
          title="Свободные места"
          value={String(props.parliamentSummary?.vacancies ?? 0)}
          description="Требуют довыборов"
          icon={<HowToRegRoundedIcon />}
          accent="secondary"
        />
      </ResponsiveGrid>
      <ResponsiveGrid columns={{ xs: "1fr", xl: "1.1fr 1fr" }}>
        <SectionCard title="Состав парламента" subtitle="Действующие мандаты и сроки полномочий.">
          <Stack spacing={1.25}>
            {props.parliamentSummary?.deputies.map((deputy) => (
              <Paper key={deputy.user_id} variant="outlined" sx={{ p: 1.75, borderRadius: 4 }}>
                <Stack
                  direction={{ xs: "column", sm: "row" }}
                  justifyContent="space-between"
                  spacing={1}
                >
                  <Stack spacing={0.4}>
                    <Typography variant="subtitle1">{deputy.full_name}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Место №{deputy.seat_number}
                    </Typography>
                  </Stack>
                  <Typography variant="body2" color="text.secondary">
                    До {formatDate(deputy.ends_at)}
                  </Typography>
                </Stack>
              </Paper>
            ))}
            {(props.parliamentSummary?.deputies.length ?? 0) === 0 && (
              <EmptyState text="Активных мандатов пока нет." />
            )}
          </Stack>
        </SectionCard>
        <SectionCard
          title="Текущие выборы"
          subtitle="Выдвижение, подписи и поддержка кандидатов."
          action={
            props.activeElection && (
              <Chip
                label={sentenceCase(props.activeElection.status)}
                color={props.activeElection.status === "open" ? "success" : "default"}
                variant="outlined"
              />
            )
          }
        >
          <Stack spacing={1.25}>
            {election ? (
              <>
                <Typography variant="h6">{election.title}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Голосование открыто до {formatDateTime(election.closes_at)}
                </Typography>
                <TextField
                  label="Партия или объединение"
                  value={props.candidatePartyName}
                  onChange={(event) => props.setCandidatePartyName(event.target.value)}
                  helperText="Если оставить поле пустым, кандидат пойдёт как самовыдвиженец."
                />
                <Button
                  variant="contained"
                  disabled={props.submitting || election.status !== "open"}
                  onClick={props.onNominate}
                >
                  Подать кандидатуру
                </Button>
                <Divider sx={{ my: 1 }} />
                <Stack spacing={1}>
                  {election.candidates.map((candidate) => (
                    <Paper key={candidate.id} variant="outlined" sx={{ p: 1.75, borderRadius: 4 }}>
                      <Stack spacing={1}>
                        <Stack
                          direction={{ xs: "column", sm: "row" }}
                          justifyContent="space-between"
                          spacing={1}
                        >
                          <Stack spacing={0.4}>
                            <Typography variant="subtitle1">{candidate.full_name}</Typography>
                            <Typography variant="body2" color="text.secondary">
                              {candidate.party_name || "Самовыдвиженец"}
                            </Typography>
                          </Stack>
                          <Chip
                            label={sentenceCase(candidate.status)}
                            color={
                              candidate.status === "registered"
                                ? "success"
                                : candidate.status === "elected"
                                  ? "primary"
                                  : "default"
                            }
                          />
                        </Stack>
                        <Typography variant="body2" color="text.secondary">
                          Подписи {candidate.signatures}/{candidate.required_signatures} ·
                          Поддержка {candidate.votes}
                        </Typography>
                        <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
                          <Button
                            size="small"
                            variant="outlined"
                            disabled={props.submitting || election.status !== "open"}
                            onClick={() => props.onSignCandidate(candidate.id)}
                          >
                            Подписать
                          </Button>
                          <Button
                            size="small"
                            variant="contained"
                            disabled={props.submitting || election.status !== "open"}
                            onClick={() => props.onVoteCandidate(candidate.id, "yes")}
                          >
                            Поддержать
                          </Button>
                          <Button
                            size="small"
                            variant="text"
                            disabled={props.submitting || election.status !== "open"}
                            onClick={() => props.onVoteCandidate(candidate.id, "no")}
                          >
                            Отозвать поддержку
                          </Button>
                        </Stack>
                      </Stack>
                    </Paper>
                  ))}
                  {election.candidates.length === 0 && (
                    <EmptyState text="Кандидаты пока не зарегистрированы." />
                  )}
                </Stack>
              </>
            ) : (
              <EmptyState text="Активных парламентских выборов сейчас нет." />
            )}
          </Stack>
        </SectionCard>
      </ResponsiveGrid>
      <ResponsiveGrid columns={{ xs: "1fr", xl: "400px minmax(0, 1fr)" }}>
        <SectionCard title="Новый законопроект" subtitle="Создание доступно парламенту и администраторам.">
          <Stack spacing={1.25}>
            <TextField
              label="Название"
              disabled={!props.canManageBills}
              value={props.billForm.title}
              onChange={(event) =>
                props.setBillForm((current) => ({
                  ...current,
                  title: event.target.value,
                }))
              }
            />
            <TextField
              label="Краткое описание"
              disabled={!props.canManageBills}
              value={props.billForm.summary}
              onChange={(event) =>
                props.setBillForm((current) => ({
                  ...current,
                  summary: event.target.value,
                }))
              }
            />
            <TextField
              label="ID изменяемого закона"
              disabled={!props.canManageBills}
              value={props.billForm.lawId}
              onChange={(event) =>
                props.setBillForm((current) => ({
                  ...current,
                  lawId: event.target.value.replace(/[^\d]/g, ""),
                }))
              }
              helperText="Необязательно. Оставьте пустым для нового закона."
            />
            <TextField
              label="Текст законопроекта"
              multiline
              minRows={8}
              disabled={!props.canManageBills}
              value={props.billForm.proposedText}
              onChange={(event) =>
                props.setBillForm((current) => ({
                  ...current,
                  proposedText: event.target.value,
                }))
              }
            />
            <Button
              variant="contained"
              disabled={
                !props.canManageBills ||
                !props.billForm.title.trim() ||
                !props.billForm.proposedText.trim() ||
                props.submitting
              }
              onClick={props.onCreateBill}
            >
              Создать проект
            </Button>
          </Stack>
        </SectionCard>
        <SectionCard title="Законопроекты" subtitle="Карточки голосования и публикации.">
          <Stack spacing={1.25}>
            {props.bills.map((bill) => (
              <Accordion key={bill.id} disableGutters>
                <AccordionSummary expandIcon={<ExpandMoreRoundedIcon />}>
                  <Stack sx={{ width: "100%" }} spacing={0.4}>
                    <Stack
                      direction={{ xs: "column", sm: "row" }}
                      justifyContent="space-between"
                      spacing={1}
                    >
                      <Typography variant="subtitle1">{bill.title}</Typography>
                      <Chip
                        label={sentenceCase(bill.status)}
                        color={
                          bill.status === "open"
                            ? "secondary"
                            : bill.status === "enacted"
                              ? "success"
                              : "default"
                        }
                        size="small"
                      />
                    </Stack>
                    <Typography variant="body2" color="text.secondary">
                      {bill.proposer_name} · За {bill.yes_votes} / Против {bill.no_votes}
                    </Typography>
                  </Stack>
                </AccordionSummary>
                <AccordionDetails>
                  <Stack spacing={1.25}>
                    <Typography variant="body2" color="text.secondary">
                      {bill.summary || "Краткое описание не указано."}
                    </Typography>
                    <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>
                      {bill.proposed_text}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Создан {formatDateTime(bill.created_at)} · Кворум{" "}
                      {bill.quorum_reached ? "достигнут" : "не достигнут"} (
                      {bill.total_votes}/{bill.quorum_required})
                    </Typography>
                    <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
                      <Button
                        size="small"
                        variant="outlined"
                        disabled={props.submitting}
                        onClick={() => props.onVoteBill(bill.id, "yes")}
                      >
                        Голосовать за
                      </Button>
                      <Button
                        size="small"
                        variant="text"
                        disabled={props.submitting}
                        onClick={() => props.onVoteBill(bill.id, "no")}
                      >
                        Голосовать против
                      </Button>
                      <Button
                        size="small"
                        variant="contained"
                        disabled={props.submitting}
                        onClick={() => props.onPublishBill(bill.id)}
                      >
                        Опубликовать
                      </Button>
                    </Stack>
                  </Stack>
                </AccordionDetails>
              </Accordion>
            ))}
            {props.bills.length === 0 && (
              <EmptyState text="Законопроектов пока нет." />
            )}
          </Stack>
        </SectionCard>
      </ResponsiveGrid>
    </Stack>
  );
}
