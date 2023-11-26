from pprint import pformat

from inews.domain import pipeline
from inews.infra.types import RunEvent


def handler(event, context=None):
    run = RunEvent.model_validate(event)
    print(f"Run Status:\n{pformat(run)}")

    pipeline.run_data(run)
    pipeline.run_mailing(run)


if __name__ == "__main__":
    event = {
        "debug": True,
        "dummy_llm_requests": True,
        "send": False,
        "send_test": False,
        "pull_from_bucket": True,
        "push_to_bucket": False,
    }
    handler(event)
