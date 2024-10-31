import React, { useContext } from 'react';
import './HomePage.css';
import  { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { UserContext } from './context';

const useTypewriter = (text, speed) => {
  const [displayText, setDisplayText] = useState('');

  useEffect(() => {
    let i = 0;
    const typingInterval = setInterval(() => {
      if (i < text.length) {
        setDisplayText(prevText => (i > 0 ? prevText : '') + text.charAt(i));
        i++;
      } else {
        setDisplayText(prevText => prevText + ' 👋');
        clearInterval(typingInterval);
      }
    }, speed);

    return () => {
      clearInterval(typingInterval);
    };
  }, [text, speed]);

  return displayText;
};

const Typewriter = ({ text, speed }) => {
  const displayText = useTypewriter(text, speed);

  return <h1 style={{paddingTop: 30}}>{displayText}</h1>;
};

function HomePage({ user }) {
  const now = new Date();

  const {userName, points} = useContext(UserContext);
  const daysOfWeek = [
    'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'
  ];
  const month = ["January","February","March","April","May","June","July","August","September","October","November","December"];

  const dayOfWeek = daysOfWeek[now.getDay()];
  const currentMonth = month[now.getMonth()];
  const currentDayOfTheMonth = now.getDate();

  const navigate = useNavigate();

  return (
    <div className="home-container" style={{backgroundColor: '#873ee6'}}>
      <nav class="navbar">
        <div class="navbar__container" style={{justifyContent: 'space-in-between'}}>
            <div style={{display: 'flex'}}>
              <img src={`${process.env.PUBLIC_URL}/ASLingo-Logo.png`} className='navbar__logo__image' style={{height: '50%', alignSelf: 'center'}} />
              <a href="/home" id="navbar__logo">ASLingo</a>
            </div>
            <div class="navbar__toggle" id="mobile-menu">
                <span class="bar"></span>
                <span class="bar"></span>
                <span class="bar"></span>
            </div>
            <ul class="navbar__menu">
                <li class="navbar__item">
                    <a href="/home/leaderboard" class="navbar__links">Leaderboard</a>
                </li>
                <li class="navbar__item">
                    <a className='navbar__links'>{`Points: ${points}`}</a>
                </li>
                <li class="navbar__btn">
                    <button onClick={() => {
                      navigate('/');
                    }} class="button"> Logout </button>
                </li>
            </ul>
        </div>
    </nav>
      {/* <div className="top-bar">
        <div className="logo">ASLingo</div>
        <div className="menu-right">
          <div className="leaderboard">Leaderboard</div>
          <div className="points">Points: 1200</div>
        </div>
      </div> */}

      <div className="welcome-message" style={{backgroundImage: `url("${process.env.PUBLIC_URL}/HomePage.png")`}}>
        <div style={{backgroundColor: 'rgb(0, 0, 0, 0.3)', height: '100%',  padding: 0}}>
          <Typewriter text={`Weelcome, ${userName}!`} speed={65} />
          <h2 style={{paddingTop: 40, paddingLeft: 25, fontSize: '48px', color: 'white'}}>Ready to master ASL?!</h2>
        </div>
      </div>
      <h1 style={{paddingTop: 30, paddingBottom: 30, color: 'white', fontSize: '32px', fontWeight: 'bold'}}>Your Tasks</h1>
      <hr style={{color: 'white', width:'80%'}} />
      <div className="cards-container">
        <div className="card">
          <img src={`${process.env.PUBLIC_URL}/daily-challenge.png`} alt="Example" className="card-image" />
          <div className="card-description">
            <h1 style={{paddingTop: 5, paddingBottom:20, fontSize: '28px', color: '#873ee6', fontWeight: 'bold'}}>Daily Challenge</h1>
            <hr style={{borderColor: '#873ee6'}} />
            <p style={{paddingTop: 20, paddingBottom:20}}>{`Continue practicing your ASL skills by trying our daily challenge for ${dayOfWeek}, ${currentMonth} ${currentDayOfTheMonth}.`}</p>
          </div>
          <button className="home-button" onClick={() => navigate('/home/daily-challenge')}>Go to task</button>
        </div>
        <div className="card">
          <img src={`${process.env.PUBLIC_URL}/freestyle.png`} alt="Example" className="card-image" />
          <div className="card-description">
            <h1 style={{paddingTop: 5, paddingBottom:20, fontSize: '28px', color: '#873ee6', fontWeight: 'bold'}}>Freestyle</h1>
            <hr style={{borderColor: '#873ee6'}} />
            <p style={{paddingTop: 20, paddingBottom:20}}>Freestyle time! Showcase your ASL - we'll figure out what you're signing.</p>
          </div>
          <button className="home-button" onClick={() => navigate('/home/freestyle')}>Go to task</button>
        </div>
        <div className="card">
          <img src={`${process.env.PUBLIC_URL}/aslingo.png`} alt="Example" className="card-image" />
          <div className="card-description">
            <h1 style={{paddingTop: 5, paddingBottom:20, fontSize: '28px', color: '#873ee6', fontWeight: 'bold'}}>ASLingo</h1>
            <hr style={{borderColor: '#873ee6'}} />
            <p style={{paddingTop: 20, paddingBottom:20}}>Time for ASLingo! Flex your ASL skills by signing commonly used words we test you with.</p>
          </div>
          <button className="home-button" onClick={() => navigate('/home/aslingo')}>Go to task</button>
        </div>
      </div>
    </div>
  );
}

export default HomePage;
