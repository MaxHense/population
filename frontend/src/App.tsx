import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './components/Home';
import GermanyMap from './components/GermanyMap';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/germany" element={<GermanyMap />} />
      </Routes>
    </Router>
  );
}

export default App;
