import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Entry from "./pages/allentries";
import EditEntry from "./pages/editentry";
import Home from './pages/home';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/entry" element={<Entry />} />
          <Route path="/entry/:id" element={<EditEntry />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
