import os
from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from parser import parse_pdf_file
from db import save_candidate, list_candidates

load_dotenv()

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'txt'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.getenv('SECRET_KEY', 'dev')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['resume']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.stream.seek(0)
            file.save(filepath)
            # re-open saved file to pass to parser
            with open(filepath, 'rb') as f:
                parsed = parse_pdf_file(f)
            # persist
            cid = save_candidate(parsed)
            flash(f'Parsed and saved candidate id={cid}')
            return render_template('results.html', parsed=parsed)
        else:
            flash('Unsupported file type')
            return redirect(request.url)
    # GET
    candidates = list_candidates(20)
    return render_template('index.html', candidates=candidates)


if __name__ == '__main__':
    app.run(debug=True)