import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///photo_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

uploads_dir = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(uploads_dir, exist_ok=True)
db = SQLAlchemy(app)

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)

@app.route('/')
def index():
    photos = Photo.query.all()
    return render_template('index.html', photos=photos)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_photo = Photo(filename=filename, description=request.form.get('description'))
            db.session.add(new_photo)
            db.session.commit()
            return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/edit/<int:photo_id>', methods=['GET', 'POST'])
def edit(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if request.method == 'POST':
        photo.description = request.form.get('description')
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', photo=photo)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

from flask import redirect, url_for

@app.route('/delete_photo/<int:photo_id>', methods=['POST'])
def delete_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    db.session.delete(photo)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
