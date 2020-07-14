import requests
from .import outlook_config as config
from .outlook_utils import get_webhook_path, future_date_in_iso_formate
#import outlook_config as config
import json


def fetch_user_details(token):
    '''
        Function to fetch mail from outlook with ID and token
        @Param id: message ID
        @Param token: message token
    '''
    ret_value = {}
    try:
        headers = {
            "Authorization": "Bearer {}".format(token)
        }
        
        mail_request = requests.get(config.USER_INFO_ENDPOINT, headers=headers)
        ret_value = json.loads(mail_request.text)

    except Exception as e:
        pass
    return ret_value


def fetch_message_by_message_id(id, token):
    '''
        Function to fetch mail from outlook with ID and token
        @Param id: message ID
        @Param token: message token
    '''
    ret_value = {}
    try:
        headers = {
            "Authorization": "Bearer {}".format(token)
        }
        message_id_endpoint = config.READ_MAIL_ENDPOINT + "/{}".format(id)
        mail_request = requests.get(message_id_endpoint, headers=headers)
        ret_value = json.loads(mail_request.text)

    except Exception as e:
        pass
    return ret_value


def subscript_for_notifications(token):
    '''
        Function to subscribe for notifications
        @Param token: auth token

    '''
    ret_value = {}
    try:
        headers = {
            "Authorization": "Bearer {}".format(token),
            "Content-Type": "application/json"
        }
        data = {
            "changeType": "updated",
            "notificationUrl": get_webhook_path(),
            "resource": "me/mailFolders('Inbox')/messages",
            "expirationDateTime": future_date_in_iso_formate(2),
            "clientState": "secretClientValue",
            "latestSupportedTlsVersion": "v1_2"
        }

        mail_request = requests.post(
            config.MAIL_NOTIFICATION_ENDPOINT, headers=headers, data=str(data))
        ret_value = json.loads(mail_request.text)
    except Exception as e:
        pass

    return ret_value


def refresh_subscription_for_notification(token, subscription_id):
    '''
        Function to subscribe for notifications
        @Param token: auth token

    '''
    ret_value = {}
    try:
        headers = {
            "Authorization": "Bearer {}".format(token),
            "Content-Type": "application/json"
        }
        data = {
            "expirationDateTime": future_date_in_iso_formate(2, with_microseconds=True),
        }

        mail_request = requests.patch(
            config.MAIL_NOTIFICATION_ENDPOINT+"/{}".format(subscription_id), headers=headers, data=str(data))
        ret_value = json.loads(mail_request.text)

    except Exception as e:
        pass

    return ret_value


def delete_subscription(token, subscription_id):
    '''
        Function to delete webhook subscription
        @Param token: auth token

    '''
    ret_value = {}
    try:
        headers = {
            "Authorization": "Bearer {}".format(token),
            "Content-Type": "application/json"
        }

        mail_request = requests.delete(
            config.MAIL_NOTIFICATION_ENDPOINT+"/{}".format(subscription_id), headers=headers)
        ret_value = json.loads(mail_request.text)

    except Exception as e:
        pass

    return ret_value
