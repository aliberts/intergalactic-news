from inews.domain import pipeline


def main():
    pipeline.run_data()
    pipeline.run_newsletter()
    pipeline.run_mailing()


if __name__ == "__main__":
    main()
