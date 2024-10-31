import React from 'react';
import './StartPage.css'

const StartPage = () => {
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
            <ul class="navbar__menu">

                {/* <li class="navbar__item">
                    <a href="/frontend/Fail.html" class="navbar__links"> Fail </a>
                </li>
                <li class="navbar__item">
                    <a href="/frontend/Success.html" class="navbar__links"> Success </a>
                </li> */}

                <li class="navbar__item">
                    <a href="/home/daily-challenge" class="navbar__links"> Daily Challenge </a>
                </li>
                <li class="navbar__item">
                    <a href="#mission-statement" class="navbar__links"> Mission Statement </a>
                </li>
                <li class="navbar__btn">
                    <a href="/login" class="button"> Register/Log In </a>
                </li>
            </ul>
        </div>
    </nav>


    <div class="main" style={{height: '100vh'}}>
        <div class="image__container">
            <img src={`${process.env.PUBLIC_URL}/ASL_Logo.png`} alt="Centered and blurred image of ASL in sign language" class="centered__image" />
        </div>
        <div class="main__container">
            <div class="main__content">
                <h1>Welcome to ASLingo!</h1>
                <p>AI Meets ASL: Learn to Sign, One Gesture at a Time</p>
                <button class="main__btn"><a href="/login"> Get Started</a></button>
            </div>
        </div>
    </div>
    <div style={{height: 20}} />
    <div class="flex justify-center items-center bg-black" style={{height: '120vh'}}>
        <div id="mission-statement" className="mission__statement" style={{paddingBottom: 20, width: '60%', paddingLeft: 20}}>
            <h1 style={{paddingTop: 20, fontWeight: 'bold', fontSize: '3rem'}}>Mission Statement</h1>
            <p style={{textAlign: 'left', paddingLeft: 40, width: '110%'}}>At ASLingo, we are dedicated to breaking down communication barriers through the innovative use of artificial intelligence. Our mission is to empower individuals by providing accessible, engaging, and effective tools for learning American Sign Language. We believe that everyone deserves the opportunity to connect and communicate, and we strive to foster inclusivity and understanding in our diverse world.</p>
        </div>
        <img src={`${process.env.PUBLIC_URL}/asl-homepage-image.jpeg`} style={{width: '38%', padding: 20, height: '50%', alignSelf: 'center', transform: 'translateY(50px)'}} />
    </div>
    </div>
  );
};

export default StartPage;
