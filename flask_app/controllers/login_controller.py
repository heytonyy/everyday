from flask_app import app, bcrypt, render_template, redirect, request, session, flash
from flask_app.models.account_model import Account

# main route
@app.get('/')
def index():
    return render_template('login.html')

# create account route
@app.get('/create_account')
def create_account():
    return render_template('create_account.html')

# process create account route
@app.post('/make_user')
def make_account():
    if not Account.validate_reg(request.form):
        return redirect('/')
    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    data = {
        'username': request.form['username'],
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email'],
        'password': pw_hash
    }
    Account.create_account(data)
    return redirect('/')

# login route
@app.post('/login')
def sign_in():
    data = { 'username': request.form['username'] }
    user_in_db = Account.read_by_username(data)
    if not user_in_db:
        flash('Invalid Credentials', 'invalid')
        return redirect('/')
    if not bcrypt.check_password_hash(user_in_db.password, request.form['password']):
        flash('Invalid Credentials', 'invalid')
        return redirect('/')
    session['user_id'] = user_in_db.id
    return redirect('/all_days')

# logout route
@app.get('/logout')
def logout():
    session.clear()
    return redirect('/')