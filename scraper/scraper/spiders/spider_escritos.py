import scrapy
import re
from scraper.items import EscritosItem 

class SpiderEscritos(scrapy.Spider):
    name = 'spider_escritos'
    allowed_domains = ['filosofia.org']
    start_urls = ['https://www.filosofia.org/cla/pla/azcarate.htm']

    def parse(self, response):
        # Extraer enlaces principales (aquellos que empiezan con 'azf')
        enlaces_principales = response.css('td a[href^="azf"]::attr(href)').getall()

        for enlace in enlaces_principales:
            # Convertir enlaces relativos en absolutos
            url_completa = response.urljoin(enlace)
            # Enviar solicitud para procesar la página detalle
            yield scrapy.Request(url_completa, callback=self.parse_pagina_detalle)

    def parse_pagina_detalle(self, response):
        # Crear una instancia de EscritosItem
        item = EscritosItem()

        # Extraer el título de la página
        item['titulo'] = response.css('h1::text').get()

        # Extraer contenido de los párrafos
        contenido = response.css('p::text').getall()

        # Limpiar contenido para eliminar líneas irrelevantes
        item['contenido'] = [
            re.sub(r'\[\d+\]', '', linea)  # Elimina los números entre corchetes
            for linea in contenido
            if not re.search(r'tomo \d+,.*\d{4},.*págs\..*', linea)
        ]

        yield item
