from typing import Iterator, Literal

from bs4 import BeautifulSoup
from scrapy.http import Response
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule

from pc_games_ecommerce_analysis.items import NuuvemItem


class NuuvemSpider(CrawlSpider):
    name = 'nuuvem'
    allowed_domains = ['nuuvem.com']
    rules = [
        Rule(LinkExtractor(allow="/item"), callback="parse"),
    ]
    
    def __init__(self, total_pages: int = 160, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.start_urls = self._create_url(total_pages)
        self.logger.info('Created all links to scrape')

    @staticmethod
    def _create_url(max_pages: int) -> Iterator[str]:
        """Function to create games catalog url pages.

        Yields:
            str: Url to make requests.
        """
        start_url = 'https://www.nuuvem.com/br-en/catalog/platforms/pc/types/games'
        for index in range(1, max_pages):
            url = start_url + f'/page/{index}' if index != 1 else start_url
            yield url
        
    def parse(self, response: Response) -> NuuvemItem:
        loader = ItemLoader(item=NuuvemItem())
        loader = self._parse_product_header(loader, response)
        loader = self._parse_price(loader, response)
        loader = self._parse_date_developer_publisher(loader, response)
        loader = self._parse_genre(loader, response)
        loader = self._parse_game_mode(loader, response)
        loader = self._parse_ratings(loader, response)
        return loader.load_item()
    
    def _parse_product_header(self, loader: ItemLoader, response: Response) -> ItemLoader:
        xpath = '/html/body/div[3]/div/main/div[3]/div[{}]/header'
        header = self.__correct_xpath(xpath, response)
        loader.add_value('title', header.css('h1 span ::text').get())
        loader.add_value('drm', header.css('ul li a div span  ::text').get())
        loader.add_value('os', header.xpath('ul[2]/li/a/div/span/text()').getall())
        return loader
        
    def _parse_price(self, loader: ItemLoader,  response: Response) -> ItemLoader:
        price = response.xpath('/html/body/div[3]/div/main/div[3]')
        soup = BeautifulSoup(price.get(), "html.parser")
        product_price = 'product-price--old'
        if product_price not in price.get():
            product_price = 'product-price--val'
        price = soup.find('span', class_=product_price).get_text()
        price = price.replace('\n', '').strip()
        loader.add_value('price', price)
        return loader
    
    def _parse_date_developer_publisher(self, loader: ItemLoader, response: Response) -> ItemLoader:
        xpath = '//*[@id="product"]/div[{}]/div/aside[2]/div/div[1]/ul'
        rows = self.__correct_xpath(xpath, response)
        rows = BeautifulSoup(rows.get(), "html.parser").find_all('li')
        for item in rows:
            values = item.get_text().replace('\n', '').split(':')
            values = [value.strip() for value in values]
            loader.add_value(values[0].lower().replace(' ', '_'), values[1])
        return loader
    
    def _parse_genre(self, loader: ItemLoader, response: Response) -> ItemLoader:
        xpath = '/html/body/div[3]/div/main/div[3]/div[{}]/div/aside[2]/div/div[2]/ul'
        genre = self.__correct_xpath(xpath, response)
        genre = genre.css('li ::text').getall()
        loader.add_value('genre', genre)
        return loader

    def _parse_game_mode(self, loader: ItemLoader, response: Response) -> ItemLoader:
        xpath = '/html/body/div[3]/div/main/div[3]/div[{}]/div/aside[2]/div/div[3]/ul'
        rows = self.__correct_xpath(xpath, response)
        new_rows = []
        for row in rows.css('li ::text').getall():
            row = row.replace('\n', '').strip() 
            if len(row) != 0: 
                new_rows.append(row)
        loader.add_value('game_mode', new_rows)
        return loader
    
    def _parse_ratings(self, loader: ItemLoader, response: Response) -> ItemLoader:
        xpath = '/html/body/div[3]/div/main/div[3]/div[{}]/div/aside[2]/div/div[{}]/ul/li/div[2]/h4/text()'
        rating = self.__correct_xpath(xpath, response, mode='alternative')
        loader.add_value('rate', rating.get())
        return loader
    
    def __correct_xpath(
        self,
        xpath_string: str,
        response: Response,
        mode: Literal['standard', 'alternative'] = 'standard'
    ) -> Response:
        match mode:
            case 'standard':
                for div in (5, 4, 3):
                    result = response.xpath(xpath_string.format(div))
                    if len(result) != 0:
                        break
            case 'alternative':
                for divs in [(5, 5), (4, 3), (4, 5)]:
                    result = response.xpath(xpath_string.format(*divs))
                    if len(result) != 0:
                        break
            case _:
                msg = f"""
                There's no mode {mode} implemented! Choose 'standard' or 'alternative'.
                """
                raise NotImplementedError(msg)
        return result
    