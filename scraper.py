from bs4 import BeautifulSoup
import requests
session = requests.Session()
response = session.get("https://duapp2.drexel.edu/webtms_du/app",verify=False)

data = response.text

parser = BeautifulSoup(data)

for tables in parser.find_all(".termPanel"):
    print(tables.get_text(()))
