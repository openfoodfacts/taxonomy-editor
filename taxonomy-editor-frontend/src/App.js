import { createTheme, CssBaseline, ThemeProvider } from "@mui/material";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import ResponsiveAppBar from "./components/ResponsiveAppBar";
import Entry from "./pages/allentries";
import Home from './pages/home';

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
        <ResponsiveAppBar />
        <div className="App">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/entry" element={<Entry />} />
          </Routes>
        </div>
    </Router>
    </ThemeProvider>
  );
}

export default App;
