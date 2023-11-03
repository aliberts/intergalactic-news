import pendulum

from inews.domain import pipeline

now = pendulum.now("Europe/Paris")


def main():
    pipeline.run_data()

    if now.day_of_week == 3:
        pipeline.run_newsletter()
        pipeline.run_mailing()


if __name__ == "__main__":
    main()
