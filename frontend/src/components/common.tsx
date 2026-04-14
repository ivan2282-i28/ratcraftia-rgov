import * as React from "react";
import {
  Avatar,
  Box,
  Card,
  CardContent,
  CardHeader,
  Divider,
  Paper,
  Stack,
  Typography,
  Chip,
} from "@mui/material";
import { alpha, useTheme } from "@mui/material/styles";

export function HeroCard(props: {
  title: string;
  description: string;
  chips?: string[];
}) {
  const theme = useTheme();

  return (
    <Card
      sx={{
        bgcolor: alpha(theme.palette.primary.main, theme.palette.mode === "light" ? 0.08 : 0.14),
        borderColor: alpha(theme.palette.primary.main, 0.18),
      }}
    >
      <CardContent sx={{ p: { xs: 3, md: 4 } }}>
        <Typography variant="h3">{props.title}</Typography>
        <Typography variant="h6" color="text.secondary" sx={{ mt: 1.5, maxWidth: 760 }}>
          {props.description}
        </Typography>
        {props.chips && props.chips.length > 0 && (
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ mt: 2.5 }}>
            {props.chips.map((chip) => (
              <Chip key={chip} label={chip} variant="outlined" />
            ))}
          </Stack>
        )}
      </CardContent>
    </Card>
  );
}

export function ResponsiveGrid(props: {
  children: React.ReactNode;
  columns?: Record<string, string>;
  sx?: object;
}) {
  return (
    <Box
      sx={{
        display: "grid",
        gap: 2.5,
        gridTemplateColumns: {
          xs: props.columns?.xs ?? "1fr",
          sm: props.columns?.sm ?? "repeat(2, minmax(0, 1fr))",
          lg: props.columns?.lg ?? "repeat(2, minmax(0, 1fr))",
          xl: props.columns?.xl ?? "repeat(3, minmax(0, 1fr))",
        },
        ...props.sx,
      }}
    >
      {props.children}
    </Box>
  );
}

export function SectionCard(props: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  action?: React.ReactNode;
}) {
  return (
    <Card>
      <CardHeader
        title={props.title}
        subheader={props.subtitle}
        action={props.action}
        slotProps={{
          title: { variant: "h5" },
          subheader: { variant: "body2" },
        }}
      />
      <Divider />
      <CardContent>{props.children}</CardContent>
    </Card>
  );
}

export function MetricCard(props: {
  title: string;
  value: string;
  description: string;
  icon: React.ReactNode;
  accent: "primary" | "secondary" | "neutral";
}) {
  const theme = useTheme();
  const accentColor =
    props.accent === "primary"
      ? theme.palette.primary.main
      : props.accent === "secondary"
        ? theme.palette.secondary.main
        : theme.palette.text.primary;

  return (
    <Card>
      <CardContent>
        <Stack direction="row" justifyContent="space-between" spacing={2}>
          <Box>
            <Typography variant="body2" color="text.secondary">
              {props.title}
            </Typography>
            <Typography variant="h4" sx={{ mt: 0.5 }}>
              {props.value}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.75 }}>
              {props.description}
            </Typography>
          </Box>
          <Avatar
            sx={{
              width: 52,
              height: 52,
              borderRadius: 4,
              bgcolor: alpha(accentColor, 0.12),
              color: accentColor,
            }}
          >
            {props.icon}
          </Avatar>
        </Stack>
      </CardContent>
    </Card>
  );
}

export function FeatureCard(props: {
  icon: React.ReactNode;
  title: string;
  text: string;
}) {
  return (
    <Paper
      variant="outlined"
      sx={{
        p: 2,
        borderRadius: 5,
        bgcolor: "background.paper",
      }}
    >
      <Stack spacing={1}>
        <Avatar sx={{ bgcolor: "transparent", color: "primary.main" }}>
          {props.icon}
        </Avatar>
        <Typography variant="subtitle1">{props.title}</Typography>
        <Typography variant="body2" color="text.secondary">
          {props.text}
        </Typography>
      </Stack>
    </Paper>
  );
}

export function HintRow(props: { text: string; icon: React.ReactNode }) {
  return (
    <Stack direction="row" spacing={1.25} alignItems="flex-start">
      {props.icon}
      <Typography variant="body2" color="text.secondary">
        {props.text}
      </Typography>
    </Stack>
  );
}

export function InfoRow(props: { label: string; value: string }) {
  return (
    <Stack
      direction={{ xs: "column", sm: "row" }}
      justifyContent="space-between"
      spacing={1}
      sx={{ py: 0.4 }}
    >
      <Typography variant="body2" color="text.secondary">
        {props.label}
      </Typography>
      <Typography variant="body2" sx={{ fontWeight: 700 }}>
        {props.value}
      </Typography>
    </Stack>
  );
}

export function EmptyState(props: { text: string }) {
  return (
    <Paper
      variant="outlined"
      sx={{
        p: 3,
        borderRadius: 5,
        textAlign: "center",
      }}
    >
      <Typography variant="body2" color="text.secondary">
        {props.text}
      </Typography>
    </Paper>
  );
}
