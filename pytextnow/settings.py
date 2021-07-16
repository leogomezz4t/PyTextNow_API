ONE_MINUTE = 60
ONE_HOUR = ONE_MINUTE * 60
ONE_DAY = ONE_HOUR * 24

  ########################
 ## Listener Settings ###
########################
LISTENER_PORT = 5050
LISTENER_HOST = "127.0.0.1"
DEBUG = True
# Default refresh interval is betwen 12 hours and 24 hours
REFRESH_INTERVALS = {'lower_limit': ONE_HOUR*12, "upper_limit": ONE_DAY}
# Where to download your files
DOWNLOAD_PATH = ""

  ######################
 ## RoboBoi Settings ##
######################

LOADING_TIMEOUT = 30 # Seconds
# Set to None to autodetect
CHROME_BINARY = None

  #######################
 ## Database Settings ##
#######################
SCHEMA = None
DB_NAME = ""
