from inews.infra.types import RunStatus


def validate_event(event: dict) -> RunStatus:
    return RunStatus.TEST if event["Status"] == "test" else RunStatus.PROD
