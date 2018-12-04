import plac
import requests
from readability import Document
from bs4 import BeautifulSoup

def main(url):
	# the_url = requests.get(url).text
	f = open(url,"r")
	doc = Document(f.read())
	res = doc.title()	
	print(res)
	res = doc.summary(html_partial=True)	
	print(res)
         
if __name__ == '__main__':
    plac.call(main)
    
