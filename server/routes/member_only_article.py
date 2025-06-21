# routes/member_only_article.py
from flask.views import MethodView
from flask import jsonify
from flask_login import current_user
from models import Article

class MemberOnlyArticle(MethodView):  # Note: Inherits from MethodView
    def get(self, id):
        if not current_user.is_authenticated:
            return {"message": "Unauthorized"}, 401
        article = Article.query.filter_by(id=id, is_member_only=True).first()
        if not article:
            return {"message": "Article not found"}, 404
        return jsonify(article.to_dict())