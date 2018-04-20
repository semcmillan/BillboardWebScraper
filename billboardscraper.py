from lxml import html
from lxml.cssselect import CSSSelector
import requests
import datetime
import urllib
from bs4 import BeautifulSoup
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import timedelta
import MySQLdb
import time

# It will be necessary to create a credentialfiles.py file, which has a class Credentials. This class should only contain
#  ClientID, ClientSecret, RedirectURI, UserID, Username, and Scope. Refer to readme for more information, and spotipy documentation 
#  on authentication
from credentialfiles import Credentials

songList = []
sp = ''
db = ''
cursor = ''
DelaySpotifySearch = 0.3

# Class which is used to track song information, can additionally be used to print information about
#  the class
class SongIndex:
	def __init__(self, SongTitle, ArtistName, Year, Month, Day, Rank):
		self.songtitle = SongTitle
		self.artistname = ArtistName
		self.date = datetime.date(Year, Month, Day)
		self.year = Year
		self.month = Month
		self.day = Day
		self.rank = Rank
		self.uri = 'N'

	def print_name(self):
		print('Song: ' + str(self.songtitle) + ' by Artist: ' + str(self.artistname) + ' reached Rank: ' + str(self.rank) + ' on ' + str(self.date))

	def print_uri(self):
		print('This song has URI: ' + str(self.uri))

	def print_features(self):
		try:
			if (self.audiofeatures != 'N'):
				for features in self.audiofeatures:
					print(features + ' : ' + str(self.audiofeatures[features]))
			else:
				print('No audio features')
		except:
			print('No Features')

	def generate_primary_key(self):
		NewDateTimeObject = datetime.datetime.strptime(str(self.date), '%Y-%m-%d')
		NewDateString = str(NewDateTimeObject.strftime('%d%m%Y'))
		RankString = str(self.rank).zfill(3)
		self.primary_key = RankString + str(NewDateString)



# Webscrapes from the billboard hot 100 list, to get the specific list for a year, date, and month
#  Takes a date in the datetime format, which it adds to a URL string to get the request URL
def scrape_billboard(date):
	global songList
	date = str(date)
	year = int(date[:4])
	month = int(date[5:7])
	day = int(date[-2:])
	pageURL = 'https://www.billboard.com/charts/hot-100/' + date
	pageContent = requests.get(pageURL)
	tree = html.fromstring(pageContent.content)
	for i in range(1, 101):
		selectorPath = '#main > div:nth-child(2) > div > div > article.chart-row.chart-row--' + str(i) + '.js-chart-row > div.chart-row__primary > div.chart-row__main-display > div.chart-row__container > div'
		sel = CSSSelector(selectorPath)
		result = sel(tree)
		song = result[0][0].text
		song = song.strip()
		artist = result[0][1].text
		artist = artist.strip()
		rank = str(i)
		SongInstance = SongIndex(song, artist, year, month, day, rank)
		songList.append(SongInstance)


# This function calls the scrape_billboard() function in a loop, with decreasing weeks. Essentially, this will allow you to change 
#  how many weeks of data you are collecting. The NumWeeks value is an integer which allows you specify that number of weeks
def loop_back_through_data(NumWeeks):
	global songList
	for i in range(0, NumWeeks):
		d = datetime.date(2016, 11, 5) - timedelta(days=7*i) #y, m, d
		scrape_billboard(d)
		time.sleep(5) #Add sleep here


def get_song_URI():
	global sp, songList, DelaySpotifySearch
	for i in range(0, len(songList)):
		time.sleep(DelaySpotifySearch)
		ArtistNameWithoutFt = songList[i].artistname.split('Featuring', 1)[0]
		ArtistNameWithoutFt = ArtistNameWithoutFt.split('&', 1)[0]
		ArtistNameWithoutFt = ArtistNameWithoutFt.split(' X ', 1)[0]
		ArtistNameWithoutFt = ArtistNameWithoutFt.split(' x ', 1)[0]
		ArtistNameWithoutFt = ArtistNameWithoutFt.replace("'", '')
		ArtistNameWithoutFt = ArtistNameWithoutFt.replace("*", '')
		SearchString = str(songList[i].songtitle) + ' ' + ArtistNameWithoutFt
		SearchResult = sp.search(SearchString, limit = 1, type = 'track')
		if (SearchResult['tracks']['total'] > 0):
			songList[i].uri = SearchResult['tracks']['items'][0]['uri']
		else:
			songList[i].uri = 'N'		

def get_spotify_details():
	global songList, sp, DelaySpotifySearch
	for i in range(0, len(songList)):
		time.sleep(DelaySpotifySearch)
		if (songList[i].uri != 'N'):
			#try:
			AudioFeatures_Array = sp.audio_features(songList[i].uri)
			AudioFeatures = AudioFeatures_Array[0]
			songList[i].audiofeatures = AudioFeatures
			songList[i].danceability = AudioFeatures['danceability']
			songList[i].energy = AudioFeatures['energy']
			songList[i].key = AudioFeatures['key']
			songList[i].loudness = AudioFeatures['loudness']
			songList[i].mode = AudioFeatures['mode']
			songList[i].speechiness = AudioFeatures['speechiness']
			songList[i].acousticness = AudioFeatures['acousticness']
			songList[i].liveness = AudioFeatures['liveness']
			songList[i].valence = AudioFeatures['valence']
			songList[i].tempo = AudioFeatures['tempo']
			songList[i].duration = AudioFeatures['duration_ms']
			songList[i].time_signature = AudioFeatures['time_signature']
			songList[i].analysis_url = AudioFeatures['analysis_url']
			#except: 
			#	print("An error in saving audio features occured with " + str(songList[i].songtitle))
			#	pass
		else:
			songList[i].audiofeatures = 'N'
			songList[i].danceability = 'N'
			songList[i].energy = 'N'
			songList[i].key = 'N'
			songList[i].loudness = 'N'
			songList[i].mode = 'N'
			songList[i].speechiness = 'N'
			songList[i].acousticness = 'N'
			songList[i].liveness = 'N'
			songList[i].valence = 'N'
			songList[i].tempo = 'N'
			songList[i].duration = 'N'
			songList[i].time_signature = 'N'
			songList[i].analysis_url = 'N'


def initialize_spotify():
	global username, scope, ClientID, ClientSecret, RedirectURI, sp
	token = util.prompt_for_user_token(Credentials.username, Credentials.scope, client_id = Credentials.ClientID, client_secret = Credentials.ClientSecret, redirect_uri = Credentials.RedirectURI)
	if token:
		sp = spotipy.Spotify(auth=token)
	else:
		print("Can't get token for", username)


def initialize_mysql():
	global db, cursor
	db = MySQLdb.connect(host=Credentials.sql_host, user=Credentials.sql_user, passwd=Credentials.sql_password, db=Credentials.sql_db)
	print("Connected to SQL database")
	cursor = db.cursor()


def update_sql():
	global songList, db, cursor
	for i in range(0, len(songList)):
		SongNameString = songList[i].songtitle.replace("'", "")
		SongNameString = SongNameString[:64]
		ArtistNameString = songList[i].artistname.replace("'", "")
		ArtistNameString = ArtistNameString[:64]
		sql = ("INSERT INTO songs(primary_key, song_name, artist_name, date_val, year_val, month_val, day_val, rank, URI)" 
			"VALUES('%s', '%s', '%s', '%s' , '%s', '%s', '%s', '%s', '%s' )" % (songList[i].primary_key, SongNameString, ArtistNameString, \
				songList[i].date, songList[i].year, songList[i].month, songList[i].day, songList[i].rank, songList[i].uri))
		cursor.execute(sql)
		db.commit()
	for i in range(0, len(songList)):
		if songList[i].uri != 'N':
			sql = ("INSERT INTO audiofeatures(primary_key, URI, danceability, energy, key_value, loudness, mode, speechiness, acousticness, liveness, valence, tempo, duration, timesignature, analysisurl)" 
				"VALUES('%s', '%s', '%s', '%s' , '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s' , '%s', '%s', '%s')" % (songList[i].primary_key, \
					songList[i].uri, songList[i].danceability \
					, songList[i].energy, songList[i].key, songList[i].loudness, songList[i].mode, songList[i].speechiness, songList[i].acousticness \
					, songList[i].liveness, songList[i].valence, songList[i].tempo, songList[i].duration, songList[i].time_signature, songList[i].analysis_url))
			cursor.execute(sql)
			db.commit()
	db.close()
	print('SQL Database Updated.')


def clear_sql_table():
	global db, cursor, songList
	for i in range(0, len(songList)):
		sql = "DELETE FROM `test`.`songs` WHERE `primary_key`=%s;" % (songList[i].primary_key)
		cursor.execute(sql)
		db.commit()
	for i in range(0, len(songList)):
		sql = "DELETE FROM `test`.`audiofeatures` WHERE `primary_key`=%s;" % (songList[i].primary_key)
		cursor.execute(sql)
		db.commit()


def main():
	global songList
	initialize_spotify()
	loop_back_through_data(1)
	get_song_URI()
	for i in range(0, len(songList)):
		songList[i].print_name()
		try:
			songList[i].print_uri()
		except:
			print("No URI Available")
	get_spotify_details()
	for i in range(0, len(songList)):
		songList[i].generate_primary_key()
	initialize_mysql()
	clear_sql_table()
	update_sql()


if __name__ == "__main__": 
	main()