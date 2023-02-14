from .whatsapp import Whatsapp
from apscheduler.schedulers.background import BackgroundScheduler


def start():
    what_obj = Whatsapp()
    scheduler = BackgroundScheduler()
    
    # scheduler.add_job(what_obj.send_alert, 'interval', seconds=59)
    # Runs from Monday to Friday at 6:30AM until 2022-06-30 00:00:00
    scheduler.add_job(what_obj.send_alert, 'cron', day_of_week= 'mon-sun', 
        hour= 6, minute= 30, id="stockalert")
    # scheduler.print_jobs()
    scheduler.start()
    # scheduler.shutdown()