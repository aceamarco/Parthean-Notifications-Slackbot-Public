from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from hashlib import md5
import json
import requests

'''
Note:
Private parameters like the auth tokens,
the Parthean email and password used for the bot,
have been removed from this file. If you would like
to use the Parthean Slackbot, you need to make your
own parthean account, and (for now) your own application
with auth tokens.
'''


class PartheanSlackBot:

    def __init__(self, email, password, both_auth_token, user_auth_token):
        self.URL = "https://platform.parthean.com/Home"
        self.email = email
        self.passw = password
        self.channel = "slackbot-test1"
        self.slack_bot_auth_token = both_auth_token
        self.slack_user_auth_token = user_auth_token
        self.username = "parthean_notification"
        self.json_path = "posts.JSON"
        self.initialize_driver()
        self.wait = WebDriverWait(self.driver, 20)

    def initialize_driver(self):
        self.headless = Options()
        self.headless.headless = True
        self.driver = webdriver.Firefox(options = self.headless)


    def navigate_through_login(self):
        self.driver.get(self.URL)
        email_input = self.wait.until(EC.presence_of_element_located((By.ID,\
                                                        'loginEmail')))
        password_input = self.wait.until(EC.presence_of_element_located((By.ID,\
                                                        'loginPassword')))
        submit_button = self.wait.until(EC.presence_of_element_located((By.XPATH,\
                                                '//button[@form="loginForm"]')))
        email_input.send_keys(self.email)
        password_input.send_keys(self.passw)
        submit_button.click()

    def navigate_through_community_card_options(self):
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME,\
                                                     'communityButtonWrapper')))
        script = "community_card = document.getElementsByClassName('communityButtonWrapper'); \
                  community_card[0].click()"
        self.driver.execute_script(script)
        # community_card.click()

    def get_known_posts(self):
        with open(self.json_path, "r+") as f:
            self.known_posts = json.load(f)

    def set_known_posts(self):
        with open(self.json_path, "w") as json_file:
            json_file.write(json.dumps(self.seen_posts))

    #Updates self.seen_posts with current unresolved threads
    def get_unresolved_posts(self):
        self.seen_posts = {}
        try:
            unresolved = self.wait.until(EC.presence_of_all_elements_located((By.XPATH,\
                                            '//span[@class="unresolvedCount"]')))
        except:
            return
        unresolved_buttons = [s.find_element_by_xpath("..") for s in unresolved]

        #Fills self.seen_posts with the currently unresolved threads
        for b in unresolved_buttons:
            #Click b
            b.click()
            #Click the unresolved button
            unresolved_button = self.wait.until(EC.element_to_be_clickable((By.ID,\
                                                            'UnresolvedFilterButton')))
            unresolved_button.click()
            #Get the unresolved threads
            thread_list = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,\
                                                            '.thread')))
            channel = b.get_attribute("textContent")[:-1]
            channel_id = b.get_attribute("value")
            self.get_threads(thread_list, channel, channel_id)

    def get_threads(self, thread_list, channel, channel_id):
        for t in thread_list:
            thread = Thread(t, self.driver, channel, channel_id)
            self.seen_posts[str(hash(thread))] = thread.__dict__

    def new_thread_notification(self, thread):
        author = thread["author"]
        channel = "#"+thread["channel"]
        subject = thread["subject"]
        thread_link = thread["thread_link"]
        text = "*%s*\n<%s|%s> from %s" % (channel, thread_link, subject, author)
        request_data = {
            "token" : self.slack_bot_auth_token,
            "channel" : self.channel,
            "text" : text
        }
        requests.post("https://slack.com/api/chat.postMessage",\
                        data = request_data)
    def follow_up_notification(self, thread):
        channel = "#"+thread["channel"]
        reply = thread["replies"][-1]
        name = reply["name"]
        subject = reply["thread_subject"]
        thread_link = thread["thread_link"]
        text = "*%s*\n%s replied to <%s|%s>" % (channel, name, thread_link, subject)
        request_data = {
        "token" : self.slack_bot_auth_token,
        "channel" : self.channel,
        "text" : text
        }
        requests.post("https://slack.com/api/chat.postMessage",\
                    data = request_data)

    def get_notification_timestamp_channel_id(self, thread):
        thread_link = thread["thread_link"]
        text = "in:#%s from:@%s '%s'" % (self.channel, self.username, thread_link)
        search_JSON = {
           "token" : self.slack_user_auth_token,
            "query" : text,
            "count" : "1",
            "sort" : "timestamp",
            "sort_dir" : "asc"
        }
        result = requests.get("https://slack.com/api/search.messages",\
                                                        params = search_JSON)
        result = result.json()
        if result['messages']["matches"]:
            timestamp = result['messages']["matches"][0]["ts"]
            channel_id = result['messages']["matches"][0]["channel"]
            channel_id = channel_id["id"]
            return timestamp, channel_id
        else:
            raise BaseException("Message timestamp not found: %s from %s" %\
                                          (thread["subject"], thread["author"]))

    def remove_checkbox_react(self, timestamp, channel_id):
        request_data = {
            "token" : self.slack_bot_auth_token,
            "name" : "white_check_mark",
            "channel" : channel_id,
            "timestamp" : timestamp
        }
        requests.post("https://slack.com/api/reactions.remove", data = request_data)

    def add_checkbox_react(self, timestamp, channel_id):
        request_data = {
            "token" : self.slack_bot_auth_token,
            "name" : "white_check_mark",
            "channel" : channel_id,
            "timestamp" : timestamp
        }
        requests.post("https://slack.com/api/reactions.add", data = request_data)

    def add_eyes_react(self, timestamp, channel_id):
        request_data = {
            "token" : self.slack_bot_auth_token,
            "name" : "eyes",
            "channel" : channel_id,
            "timestamp" : timestamp
        }
        requests.post("https://slack.com/api/reactions.add", data = request_data)

    def remove_eyes_react(self, timestamp, channel_id):
        request_data = {
            "token" : self.slack_bot_auth_token,
            "name" : "eyes",
            "channel" : channel_id,
            "timestamp" : timestamp
        }
        requests.post("https://slack.com/api/reactions.remove", data = request_data)

    def watching_detection(self):
        for key in self.seen_posts:
            upvotes = int(self.seen_posts[key]["upvotes"])
            timestamp, channel_id = self.get_notification_timestamp_channel_id(self.seen_posts[key])
            if upvotes > 0:
                self.add_eyes_react(timestamp, channel_id)
            else:
                self.remove_eyes_react(timestamp, channel_id)


    def resolved_detection(self):
        for key in self.known_posts:
            if key not in self.seen_posts:
                #Previously unresolved Question is now resolved
                timestamp, channel_id = self.get_notification_timestamp_channel_id(self.known_posts[key])
                self.add_checkbox_react(timestamp, channel_id)
                self.remove_eyes_react(timestamp, channel_id)

    def unresolved_detection(self):
        for key in self.seen_posts:
            if not (key in self.known_posts):
                if self.seen_posts[key]["replies"]:
                    try:
                        timestamp, channel_id = self.get_notification_timestamp_channel_id(self.seen_posts[key])
                        self.remove_checkbox_react(timestamp, channel_id)
                        self.follow_up_notification(self.seen_posts[key])
                    except:
                        self.new_thread_notification(self.seen_posts[key])
                else:
                    self.new_thread_notification(self.seen_posts[key])
            else:
                replies_seen = len(self.seen_posts[key]["replies"])
                replies_known = len(self.known_posts[key]["replies"])
                if replies_seen != replies_known:
                    timestamp, channel_id = self.get_notification_timestamp_channel_id(self.seen_posts[key])
                    self.remove_checkbox_react(timestamp, channel_id)
                    self.follow_up_notification(self.seen_posts[key])

    def check_for_updates(self):
        self.get_known_posts()
        self.get_unresolved_posts()

        if not self.seen_posts:
            self.resolved_detection()
            self.set_known_posts()
            self.driver.quit()
        else:
            if not self.known_posts:
                self.unresolved_detection()
                self.set_known_posts()
                try:
                    self.watching_detection()
                except: pass
            else:
                self.unresolved_detection()
                self.resolved_detection()
                self.set_known_posts()
                try:
                    self.watching_detection()
                except: pass

    def run(self):
        try:
            print("Navigating through login screen...", end="")
            self.navigate_through_login()
            print("passed.")
            print("Navigating through community card screen...", end = "")
            self.navigate_through_community_card_options()
            print("passed.")
            print("Checking for updates...", end="")
            self.check_for_updates()
            print("passed.")
            print("Quiting driver...", end="")
            self.driver.quit()
            print("done.")
            print("Bye!")
        except Exception as e:
            print("failed.")
            print("Quiting driver...", end="")
            self.driver.quit()
            print("done.")
            print("Bye!")
            raise




class Thread:
    def __init__(self, t, driver, channel, channel_id):
        self.channel = channel
        self.channel_id = channel_id
        self.get_attributes(t, driver)

    def get_thread_link(self, t, driver):
        #Get query parameters
        c = '99224b2f-9072-46b6-b442-c0c3a785439b'
        thread_id = t.get_attribute("id")
        thread_id = thread_id[thread_id.find(":") + 1 : ]
        #Construct final thread_link
        thread_link = "https://platform.parthean.com/Home?c=%s&v=%s&t=%s" %\
                         (c, self.channel_id , thread_id)
        return thread_link

    def get_attributes(self, t, driver):
        #Author
        self.author = t.find_element_by_class_name("header-left-side")\
                .find_elements_by_tag_name("span")[0]\
                .get_attribute("textContent")
        #Subject
        self.subject = t.find_element_by_class_name("subject")\
                .find_element_by_tag_name("h2")\
                .get_attribute("textContent")
        #Original Post
        self.message = t.find_element_by_id("firstMessageText")\
                        .find_element_by_tag_name("p")\
                        .get_attribute("textContent")
        #Replies
        self.replies = self.get_replies(t, driver, self.channel)
        #Upvotes
        self.upvotes = t.find_element_by_id("threadReplies")\
                        .find_element_by_class_name("options-toolbar-item")\
                        .find_elements_by_tag_name("span")[1]\
                        .get_attribute("textContent")
        #Thread Link
        self.thread_link = self.get_thread_link(t, driver)

    def get_hashables(self):
        return (self.author, self.subject,self.message, self.channel)

    def __repr__(self):
        return "%s,%s,%s,%s" % self.get_hashables()

    def __hash__(self):
        hl = md5()
        hl.update(str(self).encode("utf-8"))
        return int(hl.hexdigest(), 16)

    def __eq__(self,other):
        return (isinstance(other, Thread)) and\
               (self.author == other.author) and\
               (self.subject == other.subject) and\
               (self.message == other.message) and\
               (self.replies == other.replies)

    #Returns a tuple containing a thread's replies
    def get_replies(self, t, driver, channel):
        #Find replies button
        replies_button = t.find_element_by_id("threadReplies")\
                        .find_element_by_css_selector('button.back-button.replies-button')
        #Click the replies button
        replies_button.click()
        #Read the list of replies
        replies = t.find_element_by_id("threadReplies")\
                        .find_element_by_id("messageList")\
                        .find_elements_by_css_selector("div.bodyArea.replyWrapper")
        replies_list = list()
        for r in replies:
            reply = Reply(r, t, channel)
            replies_list.append(reply.__dict__)
        return replies_list

class Reply:
    def __init__(self, r, t, channel):
        self.channel = channel
        self.name, self.message, \
            self.thread_subject = self.get_attributes(r,t)

    def get_attributes(self, r, t):
        #Extract the reply info
        name = r.find_element_by_class_name("message-header")\
                .find_element_by_tag_name("p").get_attribute("textContent")
        message = r.find_element_by_class_name("message-body")\
                   .find_element_by_tag_name("p").get_attribute("textContent")
        thread_subject = t.find_element_by_class_name("subject")\
                          .find_element_by_tag_name("h2")\
                          .get_attribute("textContent")
        return name, message, thread_subject

    def get_hashables(self):
        return(self.name, self.message)

    def __repr__(self):
        return "%s, %s, %s" % self.get_hashables()
    
    def __hash__(self):
        hl = md5()
        hl.update(self.name.encode('utf-8'))
        hl.update(self.message.encode('utf-8'))
        return int(hl.hexdigest(), 16)

    def __eq__(self, other):
        return (isinstance(other, Reply)) and\
               (self.name == other.name) and\
               (self.message == other.message)
