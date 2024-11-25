import os
from flask import Flask, request, render_template, g, redirect, Response, abort, Blueprint
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from .db import get_db

# create a blueprint for the main page
bp = Blueprint('index', __name__)

# have to do a full outer join here because we dont want to throw away a teams home wins in a year
# if they dont have any away wins that year. But NULL values screw this up so need to use COALESCE.
top_coaches_query = """
WITH homewins (id, year, wincount) AS (
SELECT g.hometeamid, g.year, count(*)
FROM game g
WHERE g.homescore > g.awayscore
GROUP BY g.hometeamid, g.year
),
awaywins (id, year, wincount) AS (
SELECT g.awayteamid, g.year, count(*)
FROM game g
WHERE g.homescore < g.awayscore
GROUP BY g.awayteamid, g.year
),
coachteam (name, teamid, year, coachid) AS (
SELECT DISTINCT c.name, coaches.teamid, coaches.year, coaches.coachid
FROM coach c NATURAL JOIN coaches
)
SELECT c.name as coach_name, sum(COALESCE(h.wincount,0)+COALESCE(a.wincount,0)) as wins, c.coachid
FROM coachteam c, homewins h FULL OUTER JOIN awaywins a
ON h.id = a.id and h.year = a.year
WHERE (c.teamid = a.id OR c.teamid = h.id) AND (c.year = h.year OR c.year = a.year)
GROUP BY c.coachid, c.name
ORDER BY wins DESC
LIMIT 10;"""


most_recent_games_query = """
SELECT g.date, g.homescore, g.awayscore, t1.name, t2.name, g.gameid
FROM Game g, Team t1, Team t2
WHERE g.hometeamid = t1.teamid and g.awayteamid = t2.teamid
ORDER BY g.date DESC
LIMIT 5;
"""

top_players_query = """
SELECT p.first_name, p.last_name, sum(ss.goals) + sum(ss.assists) as points, p.playerid
FROM Skater_Stats_In_Game ssig, Skater_stats ss, player p
WHERE ssig.skstatsid = ss.skstatsid and ssig.playerid = p.playerid
GROUP BY p.playerid, p.first_name, p.last_name
ORDER BY points DESC
LIMIT 10;
"""

upcoming_games_query = """"""


@bp.route('/')
def index():
    db = get_db()
    cursor = db.execute(text(top_coaches_query))
    db.commit()
    coaches = []
    for result in cursor:
        coaches.append(result)

    cursor = db.execute(text(top_players_query))
    db.commit()
    players = []
    for result in cursor:
        players.append(result)

    cursor = db.execute(text(most_recent_games_query))
    db.commit()
    recent_games = []
    for result in cursor:
        recent_games.append(result)



    return render_template("index/index.html", coaches=coaches, players=players,games=recent_games)