import React, { useState, useEffect, useContext } from 'react';
import './Leaderboard.css'; // External stylesheet for styling
import { UserContext } from './context';

const Leaderboard = () => {
  // Sample data for demonstration
  const uc = useContext(UserContext)
  const [leaderboardData, setLeaderboardData] = useState([
    { username: 'Dylan', points: 1500 },
    { username: 'George', points: 1450 },
    { username: 'Felix', points: 1420 },
    { username: uc.userName, points: uc.points}
  ]);

  useEffect(() => {
    let newLeaderboardData = [...leaderboardData]
    newLeaderboardData.sort((a, b) => a.points < b.points)
    
    for (let i = 0; i < leaderboardData.length; i++){
        if (newLeaderboardData[i].username !== leaderboardData[i].username){
            setLeaderboardData(newLeaderboardData);
            return;
        }
    }
  }, [leaderboardData])

  const userRank = 120
  // Assuming currentUser is passed in as props
  const userStanding = leaderboardData.findIndex(user => user.username === uc.userName) + 1;
  const points = 1200;

  return (
    <div style={{backgroundColor: '#873ee6', height: '100vh'}}>
        <nav class="navbar">
            <div class="navbar__container">
                <div style={{display: 'flex', marginRight: 425}}>
                <img src={`${process.env.PUBLIC_URL}/ASLingo-Logo.png`} className='navbar__logo__image' style={{height: '50%', alignSelf: 'center', marginRight: 10}} />
                <a href="/home" id="navbar__logo">ASLingo</a>
                </div>
                <div class="navbar__toggle" id="mobile-menu">
                    <span class="bar"></span>
                    <span class="bar"></span>
                    <span class="bar"></span>
                </div>
                <ul class="navbar__menu">
                    <li class="navbar__item">
                        <a href="/home" class="navbar__links">Back to Home</a>
                    </li>
                    <li class="navbar__item">
                        <a className='navbar__links'>{`Points: ${uc.points}`}</a>
                    </li>
                </ul>
            </div>
        </nav>
        <div id="mission-statement" className="mission__statement" style={{paddingBottom: 20, paddingLeft: 20, paddingTop: 50}}>
            <p style={{textAlign: 'center', paddingLeft: 40}}>See how you rank alongside other ASLinguists around the world! 🌎</p>
        </div>
        <div className="leaderboard-container" style={{marginTop: 40, width: '90%'}}>
        <h1 className="leaderboard-title">Top 100 ASLinguists</h1>
        <table className="leaderboard-table">
            <thead>
            <tr className="table-header">
                <th>Ranking</th>
                <th>Username</th>
                <th>Total Points</th>
            </tr>
            </thead>
            <tbody>
            {leaderboardData.map((user, index) => (
                <tr key={index} className={user.username === uc.userName ? 'highlight' : ''}>
                <td style={{color: user.username === uc.userName ? '#ffeb3b' : 'black'}}>{index+1}</td>
                <td style={{color: user.username === uc.userName ? '#ffeb3b' : 'black'}}>{user.username}</td>
                <td style={{color: user.username === uc.userName ? '#ffeb3b' : 'black'}}>{user.points}</td>
                </tr>
            ))}
            {!userStanding && (
                <tr key={leaderboardData.length}>
                    <td style={{color: 'black', fontWeight: 'bold'}}>{userRank}</td>
                    <td style={{color: 'black', fontWeight: 'bold'}}>{uc.userName}</td>
                    <td style={{color: 'black', fontWeight: 'bold'}}>{points}</td>
                </tr>
            )}
            </tbody>
        </table>
        </div>
        <div id="mission-statement" className="mission__statement" style={{paddingBottom: 20, paddingLeft: 20, paddingTop: 50}}>
            <p style={{textAlign: 'center', paddingLeft: 40}}>Ready to rank up? <a href='/home' style={{color: 'white', fontWeight: 'bold'}}>Practice more problems now!</a></p>
        </div>
    </div>
  );
};

export default Leaderboard;