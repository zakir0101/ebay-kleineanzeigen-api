# importing datetime from datetime module
import uuid
import sys
from datetime import datetime, timezone
import time

# input timestamp
timestamp_string = 1678575724739 / 1000
current_time = time.time()
# Converting timestamp string to datetime object and formatting it
datetime_object = datetime.fromtimestamp(timestamp_string).strftime('%d-%m-%y-%H:%M')

# printing resultant datetime object
print("Resultant datetime object:", datetime_object)

# printing the type of resultant datetime object
print("Type of datetime object:", type(datetime_object))

msg_body = dict(message="hallo",
                adId="2382158583",
                adType="private",
                contactName="Zakir")

print(str(uuid.uuid4()))

days_of_week = ['Mon', 'Die', 'Mit', 'Don', 'Fri', 'Sam', 'Son']


def get_time_readable(time_str):
    time_obj = time.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%f+0100")
    my_datetime = datetime(time_obj.tm_year, time_obj.tm_mon,
                           time_obj.tm_mday, time_obj.tm_hour,
                           time_obj.tm_min, time_obj.tm_sec)

    now = time.time()
    epoch = my_datetime.timestamp()
    a_day = 24 * 60 * 60
    if (now - epoch) < a_day:
        return "Heute"+my_datetime.strftime(' %H:%M')
    elif (now - epoch) < 2 * a_day:
        return "Gersten"+my_datetime.strftime(' %H:%M')
    elif (now - epoch) < a_day * 7:
        return 'letzte ' + days_of_week[time_obj.tm_wday]+my_datetime.strftime(' %H:%M')
    else:
        return my_datetime.strftime('%d-%b-%y %H:%M')

    pass


time_result = list()
time_result.append( get_time_readable("2023-03-18T13:10:52.052+0100"))
time_result.append(  get_time_readable("2023-03-17T13:10:52.052+0100"))
time_result.append(  get_time_readable("2023-03-14T14:10:52.052+0100"))
time_result.append(  get_time_readable("2023-03-13T13:10:52.052+0100"))
time_result.append(  get_time_readable("2023-02-13T13:10:52.052+0100"))

for res in time_result:
    print(res)
