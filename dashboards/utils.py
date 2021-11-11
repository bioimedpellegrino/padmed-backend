
def get_max_waiting_time():
    """This function returns the max waiting time.
    """
    from dateutil import relativedelta
    return relativedelta.relativedelta(minutes=4*60)