import os
from flask import Flask, request, redirect, url_for, flash
from flask import render_template
from werkzeug.utils import secure_filename

from cStringIO import StringIO
import sys

import tebio_fit_importer

SERVER_DIR = '/code'
# SERVER_DIR = '.'
UPLOAD_FOLDER = SERVER_DIR + '/static/uploads-tebiofit'

ALLOWED_EXTENSIONS = {'sbml', 'xml'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

all_colors = ["#e41a1c","#377eb8","#4daf4a","#984ea3","#ff7f00","#ffff33","#a65628","#f781bf","#999999"]


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def to_int(x):
    try:
        return int(x)
    except ValueError:
        return 0


# Routes for tebio-fit config converter

@app.route('/tebiofit-form/', methods=['GET', 'POST'])
def upload_tebiofit_file():
    basedir = UPLOAD_FOLDER

    if request.method == 'POST':

        # Create a subdirectory in which to save results
        dir_name = str(max(map(lambda x: to_int(x), os.listdir(basedir))) + 1)
        tmp_path = basedir + "/" + dir_name
        os.mkdir(tmp_path)

        uploads = []

        # Save config file
        field = "configFile"
        if field not in request.files:
            flash('Must upload a config file')
            return redirect(request.url)

        f = request.files[field]

        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(os.path.join(tmp_path, filename))
            uploads.append(filename)

        # Save model files
        for i in range(1, len(request.files) + 1):
            field = "file" + str(i)

            if field not in request.files:
                continue

            f = request.files[field]

            if f and allowed_file(f.filename):
                filename = secure_filename(f.filename)
                f.save(os.path.join(tmp_path, filename))
                uploads.append(filename)

        # Actually process
        if len(uploads) == 1:
            os.rmdir(tmp_path)
            flash('Must upload at least one model')
            return redirect(request.url)

        else:

            old_stdout = sys.stdout
            sys.stdout = mystdout = StringIO()

            tebio_fit_importer.process_file(os.path.join(tmp_path, uploads[0]))

            json_results = mystdout.getvalue()
            sys.stdout = old_stdout

            f = open(os.path.join(tmp_path, 'setup.json'), 'w')
            f.write(json_results)
            f.close()

            return redirect(url_for('tebiofit_results',
                                    filename=dir_name))

    return render_template('tebio-fit-form.html')


@app.route('/tebiofit-results/<filename>', methods=['GET', 'POST'])
def tebiofit_results(filename):
    return render_template('tebio-results.html', filename=filename)


# Routes for static pages
@app.route('/')
def page_homepage():
    return redirect('/tebiofit-form')



@app.route('/tebio-fit')
def page_tebio_fit():
    return render_template('tebio-fit.html')

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html')

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')


if __name__ == "__main__":
    app.run()
