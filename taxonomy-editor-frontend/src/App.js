import { createTheme, CssBaseline, ThemeProvider } from "@mui/material";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import ResponsiveAppBar from "./components/ResponsiveAppBar";
import Entry from "./pages/allentries";
import EditEntry from "./pages/editentry";

const theme = createTheme({
  typography: {
      fontFamily : 'Plus Jakarta Sans',
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
    <CssBaseline />
    <Router>
        <div className="App">
          <ResponsiveAppBar />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/entry" element={<Entry />} />
            <Route path="/entry/:id" element={<EditEntry />} />
          </Routes>
        </div>
    </Router>
    </ThemeProvider>
  );
}

export default App;
