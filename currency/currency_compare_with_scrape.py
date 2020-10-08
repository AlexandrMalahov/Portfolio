"""Python 3.7. Compare USD and Euro course. Write currency data to Excel table. Send Excel file to email."""
import mimetypes
import os
import requests
import smtplib
import xlrd
import xlwt

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from lxml import html


class UsdEuroDiff:
    def __init__(self, file):
        self.file = file

    @staticmethod
    def get_currency_data(url):
        """Scrape data from html."""
        response = requests.get(url).content
        tree = html.fromstring(response)
        data = tree.xpath('/html/body/div[3]/div/div[2]/div[1]/div[1]/div[1]/div[2]/div/div[2]/div/div[2]')[1:]
        date = [i.xpath('div/div[1]/text()') for i in data]
        price = [i.xpath('div/div[2]/text()') for i in data]
        change = [i.xpath('div/div[3]/text()') for i in data]
        return {'date': date, 'price': price, 'change': change}

    def get_data_from_html(self):
        """Extract data from Excel table and calculate currency diff."""
        usd = self.get_currency_data('https://yandex.ru/news/quotes/2002.html')
        euro = self.get_currency_data('https://yandex.ru/news/quotes/2000')
        usd_price = iter(usd['price'])
        euro_price = iter(euro['price'])
        diff = []
        while True:
            try:
                euro_in_usd = next(euro_price) / next(usd_price)
                diff.append(euro_in_usd)
            except StopIteration:
                break
        return {'usd': usd, 'euro': euro, 'diff': diff}

    def write_data_to_excel(self, file_name):
        """Write data to Excel table."""
        book = xlwt.Workbook(file_name)
        sheet = book.add_sheet('Currency', cell_overwrite_ok=True)
        table_data = self.get_data_from_html()
        self.write_value_to_cell(table_data['usd']['date'], sheet, 'm/d/yy', 0)
        self.write_value_to_cell(
            table_data['usd']['price'], sheet, '_(* #,##0.00 _₽_);_(-* #,##0.00 _₽;_(* "-"?? _₽_);_(@_)', 1)
        self.write_value_to_cell(table_data['usd']['change'], sheet, '0.00', 2)
        self.write_value_to_cell(table_data['euro']['date'], sheet, 'm/d/yy', 3)
        self.write_value_to_cell(
            table_data['euro']['price'], sheet, '_(* #,##0.00 _₽_);_(-* #,##0.00 _₽;_(* "-"?? _₽_);_(@_)', 4)
        self.write_value_to_cell(table_data['euro']['change'], sheet, '0.00', 5)
        self.write_value_to_cell(table_data['diff'], sheet, '0.00', 6)
        book.save(file_name)

    def write_value_to_cell(self, value, sheet, num_format, cell, align='alignment: horizontal left'):
        """Write data and set format cell."""
        style = xlwt.easyxf(align)
        row = 0
        for val in value:
            sheet.col(cell).width = self.get_width(val)
            style.num_format_str = num_format
            sheet.write(row, cell, val, style)
            row += 1

    @staticmethod
    def get_width(num):
        """Calculate necessary cell width."""
        num_characters = len(str(num))
        return int((1 + num_characters) * 256)


class MailSender:
    def __init__(self, address_to, subject, text, file=''):
        self.addr_from = 'mail_sender_py@mail.ru'
        self.password = 'python3.7'
        self.addr_to = address_to
        self.subject = subject
        self.text = text
        self.file = file

    def send_mail(self):
        """Send message to email."""
        message = MIMEMultipart()
        message['from'] = self.addr_from
        message['to'] = self.addr_to
        message['Subject'] = self.subject
        body = self.text
        message.attach(MIMEText(body, 'plain'))
        if os.path.isfile(self.file):
            self.attach_file(message)
        server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
        server.login(self.addr_from, self.password)
        server.send_message(message)
        server.quit()

    def attach_file(self, message):
        """Attach file to message."""
        ctype, encoding = mimetypes.guess_type(self.file)
        maintype, subtype = ctype.split('/', 1)
        with open(self.file, 'rb') as f:
            file = MIMEBase(maintype, subtype)
            file.set_payload(f.read())
        encoders.encode_base64(file)
        file.add_header('Content-Disposition', 'attachment', filename=self.file)
        message.attach(file)


class Message:
    def __init__(self, file):
        self.file = file
        self.subject = 'Курс валют'

    def get_message(self):
        """Get message with information about rows quantity."""
        book = xlrd.open_workbook(self.file)
        sheet = book.sheet_by_index(0)
        rows_num = sheet.nrows
        if rows_num % 10 == 1 and rows_num != 11:
            declension = 'а'
        elif rows_num % 10 == 2 and rows_num != 12 or rows_num % 10 == 3 \
                and rows_num != 13 or rows_num % 10 == 4 and rows_num != 14:
            declension = 'и'
        else:
            declension = ''
        return 'В файле {file} {strings} строк{declension}.'.format(
            file=self.file, strings=rows_num, declension=declension)


if __name__ == '__main__':
    FILE_TO_SEND = 'currency.xlsx'
    UsdEuroDiff('currency_table.xlsx').write_data_to_excel(FILE_TO_SEND)
    MESSAGE = Message(FILE_TO_SEND)
    MailSender('knessdar2@gmail.com', MESSAGE.subject, MESSAGE.get_message(), file=FILE_TO_SEND).send_mail()
