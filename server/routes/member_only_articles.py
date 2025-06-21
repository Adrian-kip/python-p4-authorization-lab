# routes/member_only_articles.py
from flask.views import MethodView
from flask import jsonify
from flask_login import current_user
from models import Article

class MemberOnlyIndex(MethodView):  # Note: Inherits from MethodView
    def get(self):
        if not current_user.is_authenticated:
            return {"message": "Unauthorized"}, 401
        articles = Article.query.filter_by(is_member_only=True).all()
        return jsonify([article.to_dict() for article in articles])