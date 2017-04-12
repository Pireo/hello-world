#VERSION: 1
#AUTHORS: Charles Worthing
# qBittorrent search enging plugin for BTDB.IN
#
#


from HTMLParser import HTMLParser
#qBt
from novaprinter import prettyPrinter
from helpers import download_file, retrieve_url

class btdb(object):
    """ Search engine class """
    url = 'https://btdb.in'
    name = 'BitTorrent Database'

    def download_torrent(self, info):
        """ Downloader """
        print(download_file(info))

    class MyHtmlParseWithBlackJack(HTMLParser):
        """ Parser class """
        def __init__(self, list_searches, url):
            HTMLParser.__init__(self)
            self.list_searches = list_searches
            self.url = url
            self.current_item = {} # One torrent result
            self.add_query = True
            self.torrent_info_index = 0 # Count of the meta data encountered
            self.torrent_info_array = []
            self.meta_data_grabbing = 0
            self.meta_data_array = []
            self.torrent_no_files = 0
            self.torrent_date_added = 0
            self.torrent_popularity = 0
            self.torrent_link = ""
            self.torrent_name = ""

        def handle_starttag(self, tag, attrs):
            if tag == "span":
                span_dict = dict(attrs)
                if "class" in span_dict:
                    the_class = span_dict["class"]
                    if the_class == "item-meta-info-value":
                        self.meta_data_grabbing += 1
                    else:
                        self.meta_data_grabbing = 0
            if tag == "script":
                return
            if tag == "li":
                for attr in attrs:
                    if attr[1] == "search-ret-item":
                        self.torrent_info_index = 1
            if tag == "a":
                if self.torrent_info_index > 0:
                    params = dict(attrs)
                    if "href" in params:
                        link = params["href"]
                        if link.startswith("/torrent"):
                            self.torrent_link = "".join((self.url, link))
                            self.torrent_name = params["title"]

        def handle_endtag(self, tag): 
            if tag == "script":
                return
            if tag == "div":
                if self.meta_data_grabbing >0:
                    
                    self.torrent_no_files = self.meta_data_array[2] # Not used
                    self.torrent_date_added = self.meta_data_array[4] # Not used
                    self.torrent_popularity = self.meta_data_array[6] # Not used


                    self.current_item["size"] = self.meta_data_array[0]
                    self.current_item["name"] = self.torrent_name
                    self.current_item["engine_url"] = self.url
                    self.current_item["link"] = self.torrent_link
                    self.current_item["seeds"] = -1
                    self.current_item["leech"] = -1

                    prettyPrinter(self.current_item)
                    self.current_item = {}

                    self.meta_data_grabbing = 0
                    self.meta_data_array = []
                    self.torrent_link = ""
                    self.torrent_name = ""


        def handle_data(self, data):
            if self.torrent_info_index > 0:
            	self.torrent_info_array.append(data)
            	self.torrent_info_index += 1
            if self.meta_data_grabbing > 0:
            	self.meta_data_array.append(data)
            	self.meta_data_grabbing += 1

        def handle_entityref(self, name):
            c = unichr(name2codepoint[name])

        def handle_charref(self, name):
            if name.startswith('x'):
                c = unichr(int(name[1:], 16))
            else:
                c = unichr(int(name))


    def search(self, what, cat='all'):
        """ Performs search """
        #prepare query. 7 is filtering by seeders
        cat = cat.lower()
        query = "/".join((self.url, "q", what))

        response = retrieve_url(query)


        list_searches = []
        parser = self.MyHtmlParseWithBlackJack(list_searches, self.url)
        parser.feed(response)
        parser.close()

        parser.add_query = False
        for search_query in list_searches:
            response = retrieve_url(self.url + search_query)
            parser.feed(response)
            parser.close()

        return
