import * as React from "react";
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Stack,
  TextField,
  Typography,
  Chip,
} from "@mui/material";
import ExpandMoreRoundedIcon from "@mui/icons-material/ExpandMoreRounded";
import type { LawRead } from "../../types";
import { formatDate, sentenceCase } from "../../lib/format";
import { EmptyState, HeroCard, SectionCard } from "../common";

export function LawsSection(props: {
  laws: LawRead[];
  search: string;
  setSearch: React.Dispatch<React.SetStateAction<string>>;
}) {
  return (
    <Stack spacing={2.5}>
      <HeroCard
        title="Законы Ratcraftia"
        description="Поиск по заголовкам, уровням и действующим редакциям без перегруженной навигации."
        chips={[`${props.laws.length} документов`]}
      />
      <SectionCard title="Реестр законов" subtitle="Поиск обновляется по мере ввода.">
        <TextField
          label="Найти закон или статью"
          value={props.search}
          onChange={(event) => props.setSearch(event.target.value)}
          sx={{ mb: 2 }}
        />
        <Stack spacing={1.25}>
          {props.laws.map((law) => (
            <Accordion key={law.id} disableGutters>
              <AccordionSummary expandIcon={<ExpandMoreRoundedIcon />}>
                <Stack sx={{ width: "100%" }} spacing={0.4}>
                  <Stack
                    direction={{ xs: "column", sm: "row" }}
                    justifyContent="space-between"
                    spacing={1}
                  >
                    <Typography variant="subtitle1">{law.title}</Typography>
                    <Stack direction="row" spacing={1}>
                      <Chip label={sentenceCase(law.level)} size="small" />
                      <Chip label={`v${law.version}`} variant="outlined" size="small" />
                    </Stack>
                  </Stack>
                  <Typography variant="body2" color="text.secondary">
                    {law.slug} · {sentenceCase(law.status)} · {formatDate(law.updated_at)}
                  </Typography>
                </Stack>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>
                  {law.current_text}
                </Typography>
              </AccordionDetails>
            </Accordion>
          ))}
          {props.laws.length === 0 && (
            <EmptyState text="По вашему запросу ничего не найдено." />
          )}
        </Stack>
      </SectionCard>
    </Stack>
  );
}
