import os
from flask import Flask, request, render_template, g, redirect, Response, abort, Blueprint
from sqlalchemy import *
from sqlalchemy.pool import NullPool

bp = Blueprint('team', __name__)


teams_query = """
SELECT * 
FROM team;
"""

team_query = """
SELECT * 
FROM team t
WHERE t.teamid = :id;
"""

team_seasons_query = """
SELECT DISTINCT h.year, c.name, v.name, v.city, v.state, v.capacity, c.coachid
FROM hosts h, venue v, game g, coach c NATURAL JOIN coaches cs
WHERE h.teamid = :id AND v.venueid = h.venueid AND g.year = h.year AND (g.hometeamid = h.teamid OR g.awayteamid = h.teamid) AND
cs.year = g.year AND cs.teamid = h.teamid
ORDER BY h.year DESC;
"""


@bp.route('/teams')
def teams():
    cursor = g.conn.execute(text(teams_query))
    g.conn.commit()
    teams = []
    for result in cursor:
        teams.append(result)

    return render_template("teams/teams.html", teams = teams)

@bp.route('/teams/<int:id>')
def team(id):
    params_dict = {"id":id}
    cursor = g.conn.execute(text(team_seasons_query),params_dict)
    g.conn.commit()
    seasons = []
    for result in cursor:
        seasons.append(result)

    cursor = g.conn.execute(text(team_query),params_dict)
    g.conn.commit()
    team = []
    for result in cursor:
        team.append(result)

    return render_template("teams/team.html", team=team[0], seasons=seasons)
