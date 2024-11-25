-- Create the Venue table
CREATE TABLE Venue (
    venueid INTEGER PRIMARY KEY,
    city TEXT,
    state TEXT CHECK(length(state) = 2),
    capacity INTEGER CHECK (capacity > 0),
    name TEXT
);

-- Create the Season table
CREATE TABLE Season (
    year INTEGER PRIMARY KEY,
    start_date DATE,
    end_date DATE,
    CHECK (end_date >= start_date)
);

-- Create the Team table
CREATE TABLE Team (
    teamid INTEGER PRIMARY KEY,
    name TEXT,
    location TEXT
);

-- Create the Hosts table
CREATE TABLE Hosts (
    venueid INTEGER NOT NULL,
    year INTEGER NOT NULL,
    teamid INTEGER NOT NULL,
    PRIMARY KEY (venueid, year, teamid),
    FOREIGN KEY (venueid) REFERENCES Venue (venueid),
    FOREIGN KEY (year) REFERENCES Season (year),
    FOREIGN KEY (teamid) REFERENCES Team (teamid)
);

-- Create the Coach table
CREATE TABLE Coach (
    coachid INTEGER PRIMARY KEY,
    name TEXT,
    dateofbirth DATE,
    hometown TEXT
);

-- Create the Coaches table
CREATE TABLE Coaches (
    coachid INTEGER NOT NULL,
    teamid INTEGER NOT NULL,
    year INTEGER NOT NULL,
    PRIMARY KEY (coachid, year),
    FOREIGN KEY (coachid) REFERENCES Coach (coachid),
    FOREIGN KEY (teamid) REFERENCES Team (teamid),
    FOREIGN KEY (year) REFERENCES Season (year)
);

-- Create the Plays_Season table
CREATE TABLE Plays_Season (
    teamid INTEGER NOT NULL,
    year INTEGER NOT NULL,
    PRIMARY KEY (teamid, year),
    FOREIGN KEY (teamid) REFERENCES Team (teamid),
    FOREIGN KEY (year) REFERENCES Season (year)
);

-- Create the Game table
CREATE TABLE Game (
    gameid INTEGER PRIMARY KEY,
    date DATE,
    homescore INTEGER CHECK (homescore >= 0),
    awayscore INTEGER CHECK (awayscore >= 0),
    hometeamid INTEGER NOT NULL,
    awayteamid INTEGER NOT NULL,
    year INTEGER NOT NULL,
    CHECK (strftime('%Y', date) = year OR strftime('%Y', date) = year - 1),
    FOREIGN KEY (hometeamid) REFERENCES Team (teamid),
    FOREIGN KEY (awayteamid) REFERENCES Team (teamid),
    FOREIGN KEY (year) REFERENCES Season (year)
);

-- Create the Player table
CREATE TABLE Player (
    playerid INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    dateofbirth DATE,
    nationality TEXT,
    position TEXT,
    number INTEGER CHECK (number BETWEEN 0 AND 99)
);

-- Create the Skater table
CREATE TABLE Skater (
    playerid INTEGER PRIMARY KEY,
    tot_shots INTEGER CHECK (tot_shots >= 0),
    tot_goals INTEGER CHECK (tot_goals >= 0),
    tot_assists INTEGER CHECK (tot_assists >= 0),
    tot_hits INTEGER CHECK (tot_hits >= 0),
    tot_blocks INTEGER CHECK (tot_blocks >= 0),
    FOREIGN KEY (playerid) REFERENCES Player (playerid) ON DELETE CASCADE
);

-- Create the Goalie table
CREATE TABLE Goalie (
    playerid INTEGER PRIMARY KEY,
    tot_shots_faced INTEGER CHECK (tot_shots_faced >= 0),
    tot_saves INTEGER CHECK (tot_saves >= 0),
    tot_goals_conceded INTEGER CHECK (tot_goals_conceded >= 0),
    tot_shutouts INTEGER CHECK (tot_shutouts >= 0),
    FOREIGN KEY (playerid) REFERENCES Player (playerid) ON DELETE CASCADE
);

-- Create the Skater_Stats table
CREATE TABLE Skater_Stats (
    skstatsid INTEGER PRIMARY KEY,
    shots INTEGER CHECK (shots >= 0),
    goals INTEGER CHECK (goals >= 0),
    assists INTEGER CHECK (assists >= 0),
    hits INTEGER CHECK (hits >= 0),
    blocks INTEGER CHECK (blocks >= 0)
);

-- Create the Skater_Played_In table
CREATE TABLE Skater_Played_In (
    gameid INTEGER NOT NULL,
    playerid INTEGER NOT NULL,
    PRIMARY KEY (gameid, playerid),
    FOREIGN KEY (gameid) REFERENCES Game (gameid),
    FOREIGN KEY (playerid) REFERENCES Player (playerid)
);

-- Create the Skater_Stats_In_Game table
CREATE TABLE Skater_Stats_In_Game (
    skstatsid INTEGER NOT NULL,
    gameid INTEGER NOT NULL,
    playerid INTEGER NOT NULL,
    PRIMARY KEY (gameid, playerid),
    FOREIGN KEY (skstatsid) REFERENCES Skater_Stats (skstatsid),
    FOREIGN KEY (gameid, playerid) REFERENCES Skater_Played_In (gameid, playerid)
);

-- Create the Goalie_Stats table
CREATE TABLE Goalie_Stats (
    gstatsid INTEGER PRIMARY KEY,
    shots_faced INTEGER CHECK (shots_faced >= 0),
    saves INTEGER CHECK (saves >= 0),
    goals_conceded INTEGER CHECK (goals_conceded >= 0)
);

-- Create the Goalie_Played_In table
CREATE TABLE Goalie_Played_In (
    gameid INTEGER NOT NULL,
    playerid INTEGER NOT NULL,
    PRIMARY KEY (gameid, playerid),
    FOREIGN KEY (gameid) REFERENCES Game (gameid),
    FOREIGN KEY (playerid) REFERENCES Player (playerid)
);

-- Create the Goalie_Stats_In_Game table
CREATE TABLE Goalie_Stats_In_Game (
    gstatsid INTEGER NOT NULL,
    gameid INTEGER NOT NULL,
    playerid INTEGER NOT NULL,
    PRIMARY KEY (gameid, playerid),
    FOREIGN KEY (gstatsid) REFERENCES Goalie_Stats (gstatsid),
    FOREIGN KEY (gameid, playerid) REFERENCES Goalie_Played_In (gameid, playerid)
);

-- Create the plays_for table
CREATE TABLE plays_for (
    year INTEGER NOT NULL,
    playerid INTEGER NOT NULL,
    teamid INTEGER NOT NULL,
    PRIMARY KEY (year, playerid, teamid),
    FOREIGN KEY (year) REFERENCES Season (year),
    FOREIGN KEY (playerid) REFERENCES Player (playerid),
    FOREIGN KEY (teamid) REFERENCES Team (teamid)
);

-- Create the Skater_Career view
CREATE VIEW Skater_Career AS
SELECT ssig.playerid AS playerid, 
       SUM(ss.shots) AS total_shots, 
       SUM(ss.goals) AS total_goals, 
       SUM(ss.assists) AS total_assists, 
       SUM(ss.hits) AS total_hits, 
       SUM(ss.blocks) AS total_blocks, 
       COUNT(*) AS games_played
FROM Skater_Stats ss 
JOIN Skater_Stats_In_Game ssig ON ss.skstatsid = ssig.skstatsid
GROUP BY ssig.playerid;

-- Create the Goalie_Career view
CREATE VIEW Goalie_Career AS
SELECT gsig.playerid AS playerid, 
       SUM(gs.shots_faced) AS total_shots_faced, 
       SUM(gs.saves) AS total_saves, 
       SUM(gs.goals_conceded) AS total_goals_conceded, 
       SUM(gs.shutouts) AS total_shutouts, 
       (CAST(SUM(gs.saves) AS FLOAT) / CAST(SUM(gs.shots_faced) AS FLOAT)) AS save_percentage, 
       COUNT(*) AS games_played
FROM Goalie_Stats gs 
JOIN Goalie_Stats_In_Game gsig ON gs.gstatsid = gsig.gstatsid
GROUP BY gsig.playerid;
