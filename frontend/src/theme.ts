import "@fontsource/roboto/400.css";
import "@fontsource/roboto/500.css";
import "@fontsource/roboto/700.css";
import { alpha, createTheme } from "@mui/material/styles";

export function createAppTheme(mode: "light" | "dark") {
  const light = mode === "light";
  const palette = {
    mode,
    primary: {
      main: light ? "#006a67" : "#4fdad3",
      dark: light ? "#004f4c" : "#1abeb7",
      light: light ? "#3f8f8b" : "#8ef2ec",
      contrastText: light ? "#ffffff" : "#00201e",
    },
    secondary: {
      main: light ? "#4b635f" : "#b2ccc7",
      dark: light ? "#334946" : "#96b1ac",
      light: light ? "#748a86" : "#d0ebe6",
      contrastText: light ? "#ffffff" : "#1d352f",
    },
    background: {
      default: light ? "#f4fbf8" : "#0f1514",
      paper: light ? "#fbfefd" : "#161d1c",
    },
    success: {
      main: light ? "#426834" : "#a7d395",
    },
    warning: {
      main: light ? "#7c5800" : "#f0c86d",
    },
    error: {
      main: light ? "#ba1a1a" : "#ffb4ab",
    },
    text: {
      primary: light ? "#161d1c" : "#dce5e2",
      secondary: light ? "#3f4947" : "#bec9c6",
    },
    divider: light ? "rgba(22, 29, 28, 0.12)" : "rgba(220, 229, 226, 0.12)",
  } as const;

  return createTheme({
    palette,
    shape: {
      borderRadius: 16,
    },
    typography: {
      fontFamily: '"Roboto", "Arial", sans-serif',
      h1: {
        fontWeight: 400,
        letterSpacing: "-0.015em",
      },
      h2: {
        fontWeight: 400,
        letterSpacing: "-0.01em",
      },
      h3: {
        fontWeight: 400,
      },
      h4: {
        fontWeight: 500,
      },
      h5: {
        fontWeight: 500,
      },
      h6: {
        fontWeight: 500,
      },
      button: {
        textTransform: "none",
        fontWeight: 500,
        letterSpacing: "0.01em",
      },
    },
    components: {
      MuiCssBaseline: {
        styleOverrides: {
          body: {
            backgroundColor: palette.background.default,
            color: palette.text.primary,
          },
        },
      },
      MuiAppBar: {
        styleOverrides: {
          root: {
            backgroundImage: "none",
            backgroundColor: alpha(palette.background.paper, 0.92),
            borderBottom: `1px solid ${palette.divider}`,
            color: palette.text.primary,
            boxShadow: "none",
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: 28,
            backgroundColor: alpha(palette.background.paper, 0.98),
            border: `1px solid ${palette.divider}`,
            boxShadow: light
              ? "0 1px 2px rgba(22, 29, 28, 0.08), 0 8px 24px rgba(22, 29, 28, 0.06)"
              : "0 1px 2px rgba(0, 0, 0, 0.28), 0 8px 24px rgba(0, 0, 0, 0.18)",
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          rounded: {
            borderRadius: 24,
          },
          root: {
            backgroundImage: "none",
            backgroundColor: palette.background.paper,
          },
        },
      },
      MuiDrawer: {
        styleOverrides: {
          paper: {
            borderRight: `1px solid ${palette.divider}`,
            backgroundColor: alpha(palette.background.paper, 0.98),
          },
        },
      },
      MuiButton: {
        defaultProps: {
          disableElevation: true,
        },
        styleOverrides: {
          root: {
            borderRadius: 999,
            minHeight: 40,
            paddingInline: 24,
            paddingBlock: 10,
          },
          contained: {
            boxShadow: "none",
          },
          outlined: {
            borderWidth: 1,
          },
        },
      },
      MuiIconButton: {
        styleOverrides: {
          root: {
            borderRadius: 16,
          },
        },
      },
      MuiChip: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            fontWeight: 500,
          },
        },
      },
      MuiTextField: {
        defaultProps: {
          fullWidth: true,
          variant: "outlined",
        },
      },
      MuiOutlinedInput: {
        styleOverrides: {
          root: {
            borderRadius: 16,
            backgroundColor: alpha(palette.primary.main, light ? 0.03 : 0.08),
          },
        },
      },
      MuiCardHeader: {
        styleOverrides: {
          root: {
            padding: "20px 24px 12px",
          },
          action: {
            marginTop: 0,
            marginRight: 0,
          },
        },
      },
      MuiTabs: {
        styleOverrides: {
          indicator: {
            height: 3,
            borderRadius: 3,
          },
        },
      },
      MuiAccordion: {
        styleOverrides: {
          root: {
            borderRadius: 24,
            border: `1px solid ${palette.divider}`,
            overflow: "hidden",
            "&:before": {
              display: "none",
            },
          },
        },
      },
      MuiListItemButton: {
        styleOverrides: {
          root: {
            borderRadius: 999,
            minHeight: 52,
          },
        },
      },
    },
  });
}
