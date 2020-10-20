SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE team(
	TeamId VARCHAR(3) NOT NULL,
	ful_name VARCHAR(255) NOT NULL,
	stadium_name VARCHAR(255) NOT NULL,
	mascot VARCHAR(255),
	num_players INT,
	num_coaches INT,
	PRIMARY	KEY(TeamId)
);

CREATE TABLE player(
	PlayerId INTEGER AUTO_INCREMENT PRIMARY KEY,
	current_teamId VARCHAR(3) NULL DEFAULT NULL,
	player_name VARCHAR(255) NOT NULL,
	dominant_hand VARCHAR(1) NOT NULL,
	batting_average FLOAT,
	on_base_per FLOAT,
	slug_per FLOAT,
	games_played INTEGER,
	strikeouts INTEGER,
	FOREIGN KEY(current_teamId) REFERENCES team(TeamId)
);

CREATE TABLE coach(
	CoachId INTEGER AUTO_INCREMENT PRIMARY KEY,
	name VARCHAR(255)
);

CREATE TABLE manager(
	ManagerId INTEGER AUTO_INCREMENT PRIMARY KEY,
	name VARCHAR(255)
);

CREATE TABLE coaches_for(
	CoachId INTEGER NOT NULL,
	TeamId VARCHAR(3) NOT NULL,
	salary FLOAT,
	start_date VARCHAR(255),
	end_date VARCHAR(255),
	position VARCHAR(255),
	PRIMARY KEY(CoachId, TeamId, start_date),
	FOREIGN KEY(CoachId) REFERENCES coach(CoachId),
	FOREIGN KEY(TeamId) REFERENCES team(TeamId)
);

CREATE TABLE plays_for(
	PlayerId INTEGER NOT NULL,
	TeamId VARCHAR(3) NOT NULL,
	salary FLOAT,
	start_date VARCHAR(255),
	end_date VARCHAR(255),
	position VARCHAR(255),
	PRIMARY KEY(PlayerId, TeamId, start_date),
	FOREIGN KEY(PlayerId) REFERENCES player(PlayerId),
	FOREIGN KEY(TeamId) REFERENCES team(TeamId)
);

CREATE TABLE manages(
	ManagerId INTEGER NOT NULL,
	TeamId VARCHAR(3) NOT NULL,
	salary FLOAT,
	start_date VARCHAR(255),
	end_date VARCHAR(255),
	position VARCHAR(255),
	PRIMARY KEY(ManagerId, TeamId, start_date),
	FOREIGN KEY(ManagerId) REFERENCES manager(ManagerId),
	FOREIGN KEY(TeamID) REFERENCES team(TeamId)
);

CREATE TABLE games(
	team1 VARCHAR(3) NOT NULL,
	team2 VARCHAR(3) NOT NULL,
	score VARCHAR(255),
	winner INTEGER NOT NULL,
	location VARCHAR(255),
	date VARCHAR(255) NOT NULL,
	PRIMARY KEY(team1, team2, date),
	FOREIGN KEY(team1) REFERENCES team(TeamId),
	FOREIGN KEY(team2) REFERENCES team(TeamId)
);

SET FOREIGN_KEY_CHECKS = 1;