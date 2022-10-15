
if __name__ == "__main__":
    import configs
    configs.load()

    import scheduler
    scheduler.run('https://google.com/')
    pass
