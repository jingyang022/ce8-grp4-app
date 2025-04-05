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
        logger.exception("Error uploading file to S3: %s", exc)
        return f"Error uploading file: {str(exc)}", 500
