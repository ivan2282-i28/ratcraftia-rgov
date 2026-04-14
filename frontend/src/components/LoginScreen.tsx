import * as React from "react";
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  IconButton,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { alpha, useTheme } from "@mui/material/styles";
import DarkModeRoundedIcon from "@mui/icons-material/DarkModeRounded";
import LightModeRoundedIcon from "@mui/icons-material/LightModeRounded";

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
        placeItems: "center",
        backgroundImage: `linear-gradient(180deg, ${theme.palette.background.default}, ${alpha(
          theme.palette.primary.main,
          theme.palette.mode === "light" ? 0.05 : 0.12,
        )})`,
        px: 2,
        py: 3,
      }}
    >
      <IconButton
        onClick={props.onToggleColorMode}
        sx={{
          position: "fixed",
          top: 24,
          right: 24,
          bgcolor: alpha(theme.palette.background.paper, 0.88),
        }}
      >
        {props.colorMode === "light" ? <DarkModeRoundedIcon /> : <LightModeRoundedIcon />}
      </IconButton>

      <Card
        sx={{
          width: "100%",
          maxWidth: 420,
          bgcolor: alpha(theme.palette.background.paper, 0.98),
        }}
      >
        <CardContent sx={{ p: { xs: 3, md: 4 } }}>
          <Stack spacing={3}>
            <Stack spacing={1.5} alignItems="center" textAlign="center">
              <Box
                component="img"
                src="/ratcraftia-mark.svg"
                alt="RGOV"
                sx={{ width: 132, maxWidth: "100%" }}
              />
              <Typography variant="h4">Вход в RGOV</Typography>
            </Stack>

            <Stack spacing={1.5}>
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
                fullWidth
                disabled={
                  !props.form.identifier.trim() ||
                  !props.form.secret.trim() ||
                  props.loading
                }
                onClick={props.onSubmit}
              >
                {props.loading ? (
                  <Stack direction="row" spacing={1} alignItems="center">
                    <CircularProgress size={18} color="inherit" />
                    <span>Выполняется вход</span>
                  </Stack>
                ) : (
                  "Войти"
                )}
              </Button>
            </Stack>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
}
