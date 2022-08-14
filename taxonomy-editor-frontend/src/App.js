import { createTheme, CssBaseline, ThemeProvider } from "@mui/material";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
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
        <div className="App">
          <Routes>
            <Route path="/" element={<Home />} />
          </Routes>
        </div>
    </Router>
    </ThemeProvider>
  );
}

export default App;
