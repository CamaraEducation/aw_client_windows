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

def get_chrome_data():
	"""
	Return the active/inactive data of AW.

	This function returns active/inactive data of AW by passing
	the last synced date from our database with get_last_chrome_date()
	function, query and the current datetime to the API.

	"""
	last_date = get_last_chrome_date()
	now = datetime.now(timezone.utc)
	date_time = now.strftime('%Y-%m-%d %H:%M:%S.%f')
	last_date = str(last_date)
	date_time = str(date_time)
	headers = {"Content-type": "application/json", "charset": "utf-8"}
	query = """chrome_events = query_bucket(find_bucket('aw-watcher-web-chrome'));
		RETURN = sort_by_timestamp(chrome_events);""".split("\n")
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
	chrome_result = response.json()
	return chrome_result

def get_firefox_data():
	"""
	Return the Application data of AW.

	This function returns Application data of AW by passing
	the last synced date from our database with get_last_firefox_date()
	function, query and the current datetime to the API.

	"""
	app_last_date = get_last_firefox_date()
	app_now = datetime.now(timezone.utc)
	app_date_time = app_now.strftime('%Y-%m-%d %H:%M:%S.%f')
	app_last_date = str(app_last_date)
	app_date_time = str(app_date_time)
	headers = {"Content-type": "application/json", "charset": "utf-8"}
	appquery = """firefox_events = query_bucket(find_bucket('aw-watcher-web-firefox'));
		RETURN = sort_by_timestamp(firefox_events);""".split("\n")

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
	firefox_result = response.json()
	return firefox_result

def get_last_chrome_date():
	try:
		print("Trying to get the last chrome date........")
		sqlite_select_query = """SELECT id, chrome_id, date_time FROM aw_chrome order by id DESC limit 1"""
		cursor.execute(sqlite_select_query)
		records = cursor.fetchall()
		for row in records:
			date_time = row[2]

		print("Got the last chrome date successfully......", date_time, "\n")
		return date_time

	except sqlite3.Error as error:
		print("Failed to read row from sqlite table.......", error)

def get_last_firefox_date():
	try:
		print("Trying to get the last firefox date........")
		sqlite_select_query = """SELECT id, firefox_id, date_time FROM aw_firefox order by id DESC limit 1"""
		cursor.execute(sqlite_select_query)
		records = cursor.fetchall()
		for row in records:
			date_time = row[2]

		print("Got the last firefox date successfully", date_time, "\n")
		return date_time

	except sqlite3.Error as error:
		print("Failed to read row from sqlite table......", error)
	
def get_old_chrome_id(chrome_id):
	try:
		print("Trying to get chrome last ID to check if data is new or not........")
		sqlite_select_query = """SELECT id, chrome_id, duration, date_time FROM aw_chrome WHERE chrome_id = ?"""
		cursor.execute(sqlite_select_query, (chrome_id,))
		records = cursor.fetchall()
		rows = len(records)
		if rows > 0:
			for row in records:
				old_chrome_id = row[1]
				old_chrome_duration = row[2]
			print("Got the last chrome ID successfully.......", old_chrome_id, old_chrome_duration, "\n")
		else:
			old_chrome_id = None
			old_chrome_duration = None
	except sqlite3.Error as error:
		print("Failed to read row from sqlite table......", error)
	return [old_chrome_id,old_chrome_duration]

def get_old_firefox_id(firefox_id):
	try:
		print("Trying to get firefox last ID to check if data is new or not........")
		sqlite_select_query = """SELECT id, firefox_id, duration, date_time FROM aw_firefox WHERE firefox_id = ?"""
		cursor.execute(sqlite_select_query, (firefox_id,))
		records = cursor.fetchall()
		rows = len(records)
		if rows > 0:
			for row in records:
				old_firefox_id = row[1]
				old_firefox_duration = row[2]
			print("Got the last firefox ID successfully.......", old_firefox_id, old_firefox_duration, "\n")
		else:
			old_firefox_id = None
			old_firefox_duration = None
	except sqlite3.Error as error:
		print("Failed to read row from sqlite table......", error)
	return [old_firefox_id,old_firefox_duration]

def store_chrome_data():
	print("Started to check for new CHROME data and start insert/updating aw_chrome table.......","\n")
	time.sleep(2)
	chrome_data = get_chrome_data()
	for rows in chrome_data:
		for row in rows:
			chrome_id = row["id"]
			chrome_date_time = row['timestamp']
			chrome_duration = row['duration']
			chrome_url= row['data']['url']
			chrome_title= row['data']['title']
			chrome_audible= row['data']['audible']
			if chrome_duration > 0:
				old = get_old_chrome_id(chrome_id)
				if old[0] is not None:
					if chrome_duration > old[1]:
						print('OLD', old[0], old[1], chrome_duration)
						sqlite_update_query = """Update aw_chrome set duration = ? WHERE chrome_id = ?"""
						data = (chrome_duration,chrome_id)
						cursor.execute(sqlite_update_query, data)
						sqliteConnection.commit()
						print("Chrome Record Updated successfully", chrome_id, chrome_duration, "\n")
						time.sleep(1)
				else:
					print('NEW', chrome_id, chrome_duration)
					sqlite_insert_query = """Insert  INTO aw_chrome (chrome_id, date_time, duration, url,title,audible,username, devicename) values (?,?,?,?,?,?,?,?)  """
					data = (chrome_id,chrome_date_time,chrome_duration,chrome_url,chrome_title,chrome_audible,username,devicename)
					cursor.execute(sqlite_insert_query, data)
					sqliteConnection.commit()
					print("Chrome Record Created successfully", chrome_id, chrome_duration, "\n")
	print("***********All Chrome data is recoreded successfully!***********", "\n")
	time.sleep(3)

def store_firefox_data():
	print("Started to check for new FIREFOX data and start insert/updating aw_firefox table.......", "\n")
	time.sleep(2)
	firefox_data = get_firefox_data()
	for rows in firefox_data:
		for row in rows:
			firefox_id = row["id"]
			firefox_date_time = row['timestamp']
			firefox_duration = row['duration']
			firefox_url= row['data']['url']
			firefox_title= row['data']['title']
			firefox_audible= row['data']['audible']
			if firefox_duration > 0:
				old = get_old_chrome_id(firefox_id)
				if old[0] is not None:
					if firefox_duration > old[1]:
						print('OLD', old[0], old[1], firefox_duration)
						sqlite_update_query = """Update aw_firefox set duration = ? WHERE firefox_id = ?"""
						data = (firefox_duration,firefox_id)
						cursor.execute(sqlite_update_query, data)
						sqliteConnection.commit()
						print("Firefox Record Updated successfully", firefox_id, firefox_duration, "\n")
						time.sleep(1)
				else:
					print('NEW', firefox_id, firefox_duration)
					sqlite_insert_query = """Insert  INTO aw_firefox (firefox_id, date_time, duration, url,title,audible,username, devicename) values (?,?,?,?,?,?,?,?)  """
					data = (firefox_id,firefox_date_time,firefox_duration,firefox_url,firefox_title,firefox_audible,username,devicename)
					cursor.execute(sqlite_insert_query, data)
					sqliteConnection.commit()
					print("Firefox Record Created successfully", firefox_id, firefox_duration, "\n")
	print("***********All Firefox data is recoreded successfully!***********", "\n")
	cursor.close()
	print("The SQLite connection is closed......\n")
	time.sleep(3)
	print("***********API ALL DONE FOR STUDENT!***********")

store_chrome_data()
store_firefox_data()

