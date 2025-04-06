import os
import logging
import boto3
from flask import Flask, request, render_template_string
from werkzeug.utils import secure_filename

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

# AWS S3 setup
AWS_REGION = os.environ.get("AWS_REGION")
BUCKET_NAME = os.environ.get("BUCKET_NAME")

if not AWS_REGION or not BUCKET_NAME:
    raise RuntimeError("Missing environment variable: AWS_REGION or BUCKET_NAME")

s3_client = boto3.client("s3", region_name=AWS_REGION)

ALLOWED_EXTENSIONS = {"pdf", "docx", "jpg", "jpeg", "png"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

UPLOAD_FORM = """
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
      min-height: 20px;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(5px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .fade-in {
      animation: fadeIn 0.5s ease forwards;
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>Upload Application Form</h2>
    <div class="drop-area" id="dropArea">📂 Drag & Drop or Click to Upload</div>
    <form id="uploadForm" method="POST" enctype="multipart/form-data">
      <input type="file" id="fileInput" name="file" accept=".pdf,.docx,.jpg,.jpeg,.png" required />
      <button type="submit" id="uploadBtn">Upload</button>
    </form>
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

      function showStatus(message, color) {
        statusMessage.textContent = message;
        statusMessage.style.color = color;
        statusMessage.classList.remove("fade-in");
        void statusMessage.offsetWidth; // trigger reflow
        statusMessage.classList.add("fade-in");
      }

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
          showStatus(`Selected file: ${file.name}`, "#444");
        }
      });

      fileInput.addEventListener("change", () => {
        const file = fileInput.files[0];
        if (file) {
          showStatus(`Selected file: ${file.name}`, "#444");
        }
      });

      uploadForm.addEventListener("submit", (event) => {
        const file = fileInput.files[0];
        if (!file) {
          event.preventDefault();
          showStatus("Please select a file.", "red");
          return;
        }

        if (file.size > 10 * 1024 * 1024) {
          event.preventDefault();
          showStatus("File size exceeds 10MB.", "red");
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
            showStatus(xhr.responseText, "green");
          } else {
            showStatus(`Upload failed: ${xhr.responseText}`, "red");
          }
        };

        progressContainer.style.display = "block";
        progressBar.style.width = "0%";
        showStatus(`Uploading: ${file.name}`, "#222");
        xhr.send(formData);

        event.preventDefault();
      });
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

    if not allowed_file(filename):
        logger.warning("Disallowed file type uploaded: %s", filename)
        return "File type not allowed.", 400

    file_obj.seek(0, os.SEEK_END)
    file_size = file_obj.tell()
    if file_size > 10 * 1024 * 1024:
        return "File too large.", 400
    file_obj.seek(0)

    try:
        s3_client.upload_fileobj(file_obj, BUCKET_NAME, filename)
        logger.info("File '%s' uploaded to bucket '%s'.", filename, BUCKET_NAME)
        return "Upload complete!"
    except Exception as exc:
        logger.exception("Error uploading file to S3.")
        return f"Error uploading file: {str(exc)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
