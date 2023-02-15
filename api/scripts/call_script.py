from .whatsapp import Whatsapp
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

def start():
    what_obj = Whatsapp()
    scheduler = BackgroundScheduler()
    trigger = CronTrigger(
        year="*", month="*", day="*", hour="9", minute="27", second="0"
    )
    scheduler.add_job(
        what_obj.send_alert,
        trigger=trigger,
        id="stockalertcron",
    )
    
    
    # scheduler.add_job(what_obj.send_alert, 'interval', seconds=59)
    # Runs from Monday to Friday at 6:30AM until 2022-06-30 00:00:00
    # try:
    #     scheduler.add_job(what_obj.send_alert, 'cron', minute= 1, id="stockalert")
    # except Exception as e:
    #     raise Exception(e)
    scheduler.print_jobs()
    scheduler.start()
    # scheduler.shutdown()