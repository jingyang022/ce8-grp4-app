import os
import logging
import boto3
from flask import Flask, request, render_template_string
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")
logger = logging.getLogger(__name__)

# Flask app init
app = Flask(__name__)

# Set file size limit to 10 MB
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # Limit to 10 MB

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
        background: #f4f4f4;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        margin: 0;
      }

      .container {
        background: rgba(255, 255, 255, 0.9);
        padding: 30px;
        border-radius: 15px;
        width: 400px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        text-align: center;
      }

      input[type="file"] {
        margin: 20px 0;
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
      <form id="uploadForm" method="POST" enctype="multipart/form-data">
        <label>Select file to upload:</label><br/>
        <input type="file" id="fileInput" name="file" accept=".pdf,.docx,.jpg,.png" required />
        <button type="submit" id="uploadBtn">Upload</button>
      </form>
      <div class="file-feedback" id="fileFeedback"></div>
      <p id="statusMessage" class="status-message"></p>
    </div>

    <script>
      document.addEventListener("DOMContentLoaded", function () {
        const fileInput = document.getElementById("fileInput");
        const uploadForm = document.getElementById("uploadForm");
        const statusMessage = document.getElementById("statusMessage");
        const fileFeedback = document.getElementById("fileFeedback");

        fileInput.addEventListener("change", () => {
          const file = fileInput.files[0];
          if (file) {
            fileFeedback.textContent = `File selected: ${file.name} (${(file.size / (1024 * 1024)).toFixed(2)} MB)`;
          }
        });

        uploadForm.addEventListener("submit", function (event) {
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

          xhr.onload = function () {
            if (xhr.status === 200) {
              statusMessage.innerHTML = xhr.responseText;
              statusMessage.style.color = "green";
            } else {
              statusMessage.textContent = `Upload failed: ${xhr.responseText}`;
              statusMessage.style.color = "red";
            }
          };

          statusMessage.textContent = `Uploading: ${file.name}`;
          statusMessage.style.color = "#222";
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

    # Prevent duplicate filenames by appending a unique identifier
    unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex}_{filename}"

    try:
        # Upload to S3
        s3_client.upload_fileobj(file_obj, BUCKET_NAME, unique_filename)
        logger.info("File '%s' uploaded to bucket '%s'.", unique_filename, BUCKET_NAME)
        s3_url = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{unique_filename}"
        return f"Upload complete! <a href='{s3_url}' target='_blank'>View file</a>"
    except Exception as exc:
        logger.exception("Error uploading file to S3.")
        return f"Error uploading file: {str(exc)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
