from lxml import html
from lxml.cssselect import CSSSelector
import requests
import datetime
import urllib
from bs4 import BeautifulSoup

songList = []

# Class which is used to track song information
class SongIndex:
	def __init__(self, SongTitle, ArtistName, Year, Month, Day, Rank):
		self.songtitle = SongTitle
		self.artistname = ArtistName
		self.date = datetime.date(Year, Month, Day)
		self.rank = Rank

	def Print(self):
		print('Song: ' + str(self.songtitle) + ' by Artist: ' + str(self.artistname) + ' reached Rank: ' + str(self.rank) + ' on ' + str(self.date))
		print('This song has URI: ' + str(self.uri))


# Webscrapes from the billboard hot 100 list, to get the specific list for a year, date, and month
def ScrapeBillboard(year, month, day):
	global songList
	date = str(datetime.date(year, month, day))
	pageURL = 'https://www.billboard.com/charts/hot-100/' + date
	pageContent = requests.get(pageURL)
	tree = html.fromstring(pageContent.content)
	for i in range(1,5):
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


# Uses a simple url search to splice the uri of the track, on spotify. This will be used later to search through spotify. 
def GetSongURI():
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
					#print(songList[i].songtitle + " " + SearchResultURLSplit[2][:-1])
					songList[i].uri = uri
					break
	except:
		print("An error occured.")
					

def main():
	global songList
	ScrapeBillboard(2018,3,17)
	GetSongURI()
	for i in range(0,len(songList)):
		songList[i].Print()


if __name__ == "__main__": main()