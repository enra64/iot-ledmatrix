def clamp(n, smallest, largest):
    """
    From http://stackoverflow.com/a/4092550. Clamp a value.
    :param n: value to clamp
    :param smallest: smallest acceptable value
    :param largest: largest acceptable value
    :return:
    """
    return max(smallest, min(n, largest))