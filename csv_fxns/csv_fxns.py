"""For current date, time"""
import datetime

#Accepts a base file name, adds the preceding data folder, postfixed date, time, and file extension
def create_fn(base,relative_location,use_timestamp):
    """Create file name with timestamp"""

    postfix = ""

    if use_timestamp:
        today = datetime.date.today()           #Get date
        postfix = "-" + str(today)              #Add formatted date
        now = datetime.datetime.now()           #Get Time
        current_time = now.strftime("%H-%M-%S") #Convert time to formatted string
        postfix += "-" + str(current_time)      #Add formatted time to filename
    postfix += ".csv"                       #Append suffix
    prefix = relative_location                       #Create prefix
    file_name = prefix + base + postfix      #Append directory
    return (file_name,prefix,postfix)        #Return completed Filename
