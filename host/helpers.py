def clamp(n, smallest, largest):
    """
    Clamp a value. From http://stackoverflow.com/a/4092550.
    :param n: value to clamp
    :param smallest: smallest acceptable value
    :param largest: largest acceptable value
    :return:
    """
    return max(smallest, min(n, largest))