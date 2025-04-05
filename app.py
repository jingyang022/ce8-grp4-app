<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>Application Form Upload</title>
    <style>
      body {
        font-family: Arial, sans-serif;
        background: url("https://ce8-grp4-dev-bucket.s3.ap-southeast-1.amazonaws.com/images/singapore_bg.png") no-repeat center center/cover;
        height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
      }

      .container {
        background: rgba(255, 255, 255, 0.9);
        padding: 30px;
        border-radius: 15px;
        width: 400px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        text-align: center;
      }

      .drop-area {
        border: 3px dashed #4caf50;
        padding: 30px;
        border-radius: 10px;
        cursor: pointer;
        background: rgba(232, 245, 233, 0.8);
        color: #4caf50;
        font-weight: bold;
        margin-bottom: 20px;
      }

      .drop-area.dragover {
        background-color: rgba(200, 230, 201, 0.9);
        border-color: #388e3c;
      }

      input[type="file"] {
        position: absolute;
        left: -9999px;
      }

      button {
        padding: 12px;
        width: 100%;
        font-size: 16px;
        background: #4caf50;
        color: white;
        border: none;
        border-radius: 8px;
        cursor: pointer;
      }

      button:hover {
        background: #388e3c;
      }

      .progress-container {
        margin-top: 10px;
        background: #ddd;
        border-radius: 5px;
        overflow: hidden;
        display: none;
      }

      .progress-bar {
        height: 12px;
        width: 0%;
        background: #4caf50;
        transition: width 0.3s ease;
      }

      .status-message {
        margin-top: 10px;
        font-weight: bold;
        color: #333;
      }

      .file-feedback {
        margin-top: 10px;
        font-weight: bold;
        color: #388e3c;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <h2>Upload Application Form</h2>
      <div class="drop-area" id="dropArea">📂 Drag & Drop or Click to Upload</div>
      <form id="uploadForm" method="POST" enctype="multipart/form-data">
        <input type="file" id="fileInput" name="file" accept=".pdf,.docx,.jpg,.png" required />
        <button type="submit" id="uploadBtn">Upload</button>
      </form>
      <div class="file-feedback" id="fileFeedback"></div>
      <div class="progress-container">
        <div class="progress-bar" id="progressBar"></div>
      </div>
      <p id="statusMessage" class="status-message"></p>
    </div>

    <script>
      document.addEventListener("DOMContentLoaded", function () {
        const dropArea = document.getElementById("dropArea");
        const fileInput = document.getElementById("fileInput");
        const uploadForm = document.getElementById("uploadForm");
        const progressBar = document.getElementById("progressBar");
        const progressContainer = document.querySelector(".progress-container");
        const statusMessage = document.getElementById("statusMessage");
        const fileFeedback = document.getElementById("fileFeedback");

        dropArea.addEventListener("click", () => fileInput.click());

        dropArea.addEventListener("dragover", (event) => {
          event.preventDefault();
          dropArea.classList.add("dragover");
        });

        dropArea.addEventListener("dragleave", () => {
          dropArea.classList.remove("dragover");
        });

        dropArea.addEventListener("drop", (event) => {
          event.preventDefault();
          dropArea.classList.remove("dragover");
          const file = event.dataTransfer.files[0];
          if (file) {
            fileInput.files = event.dataTransfer.files;
            fileFeedback.textContent = `File selected: ${file.name}`;
          }
        });

        fileInput.addEventListener("change", () => {
          const file = fileInput.files[0];
          if (file) {
            fileFeedback.textContent = `File selected: ${file.name}`;
          }
        });

        uploadForm.addEventListener("submit", (event) => {
          const file = fileInput.files[0];
          if (!file) {
            event.preventDefault();
            statusMessage.textContent = "Please select a file.";
            statusMessage.style.color = "red";
            return;
          }

          const formData = new FormData();
          formData.append("file", file);

          const xhr = new XMLHttpRequest();
          xhr.open("POST", "/upload", true);

          xhr.upload.onprogress = function (e) {
            if (e.lengthComputable) {
              const percent = (e.loaded / e.total) * 100;
              progressBar.style.width = percent + "%";
            }
          };

          xhr.onload = function () {
            if (xhr.status === 200) {
              statusMessage.innerHTML = xhr.responseText;
              statusMessage.style.color = "green";
            } else {
              statusMessage.textContent = `Upload failed: ${xhr.responseText}`;
              statusMessage.style.color = "red";
            }
          };

          progressContainer.style.display = "block";
          progressBar.style.width = "0%";
          statusMessage.textContent = `Uploading: ${file.name}`;
          statusMessage.style.color = "#222";
          xhr.send(formData);

          event.preventDefault();
        });
      });
    </script>
  </body>
</html>
