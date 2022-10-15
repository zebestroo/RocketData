import requests
import json
import re
from scrapy.selector import Selector


response = requests.get('https://naturasiberica.ru/our-shops/')

items = Selector(text=response.text).xpath('//p[@class="card-list__description"]/text()').extract()

pages = [item.split('/')[-2] for item in Selector(text=response.text).xpath('//a[@class="card-list__link"]/@href').extract()]

headline = Selector(text=response.text).xpath('//*[@id="bx_1573527503_444"]/div[2]/h2/text()').get().split(' ')
name = headline[-2] + ' ' + headline[-1]

adrs = []

main_list = []


for item in items:
    adrs.append(item.replace('\t', '').replace('\r\n', ''))

for i, page in enumerate(pages):
    dc = dict()
    dc['address'] = adrs[i]

    #session = HTMLSession()

    response = requests.get(f'https://www.google.com/maps/search/{adrs[i]}')
    #response.html.render(timeout=20)
    dc['latlon'] = [float(coord) for coord in re.split('&|=|%2C', Selector(text=response.text).xpath('//meta[@itemprop="image"]/@content').get())[1:3]]

    res = requests.get('https://naturasiberica.ru/our-shops/' + page)

    dc['name'] = name
    dc['phones'] = Selector(text=res.text).xpath('//*[@id="shop-phone-by-city"]/text()').extract()
    dc['working_hours'] = Selector(text=res.text).xpath('//*[@id="schedule1"]/text()').extract()
    print(f'Collecting data from {page}... ' + f'{i+1} of {len(pages)}')
    main_list.append(dc)

print(json.dumps(main_list, indent=4, ensure_ascii=False))
