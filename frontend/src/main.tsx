import React from "react";
import ReactDOM from "react-dom/client";
import { CssBaseline, ThemeProvider } from "@mui/material";
import { App } from "./App";
import { createAppTheme } from "./theme";

const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("Root element not found.");
}

const root = ReactDOM.createRoot(rootElement);

function Root() {
  const [mode, setMode] = React.useState<"light" | "dark">(() => {
    const saved = window.localStorage.getItem("rgov-theme");
    return saved === "dark" ? "dark" : "light";
  });

  React.useEffect(() => {
    window.localStorage.setItem("rgov-theme", mode);
  }, [mode]);

  return (
    <ThemeProvider theme={createAppTheme(mode)}>
      <CssBaseline />
      <App
        colorMode={mode}
        onToggleColorMode={() =>
          setMode((current) => (current === "light" ? "dark" : "light"))
        }
      />
    </ThemeProvider>
  );
}

root.render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>,
);
