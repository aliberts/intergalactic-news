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


def _get_campaign_html(campaign_id: str) -> str:
    try:
        response = mailchimp_api.campaigns.get_content(campaign_id)
    except ApiClientError as error:
        print(error)

    return response["html"]


def _get_mailing_list(members_list_id: str) -> list[dict]:
    try:
        response = mailchimp_api.lists.get_list_members_info(members_list_id, count=1000)
    except ApiClientError as error:
        print(error)

    return response["members"]


def _get_campaigns() -> list[dict]:
    try:
        response = mailchimp_api.campaigns.list()
    except ApiClientError as error:
        print("Error: {}".format(error.text))

    keys = ["id", "web_id", "title", "create_time"]
    campaigns = []
    for campaign in response["campaigns"]:
        campaigns.append(
            {key: (campaign[key] if key != "title" else campaign["settings"][key]) for key in keys}
        )
    return campaigns


def _get_audiences() -> list[dict]:
    try:
        response = mailchimp_api.lists.get_all_lists()
    except ApiClientError as error:
        print("Error: {}".format(error.text))

    keys = [
        "id",
        "web_id",
        "name",
        "subscribe_url_short",
        "campaign_defaults",
        "contact",
        "date_created",
    ]
    audiences = []
    for audience in response["lists"]:
        audiences.append({key: audience[key] for key in keys})

    return audiences


def _get_interests_categories(audience_id: str) -> list[dict]:
    try:
        response = mailchimp_api.lists.get_list_interest_categories(audience_id)
    except ApiClientError as error:
        print("Error: {}".format(error.text))

    keys = [
        "id",
        "title",
        "type",
    ]
    interests_categories = []
    for interests_categorie in response["categories"]:
        interests_categories.append({key: interests_categorie[key] for key in keys})

    return interests_categories


def _get_interest_category_interests(audience_id: str, interest_category_id: str) -> list[dict]:
    try:
        response = mailchimp_api.lists.list_interest_category_interests(
            audience_id, interest_category_id
        )
    except ApiClientError as error:
        print("Error: {}".format(error.text))

    keys = [
        "id",
        "name",
        "subscriber_count",
    ]
    interests = []
    for interest in response["interests"]:
        interests.append({key: interest[key] for key in keys})

    return interests
