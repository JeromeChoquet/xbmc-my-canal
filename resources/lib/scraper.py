'''
    academicearth.scraper
    ~~~~~~~~~~~~~~~~~~~~~

    This module contains some functions which do the website scraping for the
    API module. You shouldn't have to use this module directly.

    This module is meant to emulate responses from a "virtual" API server. All
    website scraping is handled in this module, and clean dict responses are
    returned. The `api` module, acts as a python client library for this
    module's API.
'''
import urllib2
import pprint
import json


authenticateUrl = "http://service.mycanal.fr/authenticate.json/iphone/1.0?highResolution=1&paired=0&pdsDevice=%5B1%5D"
my_canal_ua = 'myCANAL/1.0.2 CFNetwork/609.1.4 Darwin/13.0.0'

def get(url):
    '''Performs a GET request for the given url and returns the response'''
    opener = urllib2.build_opener()
    opener.addheaders = [('User-Agent', my_canal_ua)]
    #print 'url: '
    #print url
    response = opener.open(url)

    if response and response.getcode() == 200:
        content = response.read()
    else:
         print 'Could not open URL %s to create menu' % (url)
    #print 'content: '
    #print content
    return content

def _authenticate():
    return get(authenticateUrl)

class Emission(object):

    @classmethod
    def get_emissions(cls):
        '''Returns a list of emissions available on the website.'''
        content = _authenticate()
        output_json = json.loads(content)
        output_json['arborescence'] = dict((arbo['displayName'], arbo) for arbo in output_json['arborescence'])
        a_la_demande = output_json['arborescence']['A la demande']
        emissionsUrl = a_la_demande['onClick']['URLPage'];

        content = get(emissionsUrl)
        output_json = json.loads(content)
        strates = output_json['strates'][1]['contents']

        emissions = [{
            'name': emission['onClick']['displayName'].strip(),
            'url': emission['onClick']['URLPage'],
            'icon': emission['URLImage'],
        } for emission in strates]

        #pprint.pprint(emissions)
        return emissions;

class Video(object):

    @classmethod
    def from_url(cls, url):
        content = get(url)
        output_json = json.loads(content)
        videos=[]

        for strate in output_json['strates']:
            if strate['type'] == 'contentRow' or strate['type'] == 'contentGrid':
                for item in strate['contents']:
		    if item['type'] != 'landing':
		        name = ''
		        if 'title' in item:
		            name = item['title']
		            if 'subtitle' in item:
			        name = name + ' - ' + item['subtitle']
		        else:
			    name = item['subtitle']
                        videos.append( { 'name': name.strip(),
                            'url': item['onClick']['URLMedias'].replace('{FORMAT}','hls'),
                            'icon': item['URLImage']})
        #pprint.pprint(videos)
        return videos

    @staticmethod
    def get_name(html):
        return html.find('section', {'class': 'pagenav'}).span.text

    @staticmethod
    def get_lectures(html):
        return _get_courses_or_lectures('lecture', html)

class Media(object):

    @classmethod
    def from_url(cls, url):
        content = get(url)
        output_json = json.loads(content)
	informations = output_json['detail']['informations']
	media_url = informations['videoURLs'][0]['videoURL']
        media= { 'name': informations['title'].strip(), 
		 'url': media_url,
                 'icon': informations['URLImage']}
        #pprint.pprint(videos)
        return media
