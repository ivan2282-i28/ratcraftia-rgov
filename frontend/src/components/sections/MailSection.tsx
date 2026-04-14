import * as React from "react";
import {
  Button,
  Paper,
  Stack,
  Tab,
  Tabs,
  TextField,
  Typography,
} from "@mui/material";
import SendRoundedIcon from "@mui/icons-material/SendRounded";
import type { MailRead } from "../../types";
import { formatDateTime } from "../../lib/format";
import { EmptyState, HeroCard, ResponsiveGrid, SectionCard } from "../common";

type MailForm = {
  to: string;
  subject: string;
  text: string;
};

export function MailSection(props: {
  inbox: MailRead[];
  sent: MailRead[];
  mailboxTab: "inbox" | "sent";
  setMailboxTab: React.Dispatch<React.SetStateAction<"inbox" | "sent">>;
  mailForm: MailForm;
  setMailForm: React.Dispatch<React.SetStateAction<MailForm>>;
  submitting: boolean;
  onSend: () => void;
}) {
  const messages = props.mailboxTab === "inbox" ? props.inbox : props.sent;

  return (
    <Stack spacing={2.5}>
      <HeroCard
        title="GovMail"
        description="Рабочая переписка и обращения граждан с быстрым переключением между входящими и отправленными."
        chips={[
          `${props.inbox.filter((item) => !item.read_at).length} непрочитанных`,
          `${props.sent.length} отправлено`,
        ]}
      />
      <ResponsiveGrid columns={{ xs: "1fr", xl: "380px minmax(0, 1fr)" }}>
        <SectionCard
          title="Новое письмо"
          subtitle="Адрес можно указать в формате citizen, gov или fn."
          action={<SendRoundedIcon color="primary" />}
        >
          <Stack spacing={1.25}>
            <TextField
              label="Кому"
              value={props.mailForm.to}
              onChange={(event) =>
                props.setMailForm((current) => ({
                  ...current,
                  to: event.target.value,
                }))
              }
              placeholder="Например: 1.26.563372@citizen"
            />
            <TextField
              label="Тема"
              value={props.mailForm.subject}
              onChange={(event) =>
                props.setMailForm((current) => ({
                  ...current,
                  subject: event.target.value,
                }))
              }
            />
            <TextField
              label="Текст письма"
              multiline
              minRows={6}
              value={props.mailForm.text}
              onChange={(event) =>
                props.setMailForm((current) => ({
                  ...current,
                  text: event.target.value,
                }))
              }
            />
            <Button
              variant="contained"
              disabled={
                !props.mailForm.to.trim() ||
                !props.mailForm.subject.trim() ||
                !props.mailForm.text.trim() ||
                props.submitting
              }
              onClick={props.onSend}
            >
              Отправить письмо
            </Button>
          </Stack>
        </SectionCard>
        <SectionCard
          title="Почтовые ящики"
          subtitle="Сначала показываются более свежие сообщения."
        >
          <Tabs
            value={props.mailboxTab}
            onChange={(_, value) => props.setMailboxTab(value)}
            sx={{ mb: 2 }}
          >
            <Tab value="inbox" label={`Входящие (${props.inbox.length})`} />
            <Tab value="sent" label={`Отправленные (${props.sent.length})`} />
          </Tabs>
          <Stack spacing={1.25}>
            {messages.map((message) => (
              <Paper key={message.id} variant="outlined" sx={{ p: 2, borderRadius: 4 }}>
                <Stack
                  direction={{ xs: "column", sm: "row" }}
                  justifyContent="space-between"
                  spacing={1}
                >
                  <Stack spacing={0.4}>
                    <Typography variant="h6">{message.subject}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {props.mailboxTab === "inbox"
                        ? `От ${message.sender_name} · ${message.from_address}`
                        : `Кому ${message.recipient_name} · ${message.to_address}`}
                    </Typography>
                  </Stack>
                  <Typography variant="body2" color="text.secondary">
                    {formatDateTime(message.created_at)}
                  </Typography>
                </Stack>
                <Typography variant="body2" sx={{ mt: 1.5, whiteSpace: "pre-wrap" }}>
                  {message.text}
                </Typography>
              </Paper>
            ))}
            {messages.length === 0 && (
              <EmptyState
                text={
                  props.mailboxTab === "inbox"
                    ? "Входящих писем пока нет."
                    : "Вы ещё ничего не отправляли."
                }
              />
            )}
          </Stack>
        </SectionCard>
      </ResponsiveGrid>
    </Stack>
  );
}
