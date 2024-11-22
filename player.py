import os
from flask import Flask, request, render_template, g, redirect, Response, abort, Blueprint
from sqlalchemy import *
from sqlalchemy.pool import NullPool

bp = Blueprint('player', __name__)

players_query = """
SELECT p.first_name, p.last_name, p.playerid
FROM player p
LIMIT 30;
"""

player_query = """
SELECT *
FROM player p LEFT JOIN skater_career s 
ON s.playerid = p.playerid
WHERE p.playerid = :id;
"""

player_query2 = """
SELECT *  
FROM player p
LEFT JOIN skater_career s ON s.playerid = p.playerid
LEFT JOIN goalie_career g ON g.playerid = p.playerid
WHERE p.playerid = :id;
"""

player_played_season_query = """
SELECT pf.year, t.name, t.teamid
FROM plays_for pf NATURAL JOIN Team t
WHERE pf.playerid = :id
ORDER BY pf.year DESC;
"""

add_player_query = """
INSERT INTO player (playerid, first_name, last_name, dateofbirth, nationality, position, number) 
VALUES (
:playerid, :first_name, :last_name, :DOB, :nationality, :position, :number
);
"""

update_player_query = """
UPDATE player
SET first_name = :first_name, last_name = :last_name, dateofbirth = :DOB,
nationality = :nationality, position = :position, number = :number
WHERE playerid = :playerid;
"""

max_playerid_query = """
SELECT max(p.playerid)
FROM player p;
"""

delete_player_query = """
DELETE FROM player p
WHERE p.playerid = :id;
"""

players_play_in_season_query = """
SELECT p.first_name, p.last_name, p.playerid, t.name, t.teamid, pf.year
FROM Player p, plays_for pf, Team t
WHERE p.playerid = pf.playerid AND  t.teamid = pf.teamid
AND pf.year = :year;
"""

min_max_years = """
SELECT MAX(pf.year), MIN(pf.year)
FROM plays_for pf;
"""

@bp.route('/players', methods=['GET','POST'])
def players():
    cursor = g.conn.execute(text(min_max_years))
    g.conn.commit()
    max_min_years = []
    for result in cursor:
        max_min_years.append(result)
    max_year = max_min_years[0][0]
    min_year = max_min_years[0][1]
    years=[]
    for year in range(min_year, max_year+1):
        years.append(year)

    if request.method == 'GET':
        cursor = g.conn.execute(text(players_query))
        g.conn.commit()
        players = []
        for result in cursor:
            players.append(result)
        return render_template("player/players.html", players = players, years=years)
    else:
        year = request.form['season_select']
        season = year
        if year == 'Select Season':
            return redirect('/players')
        cursor = g.conn.execute(text(players_play_in_season_query),{"year":year})
        g.conn.commit()
        players = []
        for result in cursor:
            players.append(result)

        return render_template("player/players_in_season.html", players = players, years = years, season = season)


@bp.route('/players/<int:id>')
def player(id):
    params_dict = {"id":id}
    cursor = g.conn.execute(text(player_query2),params_dict)
    g.conn.commit()
    players = []
    for result in cursor:
        players.append(result)
    cursor = g.conn.execute(text(player_played_season_query),params_dict)
    g.conn.commit()
    seasons = []
    for result in cursor:
        seasons.append(result)

    return render_template("player/player.html", player=players[0], seasons = seasons)


@bp.route('/players/add', methods=['POST'])
def add_player():
    playerid = get_max_playerid() + 1
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    nationality = request.form['nationality']
    DOB = request.form['DOB']
    position = request.form['position']
    number = request.form['number']
    params_dict = {"playerid":playerid, "first_name":first_name, "last_name":last_name, "nationality":nationality, 
                   "DOB":DOB, "position":position, "number":number}
    g.conn.execute(text(add_player_query),params_dict)
    g.conn.commit()

    return redirect('/players')


@bp.route('/players/add', methods=['GET'])
def add_player_form():
    return render_template("player/add.html")

@bp.route('/players/delete/<int:id>', methods=['GET'])
def delete_player(id):
    params_dict = {"id":id}
    g.conn.execute(text(delete_player_query),params_dict)
    g.conn.commit()
    return redirect('/players')

@bp.route('/players/update/<int:id>', methods=['GET','POST'])
def update_player(id):
    if request.method == "GET":
        params_dict = {"id":id}
        cursor = g.conn.execute(text(player_query),params_dict)
        g.conn.commit()
        players = []
        for result in cursor:
            players.append(result)
        return render_template("player/update.html", player=players[0])
    elif request.method == "POST":
        playerid = id
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        nationality = request.form['nationality']
        DOB = request.form['DOB']
        position = request.form['position']
        number = request.form['number']
        params_dict = {"playerid":playerid, "first_name":first_name, "last_name":last_name, "nationality":nationality, 
                    "DOB":DOB, "position":position, "number":number}
        g.conn.execute(text(update_player_query),params_dict)
        g.conn.commit()
        return redirect('/players/'+str(id))


def get_max_playerid():
    cursor = g.conn.execute(text(max_playerid_query))
    g.conn.commit()
    id = []
    for result in cursor:
        id.append(result)
    return id[0][0]