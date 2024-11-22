CREATE TABLE Venue (
venueid INTEGER,
city varchar(45),
state varchar(2),
capacity INTEGER CHECK (capacity > 0),
name varchar(25),
PRIMARY KEY (venueid)
)

CREATE TABLE Season (
year INTEGER,
start_date DATE,
end_date DATE,
CHECK (end_date >= start_date),
PRIMARY KEY (year)
)

CREATE TABLE Team (
teamid INTEGER,
name varchar(30),
location varchar(35),
PRIMARY KEY (teamid)
)

CREATE TABLE Hosts (
venueid INTEGER NOT NULL,
year INTEGER,
teamid INTEGER,
PRIMARY KEY (year, teamid),
FOREIGN KEY (venueid) REFERENCES Venue,
FOREIGN KEY (year) REFERENCES Season,
FOREIGN KEY (teamid) REFERENCES Team
)

CREATE TABLE Coach (
coachid INTEGER,
name CHAR(30),
dateofbirth DATE,
hometown CHAR(35),
PRIMARY KEY (coachid)
)

CREATE TABLE Coaches (
coachid INTEGER,
teamid INTEGER NOT NULL,
year INTEGER,
PRIMARY KEY (coachid, year),
FOREIGN KEY (coachid) REFERENCES Coach,
FOREIGN KEY (teamid) REFERENCES Team,
FOREIGN KEY (year) REFERENCES Season
)

CREATE TABLE Plays_Season (
teamid INTEGER,
year INTEGER,
PRIMARY KEY (teamid, year),
FOREIGN KEY (teamid) REFERENCES Team,
FOREIGN KEY (year) REFERENCES Season
)

CREATE TABLE Game (
gameid INTEGER,
date DATE,
homescore INTEGER CHECK (homescore >= 0),
awayscore INTEGER CHECK (awayscore >= 0),
hometeamid INTEGER NOT NULL,
awayteamid INTEGER NOT NULL,
year INTEGER NOT NULL,
CHECK (EXTRACT(year FROM date) = year or EXTRACT(year FROM date) = year -1),
PRIMARY KEY (gameid),
FOREIGN KEY (hometeamid) REFERENCES Team,
FOREIGN KEY (awayteamid) REFERENCES Team,
FOREIGN KEY (year) REFERENCES Season
)

CREATE TABLE Player (
playerid INTEGER,
first_name varchar(30),
last_name varchar(30),
dateofbirth DATE,
nationality varchar(45),
position varchar(10),
number INTEGER CHECK (0<=number AND number<=99),
PRIMARY KEY (playerid)
)

CREATE TABLE Skater (
playerid INTEGER,
tot_shots INTEGER CHECK (0<=tot_shots),
tot_goals INTEGER CHECK (0<=tot_goals),
tot_assists INTEGER CHECK (0<=tot_assists),
tot_hits INTEGER CHECK (0<=tot_hits),
tot_blocks INTEGER CHECK (0<=tot_blocks),
PRIMARY KEY (playerid),
FOREIGN KEY (playerid) REFERENCES Player
	ON DELETE CASCADE
)

CREATE TABLE Goalie (
playerid INTEGER,
tot_shots_faced INTEGER CHECK (0<=tot_shots_faced),
tot_saves INTEGER CHECK (0<=tot_saves),
tot_goals_conceded INTEGER CHECK (0<=tot_goals_conceded),
tot_shutouts INTEGER CHECK (0<=tot_shutouts),
PRIMARY KEY (playerid),
FOREIGN KEY (playerid) REFERENCES Player
	ON DELETE CASCADE
)

CREATE TABLE Skater_Stats (
skstatsid INTEGER,
shots INTEGER CHECK (0<=shots),
goals INTEGER CHECK (0<=goals),
assists INTEGER CHECK (0<=assists),
hits INTEGER CHECK (0<=hits),
blocks INTEGER CHECK (0<=blocks),
PRIMARY KEY (skstatsid) 
)

CREATE TABLE Skater_Played_In (
gameid INTEGER,
playerid INTEGER,
PRIMARY KEY (gameid, playerid),
FOREIGN KEY (gameid) REFERENCES Game,
FOREIGN KEY (playerid) REFERENCES Player
)

CREATE TABLE Skater_Stats_In_Game (
skstatsid INTEGER NOT NULL,
gameid INTEGER,
playerid INTEGER,
PRIMARY KEY (gameid, playerid),
FOREIGN KEY (skstatsid) REFERENCES Skater_Stats,
FOREIGN KEY (gameid, playerid) REFERENCES Skater_Played_In,
UNIQUE (skstatsid)
)

CREATE TABLE Goalie_Stats (
gstatsid INTEGER,
shots_faced INTEGER CHECK (0<=shots_faced),
saves INTEGER CHECK (0<=saves),
goals_conceded INTEGER CHECK (0<=goals_conceded),
shutouts INTEGER CHECK (0<=shutouts), # do we need this we have goals conceded?
PRIMARY KEY (gstatsid)
)

CREATE TABLE Goalie_Played_In (
gameid INTEGER,
playerid INTEGER,
PRIMARY KEY (gameid, playerid),
FOREIGN KEY (gameid) REFERENCES Game,
FOREIGN KEY (playerid) REFERENCES Player
)

CREATE TABLE Goalie_Stats_In_Game (
gstatsid INTEGER NOT NULL,
gameid INTEGER NOT NULL,
playerid INTEGER NOT NULL,
PRIMARY KEY (gameid, playerid),
FOREIGN KEY (gstatsid) REFERENCES Goalie_Stats,
FOREIGN KEY (gameid, playerid) REFERENCES Goalie_Played_In,
UNIQUE (gstatsid)
)

CREATE TABLE plays_for (
year INTEGER,
playerid INTEGER,
teamid INTEGER,
PRIMARY KEY (year,playerid,teamid),
FOREIGN KEY (year) REFERENCES Season,
FOREIGN KEY (playerid) REFERENCES Player,
FOREIGN KEY (teamid) REFERENCES Team
)

CREATE VIEW Skater_Career AS (
SELECT ssig.playerid AS playerid, SUM(ss.shots) AS total_shots, SUM(ss.goals) AS total_goals, SUM(ss.assists) AS total_assists, SUM(ss.hits) AS total_hits, SUM(ss.blocks) AS total_blocks, COUNT(*)
FROM Skater_stats ss NATURAL JOIN skater_stats_in_game ssig
GROUP BY ssig.playerid)

CREATE VIEW Goalie_Career AS (
SELECT gsig.playerid AS playerid, SUM(gs.shots_faced) AS total_shots_faced, SUM(gs.saves) AS total_saves, SUM(gs.goals_conceded) AS total_goals_conceded, SUM(gs.shutouts) AS total_shutouts, ((SUM(gs.saves))::float / (SUM(gs.shots_faced))::float) AS save_percentage, COUNT(*)
FROM Goalie_stats gs NATURAL JOIN Goalie_stats_in_game gsig
GROUP BY gsig.playerid);
