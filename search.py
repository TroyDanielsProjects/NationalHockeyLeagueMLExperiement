import os
from flask import Flask, request, render_template, g, redirect, Response, abort, Blueprint
from sqlalchemy import *
from sqlalchemy.pool import NullPool

bp = Blueprint('search', __name__)

search_players_query = """
SELECT p.first_name, p.last_name, p.playerid
FROM player p
WHERE p.first_name LIKE :search OR p.last_name LIKE :search;
"""

search_coaches_query = """
SELECT c.name, c.coachid
FROM coach c
WHERE c.name LIKE :search
"""

search_teams_query = """
SELECT t.name, t.teamid
FROM team t
WHERE t.name LIKE :search
"""

@bp.route('/search', methods=['POST'])
def search():
    search = request.form['search']
    params_dict = {"search" : f"%{search}%"}

    cursor = g.conn.execute(text(search_players_query), params_dict)
    g.conn.commit()
    players = []
    for result in cursor:
        players.append(result)

    cursor = g.conn.execute(text(search_coaches_query), params_dict)
    g.conn.commit()
    coaches = []
    for result in cursor:
        coaches.append(result)

    cursor = g.conn.execute(text(search_teams_query), params_dict)
    g.conn.commit()
    teams = []
    for result in cursor:
        teams.append(result)

    return render_template("search/search.html", players=players, coaches=coaches, teams=teams)