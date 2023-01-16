import { createTheme, CssBaseline, ThemeProvider } from "@mui/material";
import { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import ResponsiveAppBar from "./components/ResponsiveAppBar";
import Entry from "./pages/allentries";
import EditEntry from "./pages/editentry";
import ExportTaxonomy from "./pages/export";
import GotoProject from "./pages/gotoproject";
import Home from "./pages/home";
import SearchNode from "./pages/search";
import StartProject from "./pages/startproject";

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
  const [displayedPages, setDisplayedPages] = useState([]);
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <ResponsiveAppBar displayedPages={displayedPages} />
        <div>
          <Routes>
            <Route
              path="/"
              element={<Home setDisplayedPages={setDisplayedPages} />}
            />
            <Route path="/startproject" element={<StartProject />} />
            <Route path="/gotoproject" element={<GotoProject />} />
            <Route
              path=":taxonomyName/:branchName/export"
              element={<ExportTaxonomy setDisplayedPages={setDisplayedPages} />}
            ></Route>
            <Route
              path=":taxonomyName/:branchName/entry"
              element={<Entry setDisplayedPages={setDisplayedPages} />}
            />
            <Route
              path=":taxonomyName/:branchName/entry/:id"
              element={<EditEntry setDisplayedPages={setDisplayedPages} />}
            />
            <Route
              path=":taxonomyName/:branchName/search"
              element={<SearchNode setDisplayedPages={setDisplayedPages} />}
            />
          </Routes>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
