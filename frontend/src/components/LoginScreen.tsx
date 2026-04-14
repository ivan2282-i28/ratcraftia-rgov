import * as React from "react";
import {
  Box,
  Button,
  Card,
  CardContent,
  Container,
  IconButton,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { alpha, useTheme } from "@mui/material/styles";
import AccountBalanceRoundedIcon from "@mui/icons-material/AccountBalanceRounded";
import DarkModeRoundedIcon from "@mui/icons-material/DarkModeRounded";
import LightModeRoundedIcon from "@mui/icons-material/LightModeRounded";
import NotificationsRoundedIcon from "@mui/icons-material/NotificationsRounded";
import VerifiedRoundedIcon from "@mui/icons-material/VerifiedRounded";
import { FeatureCard, HintRow, ResponsiveGrid } from "./common";

export function LoginScreen(props: {
  colorMode: "light" | "dark";
  loading: boolean;
  form: { identifier: string; secret: string };
  onChange: React.Dispatch<
    React.SetStateAction<{ identifier: string; secret: string }>
  >;
  onSubmit: () => void;
  onToggleColorMode: () => void;
}) {
  const theme = useTheme();

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "grid",
        alignItems: "center",
        backgroundImage: `radial-gradient(circle at top left, ${alpha(
          theme.palette.primary.main,
          0.28,
        )}, transparent 32%), radial-gradient(circle at bottom right, ${alpha(
          theme.palette.secondary.main,
          0.24,
        )}, transparent 28%), linear-gradient(180deg, ${theme.palette.background.default}, ${alpha(
          theme.palette.background.paper,
          0.96,
        )})`,
        px: 2,
        py: 3,
      }}
    >
      <Container maxWidth="lg">
        <Stack
          direction={{ xs: "column", lg: "row" }}
          spacing={3}
          alignItems="stretch"
        >
          <Card
            sx={{
              flex: 1.1,
              minHeight: 560,
              backgroundImage: `linear-gradient(140deg, ${alpha(
                theme.palette.primary.main,
                0.15,
              )}, ${alpha(theme.palette.secondary.main, 0.16)})`,
            }}
          >
            <CardContent
              sx={{
                height: "100%",
                display: "flex",
                flexDirection: "column",
                gap: 2,
                p: { xs: 3, md: 4 },
              }}
            >
              <Stack direction="row" justifyContent="space-between" spacing={2}>
                <Box
                  component="img"
                  src="/ratcraftia-mark.svg"
                  alt="RGOV"
                  sx={{ width: 220, maxWidth: "100%" }}
                />
                <IconButton onClick={props.onToggleColorMode}>
                  {props.colorMode === "light" ? (
                    <DarkModeRoundedIcon />
                  ) : (
                    <LightModeRoundedIcon />
                  )}
                </IconButton>
              </Stack>
              <Typography variant="h2" sx={{ mt: 2, maxWidth: 560 }}>
                Портал, который объясняет себя сам.
              </Typography>
              <Typography variant="h6" color="text.secondary" sx={{ maxWidth: 640 }}>
                React-интерфейс построен вокруг реальных задач: быстро войти,
                увидеть статус учётной записи, перейти к письмам, голосованию,
                законам и операциям Ratubles без лишних экранов.
              </Typography>
              <ResponsiveGrid
                columns={{ xs: "1fr", sm: "repeat(3, minmax(0, 1fr))" }}
                sx={{ mt: "auto" }}
              >
                <FeatureCard
                  icon={<VerifiedRoundedIcon color="primary" />}
                  title="Один вход"
                  text="Логин или УИН вместе с паролем или УАН."
                />
                <FeatureCard
                  icon={<AccountBalanceRoundedIcon color="primary" />}
                  title="Ясная структура"
                  text="Разделы сгруппированы по реальным государственным потокам."
                />
                <FeatureCard
                  icon={<NotificationsRoundedIcon color="primary" />}
                  title="Push-канал"
                  text="Уведомления подключаются прямо из профиля."
                />
              </ResponsiveGrid>
            </CardContent>
          </Card>

          <Card sx={{ flex: 0.9 }}>
            <CardContent sx={{ p: { xs: 3, md: 4 } }}>
              <Typography variant="h4">Вход в RGOV</Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
                Внешняя авторизация для сторонних сервисов удалена. Вход выполняется
                только через собственные учётные данные Ratcraftia.
              </Typography>
              <Stack spacing={1.5} sx={{ mt: 3 }}>
                <TextField
                  label="Логин или УИН"
                  value={props.form.identifier}
                  onChange={(event) =>
                    props.onChange((current) => ({
                      ...current,
                      identifier: event.target.value,
                    }))
                  }
                  placeholder="Например: root или 1.26.563372"
                />
                <TextField
                  label="Пароль или УАН"
                  type="password"
                  value={props.form.secret}
                  onChange={(event) =>
                    props.onChange((current) => ({
                      ...current,
                      secret: event.target.value,
                    }))
                  }
                  onKeyDown={(event) => {
                    if (event.key === "Enter") {
                      props.onSubmit();
                    }
                  }}
                />
                <Button
                  size="large"
                  variant="contained"
                  disabled={
                    !props.form.identifier.trim() ||
                    !props.form.secret.trim() ||
                    props.loading
                  }
                  onClick={props.onSubmit}
                >
                  {props.loading ? "Выполняется вход..." : "Войти в портал"}
                </Button>
              </Stack>
              <Stack spacing={1} sx={{ mt: 3 }}>
                <HintRow
                  icon={<VerifiedRoundedIcon color="primary" sx={{ mt: 0.2, fontSize: 18 }} />}
                  text="Единая форма поддерживает обычный вход и вход по УИН/УАН."
                />
                <HintRow
                  icon={<VerifiedRoundedIcon color="primary" sx={{ mt: 0.2, fontSize: 18 }} />}
                  text="После авторизации портал загружает профиль, почту, законы и рабочие разделы автоматически."
                />
                <HintRow
                  icon={<VerifiedRoundedIcon color="primary" sx={{ mt: 0.2, fontSize: 18 }} />}
                  text="Material UI оболочка адаптирована для десктопа и мобильных экранов."
                />
              </Stack>
            </CardContent>
          </Card>
        </Stack>
      </Container>
    </Box>
  );
}
