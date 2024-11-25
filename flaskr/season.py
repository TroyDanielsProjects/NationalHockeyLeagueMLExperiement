import os
from flask import Flask, request, render_template, g, redirect, Response, abort, Blueprint
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from .db import get_db

bp = Blueprint('season', __name__)

current_seasons_query = """
SELECT s.year, s.start_date, s.end_date
FROM season s
WHERE s.year = :year;
"""

min_max_season_query = """
WITH seasons_with_games (year) AS (
SELECT s.year
FROM season s, game g
WHERE s.year = g.year
GROUP BY s.year
HAVING count(*) > 0
)
SELECT MAX(s.year), MIN(s.year)
FROM seasons_with_games s;
"""

teams_in_season_query = """
WITH totalwins (id, year, wincount) AS (
SELECT t.teamid, g.year, COUNT(*)
FROM team t, game g
WHERE (t.teamid = g.hometeamid AND g.homescore >= g.awayscore) OR (t.teamid = g.awayteamid AND g.awayscore >= g.homescore)
GROUP BY t.teamid, g.year
),
gamesplayed (id, year, gamesplayed, name) AS (
SELECT t.teamid, g.year, count(*), t.name
FROM game g, team t
WHERE g.hometeamid = t.teamid OR g.awayteamid = t.teamid
GROUP BY t.teamid, t.name, g.year
)
SELECT g.name, g.id, COALESCE(t.wincount,0) as wins, g.gamesplayed
FROM gamesplayed g LEFT JOIN totalwins t ON
g.year = t.year AND g.id = t.id
WHERE g.year = :year
ORDER BY wins DESC;
"""

team_in_season_query = """
WITH totalwins (id, year, wincount) AS (
SELECT t.teamid, g.year, COUNT(*)
FROM team t, game g
WHERE (t.teamid = g.hometeamid AND g.homescore >= g.awayscore) OR (t.teamid = g.awayteamid AND g.awayscore >= g.homescore)
GROUP BY t.teamid, g.year
),
gamesplayed (id, year, gamesplayed, name) AS (
SELECT t.teamid, g.year, count(*), t.name
FROM game g, team t
WHERE g.hometeamid = t.teamid OR g.awayteamid = t.teamid
GROUP BY t.teamid, t.name, g.year
)
SELECT g.name, g.id, COALESCE(t.wincount,0) as wins, g.gamesplayed, g.year
FROM gamesplayed g LEFT JOIN totalwins t ON
g.year = t.year AND g.id = t.id
WHERE g.year = :year AND g.id = :teamid
ORDER BY wins DESC;
"""

team_played_games_in_season_query = """
SELECT t1.name, t2.name, g.homescore, g.awayscore, g.date, t1.teamid, t2.teamid, g.gameid
FROM game g, team t1, team t2
WHERE (g.awayteamid = :teamid OR g.hometeamid = :teamid) AND g.year = :year AND t1.teamid = g.hometeamid AND t2.teamid = g.awayteamid
"""

team_roster_in_season = """
SELECT p.first_name, p.last_name, p.position, p.number, p.playerid
FROM plays_for pf, player p
WHERE pf.year = :year AND pf.teamid = :teamid AND pf.playerid = p.playerid
"""

@bp.route('/seasons', methods=['GET','POST'])
def seasons():
    db = get_db()
    cursor = db.execute(min_max_season_query)
    db.commit()
    max_min_years = []
    for result in cursor:
        max_min_years.append(result)
    print(max_min_years)
    max_year = max_min_years[0][0]
    min_year = max_min_years[0][1]
    years=[]
    for year in range(min_year, max_year+1):
        years.append(year)

    if request.method == 'GET':
        params_dict = {"year": max_year}
        cursor = db.execute(current_seasons_query, params_dict)
        db.commit()
        current_season = []
        for result in cursor:
            current_season.append(result)

        cursor = db.execute(teams_in_season_query, params_dict)
        db.commit()
        teams = []
        for result in cursor:
            teams.append(result)
        return render_template("season/seasons.html", season = current_season[0], years=years, teams=teams)
    
    else:
        year = request.form['season_select']
        params_dict = {"year": year}
        cursor = db.execute(current_seasons_query, params_dict)
        db.commit()
        current_season = []
        for result in cursor:
            current_season.append(result)

        cursor = db.execute(teams_in_season_query, params_dict)
        db.commit()
        teams = []
        for result in cursor:
            teams.append(result)
        return render_template("season/seasons.html", season = current_season[0], years=years, teams=teams)
   
@bp.route('/seasons/<int:year>')
def season(year):
    db = get_db()
    cursor = db.execute(min_max_season_query)
    db.commit()
    max_min_years = []
    for result in cursor:
        max_min_years.append(result)
    max_year = max_min_years[0][0]
    min_year = max_min_years[0][1]
    years=[]
    for year in range(min_year, max_year+1):
        years.append(year)

    params_dict = {"year": year}
    cursor = db.execute(current_seasons_query, params_dict)
    db.commit()
    current_season = []
    for result in cursor:
        current_season.append(result)

    cursor = db.execute(teams_in_season_query, params_dict)
    db.commit()
    teams = []
    for result in cursor:
        teams.append(result)
    return render_template("season/seasons.html", season = current_season[0], years=years, teams=teams)


@bp.route('/seasons/<int:year>/<int:teamid>')
def team_in_season(year, teamid):
    db = get_db()
    params_dict = {"year": year, "teamid" :teamid}
    cursor = db.execute(team_in_season_query, params_dict)
    db.commit()
    team = []
    for result in cursor:
        team.append(result)

    cursor = db.execute(team_played_games_in_season_query, params_dict)
    db.commit()
    games = []
    for result in cursor:
        games.append(result)

    cursor = db.execute(team_roster_in_season, params_dict)
    db.commit()
    players = []
    for result in cursor:
        players.append(result)

    return render_template("season/team_in_season.html", team=team[0], games=games, players=players)