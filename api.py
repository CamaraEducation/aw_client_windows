import sqlite3
import json
import requests
import os
from datetime import datetime, timedelta, timezone
import time
import pytz

sqliteConnection = sqlite3.connect(r"C:\xampp\htdocs\camaranms\nms.db")
cursor = sqliteConnection.cursor()
fileVar = open(r"C:\xampp\htdocs\camaranms\config")
devicename = fileVar.read()
username = os.getlogin()

def get_afk_data():
	"""
	Return the active/inactive data of AW.

	This function returns active/inactive data of AW by passing
	the last synced date from our database with get_last_afk_date()
	function, query and the current datetime to the API.

	"""
	last_date = get_last_afk_date()
	now = datetime.now(timezone.utc)
	date_time = now.strftime('%Y-%m-%d %H:%M:%S.%f')
	last_date = str(last_date)
	date_time = str(date_time)
	headers = {"Content-type": "application/json", "charset": "utf-8"}
	query = """afk_events = query_bucket(find_bucket('aw-watcher-afk_'));
		RETURN = sort_by_timestamp(afk_events);""".split("\n")
	data = {
		"timeperiods": [
			"/".join([last_date,date_time])
		],
		"query": query,
	}
	response = requests.post(
		"http://localhost:5600/api/0/query/",
		data=bytes(json.dumps(data), "utf-8"),
		headers=headers,
		params={},
	)
	afk_result = response.json()
	return afk_result

def get_app_data():
	"""
	Return the Application data of AW.

	This function returns Application data of AW by passing
	the last synced date from our database with get_last_afk_date()
	function, query and the current datetime to the API.

	"""
	app_last_date = get_last_app_date()
	app_now = datetime.now(timezone.utc)
	app_date_time = app_now.strftime('%Y-%m-%d %H:%M:%S.%f')
	app_last_date = str(app_last_date)
	app_date_time = str(app_date_time)
	headers = {"Content-type": "application/json", "charset": "utf-8"}
	appquery = """afk_events = query_bucket(find_bucket('aw-watcher-afk_'));
		window_events = query_bucket(find_bucket('aw-watcher-window_'));
		window_events = filter_period_intersect(window_events, filter_keyvals(afk_events, 'status', ['not-afk']));
		RETURN = window_events;""".split("\n")

	appdata = {
		"timeperiods": [
			"/".join([app_last_date,app_date_time])
		],
		"query": appquery,
	}
	response = requests.post(
		"http://localhost:5600/api/0/query/",
		data=bytes(json.dumps(appdata), "utf-8"),
		headers=headers,
		params={},
	)
	app_result = response.json()
	return app_result

def get_last_afk_date():
	try:
		print("Trying to get the last afk date........")
		sqlite_select_query = """SELECT id, afk_id,afk_status, date_time FROM aw_afk order by id DESC limit 1"""
		cursor.execute(sqlite_select_query)
		records = cursor.fetchall()
		for row in records:
			date_time = row[3]

		print("Got the last afk date successfully......", date_time, "\n")
		return date_time

	except sqlite3.Error as error:
		print("Failed to read row from sqlite table.......", error)

def get_last_app_date():
	try:
		print("Trying to get the last application date........")
		sqlite_select_query = """SELECT id, app_id, date_time FROM aw_app order by id DESC limit 1"""
		cursor.execute(sqlite_select_query)
		records = cursor.fetchall()
		for row in records:
			date_time = row[2]

		print("Got the last application date successfully", date_time, "\n")
		return date_time

	except sqlite3.Error as error:
		print("Failed to read row from sqlite table......", error)
	
def get_old_afk_id(afk_id):
	try:
		print("Trying to get afk last ID to check if data is new or not........")
		sqlite_select_query = """SELECT id, afk_id,afk_status, duration, date_time FROM aw_afk WHERE afk_id = ?"""
		cursor.execute(sqlite_select_query, (afk_id,))
		records = cursor.fetchall()
		rows = len(records)
		if rows > 0:
			for row in records:
				old_afk_id = row[1]
				old_afk_duration = row[3]
			print("Got the last afk ID successfully.......", old_afk_id, old_afk_duration, "\n")
		else:
			old_afk_id = None
			old_afk_duration = None
	except sqlite3.Error as error:
		print("Failed to read row from sqlite table......", error)
	return [old_afk_id,old_afk_duration]

def get_old_app_id(app_id):
	try:
		print("Trying to get app last ID to check if data is new or not........")
		sqlite_select_query = """SELECT id, app_id,duration, date_time FROM aw_app WHERE app_id = ?"""
		cursor.execute(sqlite_select_query, (app_id,))
		records = cursor.fetchall()
		rows = len(records)
		if rows > 0:
			for row in records:
				old_app_id = row[1]
				old_app_duration = row[2]
			print("Got the last app ID  successfully......",old_app_id, old_app_duration, "\n")
		else:
			old_app_id = None
			old_app_duration = None
	except sqlite3.Error as error:
		print("Failed to read row from sqlite table......", error)
	return [old_app_id,old_app_duration]

def store_afk_data():
	print("***********Camara NMS API STARTED FOR STUDENT!***********""\n")
	time.sleep(1)
	print("Connected to SQLite DATABASE......","\n")
	print("Started to check for new AFK data and start insert/updating AFK table.......","\n")
	time.sleep(2)
	afk_data = get_afk_data()
	for rows in afk_data:
		for row in rows:
			if not row['data']:
				continue
			afk_id = row["id"]
			afk_date_time = row['timestamp']
			afk_duration = row['duration']
			afk_status = row['data']['status']
			if afk_duration > 0:
				old = get_old_afk_id(afk_id)
				if old[0] is not None:
					if afk_duration > old[1]:
						print('OLD', old[0], old[1], afk_duration)
						sqlite_update_query = """Update aw_afk set duration = ? WHERE afk_id = ?"""
						data = (afk_duration,afk_id)
						cursor.execute(sqlite_update_query, data)
						sqliteConnection.commit()
						print("AFK Record Updated successfully", afk_id, afk_duration, "\n")
						time.sleep(1)
				else:
					print('NEW', afk_id, afk_duration)
					sqlite_insert_query = """Insert  INTO aw_afk (afk_id, date_time, duration, afk_status,username, devicename) values (?,?,?,?,?,?)  """
					data = (afk_id,afk_date_time,afk_duration,afk_status,username,devicename)
					cursor.execute(sqlite_insert_query, data)
					sqliteConnection.commit()
					print("AFK Record Created successfully", afk_id, afk_duration, "\n")
	print("***********All AFK data is recoreded successfully!***********", "\n")
	time.sleep(3)

def store_app_data():
	print("Started to check for new APP data and start insert/updating APP table.......", "\n")
	time.sleep(2)
	app_data = get_app_data()
	for rows in app_data:
		for row in rows:
			if not row['data']:
				continue
			app_id = row["id"]
			app_date_time = row['timestamp']
			app_duration = row['duration']
			app_app = row['data']['app']
			app_title = row['data']['title']
			if app_duration > 0:
				old = get_old_app_id(app_id)
				if old[0] is not None:
					if app_duration > old[1]:
						print('OLD', old[0], old[1], app_duration)
						sqlite_update_query = """Update aw_app set duration = ? WHERE app_id = ?"""
						data = (app_duration,app_id)
						cursor.execute(sqlite_update_query, data)
						sqliteConnection.commit()
						print("APP Record Updated successfully", app_id, app_duration, "\n")
						time.sleep(1)
				else:
					print('NEW', app_id, app_duration)
					sqlite_insert_query = """Insert  INTO aw_app (app_id, date_time, duration, app, title,username,devicename) values (?,?,?,?,?,?,?)  """
					data = (app_id,app_date_time,app_duration,app_app, app_title, username, devicename)
					cursor.execute(sqlite_insert_query, data)
					sqliteConnection.commit()
					print("APP Record Created successfully", app_id, app_duration, "\n")
	print("***********All APP data is recoreded successfully!***********", "\n")
	cursor.close()
store_afk_data()
store_app_data()

