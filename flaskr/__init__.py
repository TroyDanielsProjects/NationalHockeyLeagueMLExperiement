import os
from flask import Flask
from . import index, player, coach, game, season, team, search, db

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config = True)
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py',silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    db.init_app(app)
    app.register_blueprint(index.bp)
    app.register_blueprint(player.bp)
    app.register_blueprint(coach.bp)
    app.register_blueprint(game.bp)
    app.register_blueprint(season.bp)
    app.register_blueprint(team.bp)
    app.register_blueprint(search.bp)
    
    return app