from whatsapp_api_client_python import API as API
from html2image import Html2Image
# from api.models import Stock
from datetime import date
import os

from peapiv1.settings import BASE_DIR



# ID_INSTANCE = '1101789716'
# API_TOKEN_INSTANCE = '2ade3716cb384116af5af77ba4b4fa55d186b7f55f294a9793'
# GROUP_ID = '120363031328070036@g.us'

# greenAPI = API.GreenApi(ID_INSTANCE, API_TOKEN_INSTANCE)

class Whatsapp():
    def send_alert(self, data:list):
        print("schduler created")
        html = "<table border='1'><tbody><tr><th>Name</th><th>Home</th><th>Shop</th></tr>"
        # Get stock data
        for item in data:
            html = html + "<tr><td>"+item["name"]+"</td><td>"+str(item["home"])+"</td><td>"+str(item["shop"])+"</td></tr>"
        html = html + "</tbody></table>"
        print(html)


        # after your other file variables
        static_path = os.path.join(BASE_DIR, 'static')
        image_path = os.path.join(static_path, 'stock1.png')
        rel_path = "stock1.png"
        abs_file_path = os.path.join(image_path, rel_path)
        print(static_path)
        hti = Html2Image(output_path=static_path)

        css = 'body {background: white;}'

        # screenshot an HTML string (css is optional)
        hti.screenshot(html_str=html, css_str=css,  save_as=rel_path, size=(300, 700))

        return {"status":image_path}
        # with open("page.png","r") as file:
        #     x = file.name
        #     print(x)

        # chatIds = [
        #     "917503175945@c.us","919044883644@c.us"
        # ]
        # resultCreate = greenAPI.groups.createGroup('Stock Alerts', 
        #     chatIds)

        # if resultCreate.code == 200:
        #     print(resultCreate.data)
            # resultSend = greenAPI.sending.sendMessage(resultCreate.data['chatId'], 'Message text')
        # resultSend = greenAPI.sending.sendMessage(GROUP_ID, 'Message text')
        today = date.today()
        resultSend = greenAPI.sending.sendFileByUpload(GROUP_ID, abs_file_path,'stock.png','Wire Stock on '+today.strftime("%d-%m-%Y"))
        if resultSend.code == 200:
            print(resultSend.data)
            return resultSend.data
        else:
            print(resultSend.error)    
        # else:
        #     print(resultCreate.error)


    