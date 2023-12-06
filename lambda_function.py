import argparse
from pprint import pformat

from inews.infra import io
from inews.infra.types import RunEvent
from inews.pipeline import data, mailing


def handler(event, context=None):
    valid_event = RunEvent.model_validate(event)
    print(f"Run Event:\n{pformat(valid_event)}")

    data.run(valid_event)
    mailing.run(valid_event)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Lambda handler",
    )
    parser.add_argument(
        "event_filename",
        metavar="EVENT_FILENAME",
        help="Enter the filename to the event json used for the run.",
    )
    parser.add_argument(
        "-p", "--push", action="store_true", help="upload outputs to bucket (override event)"
    )
    parser.add_argument(
        "-s", "--send-test", action="store_true", help="send test email (override event)"
    )
    args = parser.parse_args()

    event = io.load_from_json_file(args.event_filename)
    if args.push:
        event["push_to_bucket"] = True
    if args.send_test:
        event["send_test"] = True

    handler(event)
