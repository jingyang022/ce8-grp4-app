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
        background: url("https://ce8-grp4-dev-bucket.s3.ap-southeast-1.amazonaws.com/images/singapore_bg.png") no-repeat center center/cover;
        height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
      }

      .container {
        background: rgba(255
