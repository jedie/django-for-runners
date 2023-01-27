"""
    Allow for_runners to be executable
    through `python -m for_runners`.
"""


from for_runners.cli import cli_app


def main():
    cli_app.main()


if __name__ == '__main__':
    main()
