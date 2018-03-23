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

songList = []
sp = ''
ClientID 		= 'cdf75d8320f640d09cc179c34d18e803'
ClientSecret 	= 'f9be99648e40467f8c52a3bc7ef2d65a'
RedirectURI 	= 'http://localhost:/callback'
UserID 			= '1224319843'
username		= 'semcmill'
scope 			= 'user-library-read'

# Class which is used to track song information
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


def loop_back_through_data():
	global songList
	for i in range(0,3):
		d = datetime.date(2017, 9, 30) - timedelta(days=7*i)
		scrape_billboard(d)


# Uses a simple url search to splice the uri of the track, on spotify. This will be used later to search through spotify. 
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
	try:
		for i in range(0, len(songList)):
			if (songList[i].uri != 'N'):
				AudioFeatures = sp.audio_features(songList[i].uri)
				songList[i].audiofeatures = AudioFeatures[0]
			else:
				songList[i].audiofeatures = 'N'
	except:
		print('No URI')


def initialize_spotify():
	global username, scope, ClientID, ClientSecret, RedirectURI, sp
	token = util.prompt_for_user_token(username, scope, client_id = ClientID, client_secret = ClientSecret, redirect_uri = RedirectURI)
	if token:
		sp = spotipy.Spotify(auth=token)
	else:
		print("Can't get token for", username)


def main():
	global songList
	loop_back_through_data()
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
	#numpy.savetxt("test.txt", str(songList), newline = " ")


if __name__ == "__main__": main()