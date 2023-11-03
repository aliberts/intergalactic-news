from inews.domain import pipeline


def main():
    pipeline.run_data()
    pipeline.run_newsletter()


if __name__ == "__main__":
    main()
