CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
SET FOREIGN_KEY_CHECKS=0;
DROP TABLE IF EXISTS Pictures CASCADE;
DROP TABLE IF EXISTS Albums CASCADE;
DROP TABLE IF EXISTS Users CASCADE;
DROP TABLE IF EXISTS Comments CASCADE;
DROP TABLE IF EXISTS Likes CASCADE;
DROP TABLE IF EXISTS Tags CASCADE;
DROP TABLE IF EXISTS Tagged CASCADE;
SET FOREIGN_KEY_CHECKS=1;

CREATE TABLE Users (
    user_id int4  AUTO_INCREMENT,
    email varchar(255) UNIQUE,
    password varchar(255),
    fname VARCHAR(40) NOT NULL,
    lname VARCHAR(40) NOT NULL,
	dob DATE NOT NULL,
    hometown VARCHAR(40),
  CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE Albums
(
	album_id int4 AUTO_INCREMENT,
    aname VARCHAR(40) NOT NULL,
    date_of_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    PRIMARY KEY (album_id),
	FOREIGN KEY (user_id) REFERENCES Users(user_id)
		ON DELETE CASCADE
);

CREATE TABLE Pictures
(
	picture_id int4 AUTO_INCREMENT,
	user_id int4,
	imgdata longblob ,
	caption VARCHAR(255),
    album_id int4 NOT NULL,
	INDEX upid_idx (user_id),
	CONSTRAINT pictures_pk PRIMARY KEY (picture_id),
	FOREIGN KEY (user_id) REFERENCES Users(user_id),
	FOREIGN KEY (album_id) REFERENCES Albums(album_id)
		ON DELETE CASCADE
);

CREATE TABLE Comments
(
	comment_id int4 NOT NULL AUTO_INCREMENT,
    ctext TEXT NOT NULL,
    cdate DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id int4 NOT NULL,
    picture_id int4 NOT NULL,
    PRIMARY KEY (comment_id),
    FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id), #added on top of answer key
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

CREATE TABLE Likes
(
	user_id int4 NOT NULL,
    picture_id int4 NOT NULL,
    PRIMARY KEY (user_id, picture_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id) ON DELETE CASCADE
);

CREATE TABLE Tags
(
    tname VARCHAR(100),
    PRIMARY KEY (tname)
);

CREATE TABLE Tagged
(
	picture_id int4,
    tname VARCHAR(100),
    PRIMARY KEY (picture_id	, tname),
    FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id) ON DELETE CASCADE, #Added
    FOREIGN KEY (tname) REFERENCES Tags(tname)
);

CREATE TABLE Friendship
(
	UID1 int4 NOT NULL,
    UID2 int4 NOT NULL,
    CHECK (UID1 <> UID2),
    PRIMARY KEY (UID1, UID2),
    FOREIGN KEY (UID1) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (UID2) REFERENCES Users(user_id) ON DELETE CASCADE
);

INSERT INTO Users (email, password, fname, lname, dob, hometown) VALUES ('simonkye@bu.edu', 'Simon200560', 'Simon', 'Kye', '2002-09-17', 'Hong Kong');
INSERT INTO Users (email, password, fname, lname, dob, hometown) VALUES ('test@bu.edu', 'test', 'test', 'test', '2002-09-17', 'Hong Kong');
