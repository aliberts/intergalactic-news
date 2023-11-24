from inews.domain import pipeline
from inews.infra.types import RunStatus


def main():
    satus = RunStatus.TEST
    pipeline.run_data(satus)
    pipeline.run_mailing(satus)


if __name__ == "__main__":
    main()
