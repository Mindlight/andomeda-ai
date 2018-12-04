import articleDateExtractor
import plac
import urllib2,re, json
from dateutil.parser import parse
try:
    from bs4 import BeautifulSoup
except ImportError:
    from BeautifulSoup import BeautifulSoup



def extractDateMe(articleLink, html = None):

    articleDate = None

    try:
        articleDate = articleDateExtractor._extractFromURL(articleLink)

        if html is None:
            request = urllib2.Request(articleLink)
            # Using a browser user agent, decreases the change of sites blocking this request - just a suggestion
            # request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36')
            html = urllib2.build_opener().open(request).read()

        parsedHTML = BeautifulSoup(html,"lxml")

        possibleDate = articleDateExtractor._extractFromLDJson(parsedHTML)
        if possibleDate is None:
            possibleDate = articleDateExtractor._extractFromMeta(parsedHTML)
        if possibleDate is None:
            possibleDate = articleDateExtractor._extractFromHTMLTag(parsedHTML)


        articleDate = possibleDate

    except Exception as e:
        print "Exception in extractArticlePublishedDate for " + articleLink
        print e.message, e.args



    return articleDate
    


def main(url):

	d = extractDateMe(url)
	
	print d
         
if __name__ == '__main__':
    plac.call(main)



