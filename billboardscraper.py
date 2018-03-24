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
import numpy
import MySQLdb

# It will be necessary to create a credentialfiles.py file, which has a class Credentials. This class should only contain
#  ClientID, ClientSecret, RedirectURI, UserID, Username, and Scope. Refer to readme for more information, and spotipy documentation 
#  on authentication
from credentialfiles import Credentials

songList = []
sp = ''

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
	for i in range(1,3):
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
		d = datetime.date(2018, 3, 17) - timedelta(days=7*i)
		scrape_billboard(d)


# Uses a simple url search to splice the uri of the track, on spotify. This will be used later to search through spotify. 
#  Although not the most effecient way, this is a safe and easy way to bypass spotify's x requests a second, and can be done much faster,
#  assuming a stable internet connection. If the song is not found to have an URI (if no links include spotify.com/track/), then an 
#  'N' is inserted instead.
def get_song_URI():
	global songList
	try:
		for i in range(0, len(songList)):
			url = "http://www.ask.com/web?q=spotify+" + str(songList[i].songtitle) + '+' + str(songList[i].artistname) 
			url	= url.replace(" ", "+")
			html = urllib.request.urlopen(url)
			soup = BeautifulSoup(html, 'html.parser')
			SearchResultURLS = soup.find_all('p', {'class':"PartialSearchResults-item-url"})
			for url in SearchResultURLS:
				if "open.spotify.com/track/" in str(url):
					SearchResultURLSplit = str(url).split('/')
					uri = SearchResultURLSplit[2][:-1]
					songList[i].uri = uri
					break
				else:
					songList[i].uri = 'N'
	except:
		print("An error occured.")
					

def get_spotify_details():
	global songList, sp
	for i in range(0, len(songList)):
		if (songList[i].uri != 'N'):
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


def main():
	global songList
	loop_back_through_data(1)
	get_song_URI()
	for i in range(0, len(songList)):
		songList[i].print_name()
		try:
			songList[i].print_uri()
		except:
			print("No URI Available")
	initialize_spotify()
	get_spotify_details()
	for i in range(0, len(songList)):
		songList[i].print_features()


if __name__ == "__main__": main()