"""
 Bing (Web)

 @website     https://www.bing.com
 @provide-api yes (http://datamarket.azure.com/dataset/bing/search),
              max. 5000 query/month

 @using-api   no (because of query limit)
 @results     HTML (using search portal)
 @stable      no (HTML can change)
 @parse       url, title, content
"""

from lxml.html import fromstring
from searx.engines.xpath import extract_text
from searx.url_utils import urlencode
from searx.utils import gen_useragent

# engine dependent config
categories = ['general']
paging = True
language_support = False
time_range_support = True

# search-url
base_url = 'https://www.bing.com/'
search_string = 'search?{query}&first={offset}'
time_range_url = '&filters={range}'

time_range_dict = {'day': 'ex1:"ez1"',
                   'week': 'ex1:"ez2"',
                   'month': 'ex1:"ez3"'}

# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 10 + 1

    search_path = search_string.format(
        query=urlencode({'q': query}),
        offset=offset)

    params['url'] = base_url + search_path

    params['headers']['User-Agent'] = gen_useragent('Macintosh; Intel Mac OS X 10_13_6')

    if params['time_range'] in time_range_dict:
        params['url'] += time_range_url.format(range=time_range_dict[params['time_range']])

    return params


# get response from search-request
def response(resp):
    results = []

    dom = fromstring(resp.text)

    try:
        count = dom.xpath('//span[@class="sb_count"]/text()')[0].split(' ')
        if len(count) > 2:
            count = count[-2]
        else:
            count = count[0]
        results.append({'number_of_results': int(count.replace(',', ''))})
    except:
        pass

    # parse results
    lists = dom.xpath('//ol[@id="b_results"]')[0]

    for result in lists.xpath('//li[@class="b_algo"]'):
        link = result.xpath('.//h2/a')[0]
        url = link.attrib.get('href')
        title = extract_text(link)
        content = extract_text(result.xpath('.//div[@class="b_caption"]//p[1]'))

        # append result
        results.append({'url': url,
                        'title': title,
                        'content': content})

    # return results
    return results
