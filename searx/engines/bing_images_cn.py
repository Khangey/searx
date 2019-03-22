"""
 Bing (Images)

 @website     https://www.bing.com/images
 @provide-api yes (http://datamarket.azure.com/dataset/bing/search),
              max. 5000 query/month

 @using-api   no (because of query limit)
 @results     HTML (using search portal)
 @stable      no (HTML can change)
 @parse       url, title, img_src
"""

from lxml import html
from json import loads
import re
from searx.url_utils import urlencode

# engine dependent config
categories = ['images']
paging = True
language_support = False
time_range_support = True

# search-url
base_url = 'https://www.bing.com/'
search_string = 'images/search?{query}&first={offset}&count=35'
time_range_string = '&qft=+filterui:age-lt{interval}'
time_range_dict = {'day': '1440',
                   'week': '10080',
                   'month': '43200',
                   'year': '525600'}


_quote_keys_regex = re.compile('({|,)([a-z][a-z0-9]*):(")', re.I | re.U)


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 35 + 1

    search_path = search_string.format(
        query=urlencode({'q': query}),
        offset=offset)

    params['url'] = base_url + search_path
    if params['time_range'] in time_range_dict:
        params['url'] += time_range_string.format(interval=time_range_dict[params['time_range']])

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    # parse results
    for result in dom.xpath('//div[@id="mmComponent_images_1"]/ul/li/div/div[@class="imgpt"]'):
        link = result.xpath('./a')[0]

        # TODO find actual title
        title = link.xpath('.//img/@alt')[0]

        # parse json-data (it is required to add a space, to make it parsable)
        json_data = loads(_quote_keys_regex.sub(r'\1"\2": \3', link.attrib.get('m')))

        url = json_data.get('purl')
        img_src = json_data.get('murl')
        thumbnail = json_data.get('turl')

        # append result
        results.append({'template': 'images.html',
                        'url': url,
                        'title': title,
                        'content': '',
                        'thumbnail_src': thumbnail,
                        'img_src': img_src})

    # return results
    return results
