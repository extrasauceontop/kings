import requests
from sgrequests import SgRequests

session = SgRequests()

response = session.get("https://www.firstcash.com/king-pawn").text

with open("data.csv", "w", encoding="utf-8") as output:
    print(response, file=output)