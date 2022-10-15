import requests
from urllib import request
import json
import re
from scrapy.selector import Selector


response = requests.get('https://som1.ru/shops/',
                        headers={'User-Agent': 'My User Agent 1.0'})


scripts = Selector(text=response.text).xpath("//script/text()").extract()
divs = Selector(text=response.text).xpath(
    "//div[@class='shops-address']/text()").extract()


ls = [script.replace("cords", "latlon")
      for script in scripts if 'showShopsMap' in script]


def func(st: str):
    coords_re = re.compile(r'\((.+)\)')
    js = json.loads(coords_re.search(st).group(1).replace("'", '"'))
    return js


ls = func(ls[0])

for dc in ls:
    l = [float(cord) for cord in dc['latlon']]
    dc['latlon'] = l

for i, div in enumerate(divs):
    ls[i]['address'] = div


pages = [link.split('/')[-2] for link in Selector(
    text=response.text).xpath("//a[@class='btn btn-blue']/@href").extract()]

for i, dc in enumerate(ls):
    response = requests.get('https://som1.ru/shops/' +
                            pages[i] + '/', headers={'User-Agent': 'My User Agent 1.0'})
    tbodys = Selector(text=response.text).xpath(
        "//table[@class='shop-info-table']/tr/td/text()").extract()
    dc['phones'] = tbodys[-4].split(',')
    dc['working_hours'] = [tbodys[-1]]


print(json.dumps(ls, indent=4, ensure_ascii=False))
