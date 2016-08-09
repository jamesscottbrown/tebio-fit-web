import os
from flask import Flask, request, redirect, url_for, flash
from flask import render_template
from werkzeug.utils import secure_filename

from cStringIO import StringIO
import sys

import sbml_diff
from sbml_diff import *

import tebio_fit_importer

SERVER_DIR = '/var/www/tebio'
# SERVER_DIR = '.'
UPLOAD_FOLDER = SERVER_DIR + '/static/uploads'

ALLOWED_EXTENSIONS = {'sbml', 'xml'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

all_colors = ["#FF7F00", "#32FF00", "#19B2FF", "#654CFF", "#E51932", "#FFFF32"]


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def to_int(x):
    try:
        return int(x)
    except ValueError:
        return 0


def process_single(models, tmp_path, dir_name, reaction_label, display_stoichiometry, abstract, elided_species,
                   selected_model_num=False):

    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()

    if selected_model_num is False:
        name = ""
        if abstract:
            sbml_diff.diff_abstract_models(models,
                                           sbml_diff.GenerateDot(all_colors, len(models), reaction_label=reaction_label,
                                                                 show_stoichiometry=display_stoichiometry),
                                           elided_species=elided_species)
        else:
            sbml_diff.diff_models(models, sbml_diff.GenerateDot(all_colors, len(models), reaction_label=reaction_label,
                                                                show_stoichiometry=display_stoichiometry))

    else:
        name = str(selected_model_num) + "-"
        if abstract:
            sbml_diff.diff_abstract_models(models,
                                           sbml_diff.GenerateDot(all_colors, len(models), reaction_label=reaction_label,
                                                                 selected_model=selected_model_num,
                                                                 show_stoichiometry=display_stoichiometry),
                                           elided_species=elided_species)
        else:
            sbml_diff.diff_models(models, sbml_diff.GenerateDot(all_colors, len(models), reaction_label=reaction_label,
                                                                selected_model=selected_model_num,
                                                                show_stoichiometry=display_stoichiometry))

    graphviz = mystdout.getvalue()
    sys.stdout = old_stdout

    f = open(os.path.join(tmp_path, name + 'results.dot'), 'w')
    f.write(graphviz)
    f.close()

    # Get png
    from subprocess import call
    pr = ["dot", "-Tpng", "-o", SERVER_DIR + "/static/uploads/" + dir_name + "/" + name + "results.png",
          SERVER_DIR + "/static/uploads/" + dir_name + "/" + name + "results.dot"]
    call(pr)

    # Get pdf
    from subprocess import call
    pr = ["dot", "-Tpdf", "-o", SERVER_DIR + "/static/uploads/" + dir_name + "/" + name + "results.pdf",
          SERVER_DIR + "/static/uploads/" + dir_name + "/" + name + "results.dot"]
    call(pr)


def process(uploads, tmp_path, dir_name, reaction_label, display_stoichiometry, abstract, elided_species):
    models = []

    f1 = open(os.path.join(tmp_path, uploads[0]), 'r')
    m1 = f1.read()
    models.append(m1)

    if len(uploads) > 1:
        f2 = open(os.path.join(tmp_path, uploads[1]), 'r')
        m2 = f2.read()
        models.append(m2)

    if len(uploads) > 2:
        f3 = open(os.path.join(tmp_path, uploads[2]), 'r')
        m3 = f3.read()
        models.append(m3)

    for i in range(0, len(uploads)):
        process_single(models, tmp_path, dir_name, reaction_label, display_stoichiometry, abstract, elided_species, i + 1)

    # all-in-one
    process_single(models, tmp_path, dir_name, reaction_label, display_stoichiometry, abstract, elided_species)


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        # Create a subdirectory in which to save results
        dir_name = str(max(map(lambda x: to_int(x), os.listdir(UPLOAD_FOLDER))) + 1)
        tmp_path = UPLOAD_FOLDER + "/" + dir_name
        os.mkdir(tmp_path)

        uploads = []
        for field in ['file1', 'file2', 'file3']:

            if field not in request.files:
                continue

            f = request.files[field]

            if f and allowed_file(f.filename):
                filename = secure_filename(f.filename)
                filename = str(len(
                    uploads) + 1) + "_" + filename  # prefix number to file to record order of files (which affects colors)

                f.save(os.path.join(tmp_path, filename))
                uploads.append(filename)

        if len(uploads) == 0:
            os.rmdir(tmp_path)
            flash('No files uploaded')
            return redirect(request.url)
        else:

            reaction_label = "none"
            if "reaction_labels" in request.form and request.form["reaction_labels"] in ["none", "name", "rate",
                                                                                         "name+rate"]:
                reaction_label = request.form["reaction_labels"]

            display_stoichiometry = False
            if "stoichiometry" in request.form and request.form["stoichiometry"] == "yes":
                display_stoichiometry = True

            elided_species = []
            abstract = False
            if "abstract" in request.form and request.form["abstract"] == "yes":
                abstract = True
                if "elided_species" in request.form and request.form["elided_species"]:
                    elided_species = request.form["elided_species"].split(',')

            process(uploads, tmp_path, dir_name, reaction_label, display_stoichiometry, abstract, elided_species)

            return redirect(url_for('results',
                                    filename=dir_name))

    return render_template('upload.html')


@app.route('/results/<filename>')
def results(filename):
    # look up list of files
    path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(path):
        return redirect('/tebio/upload')

    files = os.listdir(path)
    files = filter(lambda f: ".xml" in f or ".sbml" in f, files)

    return render_template('results.html', filename=filename, files=files, fileNumbers=range(1, len(files) + 1), colors=all_colors)


# Routes for tebio-fit config converter

@app.route('/tebiofit-form/', methods=['GET', 'POST'])
def upload_tebiofit_file():
    basedir = UPLOAD_FOLDER + "/tebiofit"

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
    return render_template('index.html')


@app.route('/sbml-diff')
def page_sbml_diff():
    return render_template('sbml-diff.html')


@app.route('/tebio-fit')
def page_tebio_fit():
    return render_template('tebio-fit.html')

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html')

if __name__ == "__main__":
    app.run()
