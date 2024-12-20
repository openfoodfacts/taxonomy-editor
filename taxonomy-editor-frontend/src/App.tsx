import {
  createBrowserRouter,
  Navigate,
  RouterProvider,
} from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { createTheme, CssBaseline, ThemeProvider } from "@mui/material";

import { EditEntryWrapper } from "./pages/project/editentry";
import { ExportTaxonomyWrapper } from "./pages/project/export";
import { GoToProject } from "./pages/go-to-project";
import { Home } from "./pages/home";
import { AdvancedSearchForm } from "./pages/project/search";
import { StartProject } from "./pages/startproject";
import { Errors } from "./pages/project/errors";
import { ProjectPage, projectLoader } from "./pages/project";
import { ProjectNotFound } from "./pages/project/ProjectNotFound";
import { PageNotFound } from "./pages/PageNotFound";
import { RootLayout } from "./pages/RootLayout";
import { AppProvider } from "./components/UseContext";
const theme = createTheme({
  typography: {
    fontFamily: "Plus Jakarta Sans",
    button: {
      fontFamily: "Roboto, Helvetica, Arial, sans-serif",
      color: "#808080",
    },
  },
});

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const router = createBrowserRouter([
  {
    element: <RootLayout />,
    errorElement: <PageNotFound />,
    children: [
      { path: "/", element: <Home /> },
      { path: "startproject", element: <StartProject /> },
      { path: "gotoproject", element: <GoToProject /> },
      {
        path: ":taxonomyName/:branchName",
        element: <ProjectPage />,
        loader: projectLoader(queryClient),
        errorElement: <ProjectNotFound />,
        children: [
          {
            path: "",
            element: <Navigate to="search" />,
          },
          {
            path: "export",
            element: <ExportTaxonomyWrapper />,
          },
          {
            path: "entry",
            element: <Navigate to="../search" relative="path" />,
          },
          {
            path: "entry/:id",
            element: <EditEntryWrapper />,
          },
          {
            path: "search",
            element: <AdvancedSearchForm />,
          },
          {
            path: "errors",
            element: <Errors />,
          },
        ],
      },
    ],
  },
]);

function App() {
  return (
    <AppProvider>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <RouterProvider router={router} />
        </ThemeProvider>
      </QueryClientProvider>
    </AppProvider>
  );
}

export default App;
