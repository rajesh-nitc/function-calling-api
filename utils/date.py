import datetime


def get_today_date() -> tuple[datetime.date, str]:
    """_summary_

    Returns:
        Tuple[datetime.date, str]: _description_
    """
    today = datetime.date.today()
    # Return the full date (YYYY-MM-DD) and the day of the week
    return today, today.strftime("%A")
