ONE_HOUR = 60 * 60 
# For celery time control, which counting time uses second.

MAX_TIMESTAMP = 9999999999999999
# This is defined by
# >> import time
# >> time.time() * 1000000
# Then change all digits to 9
# To ensure this is big enough