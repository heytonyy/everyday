from flask_app import app, render_template, redirect, request, session
from flask_app.models.account_model import Account
from datetime import date
import random
from pprint import pprint

# find friends route
@app.get('/find_friends')
def find_friends():
    #page data
    today = date.today()
    formated_today = today.strftime("%B %d, %Y")
    alldata = Account.read_by_id(data={'id':session['user_id']})
    user_info = {
        'id': session['user_id'],
        'username': alldata.username,
        'first_name': alldata.first_name,
        'last_name': alldata.last_name,
        'avatar': alldata.avatar
    }
    # my friends
    friends = Account.read_my_friends(data={'account_id':session['user_id']})
    # all accounts
    all_accounts = Account.read_all_accounts(data={'id':session['user_id']})
    other_users = []
    for account in all_accounts:
        if account not in friends:
            other_users.append(account)
    random.shuffle(other_users)

    discover = []
    for i in range(5):
        discover.append(other_users[i])

    return render_template('find_friends.html', date=formated_today, user_info=user_info, discover=discover, friends=friends)

# process add friend
@app.get('/follow/<int:friend_id>')
def add_friend(friend_id):
    data = {
        'account_id': session['user_id'],
        'friend_id': friend_id,
    }
    Account.add_friend(data)
    return redirect('/find_friends')

# process unfollow friend
@app.get('/unfollow/<int:friend_id>')
def remove_friend(friend_id):
    data = {
        'account_id': session['user_id'],
        'friend_id': friend_id,
    }
    Account.remove_friend(data)
    return redirect('/find_friends')

# process search friend
@app.post('/search')
def search_friend():
    search_query = request.form['search']
    query = f'{search_query}%%'
    data = {
        'id': session['user_id'],
        'search': query
    }
    search_results = Account.search_by_first_name(data)
    friends_list = Account.read_my_friends(data={'account_id':session['user_id']})
    friends = []
    new_friends = []
    for account in search_results:
        if account not in friends_list:
            new_friends.append(account)
        else:
            friends.append(account)

    session['friends'] = friends
    session['new_friends'] = new_friends
    return redirect('/search_results')

# show results from search
@app.get('/search_results')
def search_results():
    alldata = Account.read_by_id(data={'id':session['user_id']})
    user_info = {
        'id': session['user_id'],
        'username': alldata.username,
        'first_name': alldata.first_name,
        'last_name': alldata.last_name,
        'avatar': alldata.avatar
    }
    return render_template('search_friends.html', user_info=user_info)