import * as React from "react";
import {
  Button,
  Chip,
  InputAdornment,
  MenuItem,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import ApartmentRoundedIcon from "@mui/icons-material/ApartmentRounded";
import SavingsRoundedIcon from "@mui/icons-material/SavingsRounded";
import VerifiedRoundedIcon from "@mui/icons-material/VerifiedRounded";
import type {
  RatublesDirectoryEntryRead,
  RatublesTransactionRead,
  UserRead,
} from "../../types";
import { formatDateTime, formatNumber, sentenceCase } from "../../lib/format";
import { EmptyState, HeroCard, MetricCard, ResponsiveGrid, SectionCard } from "../common";

type MoneyForm = {
  recipient: string;
  amount: string;
  reason: string;
};

export function RatublesSection(props: {
  profile: UserRead;
  directory: RatublesDirectoryEntryRead[];
  transactions: RatublesTransactionRead[];
  ledger: RatublesTransactionRead[];
  transferForm: MoneyForm;
  setTransferForm: React.Dispatch<React.SetStateAction<MoneyForm>>;
  mintForm: MoneyForm;
  setMintForm: React.Dispatch<React.SetStateAction<MoneyForm>>;
  canMintRatubles: boolean;
  submitting: boolean;
  onTransfer: () => void;
  onMint: () => void;
}) {
  return (
    <Stack spacing={2.5}>
      <HeroCard
        title="Ratubles"
        description="Личные переводы, эмиссия для администраторов и прозрачный журнал транзакций."
        chips={[
          `${formatNumber(props.profile.ratubles)} на балансе`,
          `${props.transactions.length} операций`,
        ]}
      />
      <ResponsiveGrid>
        <MetricCard
          title="Мой баланс"
          value={formatNumber(props.profile.ratubles)}
          description="Доступно для переводов"
          icon={<SavingsRoundedIcon />}
          accent="primary"
        />
        <MetricCard
          title="Контрагенты"
          value={String(props.directory.length)}
          description="Пользователи и организации"
          icon={<ApartmentRoundedIcon />}
          accent="neutral"
        />
        <MetricCard
          title="Запись в журнале"
          value={String(props.ledger.length)}
          description="Доступно администраторам"
          icon={<VerifiedRoundedIcon />}
          accent="secondary"
        />
      </ResponsiveGrid>
      <ResponsiveGrid columns={{ xs: "1fr", xl: "repeat(3, minmax(0, 1fr))" }}>
        <SectionCard
          title="Перевод"
          subtitle="Выберите получателя и причину списания."
        >
          <Stack spacing={1.25}>
            <TextField
              select
              label="Получатель"
              value={props.transferForm.recipient}
              onChange={(event) =>
                props.setTransferForm((current) => ({
                  ...current,
                  recipient: event.target.value,
                }))
              }
            >
              {props.directory
                .filter((entry) => entry.kind !== "user" || entry.id !== props.profile.id)
                .map((entry) => (
                  <MenuItem key={`${entry.kind}:${entry.id}`} value={`${entry.kind}:${entry.id}`}>
                    {entry.full_name} · {entry.code}
                  </MenuItem>
                ))}
            </TextField>
            <TextField
              label="Сумма"
              value={props.transferForm.amount}
              onChange={(event) =>
                props.setTransferForm((current) => ({
                  ...current,
                  amount: event.target.value.replace(/[^\d]/g, ""),
                }))
              }
              InputProps={{
                endAdornment: <InputAdornment position="end">RAT</InputAdornment>,
              }}
            />
            <TextField
              label="Причина"
              value={props.transferForm.reason}
              onChange={(event) =>
                props.setTransferForm((current) => ({
                  ...current,
                  reason: event.target.value,
                }))
              }
            />
            <Button
              variant="contained"
              disabled={
                !props.transferForm.recipient ||
                !props.transferForm.amount ||
                !props.transferForm.reason.trim() ||
                props.submitting
              }
              onClick={props.onTransfer}
            >
              Отправить Ratubles
            </Button>
          </Stack>
        </SectionCard>
        <SectionCard
          title="Эмиссия"
          subtitle="Раздел доступен только при наличии права `ratubles.mint`."
        >
          <Stack spacing={1.25}>
            <TextField
              select
              label="Получатель"
              disabled={!props.canMintRatubles}
              value={props.mintForm.recipient}
              onChange={(event) =>
                props.setMintForm((current) => ({
                  ...current,
                  recipient: event.target.value,
                }))
              }
            >
              {props.directory.map((entry) => (
                <MenuItem key={`${entry.kind}:${entry.id}`} value={`${entry.kind}:${entry.id}`}>
                  {entry.full_name} · {entry.code}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              label="Сумма"
              disabled={!props.canMintRatubles}
              value={props.mintForm.amount}
              onChange={(event) =>
                props.setMintForm((current) => ({
                  ...current,
                  amount: event.target.value.replace(/[^\d]/g, ""),
                }))
              }
            />
            <TextField
              label="Основание"
              disabled={!props.canMintRatubles}
              value={props.mintForm.reason}
              onChange={(event) =>
                props.setMintForm((current) => ({
                  ...current,
                  reason: event.target.value,
                }))
              }
            />
            <Button
              variant="outlined"
              disabled={
                !props.canMintRatubles ||
                !props.mintForm.recipient ||
                !props.mintForm.amount ||
                !props.mintForm.reason.trim() ||
                props.submitting
              }
              onClick={props.onMint}
            >
              Выпустить Ratubles
            </Button>
          </Stack>
        </SectionCard>
        <SectionCard
          title="Журнал транзакций"
          subtitle="Личная лента операций и общий ledger для администраторов."
        >
          <Stack spacing={1.25}>
            {props.transactions.slice(0, 5).map((transaction) => (
              <Paper key={transaction.id} variant="outlined" sx={{ p: 1.5, borderRadius: 4 }}>
                <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={1}>
                  <Stack spacing={0.4}>
                    <Typography variant="subtitle2">
                      {transaction.direction === "outgoing"
                        ? "Исходящий перевод"
                        : transaction.direction === "incoming"
                          ? "Входящий перевод"
                          : sentenceCase(transaction.kind)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {transaction.recipient_name ?? transaction.sender_name ?? "Операция"}
                    </Typography>
                  </Stack>
                  <Chip
                    label={`${transaction.amount} RAT`}
                    color={
                      transaction.direction === "incoming"
                        ? "success"
                        : transaction.direction === "outgoing"
                          ? "warning"
                          : "default"
                    }
                  />
                </Stack>
                <Typography variant="body2" sx={{ mt: 1 }}>
                  {transaction.reason}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {formatDateTime(transaction.created_at)}
                </Typography>
              </Paper>
            ))}
            {props.transactions.length === 0 && (
              <EmptyState text="История операций пока пуста." />
            )}
          </Stack>
        </SectionCard>
      </ResponsiveGrid>
      {props.ledger.length > 0 && (
        <SectionCard title="Общий ledger" subtitle="Системный журнал операций RGOV.">
          <Stack spacing={1}>
            {props.ledger.map((transaction) => (
              <Paper key={transaction.id} variant="outlined" sx={{ p: 1.75, borderRadius: 4 }}>
                <Typography variant="subtitle2">
                  {transaction.sender_name ?? "Система"} →{" "}
                  {transaction.recipient_name ?? "Получатель"}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {transaction.amount} RAT · {transaction.reason}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {formatDateTime(transaction.created_at)}
                </Typography>
              </Paper>
            ))}
          </Stack>
        </SectionCard>
      )}
    </Stack>
  );
}
