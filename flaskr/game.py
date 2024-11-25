import os
from flask import Flask, request, render_template, g, redirect, Response, abort, Blueprint
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from .db import get_db

bp = Blueprint('game', __name__)

games_query = """
WITH roster (gameid, count) AS (
SELECT g.gameid, count(*)
FROM game g, skater_played_in spi, plays_for pf, player p
WHERE spi.gameid = g.gameid AND spi.playerid = p.playerid AND
g.year = pf.year AND p.playerid = pf.playerid
GROUP BY g.gameid
)
SELECT g.date, g.homescore, g.awayscore, t1.name, t2.name, g.gameid
FROM game g, Team t1, Team t2, roster r
WHERE g.hometeamid = t1.teamid AND g.awayteamid = t2.teamid AND g.gameid = r.gameid
ORDER BY r.count DESC
LIMIT 20;
"""

game_query = """
SELECT g.date, g.homescore, g.awayscore, t1.name, t2.name, g.year, g.hometeamid, g.awayteamid
FROM game g, Team t1, Team t2
WHERE g.hometeamid = t1.teamid AND g.awayteamid = t2.teamid AND g.gameid = :id;
"""

home_players_in_game_query = """
WITH home_players (first_name, last_name, position, number, playerid, gameid) AS (
SELECT p.first_name, p.last_name, p.position, p.number, p.playerid, g.gameid
FROM game g, skater_played_in spi, plays_for pf, player p
WHERE g.gameid = :id AND spi.gameid = g.gameid AND spi.playerid = p.playerid AND
g.year = pf.year AND p.playerid = pf.playerid AND g.hometeamid = pf.teamid

UNION ALL

 SELECT p.first_name, p.last_name, p.position, p.number, p.playerid, g.gameid
    FROM game g
    JOIN goalie_played_in gpi ON gpi.gameid = g.gameid
    JOIN plays_for pf ON gpi.playerid = pf.playerid AND g.year = pf.year
    JOIN player p ON p.playerid = gpi.playerid
    WHERE g.gameid = :id 
      AND g.hometeamid = pf.teamid
),
player_stats (gameid, playerid, goals, assists, shots, hits) AS (
SELECT ssig.gameid , ssig.playerid, ss.goals, ss.assists, ss.shots, ss.hits
FROM Skater_Stats_In_Game ssig NATURAL JOIN Skater_Stats ss
),
goalie_stats_total (gameid, playerid, shots_faced, goals_conceded, saves, save_pct, shutouts) AS (
    SELECT gsig.gameid, gsig.playerid, gs.shots_faced, gs.goals_conceded, gs.saves, gs.save_pct, gs.shutouts
    FROM Goalie_Stats_In_Game gsig
    JOIN Goalie_Stats gs ON gsig.gstatsid = gs.gstatsid
)
SELECT h.first_name, h.last_name, h.position, h.number, h.playerid, p.goals, p.assists, p.shots, p.hits,
g.shots_faced, g.goals_conceded, g.saves, g.save_pct, g.shutouts
FROM home_players h LEFT JOIN player_stats p
ON h.gameid = p.gameid AND h.playerid = p.playerid
LEFT JOIN goalie_stats_total g ON h.gameid = g.gameid AND h.playerid = g.playerid;
"""

away_players_in_game_query = """
WITH home_players (first_name, last_name, position, number, playerid, gameid) AS (
SELECT p.first_name, p.last_name, p.position, p.number, p.playerid, g.gameid
FROM game g, skater_played_in spi, plays_for pf, player p
WHERE g.gameid = :id AND spi.gameid = g.gameid AND spi.playerid = p.playerid AND
g.year = pf.year AND p.playerid = pf.playerid AND g.awayteamid = pf.teamid

UNION ALL

 SELECT p.first_name, p.last_name, p.position, p.number, p.playerid, g.gameid
    FROM game g
    JOIN goalie_played_in gpi ON gpi.gameid = g.gameid
    JOIN plays_for pf ON gpi.playerid = pf.playerid AND g.year = pf.year
    JOIN player p ON p.playerid = gpi.playerid
    WHERE g.gameid = :id 
      AND g.awayteamid = pf.teamid
),
player_stats (gameid, playerid, goals, assists, shots, hits) AS (
SELECT ssig.gameid , ssig.playerid, ss.goals, ss.assists, ss.shots, ss.hits
FROM Skater_Stats_In_Game ssig NATURAL JOIN Skater_Stats ss
),
goalie_stats_total (gameid, playerid, shots_faced, goals_conceded, saves, save_pct, shutouts) AS (
    SELECT gsig.gameid, gsig.playerid, gs.shots_faced, gs.goals_conceded, gs.saves, gs.save_pct, gs.shutouts
    FROM Goalie_Stats_In_Game gsig
    JOIN Goalie_Stats gs ON gsig.gstatsid = gs.gstatsid
)
SELECT h.first_name, h.last_name, h.position, h.number, h.playerid, p.goals, p.assists, p.shots, p.hits,
g.shots_faced, g.goals_conceded, g.saves, g.save_pct, g.shutouts
FROM home_players h LEFT JOIN player_stats p
ON h.gameid = p.gameid AND h.playerid = p.playerid
LEFT JOIN goalie_stats_total g ON h.gameid = g.gameid AND h.playerid = g.playerid;
"""



@bp.route('/games', methods=['GET','POST'])
def games():
    db = get_db()
    cursor = db.execute(games_query)
    db.commit()
    games = []
    for result in cursor:
        games.append(result)
    return render_template("game/games.html", games=games)

@bp.route('/games/<int:id>', methods=['GET','POST'])
def game(id):
    db = get_db()
    params_dict = {"id":id}
    cursor = db.execute(game_query,params_dict)
    db.commit()
    games = []
    for result in cursor:
        games.append(result)
    
    cursor = db.execute(home_players_in_game_query,params_dict)
    db.commit()
    home_players = []
    for result in cursor:
        home_players.append(result)

    cursor = db.execute(away_players_in_game_query,params_dict)
    db.commit()
    away_players = []
    for result in cursor:
        away_players.append(result)
    return render_template("game/game.html", game=games[0],home_players=home_players, away_players=away_players)