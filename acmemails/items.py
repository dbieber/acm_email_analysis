# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class ACMEmailItem(Item):
    sender = Field()
    sender_email = Field()
    date = Field()
    size = Field()
    subject = Field()
    message = Field()
    message_html = Field()
    has_attachment = Field()
    attachment_name = Field()
