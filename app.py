import os
import logging
import boto3
from flask import Flask, request, render_template_string
from werkzeug.utils import secure_filename

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Flask app init
app = Flask(__name__)

# AWS S3 setup
AWS_REGION = os.environ.get("AWS_REGION")
BUCKET_NAME = os.environ.get("BUCKET_NAME")

# Log env values for debugging (optional - remove in production)
logger.info(f"AWS_REGION: {AWS_REGION}")
logger.info(f"BUCKET_NAME: {BUCKET_NAME}")

# Check env vars
if not AWS_REGION or not BUCKET_NAME:
    raise RuntimeError("Missing environment variable: AWS_REGION or BUCKET_NAME")

s3_client = boto3.client("s3", region_name=AWS_REGION)

# File type filter
ALLOWED_EXTENSIONS = {"pdf", "docx", "jpg", "jpeg", "png"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# HTML form
UPLOAD_FORM = """<html>... (same HTML as before) ...</html>"""  # You can keep your existing HTML block here

# Upload route
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
        s3_url = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{filename}"
        return f"Upload complete! <a href='{s3_url}' target='_blank'>View file</a>"
    except Exception as exc:
        logger.exception("Error uploading file to S3.")
        return f"Error uploading file: {str(exc)}", 500

# Run app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
