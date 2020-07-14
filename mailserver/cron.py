from apscheduler.schedulers.background import BackgroundScheduler
from .models import OutlookServerDetails
from .utilities_dir import outlook_utils as utils
from .utilities_dir.outlook_requests import refresh_subscription_for_notification

def my_scheduled_job():
    '''
      Function to update all the subscriptions of the webhooks
    '''
    subscriptions = OutlookServerDetails.objects.exclude(
        subscription_id__isnull=True)
    for subscription in subscriptions:
        cache = utils._load_cache(subscription)
        result = utils._get_token_from_cache(cache, subscription.user_id)
        if "access_token" in result:
            response = refresh_subscription_for_notification(result["access_token"],subscription.subscription_id)


def start():
    '''
      Function to make a background job which is called from app.py file
    '''
    scheduler = BackgroundScheduler()
    scheduler.add_job(my_scheduled_job, 'interval', days=1)
    scheduler.start()
