
create table if not exists channels
(
	id text NOT NULL PRIMARY KEY
);
create table if not exists numberNotes
(
	id text NOT NULL PRIMARY KEY,
	content int
);
