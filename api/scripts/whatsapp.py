from whatsapp_api_client_python import API as API
from html2image import Html2Image
# from api.models import Stock
from datetime import date
import os



ID_INSTANCE = '1101789716'
API_TOKEN_INSTANCE = '2ade3716cb384116af5af77ba4b4fa55d186b7f55f294a9793'
GROUP_ID = '120363031328070036@g.us'

greenAPI = API.GreenApi(ID_INSTANCE, API_TOKEN_INSTANCE)

class Whatsapp():
    def send_alert(self, data:list):
        print("schduler created")
        html = "<table border='1'><tbody><tr><th>Name</th><th>Home</th><th>Shop</th></tr>"
        # Get stock data
        for item in data:
            print(item)
            html = html + "<tr><td>"+item["name"]+"</td><td>"+str(item["home"])+"</td><td>"+str(item["shop"])+"</td></tr>"
        html = html + "</tbody></table>"
        # stock_queryset = Stock.objects.all()
        # for obj in stock_queryset:
        #     html = html + "<tr><td>"+obj.name+"</td><td>"+str(obj.home)+"</td><td>"+str(obj.shop)+"</td></tr>"
        # html = html + "</tbody></table>"

        script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
        rel_path = "stock.png"
        abs_file_path = os.path.join(script_dir, rel_path)
        print(abs_file_path)
        hti = Html2Image(output_path=script_dir)

        css = 'body {background: white;}'

       

        # screenshot an HTML string (css is optional)
        hti.screenshot(html_str=html, css_str=css,  save_as=rel_path, size=(300, 700))
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


    