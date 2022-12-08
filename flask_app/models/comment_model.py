from flask_app.config.mysqlconnection import connectToMySQL

DATABASE = 'everyday_db'

class Comment:
    def __init__(self, data):
        # for reference
        self.id = data['id']
        # foreign keys of post and account ID
        self.post_id = data['post_id']
        self.friend_id = data['friend_id']
        # comment attributes, matches columns in db
        self.content = data['content']
        # time stamps
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        
    def __repr__(self):
        return f'<Comment ID: {self.id} , Account ID: {self.account_id}>'
    
    # BASIC CRUD
    # create comment
    @classmethod
    def create_comment(cls, data):
        query = "INSERT INTO comments ( post_id, friend_id, content, created_at, updated_at ) VALUES ( %(post_id)s, %(friend_id)s, %(content)s, NOW(), NOW() );"
        return connectToMySQL(DATABASE).query_db(query, data)

    # check if they already commented
    @classmethod
    def already_commented(cls, data):
        query = "SELECT posts.account_id FROM accounts LEFT JOIN posts ON accounts.id = posts.account_id WHERE posts.account_id = %(account_id)s"
        result = connectToMySQL(DATABASE).query_db(query,data)
        # true if they already commented today
        return len(result) > 0

    # read all comments for your post from newest --> oldest on feed
    @classmethod
    def read_all_comments(cls, data):
        query ="SELECT * FROM accounts LEFT JOIN comments ON accounts.id = comments.friend_id LEFT JOIN posts ON posts.id = comments.post_id WHERE posts.id = %(post_id)s ORDER BY comments.created_at DESC;"
        results = connectToMySQL(DATABASE).query_db(query,data)
        return results
