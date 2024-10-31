import React, { useContext, useEffect, useRef, useState } from 'react';
import './App.css'; 
import { UserContext } from './context';
import { useNavigate } from 'react-router-dom';

const LoginPage = () => {
  const gifList = [
    '/gif1.gif',
    '/gif2.gif',
    '/gif3.gif',
    '/gif4.gif',
    '/gif5.gif',
    '/gif6.gif'
  ];

  const [currentGifIndex, setCurrentGifIndex] = useState(0);
  const [showSignUp, setShowSignUp] = useState(false);
  const uc = useContext(UserContext);
  const navigate = useNavigate();
  const formRef = useRef(null);

  const onLogin = (e) => {
      e.preventDefault();

      if (formRef.current) {
        var data = new FormData(formRef.current);

        if (data && data.get('user') === uc.userName && data.get('pass') === 'hello123') {
          navigate('/home');  
        } else {
          alert('Incorrect username or password! Try again')
        }
      } else {
        alert("An internal error occured! Try again later");
      }
  }

  const toggleSignUp = () => {
    setShowSignUp(!showSignUp);
  };

  const switchGif = () => {
    setCurrentGifIndex((currentGifIndex) => (currentGifIndex + 1) % gifList.length); 
  };

  useEffect(() => {
    const interval = setInterval(switchGif, 5000);
    return () => clearInterval(interval);
  });

  return (
    <div>
       <nav class="navbar">
          <div class="navbar__container_h">
            <div style={{display: 'flex'}}>
              <img src={`${process.env.PUBLIC_URL}/ASLingo-Logo.png`} className='navbar__logo__image' style={{height: '50%', alignSelf: 'center', marginRight: 10}} />
              <a href="/" id="navbar__logo">ASLingo</a>
            </div>
            <div class="navbar__toggle" id="mobile-menu">
                <span class="bar"></span>
                <span class="bar"></span>
                <span class="bar"></span>
            </div>
            <div style={{width: 720}} />
        </div>
    </nav>
      <div className="background-wrapper">
        <div
          className="background-gif"
          style={{
            backgroundImage: `url("/gifs/${gifList[currentGifIndex]}")`, // First GIF
          }}
        />
        <div
          className="background-gif"
          style={{
            backgroundImage: `url("/gifs/${(gifList[(currentGifIndex + 3) % gifList.length])}")`, // Second GIF
          }}
        />
        <div className="login-form-2">
          <h2>Login</h2>
          <form className="login-form" id="login-form" ref={formRef}>
            <input type="text" placeholder="Username" name='user' required />
            <input type="password" placeholder="Password" name='pass' required />
            <button type="submit" className="btn" onClick={onLogin}>Login</button>

            <p>Or log in with:</p>
            <div className="sso-buttons">
              <button className="btn sso-btn">Google</button>
              <button className="btn sso-btn">Facebook</button>
            </div>

            <p>
              Don't have an account?{' '}
              <button type="button" className="link-btn" onClick={toggleSignUp}>
                Sign up here
              </button>
            </p>
          </form>
        </div>
        {showSignUp && <SignUpModal toggleSignUp={toggleSignUp} />}
      </div>
    </div>
  );
};

const SignUpModal = ({ toggleSignUp }) => {
  return (
    <div className="signup-modal">
      <div className="modal-content">
        <h2>Sign Up</h2>
        <form className="signup-form">
          <input type="email" placeholder="Email" required />
          <input type="text" placeholder="Username" required />
          <input type="password" placeholder="Password" required />
          <button type="submit" className="btn">Sign Up</button>

          <p>Or sign up with:</p>
          <div className="sso-buttons">
            <button className="btn sso-btn">Google</button>
            <button className="btn sso-btn">Facebook</button>
          </div>
        </form>

        <button className="link-btn" style={{paddingTop: 15}} onClick={toggleSignUp}>Back to Login</button>
      </div>
    </div>
  );
};

export default LoginPage;
