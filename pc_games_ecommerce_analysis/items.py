from datetime import date, datetime

from scrapy import Field, Item


def serialize_date(date_str: str) -> date:
    return datetime.strptime(date_str, '%d/%m/%Y').date()

class NuuvemItem(Item):
    title = Field()
    drm =  Field()
    os = Field()
    price = Field(serializer=float)
    release_date = Field(serializer=serialize_date)
    developer = Field()
    publisher = Field()
    genre = Field()
    game_mode = Field()
    rate = Field()