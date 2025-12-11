from flask import Blueprint

games_bp = Blueprint('games', __name__, url_prefix='/games', template_folder='templates')

from . import routes

