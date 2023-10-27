from pprint import pprint

from mailchimp_marketing.api_client import ApiClientError

from inews.infra import apis

mailchimp_api, members_list_id = apis.get_mailchimp()


def get_mailing_list():
    try:
        response = mailchimp_api.lists.get_list_members_info(members_list_id, count=1000)
    except ApiClientError as error:
        print(error)

    for member in response["members"]:
        pprint(member["email_address"])
        pprint(member["merge_fields"])
