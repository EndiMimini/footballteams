from flask_app.config.mysqlconnection import connectToMySQL
import re	# the regex module
from flask import flash
# create a regular expression object that we'll use later   
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 


class User:
    db_name = 'tvshows'
    def __init__( self , data ):
        self.id = data['id']
        self.username = data['username']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']


    @classmethod
    def create(cls, data):
        query = 'INSERT INTO users (username, email, password, verificationCode) VALUES ( %(username)s, %(email)s, %(password)s, %(verificationCode)s);'
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def getAllUsers(cls):
        query = "SELECT id, username, email FROM users;"
        results = connectToMySQL(cls.db_name).query_db(query)
        users = []
        if results:
            for eachUser in results:
                users.append(eachUser)
        return users
    
    @classmethod
    def get_user_by_id(cls, data):
        query = "SELECT * FROM users where id = %(id)s;"
        results =  connectToMySQL(cls.db_name).query_db(query, data)
        if results:
            return results[0]
        return False
    
    @classmethod
    def get_user_by_email(cls, data):
        query = "SELECT * FROM users where email = %(email)s;"
        results =  connectToMySQL(cls.db_name).query_db(query, data)
        if results:
            return results[0]
        return False
    
    @classmethod
    def updateVerificationCode(cls, data):
        query = "UPDATE users set verificationCode = %(verificationCode)s where id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def activateAccount(cls, data):
        query = "UPDATE users set isVerified = 1 where id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def delete_user(cls, data):
        query = "DELETE FROM USERS WHERE id= %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    

    @classmethod
    def update_user(cls, data):
        query = "UPDATE users set username = %(username)s, email = %(email)s WHERE id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @staticmethod
    def validate_user(data):
        is_valid = True
        # test whether a field matches the pattern
        if not EMAIL_REGEX.match(data['email']): 
            flash("Invalid email address!", 'emailRegister')
            is_valid = False
        if len(data['username']) < 3:
            flash("Username should be at least 3 characters!", 'usernameRegister')
            is_valid = False
        if len(data['password']) < 8:
            flash("Password should be at least 8 characters!", 'passwordRegister')
            is_valid = False
        if data['password'] != data['confirmpassword']:
            flash("Passwords should match!", 'confirmPasswordRegister')
            is_valid = False
        return is_valid