import pandas as pd
import numpy as np
import json
import re
import unidecode

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class CarrosMercadoLivreSpider(CrawlSpider):
    name = "carros_mercado_livre"
    start_urls = ["https://lista.mercadolivre.com.br/veiculos/carros-caminhonetes/"]

    rules = (
        Rule(LinkExtractor(allow='/veiculos/carros-caminhonetes/')),
        Rule(LinkExtractor(allow='/MLB-\d+'), callback='parse_item')
    )

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'DOWNLOAD_DELAY': 1, # espera de 1 segundos antes de baixar a próxima página
    }

    def parse_item(self, response):
        yield {
            'name': response.xpath('.//h1[@class="ui-pdp-title"]//text()').get(),
            'price': response.xpath('.//span[@class="andes-money-amount__fraction"]//text() ').get(),
            'services': response.xpath('.//div[@class="ui-pdp-highlighted-sale-specs__specs-list"]'
                                       '//p[@class="ui-pdp-color--BLACK ui-pdp-size--XSMALL ui-pdp-family--REGULAR"]//text()').getall(),
            'details': response.xpath('.//th[@class="andes-table__header andes-table__header--left ui-pdp-specs__table__column ui-pdp-specs__table__column-title"]//text()').getall(),
            'response_details': response.xpath('.//td[@class="andes-table__column andes-table__column--left ui-pdp-specs__table__column"]//span[@class="andes-table__column--value"]//text()').getall()
        }


