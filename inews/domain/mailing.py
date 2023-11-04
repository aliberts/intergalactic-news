from mailchimp_marketing.api_client import ApiClientError

from inews.infra import apis
from inews.infra.types import MCCampaignP

mailchimp_api = apis.get_mailchimp()


def create_campaign(campaign: MCCampaignP) -> str:
    try:
        response = mailchimp_api.campaigns.create(campaign.settings)
    except ApiClientError as error:
        print("Error: {}".format(error.text))

    return response["id"]


def set_campaign_html(campaign_id: str, html: str) -> None:
    body = {"html": html}
    try:
        mailchimp_api.campaigns.set_content(campaign_id, body)
    except ApiClientError as error:
        print(error)


def send_campaign(campaign_id: str) -> None:
    try:
        mailchimp_api.campaigns.send(campaign_id)
    except ApiClientError as error:
        print("Error: {}".format(error.text))


def send_campaign_test(campaign_id: str, test_emails: list[str]) -> None:
    body = {"test_emails": test_emails, "send_type": "html"}
    try:
        mailchimp_api.campaigns.send_test_email(campaign_id, body)
    except ApiClientError as error:
        print("Error: {}".format(error.text))


def _get_mailing_list(members_list_id: str) -> list[dict]:
    try:
        response = mailchimp_api.lists.get_list_members_info(members_list_id, count=1000)
    except ApiClientError as error:
        print(error)

    return response["members"]
