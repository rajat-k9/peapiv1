# importing the requests library
# import requests
import json
from .whatsapp import Whatsapp
from api.models import Stock

def call_api():
    data = []
    what_obj = Whatsapp()
    stock_queryset = Stock.objects.all()
    lst = []
    for item in stock_queryset:
        data.append({"name":item.name,"shop":item.shop,"home":item.home})
    # # api-endpoint
    # URL = "https://rajatinfo.pythonanywhere.com/api/stocks/"


    # # sending get request and saving the response as response object
    # r = requests.get(url = URL)

    # # extracting data in json format
    # data = r.json()
    
    return json.dumps(what_obj.send_alert(data))
    

    # # extracting latitude, longitude and formatted address
    # # of the first matching location
    # latitude = data['results'][0]['geometry']['location']['lat']
    # longitude = data['results'][0]['geometry']['location']['lng']
    # formatted_address = data['results'][0]['formatted_address']

    # # printing the output
    # print("Latitude:%s\nLongitude:%s\nFormatted Address:%s"
    # 	%(latitude, longitude,formatted_address))


# if __name__ == "__main__":
#     call_api()

