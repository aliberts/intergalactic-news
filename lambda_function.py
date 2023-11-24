from inews.domain import pipeline
from inews.infra import utils


def handler(event, context):
    status = utils.validate_event(event)
    pipeline.run_data(status)
    pipeline.run_mailing(status)
