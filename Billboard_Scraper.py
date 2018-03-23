from lxml import html
from lxml.cssselect import CSSSelector
import requests
import datetime

songList = []

class SongIndex:
	def __init__(self, SongTitle, ArtistName, Year, Month, Day, Rank):
		self.songtitle = SongTitle
		self.artistname = ArtistName
		self.date = datetime.date(Year, Month, Day)
		self.rank = Rank
	
	def Print(self):
		print('Song: ' + str(self.songtitle) + ' by Artist: ' + str(self.artistname) + ' reached Rank: ' + str(self.rank) + ' on ' + str(self.date))

def ScrapeBillboard(year, month, day):
	global songList
	pageContent = requests.get('https://www.billboard.com/charts/hot-100/2018-03-17')
	tree = html.fromstring(pageContent.content)
	for i in range(1,100):
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
		#SongInstance.Print()

def main():
	global songList
	ScrapeBillboard(2018,3,17)
	for i in range(0,99):
		songList[i].Print()


if __name__ == "__main__": main()