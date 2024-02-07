BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "aw_firefox" (
	"id"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"firefox_id"	INTEGER,
	"date_time"	TEXT,
	"duration"	REAL,
	"url"	TEXT,
	"title"	TEXT,
	"audible"	TEXT,
	"username"	TEXT,
	"devicename"	TEXT
);
CREATE TABLE IF NOT EXISTS "aw_chrome" (
	"id"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"chrome_id"	INTEGER,
	"date_time"	TEXT,
	"duration"	REAL,
	"url"	TEXT,
	"title"	TEXT,
	"audible"	TEXT,
	"username"	TEXT,
	"devicename"	TEXT
);
CREATE TABLE IF NOT EXISTS "aw_app" (
	"id"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"app_id"	INTEGER,
	"date_time"	TEXT,
	"duration"	REAL,
	"app"	TEXT,
	"title"	TEXT,
	"username"	TEXT,
	"devicename"	TEXT
);
CREATE TABLE IF NOT EXISTS "aw_afk" (
	"id"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"afk_id"	INTEGER,
	"date_time"	TEXT,
	"duration"	REAL,
	"afk_status"	TEXT,
	"username"	TEXT,
	"devicename"	TEXT
);
CREATE TABLE IF NOT EXISTS "aw_last_sync" (
	"id"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"aw_type"	TEXT,
	"aw_id"	TEXT DEFAULT 0,
	"aw_duration"	REAL
);
COMMIT;
