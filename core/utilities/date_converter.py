from datetime import datetime

def convert_date_to_datetime(date):
    return datetime.strptime(date, "%d/%m/%Y")