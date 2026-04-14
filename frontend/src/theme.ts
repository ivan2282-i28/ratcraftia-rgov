import "@fontsource/manrope/400.css";
import "@fontsource/manrope/500.css";
import "@fontsource/manrope/700.css";
import "@fontsource/source-serif-4/600.css";
import { alpha, createTheme } from "@mui/material/styles";

export function createAppTheme(mode: "light" | "dark") {
  const light = mode === "light";
  const palette = {
    mode,
    primary: {
      main: light ? "#0f766e" : "#6ee7d8",
      dark: light ? "#0b5a54" : "#45c9ba",
      light: light ? "#4cc0b4" : "#9ff4e9",
      contrastText: light ? "#f5fbfa" : "#052826",
    },
    secondary: {
      main: light ? "#c2410c" : "#ffb089",
      dark: light ? "#9b2f07" : "#ff9966",
      light: light ? "#ef7f52" : "#ffd0b7",
      contrastText: light ? "#fff7f2" : "#3f1803",
    },
    background: {
      default: light ? "#f6f3eb" : "#11161b",
      paper: light ? "#fffdf8" : "#182029",
    },
    success: {
      main: light ? "#2f855a" : "#80e4a6",
    },
    warning: {
      main: light ? "#b7791f" : "#f8c96b",
    },
    error: {
      main: light ? "#c53030" : "#ff9b9b",
    },
    text: {
      primary: light ? "#1c2526" : "#f5f7fb",
      secondary: light ? "#5c6a6b" : "#b8c3d1",
    },
    divider: light ? "rgba(17, 24, 39, 0.08)" : "rgba(235, 241, 255, 0.1)",
  } as const;

  return createTheme({
    palette,
    shape: {
      borderRadius: 20,
    },
    typography: {
      fontFamily: '"Manrope", "Segoe UI", sans-serif',
      h1: {
        fontFamily: '"Source Serif 4", Georgia, serif',
        fontWeight: 600,
      },
      h2: {
        fontFamily: '"Source Serif 4", Georgia, serif',
        fontWeight: 600,
      },
      h3: {
        fontFamily: '"Source Serif 4", Georgia, serif',
        fontWeight: 600,
      },
      h4: {
        fontFamily: '"Source Serif 4", Georgia, serif',
        fontWeight: 600,
      },
      h5: {
        fontFamily: '"Source Serif 4", Georgia, serif',
        fontWeight: 600,
      },
      h6: {
        fontFamily: '"Source Serif 4", Georgia, serif',
        fontWeight: 600,
      },
      button: {
        textTransform: "none",
        fontWeight: 700,
      },
    },
    components: {
      MuiAppBar: {
        styleOverrides: {
          root: {
            backgroundImage: "none",
            borderBottom: `1px solid ${palette.divider}`,
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            border: `1px solid ${palette.divider}`,
            boxShadow: light
              ? "0 20px 50px rgba(15, 23, 42, 0.08)"
              : "0 18px 40px rgba(4, 10, 17, 0.35)",
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          rounded: {
            borderRadius: 20,
          },
          root: {
            backgroundImage: "none",
          },
        },
      },
      MuiDrawer: {
        styleOverrides: {
          paper: {
            borderRight: `1px solid ${palette.divider}`,
            backgroundImage: light
              ? "linear-gradient(180deg, rgba(15,118,110,0.08), rgba(255,253,248,0.9))"
              : "linear-gradient(180deg, rgba(110,231,216,0.12), rgba(24,32,41,0.96))",
          },
        },
      },
      MuiButton: {
        defaultProps: {
          disableElevation: true,
        },
        styleOverrides: {
          root: {
            borderRadius: 14,
            paddingInline: 18,
          },
        },
      },
      MuiChip: {
        styleOverrides: {
          root: {
            borderRadius: 999,
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
            backgroundColor: light
              ? alpha("#ffffff", 0.82)
              : alpha("#0f172a", 0.55),
          },
        },
      },
      MuiListItemButton: {
        styleOverrides: {
          root: {
            borderRadius: 16,
          },
        },
      },
    },
  });
}
