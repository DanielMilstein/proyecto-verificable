from flask import render_template, request, redirect, flash

def render_home_page():
    if is_file_upload_request():
        return handle_file_upload()
    return render_template('home.html')

def is_file_upload_request():
    return request.method == 'POST' and 'upload_file' in request.files

def handle_file_upload():
    file = request.files['upload_file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:
        save_uploaded_file(file)
        return 'File Uploaded Successfully'
    flash('No file uploaded')
    return redirect(request.url)

def save_uploaded_file(file):
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))