# CRM

## Description 

Each url page in the app can only be access if the previous page data required are filled in already and click next/complete to progress to the next page.

## Configure mail server

### To do on Microsoft Azure portal 

1. Create an Azure app
   1. goto https://portal.azure.com/#home 
2. App registration
   1. goto app registrations
   2. open application you just created
   3. Goto Authentication
   4. Click add URI and input your server uri as https://IP_Address:443/mailserver/authorized
   5. Hit save

### To do in code

1. Goto mailserver/utilities_dir/outlook_config.py file
2. Specify the protocol used "http/https"
3. Specify the domain/IP address in HOST_IP (the server ip address)
4. Specify the port (443 for https)
5. Goto mailserver/utilities_dir/outlook_utils.py file
6. Find get_webhook_path function uncomment the commected return and delete the static return

### To do in Django admin

1. Goto Sites
   3. Domain: graph.microsoft.com
   4. Name: Microsoft
2. Go back to Admin and Social Applications
   3. Create Add Account > Select Provider as "Microsoft Graph"
   4. Name it "Outlook Mail" [make sure to copy and paste without "]
   5. Copy and paste Client Id and Client secrete from Azure portal
   6. From sites select graph.microsoft.com

## Troubleshooting

1. If you don't see any item in a page, that's because no previous page has been moved to the current page. You need to go to the previous page, fill in required data and click the next stage button(s) in green colour at the top. 
2. Mailserver
   1. If you are not receiving new leads from email, try revoking access in /mailserver page, restart server and try login again. 
   2. If you are getting incorrect lead information, check django code, mailserver/utilities_dir/scrapper.py

## Python version

Python 3.7.4
