CREATE TABLE users (
  ID int default '0' NOT NULL,
  Username varchar(50) default ''  NOT NULL,
  FirstName varchar(50) default '' NOT NULL,
  LastName varchar(50) default '' NOT NULL,
  Password varchar(100),
  PRIMARY KEY  (ID)
);
