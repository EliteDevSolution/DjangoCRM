from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404
from .utilities_dir.outlook_utils import (_build_preconfigured_auth_url_, _save_cache, _load_cache,
                                          _build_msal_app, get_outlook_auth_redirect_path, _get_token_from_cache,
                                          _get_outlook_cache_for_subscription_id,
                                          _load_cache_for_user, get_sign_out_path)
from .utilities_dir import outlook_config as app_config
from .utilities_dir import outlook_requests
from .utilities_dir import scrapper
from django.views.decorators.http import require_POST
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from mailserver.models import (OutlookServerDetails)
from customer.models import Customer, Requirement, CreditCard
from django.urls import reverse
# Create your views here.


@login_required
@permission_required(["mailserver.mailserver_view"])
def mail_server_view(request):
    '''
        Home view for mailserver where login/revoke functionality
    '''
    is_used_login = False
    outlook_cache = OutlookServerDetails.objects.filter(
        user_id=request.user.id)
    if outlook_cache.count():
        is_used_login = True

    context = {
        "outlook_auth_url": _build_preconfigured_auth_url_(request),
        "is_user_login":is_used_login
    }
    return render(request, 'mail-server-home.html', context=context)


@login_required
def remove_outlook_auth(request):
    '''
        View to delete webhook of outlook and delete user creds from database
    '''
    outlook_cache = OutlookServerDetails.objects.filter(
        user_id=request.user.id)
    if outlook_cache.count():
        outlook_cache = outlook_cache[0]
        cache = _load_cache(outlook_cache)
        result = _get_token_from_cache(cache, outlook_cache.user_id)

        if "access_token" in result and outlook_cache.subscription_id:
            token = result["access_token"]
            outlook_requests.delete_subscription(
                token, outlook_cache.subscription_id)

        outlook_cache.delete()

    return redirect(reverse("mail-server-home"))

    # return redirect(  # Also logout from your tenant's web session
    #     app_config.AUTHORITY + "/oauth2/v2.0/logout" +
    #     "?post_logout_redirect_uri=" + get_sign_out_path())



@login_required
def outlook_authorized(request):
    '''
        View for getting the authication code from microsoft
    '''
    if request.GET.get('state') != request.session.get("state"):
        return redirect("/")  # No-OP. Goes back to Index page
    if "error" in request.GET:  # Authentication/Authorization failure
        context = {
            "result": request.GET
        }
        return render(request, "auth_error.html", context=context)
    if request.GET.get('code'):
        cache = _load_cache_for_user(request.user.id)

        result = _build_msal_app(cache=cache).acquire_token_by_authorization_code(
            request.GET['code'],
            # Misspelled scope would cause an HTTP 400 error here
            scopes=app_config.SCOPE,
            redirect_uri=get_outlook_auth_redirect_path())
        if "error" in result:
            context = {
                "result": result
            }
            return render(request, "auth_error.html", context=context)
        request.session["user"] = result.get("id_token_claims")
        _save_cache(request.user.id, cache)
        outlook_cache = OutlookServerDetails.objects.filter(
            user_id=request.user.id)
        if len(outlook_cache):
            outlook_cache = outlook_cache[0]
            if not outlook_cache.subscription_id:
                subscription = outlook_requests.subscript_for_notifications(
                    result["access_token"])
                if "id" in subscription:
                    # Successful subscription
                    subscription_id = subscription["id"]
                    outlook_cache.subscription_id = subscription_id
                    outlook_cache.save()
                else:
                    print("Error while subscribing to webhook")
            else:
                print("Webhook already exists")
        else:
            print("outlook cache doesn't exist")

    response = redirect("/")

    return response


@csrf_exempt
@require_POST
def webhook(request):
    '''
        Webhook view for outlook, this is called when new notification is recieved from outlook
    '''
    content = ''
    if "validationToken" in request.GET:
        content = request.GET.get("validationToken")
    else:
        jsondata = request.body.decode("utf-8")
        notificaiton = json.loads(jsondata)
        if "value" in notificaiton and len(notificaiton["value"]) > 0:
            if "resourceData" in notificaiton["value"][0]:
                message_id = notificaiton["value"][0]["resourceData"]["id"]
                # Getting the cache
                if "subscriptionId" in notificaiton["value"][0]:
                    subscription_id = notificaiton["value"][0]["subscriptionId"]
                    #result = _get_token_from_cache_with_subscription_id(request)
                    cache, outlook_cache = _get_outlook_cache_for_subscription_id(
                        subscription_id)
                    if cache and outlook_cache:

                        result = _get_token_from_cache(
                            cache, outlook_cache.user_id)

                        if "error" in result:
                            print("ERROR in Webhook")

                        current_token = result["access_token"]
                        mail = outlook_requests.fetch_message_by_message_id(
                            message_id, current_token)

                        if not "error" in mail:
                            customer_details = scrapper.scrap_customer_info_from_form(
                                mail)
                            # try:
                            creator_id = outlook_cache.user_id
                            creator = User.objects.filter(id=creator_id)
                            if (len(customer_details.keys())):
                                if(len(creator)):
                                    customer_details["creator"] = creator[0]

                                new_customer = Customer(**customer_details)
                                new_customer.save()
                                requirement = Requirement(
                                    customer=new_customer, status="CREATED")
                                requirement.save()
                                credit_card = CreditCard(customer=new_customer)
                                credit_card.save()
                                outlook_cache.new_message = True
                                outlook_cache.save()
                            # except:
                            #     pass
                        else:
                            print(mail["error"])

    return HttpResponse(content=content, content_type="text/plain", status=200)


@login_required
@permission_required(["mailserver.mailserver_view"])
def get_notification(request):
    '''
        API endpoint to check if there are any new customer added through mail
    '''
    outlook_cache = OutlookServerDetails.objects.filter(
        user_id=request.user.id)
    if(len(outlook_cache)):
        outlook_cache = outlook_cache[0]
        response = {
            "new_message": outlook_cache.new_message
        }
        if outlook_cache.new_message == True:
            outlook_cache.new_message = False
            outlook_cache.save()

        return JsonResponse(response)

    return HttpResponse(status=404)
