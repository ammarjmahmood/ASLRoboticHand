import logo from './logo.svg';
import './App.css';
import StartPage from './StartPage';
import LoginPage from './LoginPage';
import { Route, BrowserRouter, Routes } from 'react-router-dom';
import HomePage from './HomePage';
import Leaderboard from './Leaderboard';
import DailyChallenge from './DailyChallenge';
import Freestyle from './Freestyle';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<StartPage />} /> 
        <Route path="/login" element={<LoginPage />} />  
        <Route path="/home" element={<HomePage />} />
        <Route path="/home/leaderboard" element={<Leaderboard />} />
        <Route path="/home/daily-challenge" element={<DailyChallenge />} />
        <Route path="/home/freestyle" element={<Freestyle />} />
        <Route path="/home/aslingo" element={<HomePage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
