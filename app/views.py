import os
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort, jsonify, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app.models import UserProfile
from app.forms import LoginForm, UploadForm


app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
###
# Routing for your application.
###
@app.route('/generate_user')
def generate_users():
    sample_users = [
        {"first_name": "Sam", "last_name": "Smith", "username": "Sam12", "password": "password1"},
        {"first_name": "Damione", "last_name": "Ginger", "username": "Diamond12", "password": "password2"},
        {"first_name": "Paul", "last_name": "Gordon", "username": "Padon12", "password": "password3"}
    ]
    for user_data in sample_users:
        if not UserProfile.query.filter_by(username=user_data["username"]).first():
            user = UserProfile(**user_data)
            db.session.add(user)
    db.session.commit()
    return jsonify({"message": f"Sample users generated: {len(sample_users)}"})

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")


@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    # Instantiate your form class
    photoform = UploadForm()
    # Validate file upload on submit
    if photoform.validate_on_submit():
        # Get file data and save to your uploads folder
        photo = photoform.photo.data
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('File Saved', 'success')
        return redirect(url_for('upload')) # Update this to redirect the user to a route that displays all uploaded image files

    return render_template('upload.html', form=photoform)

@app.route('/')
def get_upload_images():
    images = []
    image_extensions = ('.jpg','.png') 
    up_path = app.config['UPLOAD_FOLDER']
    for subdir, dirs, files in os.walk(up_path): 
        for file in files: 
            if file.lower().endswith(image_extensions):
                images.append(file) 
    return images

@app.route('/uploads/<filename>')
def get_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/file')
@login_required
def file():
    images = get_upload_images()
    return(render_template('files.html', images=images))

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    # change this to actually validate the entire form submission
    # and not just one field
    if form.validate_on_submit():
        # Get the username and password values from the form.
        username = form.username.data
        password = form.password.data
        user = UserProfile.query.filter_by(username=username).first()
        # Using your model, query database for a user based on the username
        # and password submitted. Remember you need to compare the password hash.
        # You will need to import the appropriate function to do so.
        # Then store the result of that query to a `user` variable so it can be
        # passed to the login_user() method below.

        # Gets user id, load into session
        if user and user.check_password(password):
            login_user(user)
        # Remember to flash a message to the user
            flash('Logged in successfully.')
            next = request.args.get('next')
            return redirect(next or url_for('upload'))  # The user should be redirected to the upload form instead
        else:
            flash("Invalid username or password")
    return render_template("login.html", form=form)

# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Sucessfully logged out")
    return redirect(url_for('home'))

###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
