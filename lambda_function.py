from inews.domain import pipeline


def handler(event, context):
    pipeline.run_data()
    pipeline.run_mailing()
