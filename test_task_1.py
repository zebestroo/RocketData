import requests
import json
import re
from scrapy.selector import Selector


def parse_latlon_from_url(map_url: str):
    coords_re = re.compile(r'\!2d([^!]+)\!3d([^!]+)')
    return list(map(float, coords_re.search(map_url).group(1, 2)))


def working_time_parse_func(span_list):
    morning_time_list = span_list[0].replace('.', ':').split(' ')
    evening_time_list = span_list[1].replace('.', ':').split(' ')
    mon_thu_time = 'mon-thu ' + morning_time_list[2] + '-' + morning_time_list[4] + ' ' \
        + evening_time_list[2] + '-' + evening_time_list[4]
    fri_time = 'fri ' + morning_time_list[2] + '-' + morning_time_list[4] + ' ' \
        + evening_time_list[2] + '-' + evening_time_list[-3]
    return [mon_thu_time, fri_time]


main_response = requests.get('https://oriencoop.cl/sucursales.htm')
main_list = []

pages = [st.split('/')[-1] for st in Selector(
    text=main_response.text).xpath("//ul[@class='sub-menu']/li/a/@href").extract()]


for page in pages:

    response = requests.get('https://oriencoop.cl/sucursales/' + page)
    print('Collecting data from ' + page + ' page...')


    div = Selector(text=response.text).xpath(
        "//div[@class='s-dato']/p").extract()
    mapa_url = Selector(text=response.text).xpath(
        "//div[@class='s-mapa']/iframe/@src").get()

    data = dict()

    time_span_list = Selector(text=div[3]).xpath("//span/text()").extract()

    data['address'] = Selector(text=div[0]).xpath("//span/text()").get()
    data['latlon'] = parse_latlon_from_url(mapa_url)
    data['name'] = Selector(text=response.text).xpath(
        '//div[@class="s-dato"]/h3/text()').get()
    data['phones'] = [
        Selector(text=div[1]).xpath("//span/text()").get(),
        *Selector(text=response.text).xpath("//li[@class='call']/a/text()").extract()
    ]
    data['working_hours'] = working_time_parse_func(time_span_list)
    main_list.append(data)

print(json.dumps(main_list, indent=4, ensure_ascii=False))
