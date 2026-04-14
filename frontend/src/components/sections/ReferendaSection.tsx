import * as React from "react";
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Button,
  Chip,
  MenuItem,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import ExpandMoreRoundedIcon from "@mui/icons-material/ExpandMoreRounded";
import type { ReferendumRead } from "../../types";
import { sentenceCase } from "../../lib/format";
import { EmptyState, HeroCard, ResponsiveGrid, SectionCard } from "../common";

type ReferendumForm = {
  title: string;
  description: string;
  proposedText: string;
  lawId: string;
  targetLevel: string;
  matterType: string;
  subjectIdentifier: string;
};

export function ReferendaSection(props: {
  referenda: ReferendumRead[];
  referendumForm: ReferendumForm;
  setReferendumForm: React.Dispatch<React.SetStateAction<ReferendumForm>>;
  canManageReferenda: boolean;
  submitting: boolean;
  matterTypeOptions: Array<{ value: string; label: string }>;
  targetLevelOptions: Array<{ value: string; label: string }>;
  onCreate: () => void;
  onSign: (referendumId: number) => void;
  onVote: (referendumId: number, vote: "yes" | "no") => void;
  onPublish: (referendumId: number) => void;
}) {
  return (
    <Stack spacing={2.5}>
      <HeroCard
        title="Референдумы"
        description="Инициативы, сбор подписей, голосование и публикация итогов."
        chips={[
          `${props.referenda.length} инициатив`,
          `${props.referenda.filter((item) => item.status === "open").length} открыто`,
        ]}
      />
      <ResponsiveGrid columns={{ xs: "1fr", xl: "420px minmax(0, 1fr)" }}>
        <SectionCard title="Новая инициатива" subtitle="Форма подсказывает тип вопроса и целевой уровень.">
          <Stack spacing={1.25}>
            <TextField
              label="Название"
              disabled={!props.canManageReferenda}
              value={props.referendumForm.title}
              onChange={(event) =>
                props.setReferendumForm((current) => ({
                  ...current,
                  title: event.target.value,
                }))
              }
            />
            <TextField
              label="Описание"
              disabled={!props.canManageReferenda}
              value={props.referendumForm.description}
              onChange={(event) =>
                props.setReferendumForm((current) => ({
                  ...current,
                  description: event.target.value,
                }))
              }
            />
            <TextField
              select
              label="Тип вопроса"
              disabled={!props.canManageReferenda}
              value={props.referendumForm.matterType}
              onChange={(event) =>
                props.setReferendumForm((current) => ({
                  ...current,
                  matterType: event.target.value,
                }))
              }
            >
              {props.matterTypeOptions.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              label="Целевой уровень"
              disabled={!props.canManageReferenda}
              value={props.referendumForm.targetLevel}
              onChange={(event) =>
                props.setReferendumForm((current) => ({
                  ...current,
                  targetLevel: event.target.value,
                }))
              }
            >
              {props.targetLevelOptions.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              label="ID закона"
              disabled={!props.canManageReferenda}
              value={props.referendumForm.lawId}
              onChange={(event) =>
                props.setReferendumForm((current) => ({
                  ...current,
                  lawId: event.target.value.replace(/[^\d]/g, ""),
                }))
              }
            />
            <TextField
              label="Должностное лицо, логин или УИН"
              disabled={!props.canManageReferenda}
              value={props.referendumForm.subjectIdentifier}
              onChange={(event) =>
                props.setReferendumForm((current) => ({
                  ...current,
                  subjectIdentifier: event.target.value,
                }))
              }
              helperText="Нужно только для отзывов депутата или должностного лица."
            />
            <TextField
              label="Текст инициативы"
              multiline
              minRows={8}
              disabled={!props.canManageReferenda}
              value={props.referendumForm.proposedText}
              onChange={(event) =>
                props.setReferendumForm((current) => ({
                  ...current,
                  proposedText: event.target.value,
                }))
              }
            />
            <Button
              variant="contained"
              disabled={
                !props.canManageReferenda ||
                !props.referendumForm.title.trim() ||
                !props.referendumForm.proposedText.trim() ||
                props.submitting
              }
              onClick={props.onCreate}
            >
              Запустить инициативу
            </Button>
          </Stack>
        </SectionCard>
        <SectionCard title="Список инициатив" subtitle="Подписывайте, голосуйте и публикуйте итоги.">
          <Stack spacing={1.25}>
            {props.referenda.map((referendum) => (
              <Accordion key={referendum.id} disableGutters>
                <AccordionSummary expandIcon={<ExpandMoreRoundedIcon />}>
                  <Stack sx={{ width: "100%" }} spacing={0.4}>
                    <Stack
                      direction={{ xs: "column", sm: "row" }}
                      justifyContent="space-between"
                      spacing={1}
                    >
                      <Typography variant="subtitle1">{referendum.title}</Typography>
                      <Chip
                        label={sentenceCase(referendum.status)}
                        size="small"
                        color={
                          referendum.status === "approved"
                            ? "success"
                            : referendum.status === "open"
                              ? "secondary"
                              : "default"
                        }
                      />
                    </Stack>
                    <Typography variant="body2" color="text.secondary">
                      {referendum.proposer_name} · Подписи {referendum.signature_count}/
                      {referendum.required_signatures}
                    </Typography>
                  </Stack>
                </AccordionSummary>
                <AccordionDetails>
                  <Stack spacing={1.25}>
                    <Typography variant="body2" color="text.secondary">
                      {referendum.description || "Описание не указано."}
                    </Typography>
                    <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>
                      {referendum.proposed_text}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      За {referendum.yes_votes} / Против {referendum.no_votes} · Кворум{" "}
                      {referendum.total_votes}/{referendum.required_quorum}
                    </Typography>
                    <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
                      <Button
                        size="small"
                        variant="outlined"
                        disabled={props.submitting}
                        onClick={() => props.onSign(referendum.id)}
                      >
                        Подписать
                      </Button>
                      <Button
                        size="small"
                        variant="contained"
                        disabled={props.submitting}
                        onClick={() => props.onVote(referendum.id, "yes")}
                      >
                        Голосовать за
                      </Button>
                      <Button
                        size="small"
                        variant="text"
                        disabled={props.submitting}
                        onClick={() => props.onVote(referendum.id, "no")}
                      >
                        Голосовать против
                      </Button>
                      <Button
                        size="small"
                        variant="contained"
                        disabled={props.submitting}
                        onClick={() => props.onPublish(referendum.id)}
                      >
                        Опубликовать итог
                      </Button>
                    </Stack>
                  </Stack>
                </AccordionDetails>
              </Accordion>
            ))}
            {props.referenda.length === 0 && (
              <EmptyState text="Референдумов пока нет." />
            )}
          </Stack>
        </SectionCard>
      </ResponsiveGrid>
    </Stack>
  );
}
