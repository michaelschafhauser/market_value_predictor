import requests
from bs4 import BeautifulSoup

url = "https://sofifa.com/players?keyword=Sergi+Darder"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
print(soup)
