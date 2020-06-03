from selenium import webdriver
from bs4 import BeautifulSoup
import json


class dig_shodan():
    def __init__(self, path):
        self.path = path
        self.driver = webdriver.Chrome(self.path)
        self.ip = ""
        self.soup = ""
        self.json = {}

    def get_path(self):
        return self.path

    def set_ip(self, ip):
        self.ip = str(ip)

    def get_ip(self):
        return self.ip

    def crawl_web(self):
        print "===== start crawl %s =====" % self.ip
        self.driver.get("https://www.shodan.io/host/" + self.ip)
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        # self.soup = BeautifulSoup(doc, "html.parser")
        if self.crawl_check(self.soup):
            self.crawl_header(self.soup)
            self.crawl_table(self.soup)
            self.crawl_security(self.soup)
            self.crawl_tech(self.soup)
            self.crawl_ports(self.soup)
            self.crawl_services(self.soup)
        print "===== end crawl %s =====" % self.ip

    def crawl_check(self, soup):
        self.soup = soup
        print soup.title.string
        if soup.title.string == '404 Not Found':
            self.json = {self.ip: '404 Not Found'}
            return 0
        if soup.title.string == 'www.shodan.io':
            print "internet error"
            exit()
        else:
            return 1

    def crawl_header(self, soup):
        self.soup = soup
        header = self.soup.find(
            "div", class_="page-header").find("h2").text.split("\n")
        for i in header:
            if i == "":
                header.remove(i)
        self.json = {"header": header}

    def crawl_table(self, soup):
        self.soup = soup
        self.json["table"] = {}
        table = self.soup.find("table", class_="table").find(
            "tbody").find_all("tr")
        for i in table:
            line = i.text.split("\n")
            self.json["table"][line[1]] = line[2]

    def crawl_security(self, soup):
        self.soup = soup
        self.json["security"] = {}
        security_table = self.soup.find_all("table")
        if len(security_table) < 2:
            return 0
        security = security_table[1]
        security = security.find("tbody").find_all("tr")
        for i in security:
            line = i.text.split("\n")
            self.json["security"][line[1]] = line[2]

    def crawl_tech(self, soup):
        self.soup = soup
        self.json["tech"] = []
        tech = self.soup.find("div", class_="http-components")
        if tech == None:
            return 0
        tech = tech.find_all("a")
        for i in tech:
            self.json["tech"].append(i.text.split("\n")[0])

    def crawl_ports(self, soup):
        self.soup = soup
        self.json["ports"] = []
        ports = self.soup.find("ul", class_="ports").find_all("a")
        for i in ports:
            self.json["ports"].append(i.text)

    def crawl_services(self, soup):
        self.soup = soup
        self.json["services"] = {}
        services = self.soup.find("ul", class_="services").find_all(
            "li", class_="service service-long")
        for i in services:
            port = i.find("div", class_="port").text
            protocol = i.find("div", class_="protocol").text
            state = i.find("div", class_="state").text
            detail = i.find("pre").text
            self.json["services"][port] = {}
            self.json["services"][port]["port"] = port
            self.json["services"][port]["protocol"] = protocol
            self.json["services"][port]["state"] = state
            self.json["services"][port]["detail"] = detail

    def show_json(self):
        print json.dumps(self.json)

    def del_json(self):
        self.json = {}

    def __del__(self):
        self.driver.close()

if __name__ == "__main__":
    dig = dig_shodan("./chromedriver")

    for i in range(1,256):
        dig.set_ip("8.8.8.%d"%i)
        dig.crawl_web()
        dig.show_json()
        dig.del_json()
