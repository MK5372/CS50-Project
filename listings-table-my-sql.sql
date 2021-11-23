CREATE TABLE listings (
  Listing-ID int default '0' NOT NULL,
  Product NVARCHAR(50) default ''  NOT NULL,
  Username NVARCHAR(50) default '' NOT NULL,
  Price int default '0' NOT NULL,
  Image VARBINARY(max) NOT NULL ,
  PRIMARY KEY (Listing-ID)
);
