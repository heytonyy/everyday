from flask_app import app, render_template, redirect, request, session, flash, \
    allowed_file, secure_filename, os, make_unique, AVATAR_ABSOLUTE_PATH, RELATIVE_PATH
from flask_app.models.account_model import Account

# account route
@app.get('/settings')
def show_account_settings():
    alldata = Account.read_by_id(data={'id':session['user_id']})
    user_info = {
        'id': session['user_id'],
        'username': alldata.username,
        'first_name': alldata.first_name,
        'last_name': alldata.last_name,
        'email': alldata.email,
        'avatar': alldata.avatar,
        'bio': alldata.bio
    }
    return render_template('settings.html', user_info=user_info)

# process update account info (text form)
@app.post('/update_info')
def update_account_info():
    alldata = Account.read_by_id(data={'id':session['user_id']})
    current_username = alldata.username
    if current_username == request.form['username']:
        if not Account.validate_same_username(request.form):
            return redirect('/settings')
    else:
        if not Account.validate_different_username(request.form):
            return redirect('/settings')
    data = {
        'id': session['user_id'],
        'username': request.form['username'],
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email'],
        'avatar': alldata.avatar,
        'bio': request.form['bio']
    }
    Account.update_account(data)
    return redirect('/settings')

# process update avatar (file form)
@app.route('/update_avatar', methods=['GET', 'POST'])
def update_avatar():
    alldata = Account.read_by_id(data={'id':session['user_id']})
    current_avatar = alldata.avatar

    if request.method == 'POST' and ('file' in request.files):
        file = request.files['file']
        # validate if the file was blank
        if file.filename == '':
            flash('File uploaded was empty.', 'no_photo')
            return redirect(request.url)
        # file is acceptable type and exists
        if file and allowed_file(file.filename):
            og_filename = secure_filename(file.filename)
            # makes sure new upload has a unique name
            unique_filename = make_unique(og_filename)
            file.save(os.path.join(AVATAR_ABSOLUTE_PATH, unique_filename))
            relpath = os.path.relpath(AVATAR_ABSOLUTE_PATH, RELATIVE_PATH)
            image_path = f'/{relpath}/{unique_filename}'
            current_avatar = image_path

    data = {
        'id': session['user_id'],
        'username': alldata.username,
        'first_name': alldata.first_name,
        'last_name': alldata.last_name,
        'email': alldata.email,
        'avatar': current_avatar,
        'bio': alldata.bio
    }
    Account.update_account(data)
    return redirect('/settings')

