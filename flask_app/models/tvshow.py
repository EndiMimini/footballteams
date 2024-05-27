from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash


class Show:
    db_name = 'tvshows'
    def __init__( self , data ):
        self.id = data['id']



    @classmethod
    def create(cls, data):
        query = 'INSERT INTO tvshows (name, network, releaseDate, description, user_id, image) VALUES ( %(name)s, %(network)s, %(releaseDate)s, %(description)s, %(user_id)s, %(image)s);'
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def getAlltvshows(cls):
        query = "SELECT * FROM tvshows;"
        results = connectToMySQL(cls.db_name).query_db(query)
        tvshows = []
        if results:
            for show in results:
                tvshows.append(show)
        return tvshows
    
    @classmethod
    def get_logged_tvshows(cls,data):
        query = "SELECT * FROM tvshows where user_id = %(id)s;"
        results = connectToMySQL(cls.db_name).query_db(query,data)
        tvshows = []
        if results:
            for show in results:
                tvshows.append(show)
        return tvshows
    

    
    
    @classmethod
    def get_show_by_id(cls, data):
        query = "SELECT * FROM tvshows left join users on tvshows.user_id = users.id where tvshows.id = %(tvshow_id)s;"
        results =  connectToMySQL(cls.db_name).query_db(query, data)
        if results:
            return results[0]
        return False
    
    
    @classmethod
    def delete_show(cls, data):
        query = "DELETE FROM tvshows WHERE id= %(tvshow_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    

    @classmethod
    def update_show(cls, data):
        query = "UPDATE tvshows set name = %(name)s, releaseDate = %(releaseDate)s, network = %(network)s, description = %(description)s WHERE id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def delete_users_show(cls, data):
        query = "delete from tvshows where tvshows.user_id = %(user_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)

    @classmethod
    def addLike(cls,data):
        query = "INSERT INTO likes (user_id, tvshow_id) VALUES (%(id)s, %(tvshow_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def removeLike(cls,data):
        query = "DELETE FROM likes where tvshow_id = %(tvshow_id)s and user_id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)

    
    @classmethod
    def get_likers(cls, data):
        query = "SELECT user_id from likes where likes.tvshow_id = %(tvshow_id)s;"
        results = connectToMySQL(cls.db_name).query_db(query, data)
        likers = []
        if results:
            for person in results:
                likers.append(person['user_id'])
        return likers
    
    @classmethod
    def get_likers_info(cls, data):
        query = "SELECT * from likes left join users on likes.user_id = users.id where likes.tvshow_id = %(tvshow_id)s;"
        results = connectToMySQL(cls.db_name).query_db(query, data)
        likers = []
        if results:
            for person in results:
                likers.append(person)
        return likers



    @classmethod
    def delete_all_likes(cls,data):
        query = "DELETE FROM likes where tvshow_id = %(tvshow_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)

    @staticmethod
    def validate_show(data):
        is_valid = True
        # test whether a field matches the pattern
        if len(data['name']) < 3:
            flash("Tv show should be at least 3 characters!", 'name')
            is_valid = False
        if not data['releaseDate']:
            flash("The release date is required!", 'releaseDate')
            is_valid = False
        if len(data['network']) < 3:
            flash("The network should be at least 3 characters!", 'network')
            is_valid = False
        if len(data['description']) < 3:
            flash("The description should be at least 3 characters!", 'description')
            is_valid = False
        return is_valid
    
