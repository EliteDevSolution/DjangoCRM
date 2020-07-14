from bs4 import BeautifulSoup
import json
from datetime import datetime
import sys
import traceback
import pprint

def get_text_from_span(spans):
    '''
        Function to extract text from span tag
        @@Param spans: list of span tags
        @@Retusn text
    '''
    ret_value = ''
    try:
        for span in spans:
            if span.text and (span.text != '\xa0') :
                ret_value = span.text
                break
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
    return ret_value


def scrap_customer_info_from_form(mail):
    '''
        Function to scrap information from mail
    '''
    ret_value = {}

    filed_model_key_mapping = {
        'First Name': "First Name",
        'Last Name': "Last Name",
        'Email': "customer_email",
        'Phone Number': "phone_number",
        'Post Code': "Post Code",
        'Address': "customer_address",
        'Message': "customer_notes",

    }

    try:
        if True:
            if "body" in mail:
                print("here")
                content = mail["body"]["content"]
                markup = BeautifulSoup(content, "html.parser")

                rows = markup.select("table tr")
                for index in range(0, len(rows), 2):
                    spans = rows[index].select("span")
                    heading = get_text_from_span(spans)
                    if heading in filed_model_key_mapping:
                        form_contexts = rows[index+1].select("span")

                        information = get_text_from_span(form_contexts)
                        if information:
                           ret_value[filed_model_key_mapping[heading]] = information
                ret_value["leads_from_id"] = 1

                if "First Name" in ret_value:
                    name = ret_value["First Name"]
                    if "Last Name" in ret_value:
                        name += " "+ret_value["Last Name"]
                        del ret_value["Last Name"]
                    del ret_value["First Name"]
                    ret_value["customer_name"] = name
                

                if "Post Code" in ret_value:
                    if "customer_address" in ret_value:
                        ret_value["customer_address"] += " ,"+ ret_value["Post Code"]
                    del ret_value["Post Code"]
                
                if True:
                    mail_date = datetime.strptime(mail["receivedDateTime"],"%Y-%m-%dT%H:%M:%SZ")
                    ret_value["created_date"] = mail_date
                
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
    
    return ret_value
