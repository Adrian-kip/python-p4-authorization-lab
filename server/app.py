#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_login import LoginManager
from flask.views import MethodView

from models import db, Article, User
from routes.member_only_articles import MemberOnlyIndex
from routes.member_only_article import MemberOnlyArticle

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

# Register MethodView routes for member-only content
app.add_url_rule('/member-only-articles',
                view_func=MemberOnlyIndex.as_view('member_only_index'))
app.add_url_rule('/member-only-articles/<int:id>',
                view_func=MemberOnlyArticle.as_view('member_only_article'))

# Regular Flask-RESTful resources
class ClearSession(Resource):
    def delete(self):
        session['page_views'] = None
        session['user_id'] = None
        return {}, 204

class IndexArticle(Resource):
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200  # Flask-RESTful handles jsonification

class ShowArticle(Resource):
    def get(self, id):
        article = Article.query.filter_by(id=id).first()
        if not article:
            return {'message': 'Article not found'}, 404

        if not session.get('user_id'):
            session['page_views'] = session.get('page_views', 0) + 1
            if session['page_views'] > 3:
                return {'message': 'Maximum pageview limit reached'}, 401
        return article.to_dict(), 200

class Login(Resource):
    def post(self):
        username = request.get_json().get('username')
        user = User.query.filter_by(username=username).first()
        if user:
            session['user_id'] = user.id
            return user.to_dict(), 200
        return {'message': 'Invalid credentials'}, 401

class Logout(Resource):
    def delete(self):
        session['user_id'] = None
        return {}, 204

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user:
                return user.to_dict(), 200
        return {'message': 'Not logged in'}, 401

# Register all Flask-RESTful resources
api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')

if __name__ == '__main__':
    app.run(port=5555, debug=True)