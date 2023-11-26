from inews.infra.types import RunStatus


def validate_event(event: dict) -> RunStatus:
    print(event)
    if event["Status"] == "test":
        return RunStatus.TEST
    elif event["Status"] == "prod":
        return RunStatus.PROD
    else:
        raise ValueError
