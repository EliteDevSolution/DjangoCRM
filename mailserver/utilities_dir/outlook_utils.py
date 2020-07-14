
from mailserver.models import OutlookServerDetails
import msal
import uuid
from . import outlook_config as config
import sys
from datetime import datetime, timedelta
from allauth.socialaccount.models import SocialApp
from django.urls import reverse


def _load_cache(outlook_cache):
    '''
        Function to load a Serialized token Cache object\n
        @@Param outlook_cache: Modal of OutlookServerDetails
        @@Returns: a cache object
    '''
    cache = msal.SerializableTokenCache()
    if outlook_cache and outlook_cache.token_cache:
        cache.deserialize(outlook_cache.token_cache)
    return cache


def _load_cache_for_user(user_id):
    '''
        Function to load cache for the user taking user_id as paramter
        @@Param user_id: userid
        @@Retruns: a cache object
    '''
    outlook_cache = OutlookServerDetails.objects.filter(
        user_id=user_id)
    if (len(outlook_cache)):
        return _load_cache(outlook_cache[0])
    return _load_cache(None)


def _get_outlook_cache_for_subscription_id(subscription_id):
    '''
        Function to load cache for the user taking subscription_id as paramter
        @@Param subscription_id: webhook subscription id
        @@Retruns: a cache object
    '''
    outlook_cache = OutlookServerDetails.objects.filter(
        subscription_id=subscription_id)
    if(len(outlook_cache)):
        return _load_cache(outlook_cache[0]), outlook_cache[0]
    return _load_cache(None), None


def _save_cache(user_id, cache):
    '''
        Function to save the cache object into database
        @@Param cache: SerializableTokenCache
    '''
    if cache.has_state_changed:
        outlook_cache = OutlookServerDetails.objects.filter(
            user_id=user_id)
        if len(outlook_cache) == 0:
            cache_data = {
                "user_id": user_id,
                "token_cache": cache.serialize()
            }
            OutlookServerDetails(**cache_data).save()
        else:

            outlook_cache = outlook_cache[0]
            outlook_cache.cache = cache.serialize()
            outlook_cache.save()


def _build_msal_app(cache=None, authority=None):
    '''
        Function to build MSAL application
        @@Param cache: SerializableTokenCache object
        @@Param authority: refer https://docs.microsoft.com/en-us/graph/security-authorization
        @@Returns a msal application
    '''
    app_config = SocialApp.objects.filter(name="Outlook Mail")
    CLIENT_ID = ''
    CLIENT_SECRET = ''

    if app_config.count():
        app_config = app_config.first()
        CLIENT_ID = app_config.client_id
        CLIENT_SECRET = app_config.secret
        print(CLIENT_ID, CLIENT_SECRET)
    return msal.ConfidentialClientApplication(
        CLIENT_ID, authority=authority or config.AUTHORITY,
        client_credential=CLIENT_SECRET, token_cache=cache)


def _get_token_from_cache(cache, user_id, scope=None):
    '''
        Funtion to get token from cache
        @@Param cache: SerializableTokenCache object
        @@Param user_id: userid
        @@Scope: refer https://docs.microsoft.com/en-us/graph/permissions-reference
    '''

    if scope == None:
        scope = config.SCOPE
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(user_id, cache)
        return result



def get_outlook_auth_redirect_path():
    '''
        Function to get the outlook auth redirect path
    '''
    protocol = config.PROTOCOL
    host = config.HOST_IP
    port = config.PORT
    return "{}://{}:{}/mailserver/authorized".format(
        protocol, host, port
    )

def get_webhook_path():
    '''
     Function the get the current webhook path for outlook
    '''
    protocol = config.PROTOCOL
    host = config.HOST_IP
    port = config.PORT
    return "{}://{}:{}/mailserver/outlook_webhook".format(
        protocol, host, port
    )
    ## Below code for debugging locally
    # return "https://webhook.site/f5aa1c37-2c99-41e5-91b9-0913fccba193"


def get_sign_out_path():
    protocol = config.PROTOCOL
    host = config.HOST_IP
    port = config.PORT
    return "{}://{}:{}/{}".format(
        protocol, host, port, reverse("mail-server-home")
    )


def _build_auth_url(authority=None, scopes=None, state=None):
    '''
        Function to create the auth url for outlook signup
        @Param authority: base url
        @@Param scopes: premessions
        @@state unique number
        @Returns URL
    '''
    return _build_msal_app(authority=authority).get_authorization_request_url(
        scopes or [],
        state=state or str(uuid.uuid4()),
        redirect_uri=get_outlook_auth_redirect_path())


def _build_preconfigured_auth_url_(request):
    '''
        Function to create the preconfigured auth url with parameters from config file
    '''
    request.session["state"] = str(uuid.uuid4())
    return _build_auth_url(authority=config.AUTHORITY, scopes=config.SCOPE, state=request.session.get("state"))


def future_date_in_iso_formate(days, with_microseconds=False):
    '''
        Function to get date in future in ISO format
        @@Param days: future date
        @@Param with_microseconds: data format 
        @@Retuns Date
    '''
    future_date = datetime.now() + timedelta(days=days)
    date_format = "%Y-%m-%dT%H:%M:%SZ"

    if with_microseconds:
        date_format = "%Y-%m-%dT%H:%M:%S.%fZ"

    return datetime.strftime(future_date, date_format)
