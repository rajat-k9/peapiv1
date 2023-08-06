from datetime import datetime
from api.models import SaleOrder


class DateUtil():
    def numberOfDays(self, y, m):
      leap = 0
      if y% 400 == 0:
         leap = 1
      elif y % 100 == 0:
         leap = 0
      elif y% 4 == 0:
         leap = 1
      if m==2:
         return 28 + leap
      list = [1,3,5,7,8,10,12]
      if m in list:
         return 31
      return 30
    
class OrderUtil():
   def _generate_order_id(self, type="sale"):
      today_date = datetime.now().strftime("%y%m%d")
      orderdate = None
      if type=="sale":
         item = SaleOrder.objects.all().values("order_id").order_by("-created_on")[0]
         if item:
            orderdate = item['order_id'][4:10]
            if orderdate == today_date:
                index = int(item['order_id'][-3:])
            else:
                orderdate = today_date
                index = 1
         else: #should run only first time
            orderdate = today_date
            index = 1
         return "PESL"+orderdate+str(index+1).zfill(3)
