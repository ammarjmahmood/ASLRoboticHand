const video = document.getElementById("video");
const captureButton = document.getElementById("captureButton");
const downloadLink = document.getElementById("downloadLink");

navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => {
    video.srcObject = stream;
  })
  .catch(error => {
    document.write("permission denied");
  });

captureButton.addEventListener("click", () => {
  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  const context = canvas.getContext("2d");
  context.drawImage(video, 0, 0, canvas.width, canvas.height);

  canvas.toBlob(blob => {
    const blobURL = URL.createObjectURL(blob);

    // Create a temporary download link
    const downloadLink = document.createElement("a");
    downloadLink.href = blobURL;
    downloadLink.download = "image.jpg";

    // Simulate a click on the download link
    downloadLink.click();

    // Optionally, revoke the object URL to free up memory
    URL.revokeObjectURL(blobURL);


  }, "image/jpeg");



    // Prevent the default form submission behavior
document.addEventListener('load', uploadBlob())
});

document.getElementById('uploadForm').addEventListener('submit', function (e) {
  e.preventDefault();

  //Reads image file given 
  var input = document.querySelector('input[type="file"]')

  var data = new FormData()
  for (const file of input.files) {
    data.append('avatar',file,file.name)
  }
    
  fetch('http://localhost:8765/api/landmarks', {
    method: 'POST',
    body: data
  })
  .then(response => {
    if (response.ok) {
      document.getElementById('status').textContent = 'File uploaded successfully!';
    } else {
      document.getElementById('status').textContent = 'Upload failed.';
    }
  })
})