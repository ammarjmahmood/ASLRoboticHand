import React, { useState, useEffect, useRef, useContext } from 'react';
import { UserContext } from './context';

function dataURItoBlob(dataURI) {
  // convert base64/URLEncoded data component to raw binary data held in a string
  var byteString;
  if (dataURI.split(',')[0].indexOf('base64') >= 0)
      byteString = atob(dataURI.split(',')[1]);
  else
      byteString = unescape(dataURI.split(',')[1]);

  // separate out the mime component
  var mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];

  // write the bytes of the string to a typed array
  var ia = new Uint8Array(byteString.length);
  for (var i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i);
  }

  return new Blob([ia], {type:mimeString});
}

function Freestyle() {
  const [feedback, setFeedback] = useState('Waiting for your sign...');
  const [isCameraEnabled, setIsCameraEnabled] = useState(false);
  const uc = useContext(UserContext);
  const canvasRef = useRef(null);
  const videoRef = useRef(null);
  const dailyObjective = "Daily Challenge: Sign 3 numbers";
  const [numbers, updateNumbers]  = useState([]);
  const [numMistakes, updateNumMistakes] = useState(0);
  const [maybe, setMaybe] = useState(false);
  const [newSign, setNewSign] = useState('');
  const points = 100;

  useEffect(() => {
    startCamera();

    const interval = setInterval(captureImage, 2000);

    if (numbers.length >= 3) {
      clearInterval(interval);
    }

    return () => {
      clearInterval(interval); 
      stopCamera(); 
    };
  }, []);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoRef.current.srcObject = stream;
    } catch (error) {
      console.error("Error accessing camera: ", error);
    }
  };

  const stopCamera = () => {
    const stream = videoRef.current?.srcObject;
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
    }
  };

  const sendImageToServer = async (imageData) => {
    try {
      let form = new FormData();
      form.append("image", dataURItoBlob(imageData));
      const response = await fetch("http://localhost:8765/api/closest", {
        method: 'POST',
        body: form,
      });

      let result = await response.json();

      if (result){
        let name = result[0][1];
        let closeness = result[0][0];
        console.log(name, closeness, numbers);
        if (closeness < 10) {
          setNewSign(_ => name);
          setMaybe(false);
        } else {
          if (response.ok){
            setNewSign(_ => name);
          }
          setMaybe(true);
          console.log("not close or smth?")
        }
      } else {
        console.log("no match found");
      }

    } catch (error) {
      console.error("Error sending image:", error);
    }
  };

  const captureImage = () => {
    const canvas = canvasRef.current;
    const video = videoRef.current;

    if (canvas && video) {
      if (video !== undefined && video.currentTime > 0 && !video.paused && !video.ended && video.readyState > 2) {
        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        const imageData = canvas.toDataURL('image/png');

        sendImageToServer(imageData);
      }
    }
  };

  return (
    <div style={{backgroundColor: '#873ee6', height: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'space-between'}}>
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
        {numbers.length < 3 ? (
          <div class="flex flex-col md:flex-row items-center justify-around space-y-8 md:space-y-0 md:space-x-8">
              <div class="w-full md:w-1/2 flex flex-col items-center">
              <div class="w-full" style={{backgroundColor: '#873ee6'}}>
                  <video ref={videoRef} autoPlay playsInline style={{ width: '100%', height: 'auto', paddingTop: 20}}></video>
                  <canvas ref={canvasRef} style={{ display: 'none' }}></canvas>
              </div>
              <p class="mt-4 text-center text-gray-700 text-white text-bold text-xl pb-4">Sign directly into the camera! The camera will interpret your ASL.</p>
              {newSign && <p style={{paddingTop: 30, paddingBottom: 30, fontSize: 100, textAlign: 'center', width:'100vw', color: '#54c922', fontSize: '48px', fontWeight: 'bold'}}>{maybe ? (newSign ? `Unclear sign. Did you mean to sign "${newSign}"?` : `Unclear sign.`) : `You signed "${newSign}"!`}</p>}
              </div>
          </div>
        ) : (
          <div class="success">
            <div class="success__container" style={{alignItems: 'center'}}>
                <div class="success__content">
                    <h1>Well Done!</h1>
                    <p>{`You signed the following numbers: ` + numbers.join(',')}</p>
                    <p>{`You've earned ${points} points`}</p>
                    <button class="dm__btn"><a href="/home"> Home </a></button>
                    <button class="dm__btn"><a href="/home/daily-challenge"> Try Again </a></button>
                </div>
            </div>
        </div>
        )}
    </div>
  );
}

export default Freestyle;