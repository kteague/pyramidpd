

create table profile (
	id varchar(64) PRIMARY KEY DEFAULT nextval('serial'),
	orientation orientation,
	gender gender NOT NULL,
	country country NOT NULL,
	city varchar(500) NOT NULL,
	birthdate date NOT NULL,
	email varchar(1000) NOT NULL,
	password varchar(500),
	name varchar(500),
	about_me text,
	interests text,
	looking_for text
);

