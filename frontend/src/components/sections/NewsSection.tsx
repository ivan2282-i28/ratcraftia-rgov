import * as React from "react";
import {
  Button,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import type { NewsRead } from "../../types";
import { formatDateTime } from "../../lib/format";
import { EmptyState, HeroCard, ResponsiveGrid, SectionCard } from "../common";

type NewsForm = {
  title: string;
  body: string;
};

export function NewsSection(props: {
  news: NewsRead[];
  newsForm: NewsForm;
  setNewsForm: React.Dispatch<React.SetStateAction<NewsForm>>;
  canManageNews: boolean;
  submitting: boolean;
  onCreate: () => void;
  onDelete: (newsId: number) => void;
}) {
  return (
    <Stack spacing={2.5}>
      <HeroCard
        title="Новости"
        description="Официальные публикации портала и оперативное управление лентой для уполномоченных сотрудников."
        chips={[`${props.news.length} публикаций`]}
      />
      <ResponsiveGrid columns={{ xs: "1fr", xl: "400px minmax(0, 1fr)" }}>
        <SectionCard
          title="Новая публикация"
          subtitle="Создание и удаление доступны пользователям с правом `news.manage`."
        >
          <Stack spacing={1.25}>
            <TextField
              label="Заголовок"
              disabled={!props.canManageNews}
              value={props.newsForm.title}
              onChange={(event) =>
                props.setNewsForm((current) => ({
                  ...current,
                  title: event.target.value,
                }))
              }
            />
            <TextField
              label="Текст новости"
              multiline
              minRows={8}
              disabled={!props.canManageNews}
              value={props.newsForm.body}
              onChange={(event) =>
                props.setNewsForm((current) => ({
                  ...current,
                  body: event.target.value,
                }))
              }
            />
            <Button
              variant="contained"
              disabled={
                !props.canManageNews ||
                !props.newsForm.title.trim() ||
                !props.newsForm.body.trim() ||
                props.submitting
              }
              onClick={props.onCreate}
            >
              Опубликовать
            </Button>
          </Stack>
        </SectionCard>
        <SectionCard
          title="Лента новостей"
          subtitle="Публикации показываются в обратном хронологическом порядке."
        >
          <Stack spacing={1.25}>
            {props.news.map((item) => (
              <Paper key={item.id} variant="outlined" sx={{ p: 2, borderRadius: 4 }}>
                <Stack spacing={1}>
                  <Stack
                    direction={{ xs: "column", sm: "row" }}
                    justifyContent="space-between"
                    spacing={1}
                  >
                    <Stack spacing={0.4}>
                      <Typography variant="h6">{item.title}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {item.author_name} · {formatDateTime(item.created_at)}
                      </Typography>
                    </Stack>
                    {props.canManageNews && (
                      <Button
                        size="small"
                        color="error"
                        onClick={() => props.onDelete(item.id)}
                      >
                        Удалить
                      </Button>
                    )}
                  </Stack>
                  <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>
                    {item.body}
                  </Typography>
                </Stack>
              </Paper>
            ))}
            {props.news.length === 0 && <EmptyState text="Новостей пока нет." />}
          </Stack>
        </SectionCard>
      </ResponsiveGrid>
    </Stack>
  );
}
