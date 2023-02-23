CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
DROP TABLE IF EXISTS Pictures CASCADE;
DROP TABLE IF EXISTS Users CASCADE;

CREATE TABLE Users (
    user_id int4 AUTO_INCREMENT,
    gender VARCHAR(6),
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(40) NOT NULL,
    dob DATE NOT NULL,
    hometown VARCHAR(40),
    fname VARCHAR(40) NOT NULL,
    lname VARCHAR(40) NOT NULL,
    contribution_score INTEGER,
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
  likes INTEGER,
  album_id INT NOT NULL,
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
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

CREATE TABLE User_Likes
(
	user_id int4 NOT NULL,
    picture_id int4 NOT NULL,
    PRIMARY KEY (user_id, picture_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id) ON DELETE CASCADE
);

CREATE TABLE Tags
(
	tag_name VARCHAR(100),
    popularity INTEGER,
    PRIMARY KEY (tag_name)
);

CREATE TABLE Tagged
(
	tag_name VARCHAR(100),
    picture_id int4,
    PRIMARY KEY (tag_name, picture_id),
    FOREIGN KEY (tag_name) REFERENCES Tags(tag_name),
    FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id)
);

CREATE TABLE Uses_Tags
(
    user_id int4,
    tag_name VARCHAR(100),
    frequency INTEGER,
    PRIMARY KEY (user_id, tag_name),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (tag_name) REFERENCES Tags(tag_name)
);
    
CREATE TABLE Friendship 
(	
	user_id1 int4 NOT NULL,
    user_id2 int4 NOT NULL,
    CHECK(user_id1 <> user_id2),
    PRIMARY KEY (user_id1, user_id2),
    FOREIGN KEY (user_id1) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id2) REFERENCES Users(user_id) ON DELETE CASCADE
);

INSERT INTO Users (gender, email, password, dob, hometown, fname, lname, contribution_score)
	VALUES ('male', 'simonkye@bu.edu', 'Simon200560', '2002-09-17', 'Hong Kong', 'Simon', 'Kye', 0);
