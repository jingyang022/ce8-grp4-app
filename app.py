import os
import logging
import boto3
from flask import Flask, request, render_template_string
from werkzeug.utils import secure_filename

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

AWS_REGION = os.environ["AWS_REGION"]
BUCKET_NAME = os.environ["BUCKET_NAME"]
s3_client = boto3.client("s3", region_name=AWS_REGION)

# Simple HTML form for file upload
UPLOAD_FORM = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Application Form Upload Portal</title>
    <style>
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: "Arial", sans-serif;
      }

      body {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        background: url("https://ce8-grp4-bucket.s3.ap-southeast-1.amazonaws.com/singapore_bg.png") no-repeat center center/cover;
      }

      .container {
        background: rgba(255, 255, 255, 0.85);
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        text-align: center;
        width: 450px;
        backdrop-filter: blur(10px);
      }

      h2 {
        margin-bottom: 20px;
        font-size: 28px;
        color: #222;
        font-weight: bold;
      }

      p.instructions {
        font-size: 18px;
        color: #444;
        margin-bottom: 25px;
      }

      .drop-area {
        border: 3px dashed #4caf50;
        padding: 40px;
        border-radius: 12px;
        margin-bottom: 25px;
        cursor: pointer;
        background: rgba(232, 245, 233, 0.8);
        color: #4caf50;
        font-size: 20px;
        font-weight: bold;
        transition: background 0.3s;
      }

      .drop-area:hover,
      .drop-area.dragover {
        background-color: rgba(200, 230, 201, 0.9);
        border-color: #388e3c;
      }

      input[type="file"] {
        display: none;
      }

      button {
        width: 100%;
        padding: 18px;
        font-size: 18px;
        color: white;
        background-color: #4caf50;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        transition: background-color 0.3s, transform 0.2s;
      }

      button:hover {
        background-color: #388e3c;
        transform: scale(1.05);
      }

      .progress-container {
        width: 100%;
        background: #ddd;
        border-radius: 5px;
        overflow: hidden;
        display: none;
        margin-top: 15px;
      }

      .progress-bar {
        height: 15px;
        width: 0%;
        background: #4caf50;
        transition: width 0.4s ease;
      }

      .status-message {
        margin-top: 15px;
        font-size: 18px;
        font-weight: bold;
        color: #222;
      }

      @media (max-width: 400px) {
        .container {
          width: 90%;
        }
      }
    </style>
  </head>
  <body>
    <div class="container">
      <h2>Upload Application Form</h2>
      <p class="instructions">
        Please upload your completed application form here. Supported file
        formats: <strong>.pdf, .docx, .jpg, .png</strong>. Maximum size: 10MB.
      </p>
      <div class="drop-area" id="dropArea">
        📂 Drag & Drop or Click to Upload
      </div>
      <input
        type="file"
        id="fileInput"
        name="file"
        accept=".pdf,.docx,.jpg,.png"
        required
      />
      <button id="uploadBtn">Upload Application</button>
      <div class="progress-container">
        <div class="progress-bar" id="progressBar"></div>
      </div>
      <p id="statusMessage" class="status-message"></p>
    </div>

    <script>
      document.addEventListener("DOMContentLoaded", function () {
        const dropArea = document.getElementById("dropArea");
        const fileInput = document.getElementById("fileInput");
        const uploadBtn = document.getElementById("uploadBtn");
        const progressBar = document.getElementById("progressBar");
        const progressContainer = document.querySelector(".progress-container");
        const statusMessage = document.getElementById("statusMessage");

        // Open file selector on click
        dropArea.addEventListener("click", () => fileInput.click());

        // Handle file selection
        fileInput.addEventListener("change", (event) => {
          const file = event.target.files[0];
          if (file) {
            handleFileUpload(file);
          }
        });

        // Drag and Drop functionality
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
            fileInput.files = event.dataTransfer.files; // Sync with input
            handleFileUpload(file);
          }
        });

        // Simulated Upload Function
        function handleFileUpload(file) {
          if (file.size > 10 * 1024 * 1024) {
            statusMessage.textContent = "Error: File size exceeds 10MB.";
            statusMessage.style.color = "red";
            return;
          }

          statusMessage.textContent = `Uploading: ${file.name}`;
          statusMessage.style.color = "#222";
          progressContainer.style.display = "block";
          progressBar.style.width = "0%";

          let progress = 0;
          const interval = setInterval(() => {
            if (progress >= 100) {
              clearInterval(interval);
              statusMessage.textContent = "Upload Complete!";
              statusMessage.style.color = "green";
            } else {
              progress += 10;
              progressBar.style.width = `${progress}%`;
            }
          }, 300);
        }

        // Upload Button triggers file input click
        uploadBtn.addEventListener("click", () => fileInput.click());
      });
    </script>
  </body>
</html>
"""

@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "GET":
        return render_template_string(UPLOAD_FORM)
        
    file_obj = request.files.get("file")
    if not file_obj or file_obj.filename.strip() == "":
        logger.warning("No valid file provided.")
        return "No valid file provided.", 400

    filename = secure_filename(file_obj.filename)

    try:
        s3_client.upload_fileobj(file_obj, BUCKET_NAME, filename)
        logger.info("File '%s' uploaded to bucket '%s'.", filename, BUCKET_NAME)
        return f"File '{filename}' uploaded successfully to S3 bucket '{BUCKET_NAME}'!"
    except Exception as exc:
        logger.exception("Error uploading file to S3.")
        return f"Error uploading file: {str(exc)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
