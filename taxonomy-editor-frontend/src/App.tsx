import { useState, useCallback } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { createTheme, CssBaseline, ThemeProvider } from "@mui/material";

import ResponsiveAppBar from "./components/ResponsiveAppBar";
import RootNodes from "./pages/root-nodes";
import EditEntry from "./pages/editentry";
import ExportTaxonomy from "./pages/export";
import GoToProject from "./pages/go-to-project";
import Home from "./pages/home";
import SearchNode from "./pages/search";
import StartProject from "./pages/startproject";
import Errors from "./pages/errors";

const theme = createTheme({
  typography: {
    fontFamily: "Plus Jakarta Sans",
    button: {
      fontFamily: "Roboto, Helvetica, Arial, sans-serif",
      color: "#808080",
    },
  },
});

function App() {
  const [navLinks, setNavLinks] = useState<
    Array<{ translationKey: string; url: string }>
  >([]);

  const resetNavLinks = useCallback(() => setNavLinks([]), []);

  const addTaxonomyBranchNavLinks = useCallback(
    ({
      taxonomyName,
      branchName,
    }: {
      taxonomyName: string;
      branchName: string;
    }) => {
      const urlPrefix = `${taxonomyName}/${branchName}/`;

      const newNavLinks = [
        { url: urlPrefix + "entry", translationKey: "Nodes" },
        { url: urlPrefix + "search", translationKey: "Search" },
        { url: urlPrefix + "export", translationKey: "Export" },
        { url: urlPrefix + "errors", translationKey: "Errors" },
      ];

      setNavLinks(newNavLinks);
    },
    []
  );

  const queryClient = new QueryClient();

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <ResponsiveAppBar displayedPages={navLinks} />
          <Routes>
            <Route
              path="/"
              element={<Home clearNavBarLinks={resetNavLinks} />}
            />
            <Route
              path="startproject"
              element={<StartProject clearNavBarLinks={resetNavLinks} />}
            />
            <Route
              path="gotoproject"
              element={<GoToProject clearNavBarLinks={resetNavLinks} />}
            />
            <Route
              path=":taxonomyName/:branchName/export"
              element={
                <ExportTaxonomy addNavLinks={addTaxonomyBranchNavLinks} />
              }
            />
            <Route
              path=":taxonomyName/:branchName/entry"
              element={<RootNodes addNavLinks={addTaxonomyBranchNavLinks} />}
            />
            <Route
              path=":taxonomyName/:branchName/entry/:id"
              element={<EditEntry addNavLinks={addTaxonomyBranchNavLinks} />}
            />
            <Route
              path=":taxonomyName/:branchName/search"
              element={<SearchNode addNavLinks={addTaxonomyBranchNavLinks} />}
            />
            <Route
              path=":taxonomyName/:branchName/errors"
              element={<Errors addNavLinks={addTaxonomyBranchNavLinks} />}
            />
          </Routes>
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
