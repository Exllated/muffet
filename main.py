import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit('Provide link with scheme (e.g. \'https://example.com/\')')

    if not sys.argv[1].startswith('http://') and not sys.argv[1].startswith('https://'):
        sys.exit('Provide link with scheme (e.g. \'https://example.com/\')')

    import configs
    configs.load()

    import scheduler
    scheduler.run(sys.argv[1])
    pass
