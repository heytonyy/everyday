from flask_app.config.mysqlconnection import connectToMySQL

DATABASE = 'everyday_db'

class Post:
    def __init__(self, data):
        # for reference
        self.id = data['id']
        # account ID of the post
        self.account_id = data['account_id']
        # post attributes, matches columns in db
        self.image = data['image']
        self.description = data['description']
        # time stamps
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        
    def __repr__(self):
        return f'<Post ID: {self.id} , Account ID: {self.account_id}>'
    
    # BASIC CRUD
    # create post
    @classmethod
    def create_post(cls, data):
        query = "INSERT INTO posts ( account_id, image, description, created_at, updated_at ) VALUES ( %(account_id)s, %(image)s, %(description)s, NOW(), NOW() );"
        return connectToMySQL(DATABASE).query_db(query, data)

    # read post
    @classmethod
    def read_post(cls, data):
        query = "SELECT posts.id, image, description FROM accounts LEFT JOIN posts ON accounts.id = posts.account_id WHERE posts.account_id = %(account_id)s"
        result = connectToMySQL(DATABASE).query_db(query,data)
        return result[0]

    # boolean, check if they posted already
    @classmethod
    def already_posted(cls, data):
        query = "SELECT image FROM accounts LEFT JOIN posts ON accounts.id = posts.account_id WHERE posts.account_id = %(account_id)s"
        result = connectToMySQL(DATABASE).query_db(query,data)
        # true if they already posted today
        return len(result) > 0

    # read all posts (not including your own), if order from newest --> oldest on feed
    @classmethod
    def read_all_posts(cls, data):
        query = "SELECT * FROM posts JOIN accounts ON posts.account_id = accounts.id WHERE posts.account_id != %(account_id)s ORDER BY posts.created_at DESC"
        results = connectToMySQL(DATABASE).query_db(query,data)
        return results
