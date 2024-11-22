import os
from flask import Flask, request, render_template, g, redirect, Response, abort, Blueprint
from jinja2.filters import do_max
from sqlalchemy import *
from sqlalchemy.pool import NullPool

bp = Blueprint('stats', __name__)


get_shots_leaders_every_season = """
SELECT 
    p.first_name || ' ' || p.last_name AS player_name,
    SUM(s.tot_shots) AS total_shots
FROM 
    Skater s
JOIN 
    Player p ON s.playerid = p.playerid
GROUP BY 
    p.playerid
ORDER BY 
    total_shots DESC;
"""

get_goals_leaders_every_season = """
SELECT 
    p.first_name || ' ' || p.last_name AS player_name,
    SUM(s.tot_goals) AS total_goals
FROM 
    Skater s
JOIN 
    Player p ON s.playerid = p.playerid
GROUP BY 
    p.playerid
ORDER BY 
    total_goals DESC;
"""


get_assists_leaders_every_season = """
SELECT 
    p.first_name || ' ' || p.last_name AS player_name,
    SUM(s.tot_assists) AS total_assists
FROM 
    Skater s
JOIN 
    Player p ON s.playerid = p.playerid
GROUP BY 
    p.playerid
ORDER BY 
    total_assists DESC;
"""


get_hits_leaders_every_season = """
SELECT 
    p.first_name || ' ' || p.last_name AS player_name,
    SUM(s.tot_hits) AS total_hits
FROM 
    Skater s
JOIN 
    Player p ON s.playerid = p.playerid
GROUP BY 
    p.playerid
ORDER BY 
    total_hits DESC;
"""

get_blocks_leaders_every_season = """
SELECT 
    p.first_name || ' ' || p.last_name AS player_name,
    SUM(s.tot_blocks) AS total_blocks
FROM 
    Skater s
JOIN 
    Player p ON s.playerid = p.playerid
GROUP BY 
    p.playerid
ORDER BY 
    total_blocks DESC;
"""

get_shots_faced_leaders_every_season = """
SELECT 
    p.first_name || ' ' || p.last_name AS player_name,
    SUM(g.tot_shots_faced) AS total_shots_faced
FROM 
    Goalie g
JOIN 
    Player p ON g.playerid = p.playerid
GROUP BY 
    p.playerid
ORDER BY 
    total_shots_faced DESC;
"""

get_saves_leaders_every_season = """
SELECT 
    p.first_name || ' ' || p.last_name AS player_name,
    SUM(g.tot_saves) AS total_saves
FROM 
    Goalie g
JOIN 
    Player p ON g.playerid = p.playerid
GROUP BY 
    p.playerid
ORDER BY 
    total_saves DESC;
"""

get_goals_conceded_leaders_every_season = """
SELECT 
    p.first_name || ' ' || p.last_name AS player_name,
    SUM(g.tot_goals_conceded) AS total_goals_conceded
FROM 
    Goalie g
JOIN 
    Player p ON g.playerid = p.playerid
GROUP BY 
    p.playerid
ORDER BY 
    total_goals_conceded ASC;
"""

get_save_pct_every_season = """
SELECT 
    p.first_name || ' ' || p.last_name AS player_name,
    AVG(g.tot_save_pct) AS avg_save_pct
FROM 
    Goalie g
JOIN 
    Player p ON g.playerid = p.playerid
GROUP BY 
    p.playerid
ORDER BY 
    avg_save_pct DESC;
"""

get_shutouts_leaders_every_season = """
SELECT 
    p.first_name || ' ' || p.last_name AS player_name,
    SUM(g.tot_shutouts) AS total_shutouts
FROM 
    Goalie g
JOIN 
    Player p ON g.playerid = p.playerid
GROUP BY 
    p.playerid
ORDER BY 
    total_shutouts DESC;
"""





get_shots_leaders_for_season = """
SELECT 
    p.first_name || ' ' || p.last_name AS player_name,
    SUM(ss.shots) AS total_shots
FROM 
    Skater_Stats ss
JOIN 
    Skater_Stats_In_Game ssig ON ss.skstatsid = ssig.skstatsid
JOIN 
    Player p ON ssig.playerid = p.playerid
JOIN
    Game g ON ssig.gameid = g.gameid
WHERE 
    g.year = :season
GROUP BY 
    p.playerid
ORDER BY 
    total_shots DESC;
"""

get_goals_leaders_for_season = """
SELECT 
    p.first_name || ' ' || p.last_name AS player_name,
    SUM(ss.goals) AS total_goals
FROM 
    Skater_Stats ss
JOIN 
    Skater_Stats_In_Game ssig ON ss.skstatsid = ssig.skstatsid
JOIN 
    Player p ON ssig.playerid = p.playerid
JOIN
    Game g ON ssig.gameid = g.gameid
WHERE 
    g.year = :season
GROUP BY 
    p.playerid
ORDER BY 
    total_goals DESC;
"""


get_assists_leaders_for_season = """
SELECT 
    p.first_name || ' ' || p.last_name AS player_name,
    SUM(ss.assists) AS total_assists
FROM 
    Skater_Stats ss
JOIN 
    Skater_Stats_In_Game ssig ON ss.skstatsid = ssig.skstatsid
JOIN 
    Player p ON ssig.playerid = p.playerid
JOIN
    Game g ON ssig.gameid = g.gameid
WHERE 
    g.year = :season
GROUP BY 
    p.playerid
ORDER BY 
    total_assists DESC;
"""


get_hits_leaders_for_season = """
SELECT 
    p.first_name || ' ' || p.last_name AS player_name,
    SUM(ss.hits) AS total_hits
FROM 
    Skater_Stats ss
JOIN 
    Skater_Stats_In_Game ssig ON ss.skstatsid = ssig.skstatsid
JOIN 
    Player p ON ssig.playerid = p.playerid
JOIN
    Game g ON ssig.gameid = g.gameid
WHERE 
    g.year = :season
GROUP BY 
    p.playerid
ORDER BY 
    total_hits DESC;
"""

get_blocks_leaders_for_season = """
SELECT 
    p.first_name || ' ' || p.last_name AS player_name,
    SUM(ss.blocks) AS total_blocks
FROM 
    Skater_Stats ss
JOIN 
    Skater_Stats_In_Game ssig ON ss.skstatsid = ssig.skstatsid
JOIN 
    Player p ON ssig.playerid = p.playerid
JOIN
    Game g ON ssig.gameid = g.gameid
WHERE 
    g.year = :season
GROUP BY 
    p.playerid
ORDER BY 
    total_blocks DESC;
"""

get_shots_faced_leaders_for_season = """
SELECT 
    p.first_name || ' ' || p.last_name AS player_name,
    SUM(gs.shots_faced) AS total_shots_faced
FROM 
    Goalie_Stats gs
JOIN 
    Goalie_Stats_In_Game gsig ON gs.gstatsid = gsig.gstatsid
JOIN 
    Player p ON gsig.playerid = p.playerid
JOIN
    Game g ON gsig.gameid = g.gameid
WHERE 
    g.year = :season
GROUP BY 
    p.playerid
ORDER BY 
    total_shots_faced DESC;
"""

get_saves_leaders_for_season = """
SELECT 
    p.first_name || ' ' || p.last_name AS player_name,
    SUM(gs.saves) AS total_saves
FROM 
    Goalie_Stats gs
JOIN 
    Goalie_Stats_In_Game gsig ON gs.gstatsid = gsig.gstatsid
JOIN 
    Player p ON gsig.playerid = p.playerid
JOIN
    Game g ON gsig.gameid = g.gameid
WHERE 
    g.year = :season
GROUP BY 
    p.playerid
ORDER BY 
    total_saves DESC;
"""

get_goals_conceded_leaders_for_season = """
SELECT 
    p.first_name || ' ' || p.last_name AS player_name,
    SUM(gs.goals_conceded) AS total_goals_conceded
FROM 
    Goalie_Stats gs
JOIN 
    Goalie_Stats_In_Game gsig ON gs.gstatsid = gsig.gstatsid
JOIN 
    Player p ON gsig.playerid = p.playerid
JOIN
    Game g ON gsig.gameid = g.gameid
WHERE 
    g.year = :season
GROUP BY 
    p.playerid
ORDER BY 
    total_goals_conceded ASC;
"""

get_shots_save_pct_for_season = """
SELECT 
    p.first_name || ' ' || p.last_name AS player_name,
    AVG(gs.save_pct) AS avg_save_pct
FROM 
    Goalie_Stats gs
JOIN 
    Goalie_Stats_In_Game gsig ON gs.gstatsid = gsig.gstatsid
JOIN 
    Player p ON gsig.playerid = p.playerid
JOIN
    Game g ON gsig.gameid = g.gameid
WHERE 
    g.year = :season
GROUP BY 
    p.playerid
ORDER BY 
    avg_save_pct DESC;
"""

get_shutouts_leaders_for_season = """
SELECT 
    p.first_name || ' ' || p.last_name AS player_name,
    SUM(gs.shutouts) AS total_shutouts
FROM 
    Goalie_Stats gs
JOIN 
    Goalie_Stats_In_Game gsig ON gs.gstatsid = gsig.gstatsid
JOIN 
    Player p ON gsig.playerid = p.playerid
JOIN
    Game g ON gsig.gameid = g.gameid
WHERE 
    g.year = :season
GROUP BY 
    p.playerid
ORDER BY 
    total_shutouts DESC;
"""

@bp.route('/stats', methods=['GET','POST'])
def stats():
    stat = request.form.get('stat_select', None)
    year = request.form.get('year', None)
    players = []


    # Stat selection buttons
    if stat:
        if year:
            if stat == 'Shots':
                stat_query = get_shots_leaders_for_season
            elif stat == 'Goals':
                stat_query = get_goals_leaders_for_season
            elif stat == 'Assists':
                stat_query = get_assists_leaders_for_season
            elif stat == 'Hits':
                stat_query = get_hits_leaders_for_season
            elif stat == 'Blocks':
                stat_query = get_blocks_leaders_for_season
            elif stat == 'Shots Faced':
                stat_query = get_shots_faced_leaders_for_season
            elif stat == 'Saves':
                stat_query = get_saves_leaders_for_season
            elif stat == 'Goals Conceded':
                stat_query = get_goals_conceded_leaders_for_season
            elif stat == 'Save Pct':
                stat_query = get_shots_save_pct_for_season
            elif stat == "Shutouts":
                stat_query = get_shutouts_leaders_for_season
            else:
                stat_query = None

            if stat_query:
                cursor = g.conn.execute(text(stat_query), {"season": year})
                g.conn.commit()
                players = [result for result in cursor]

        else:
            if stat == 'Shots':
                stat_query = get_shots_leaders_every_season
            elif stat == 'Goals':
                stat_query = get_goals_leaders_every_season
            elif stat == 'Assists':
                stat_query = get_assists_leaders_every_season
            elif stat == 'Hits':
                stat_query = get_hits_leaders_every_season
            elif stat == 'Blocks':
                stat_query = get_blocks_leaders_every_season
            elif stat == 'Shots Faced':
                stat_query = get_shots_faced_leaders_every_season
            elif stat == 'Saves':
                stat_query = get_saves_leaders_every_season
            elif stat == 'Goals Conceded':
                stat_query = get_goals_conceded_leaders_every_season
            elif stat == 'Save Pct':
                stat_query = get_save_pct_every_season
            elif stat == "Shutouts":
                stat_query = get_shutouts_leaders_every_season
            else:
                stat_query = None

            if stat_query:
                cursor = g.conn.execute(text(stat_query))
                g.conn.commit()
                players = [result for result in cursor]



    return render_template("stats/stats.html", players=players, year=year, stat=stat)


