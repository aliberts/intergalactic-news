from inews.domain import pipeline
from inews.infra import utils


def handler(event, context):
    status = utils.validate_event(event)
    print(status)
    pipeline.run_data(status)
    pipeline.run_mailing(status)
