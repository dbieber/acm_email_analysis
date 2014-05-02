from scrapy.spider import BaseSpider
from scrapy.selector import XPathSelector
from scrapy.http import Request
from scrapy.http import FormRequest

from acmemails.items import *
from getpass import getpass

password = getpass()
count = 0

def get_href(sel, xpath):
    return sel.select(("%s/@href" % xpath).replace("/tbody","")).extract()[0]

def select(sel, xpath):
    return sel.select(xpath.replace("/tbody",""))

def select_if_exists(sel, xpath):
    text = sel.select(xpath)
    if text:
        return text.extract()[0]

class ACMEmailsSpider(BaseSpider):
    name = "acm_emails"
    allowed_domains = ["princeton.edu", "lists.princeton.edu"]

    start_urls = [a % {"token": "12A1B40B94DD71F62A", "email": "dbieber@princeton.edu"} for a in [
        "https://lists.princeton.edu/cgi-bin/wa?A1=ind1404&L=PrincetonACM&X=%(token)s&Y=%(email)s",
        "https://lists.princeton.edu/cgi-bin/wa?A1=ind1403&L=PrincetonACM&X=%(token)s&Y=%(email)s",
        "https://lists.princeton.edu/cgi-bin/wa?A1=ind1402&L=PrincetonACM&X=%(token)s&Y=%(email)s",
        "https://lists.princeton.edu/cgi-bin/wa?A1=ind1401&L=PrincetonACM&X=%(token)s&Y=%(email)s",
        "https://lists.princeton.edu/cgi-bin/wa?A1=ind1312&L=PrincetonACM&X=%(token)s&Y=%(email)s",
        "https://lists.princeton.edu/cgi-bin/wa?A1=ind1311&L=PrincetonACM&X=%(token)s&Y=%(email)s",
        "https://lists.princeton.edu/cgi-bin/wa?A1=ind1310&L=PrincetonACM&X=%(token)s&Y=%(email)s",
        "https://lists.princeton.edu/cgi-bin/wa?A1=ind1309&L=PrincetonACM&X=%(token)s&Y=%(email)s",
        "https://lists.princeton.edu/cgi-bin/wa?A1=ind1308&L=PrincetonACM&X=%(token)s&Y=%(email)s",
        "https://lists.princeton.edu/cgi-bin/wa?A1=ind1305&L=PrincetonACM&X=%(token)s&Y=%(email)s",
        "https://lists.princeton.edu/cgi-bin/wa?A1=ind1304&L=PrincetonACM&X=%(token)s&Y=%(email)s",
        "https://lists.princeton.edu/cgi-bin/wa?A1=ind1303&L=PrincetonACM&X=%(token)s&Y=%(email)s",
        "https://lists.princeton.edu/cgi-bin/wa?A1=ind1302&L=PrincetonACM&X=%(token)s&Y=%(email)s",
        "https://lists.princeton.edu/cgi-bin/wa?A1=ind1301&L=PrincetonACM&X=%(token)s&Y=%(email)s",
        "https://lists.princeton.edu/cgi-bin/wa?A1=ind1212&L=PrincetonACM&X=%(token)s&Y=%(email)s",
        "https://lists.princeton.edu/cgi-bin/wa?A1=ind1211&L=PrincetonACM&X=%(token)s&Y=%(email)s",
        "https://lists.princeton.edu/cgi-bin/wa?A1=ind1210&L=PrincetonACM&X=%(token)s&Y=%(email)s",
        "https://lists.princeton.edu/cgi-bin/wa?A1=ind1209&L=PrincetonACM&X=%(token)s&Y=%(email)s",
        "https://lists.princeton.edu/cgi-bin/wa?A1=ind1208&L=PrincetonACM&X=%(token)s&Y=%(email)s",
        "https://lists.princeton.edu/cgi-bin/wa?A1=ind1207&L=PrincetonACM&X=%(token)s&Y=%(email)s",
        "https://lists.princeton.edu/cgi-bin/wa?A1=ind1206&L=PrincetonACM&X=%(token)s&Y=%(email)s",
        "https://lists.princeton.edu/cgi-bin/wa?A1=ind1205&L=PrincetonACM&X=%(token)s&Y=%(email)s",
        "https://lists.princeton.edu/cgi-bin/wa?A1=ind1204&L=PrincetonACM&X=%(token)s&Y=%(email)s",
        "https://lists.princeton.edu/cgi-bin/wa?A1=ind1203&L=PrincetonACM&X=%(token)s&Y=%(email)s"
    ]]

    def parse(self, response):
        sel = XPathSelector(response)
        rows = sel.select("/html/body/table/tbody/tr/td/table[5]/tbody/tr/td/table[1]/tbody/tr[2]/td[1]/table[1]/tbody/tr[position() > 1]".replace("/tbody",""))


        items = []
        for row in rows:
            email = ACMEmailItem()
            email['subject'] = select_if_exists(row, "./td[1]/p/span/a/text()")
            email['sender'] = select_if_exists(row, "./td[2]/p/text()")
            email['date'] = select_if_exists(row, "./td[3]/p/text()")
            email['size'] = select_if_exists(row, "./td[4]/p/text()")
            if not email['size']:
                continue

            partial_url = select_if_exists(row, "./td[1]/p/span/a/@href")
            message_url = "https://lists.princeton.edu/%s" % partial_url

            def create_message_parser(email):

                def parse_message(response):
                    sel = XPathSelector(response)
                    text_link = select(sel, "/html/body/table/tbody/tr/td/table[5]/tbody/tr/td/table[1]/tbody/tr[2]/td[1]/table/tbody/tr/td/table/tbody/tr[1]/td[1]/table/tbody/tr[6]/td[3]/table/tbody/tr/td[2]/p/a[1]")
                    attachment = select(sel, "/html/body/table/tbody/tr/td/table[5]/tbody/tr/td/table[1]/tbody/tr[2]/td[1]/table/tbody/tr/td/table/tbody/tr[1]/td[1]/table/tbody/tr[6]/td[3]/table/tbody/tr/td[2]/p/a[3]")

                    raw_message_parser = create_raw_message_parser(email, text_link)
                    if attachment:
                        email['has_attachment'] = True
                        email['attachment_name'] = attachment.select("./text()").extract()[0]

                    partial_src = select_if_exists(sel, '//*[@id="awesomepre"]/iframe/@src')
                    if partial_src:
                        # Load the iframe and parse that
                        msg_src = "https://lists.princeton.edu%s" % partial_src
                        return [Request(msg_src, callback=raw_message_parser)]
                    else:
                        # The email is text/plain, rather than being in an iframe
                        messages = sel.select('//*[@id="awesomepre"]/pre')
                        if messages:
                            email['message'] = ' '.join(messages.select(".//text()").extract())
                            email['message_html'] = messages.extract()[0]
                        return [email]

                return parse_message

            def create_raw_message_parser(email, text_link):
                def parse_raw_message(response):
                    sel = XPathSelector(response)
                    if sel.select("//form"):
                        return [FormRequest.from_response(response,
                            formdata={'Y': 'dbieber@princeton.edu', 'p':password},
                            callback=parse_raw_message
                        )]

                    messages = sel.select("/html/body/div")
                    if messages:
                        email['message'] = ' '.join(messages.select(".//text()").extract())
                        email['message_html'] = messages.extract()[0]
                    elif text_link:
                        partial_src = text_link.select("./@href").extract()[0]
                        msg_src = "https://lists.princeton.edu%s" % partial_src

                        text_message_parser = create_text_message_parser(email)
                        return [Request(msg_src, callback=text_message_parser)]

                    return [email]

                return parse_raw_message

            def create_text_message_parser(email):
                def text_message_parser(response):
                    sel = XPathSelector(response)
                    message = select(sel, "/html/body/pre")
                    if message:
                        email['message'] = ' '.join(message.select(".//text()").extract())
                        email['message_html'] = None
                    return [email]

                return text_message_parser

            if partial_url:
                items.append(Request(message_url, callback=create_message_parser(email)))
            else:
                items.append(email)

        return items

