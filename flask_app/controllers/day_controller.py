from flask_app import app, render_template, redirect, request, session, flash, \
     secure_filename, os, allowed_file, POST_ABSOLUTE_PATH, RELATIVE_PATH, make_unique
from flask_app.models.account_model import Account
from flask_app.models.post_model import Post
from flask_app.models.comment_model import Comment
from datetime import datetime

# dashboard - all days
@app.get('/all_days')
def all_days():
    # page data
    today = datetime.now()
    formated_today = today.strftime("%B %d, %Y")
    data = {'id': session['user_id']}
    alldata = Account.read_by_id(data)
    friends = Account.read_my_friends(data={'account_id':session['user_id']})
    user_info = {
        'id': session['user_id'],
        'username': alldata.username,
        'first_name': alldata.first_name,
        'last_name': alldata.last_name,
        'friends_list': friends,
        'avatar': alldata.avatar
    }
    all_posts = Post.read_all_posts(data={'account_id':session['user_id']})
    my_feed = []
    for post in all_posts:
        # i dont know why this works but thank you stack overflow <3
        if any(d['id'] == post['account_id'] for d in user_info['friends_list']):
            my_feed.append(post)
    return render_template('all_days.html', today=today, date=formated_today, my_feed=my_feed, user_info=user_info)

# my_day route
@app.get('/my_day')
def my_day():
    #page data
    today = datetime.now()
    formated_today = today.strftime("%B %d, %Y")
    alldata = Account.read_by_id(data={'id':session['user_id']})
    # check if they posted, and if so read DB
    post_check = Post.already_posted(data={'account_id':session['user_id']})
    if post_check:
        post_info = Post.read_post(data={'account_id':session['user_id']})
        comments = Comment.read_all_comments(data={'post_id': post_info['id']})
    else:
        post_info = None
        comments = None
    user_info = {
        'id': session['user_id'],
        'username': alldata.username,
        'first_name': alldata.first_name,
        'last_name': alldata.last_name,
        'post_check': post_check,
        'avatar': alldata.avatar
    }
    return render_template('my_day.html', today=today, date=formated_today, user_info=user_info, post_info=post_info, comments=comments)

# process - create my_day post
@app.route('/new_post/<int:user_id>', methods=['GET', 'POST'])
def create_post(user_id):
    if request.method == 'POST':
        # validate if no file choses
        if 'file' not in request.files:
            flash('No file uploaded.', 'no_photo')
            return redirect(request.url)
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
            file.save(os.path.join(POST_ABSOLUTE_PATH, unique_filename))
            relpath = os.path.relpath(POST_ABSOLUTE_PATH, RELATIVE_PATH)
            image_path = f'/{relpath}/{unique_filename}'
            data = {
                'account_id': user_id,
                'image': image_path,
                'description': request.form['description']
            }
            Post.create_post(data)
            return redirect('/my_day')

# process comment on post
@app.post('/add_comment/<int:user_id>/<int:post_id>')
def add_comment(user_id, post_id):
    data = {
        'post_id': post_id,
        'friend_id': user_id,
        'content': request.form['content']
    }
    Comment.create_comment(data)
    return redirect('/all_days')