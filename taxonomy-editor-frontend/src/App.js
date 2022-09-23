import { createTheme, CssBaseline, ThemeProvider } from "@mui/material";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import ResponsiveAppBar from "./components/ResponsiveAppBar";
import Entry from "./pages/allentries";
import EditEntry from "./pages/editentry";
import Home from './pages/home';
import SearchNode from "./pages/search";
import SearchResults from "./pages/search/results";

const theme = createTheme({
  typography: {
      fontFamily : 'Plus Jakarta Sans',
      button: {
        fontFamily : 'Roboto, Helvetica, Arial, sans-serif'
      },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
    <CssBaseline />
    <Router>
        <ResponsiveAppBar />
        <div className="App">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/entry" element={<Entry />} />
            <Route path="/entry/:id" element={<EditEntry />} />
            <Route path="/search" element={<SearchNode />} />
            <Route path="/results" element={<SearchResults />} />
          </Routes>
        </div>
    </Router>
    </ThemeProvider>
  );
}

export default App;