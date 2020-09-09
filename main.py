from models import PartheanSlackBot
import datetime
import time

'''
Note: Example parameters have been
provided but you must replace them
with your own. See models.py for
more information.
''' 

print("##############################")
now = datetime.datetime.now()
print(now.strftime("%Y-%m-%d %H:%M:%S"))
print("##############################")
t1 = time.time()
slack_bot = PartheanSlackBot("example_email@gmail.com",
                             "sample_password",
                             "sample_bot_auth_token",
                             "sample_user_auth_token")
slack_bot.run()
t2 = time.time()
print("Runtime: %s second(s)" % (t2 - t1) )
