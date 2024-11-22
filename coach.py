import os
from flask import Flask, request, render_template, g, redirect, Response, abort, Blueprint
from sqlalchemy import *
from sqlalchemy.pool import NullPool

bp = Blueprint('coach', __name__)

coaches_query = """
SELECT c.name, c.coachid
FROM Coach c, coaches cs
WHERE c.coachid = cs.coachid AND 
(cs.teamid IN (SELECT g.hometeamid FROM game g WHERE g.year = cs.year) OR
cs.teamid IN (SELECT g.awayteamid FROM game g WHERE g.year = cs.year))
GROUP BY c.name, c.coachid
ORDER BY COUNT(*) DESC;
"""

coaches_during_season_query = """
SELECT c.name, c.coachid, t.name, t.teamid, cs.year
FROM Coach c, Coaches cs, Team t
WHERE c.coachid = cs.coachid AND t.teamid = cs.teamid AND 
(cs.teamid IN (SELECT g.hometeamid FROM game g WHERE g.year = cs.year) OR
cs.teamid IN (SELECT g.awayteamid FROM game g WHERE g.year = cs.year))
AND cs.year = :year;
"""

min_max_years = """
SELECT MAX(cs.year), MIN(cs.year)
FROM Coaches cs, game g
WHERE cs.year = g.year;
"""

coach_query = """
SELECT *
FROM coach c
WHERE c.coachid = :id;
"""

add_coach_query = """
INSERT INTO Coach (coachid, name, dateofbirth) 
VALUES (
:coachid, :name, :DOB
);
"""

max_coachid_query = """
SELECT max(c.coachid)
FROM Coach c;
"""

coached_seasons_query = """
SELECT t.name, cs.year, t.teamid
FROM coaches cs NATURAL JOIN Team t
WHERE cs.coachid = :id AND cs.year IN (SELECT s.year FROM plays_season s GROUP BY s.year)
AND 
(cs.teamid in (SELECT g.hometeamid FROM game g WHERE g.year = cs.year) 
OR
cs.teamid in (SELECT g.awayteamid FROM game g WHERE g.year = cs.year))
ORDER BY cs.year DESC;
"""

update_player_query = """
UPDATE Coach
SET name = :name, dateofbirth = :DOB,
WHERE coachid = :coachid;
"""

delete_coach_query = """
DELETE FROM Coach c
WHERE c.coachid = :id;
"""

@bp.route('/coaches', methods=['GET','POST'])
def coaches():
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
        cursor = g.conn.execute(text(coaches_query))
        g.conn.commit()
        coaches = []
        for result in cursor:
            coaches.append(result)
        return render_template("coach/coaches.html", coaches = coaches, years = years)
    else:
        year = request.form['season_select']
        season = year
        if year == 'Select Season':
            return redirect('/coaches')
        cursor = g.conn.execute(text(coaches_during_season_query),{"year":year})
        g.conn.commit()
        coaches = []
        for result in cursor:
            coaches.append(result)
        return render_template("coach/coaches_for_season.html", coaches = coaches, years = years, season = season)



@bp.route('/coaches/<int:id>')
def coach(id):
    params_dict = {"id":id}
    cursor = g.conn.execute(text(coach_query),params_dict)
    g.conn.commit()
    coach = []
    for result in cursor:
        coach.append(result)

    cursor = g.conn.execute(text(coached_seasons_query),params_dict)
    g.conn.commit()
    seasons_coached = []
    for result in cursor:
        seasons_coached.append(result)
    
    return render_template("coach/coach.html", coach=coach[0], seasons_coached=seasons_coached)


@bp.route('/coaches/add', methods=['POST'])
def add_coach():
    coachid = get_max_playerid() + 1
    name = request.form['name']
    DOB = request.form['DOB']
    params_dict = {"coachid":coachid, "name":name, "DOB":DOB}
    g.conn.execute(text(add_coach_query),params_dict)
    g.conn.commit()

    return redirect('/coaches')


@bp.route('/coaches/add', methods=['GET'])
def add_coaches_form():
    return render_template("coach/add.html")

# todo -- test this
@bp.route('/coaches/delete/<int:id>', methods=['GET'])
def delete_coach(id):
    params_dict = {"id":id}
    g.conn.execute(text(delete_coach_query),params_dict)
    g.conn.commit()
    return redirect('/coaches')

# todo -- test this
@bp.route('/coach/update/<int:id>', methods=['GET','POST'])
def update_coach(id):
    if request.method == "GET":
        params_dict = {"id":id}
        cursor = g.conn.execute(text(coach_query),params_dict)
        g.conn.commit()
        coaches = []
        for result in cursor:
            coaches.append(result)
        return render_template("player/update.html", coaches=coaches[0])
    elif request.method == "POST":
        coachid = id
        name = request.form['name']
        DOB = request.form['DOB']
        params_dict = {"coachid":coachid, "name":name, "DOB":DOB}
        g.conn.execute(text(update_player_query),params_dict)
        g.conn.commit()
        return redirect('/coaches'+str(id))

def get_max_playerid():
    cursor = g.conn.execute(text(max_coachid_query))
    g.conn.commit()
    id = []
    for result in cursor:
        id.append(result)
    return id[0][0]