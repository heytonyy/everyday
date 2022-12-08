from flask_app import flash
from flask_app.config.mysqlconnection import connectToMySQL
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
# 8 character minimum, 1 special character, 1 number, 1 uppercase
PW_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')

DATABASE = 'everyday_db'

class Account:
    def __init__(self, data):
        # for reference
        self.id = data['id']
        # account attributes, matches columns in db
        self.username = data['username']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.avatar = data['avatar']
        self.bio = data['bio']
        # time stamps
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        # list of other data with account as primary key
        self.friend_list = []
        self.comment_list = []
        
    def __repr__(self):
        return f'<Account ID: {self.id} , Username: {self.username}>'
    
    # search field query by first name
    @classmethod
    def search_by_first_name(cls, data):
        # only need id, username, first_name, last_name, avatar, bio
        query = '''SELECT id, username, first_name, last_name, avatar, bio FROM accounts WHERE (first_name LIKE %(search)s OR username LIKE %(search)s OR last_name LIKE %(search)s) AND id!=%(id)s'''
        results = connectToMySQL(DATABASE).query_db(query, data)
        return results

    # BASIC CRUD
    # create account
    @classmethod
    def create_account(cls, data):
        # save form data to DB, hash pw before using this method
        query = "INSERT INTO accounts ( username, first_name, last_name, email, password, created_at, updated_at ) VALUES ( %(username)s, %(first_name)s, %(last_name)s, %(email)s, %(password)s, NOW(), NOW() );"
        return connectToMySQL(DATABASE).query_db(query, data)

    # create - add friend
    @classmethod
    def add_friend(cls, data):
        query = "SELECT * FROM friends WHERE account_id = %(account_id)s AND friend_id = %(friend_id)s;"
        result = connectToMySQL(DATABASE).query_db(query, data)
        if len(result) > 0:
            return True
        query = "INSERT INTO friends ( account_id, friend_id, created_at, updated_at ) VALUES ( %(account_id)s, %(friend_id)s, NOW(), NOW() );"
        return connectToMySQL(DATABASE).query_db(query, data)

    # read - all my friends
    @classmethod
    def read_my_friends(cls, data):
        query = "SELECT * FROM accounts LEFT JOIN friends ON accounts.id = friends.friend_id WHERE account_id=%(account_id)s"
        results = connectToMySQL(DATABASE).query_db(query, data)
        friends = []
        for dict in results:
            friend_data = {
                'id': dict['id'],
                'username': dict['username'],
                'first_name': dict['first_name'],
                'last_name': dict['last_name'],
                'avatar': dict['avatar'],
                'bio': dict['bio']
            }
            friends.append(friend_data)
        return friends

    # delete - remove friend
    @classmethod
    def remove_friend(cls, data):
        query = "DELETE FROM friends WHERE account_id = %(account_id)s AND friend_id = %(friend_id)s"
        return connectToMySQL(DATABASE).query_db(query, data)

    #read - by ID in DB
    @classmethod
    def read_by_id(cls, data):
        query = "SELECT * FROM accounts WHERE id=%(id)s"
        results = connectToMySQL(DATABASE).query_db(query, data)
        return Account(results[0])

    # read all accounts
    @classmethod
    def read_all_accounts(cls, data):
        query = "SELECT id, username, first_name, last_name, avatar, bio FROM accounts WHERE id != %(id)s"
        results = connectToMySQL(DATABASE).query_db(query, data)
        accounts = []
        for dict in results:
            friend_data = {
                'id': dict['id'],
                'username': dict['username'],
                'first_name': dict['first_name'],
                'last_name': dict['last_name'],
                'avatar': dict['avatar'],
                'bio': dict['bio']
            }
            accounts.append(friend_data)
        return accounts

    # update account info
    @classmethod
    def update_account(cls, data):
        query = "UPDATE accounts SET username = %(username)s, first_name = %(first_name)s, last_name = %(last_name)s, email = %(email)s, avatar = %(avatar)s, bio = %(bio)s WHERE id=%(id)s"
        connectToMySQL(DATABASE).query_db(query, data)
        return True
    
    # read - by username in DB
    @classmethod
    def read_by_username(cls, data):
        query = "SELECT * FROM accounts WHERE username = %(username)s;"
        result = connectToMySQL(DATABASE).query_db(query,data)
        # Didn't find a matching user
        if len(result) < 1:
            return False
        return Account(result[0])

    # returns true if email already in DB
    @classmethod
    def is_email_taken(cls, data):
        query = "SELECT email FROM accounts WHERE email = %(email)s;"
        result = connectToMySQL(DATABASE).query_db(query,data)
        # Didn't find a matching user
        return len(result) > 0

    # returns true if username already in DB
    @classmethod
    def is_username_taken(cls, data):
        query = "SELECT username FROM accounts WHERE username = %(username)s;"
        result = connectToMySQL(DATABASE).query_db(query,data)
        # Didn't find a matching user
        return len(result) > 0

    #validate account for registration
    @staticmethod
    def validate_reg(form):
        is_valid = True
        if Account.is_username_taken(data={'username':form['username']}):
            flash('Username has been already taken.', 'username_taken')
            is_valid = False
        if len(form['first_name']) < 2:
            flash('First name must be at least 2 characters.', 'first_name')
            is_valid = False
        if len(form['last_name']) < 2:
            flash('Last name must be at least 2 characters.', 'last_name')
            is_valid = False
        if not EMAIL_REGEX.match(form['email']):
            flash('Not a valid email.', 'email')
            is_valid = False
        if Account.is_email_taken(data={'email':form['email']}):
            flash('Email has been already taken.', 'email_taken')
            is_valid = False
        if not PW_REGEX.match(form['password']):
            flash('Password must have a minimum of 8 characters, which includes at least 1 uppercase, 1 number, and 1 special character.', 'password')
            is_valid = False
        if form['password'] != form['password_confirm']:
            flash('Password and Confirm Password must match.', 'password_match')
            is_valid = False
        return is_valid

    #validate account for update, same username
    @staticmethod
    def validate_same_username(form):
        is_valid = True
        if len(form['first_name']) < 2:
            flash('First name must be at least 2 characters.', 'first_name')
            is_valid = False
        if len(form['last_name']) < 2:
            flash('Last name must be at least 2 characters.', 'last_name')
            is_valid = False
        if not EMAIL_REGEX.match(form['email']):
            flash('Not a valid email.', 'email')
            is_valid = False
        return is_valid

    #validate account for update, different username
    @staticmethod
    def validate_different_username(form):
        is_valid = True
        if Account.is_username_taken(data={'username':form['username']}):
            flash('Username has been already taken.', 'username_taken')
            is_valid = False
        if len(form['first_name']) < 2:
            flash('First name must be at least 2 characters.', 'first_name')
            is_valid = False
        if len(form['last_name']) < 2:
            flash('Last name must be at least 2 characters.', 'last_name')
            is_valid = False
        if not EMAIL_REGEX.match(form['email']):
            flash('Not a valid email.', 'email')
            is_valid = False
        return is_valid