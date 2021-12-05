
def get_max_waiting_time():
    """This function returns the max waiting time.
    """
    from dateutil import relativedelta
    return relativedelta.relativedelta(minutes=4*60)

def timesteps_builder(start_date,end_date,mode):
    """This function get as input a start and end date, and returns a list datetime.date stepped from start to end
    date for each month, week, day.
    """
    import datetime as dt
    steps = []
    steps.append(start_date)
    if mode=="m":
        delta = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        for time_step in range(delta):
            if steps[-1].month == 12:
                new_year = steps[-1].year + 1
                new_month = 1
                new_day = 1
            else:
                new_year = steps[-1].year
                new_month = steps[-1].month + 1
                new_day = 1
            new_step = dt.date(year=new_year,month=new_month,day=new_day)
            steps.append(new_step)
    elif mode=="d":
        delta = (end_date - start_date)
        delta = delta.days
        new_step = steps[-1]
        for time_step in range(delta):
            new_step += dt.timedelta(days=1)
            steps.append(new_step)
    elif mode=="w":
        delta = (end_date - start_date)
        delta = delta.days
        new_step = steps[-1]
        for time_step in range(delta):
            new_step += dt.timedelta(days=1)
            if new_step.weekday()==0: 
                steps.append(new_step)
    if steps[-1]!=end_date:
        steps.append(end_date)
    return steps
