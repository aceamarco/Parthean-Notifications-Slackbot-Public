# Parthean Notifications Slack Bot
## Introduction
This is a private Slack workspace app for Carnegie Mellon Universities offering of Fundamentals of Programming 15-112 M20. It will notify a specific Slack Channel dedicated to notifcations from Parthean about any new posts made to the website.

## Features
### Thread and Reply Objects
- This scripts uses two models of information on Parthean.
#### Threads
- Attributes: Author, subject, original message, list of replies, date posted, number of upvotes, and a link to the thread — all values stored as strings.
#### Replies
- Attributes: Channel, name, message, date, parent thread subject — all values stored as strings.
### Unresolved Detection
- This script generates a list of currently unresolved threads by scrapping the channels list for any channel element containing a span tag containing a number.
- The script builds a dictionary containing all the currently unresolved threads' dictionary representations.
- This dictionary is later stored into a JSON file to be used during it's next session as it's previously known posts.
### Resolved Detection
- This script loops through the last known posts from the posts.json file and checks whether it was in the list of currently seen unresolved threads.
### Slack Messages
#### Notifications
- In the case of a new thread, the script will send a message to a slack channel containing: The thread's channel, subject, and author.
- In the case of a follow up reply, the script will send a message to a slack channel containing: The reply's channel, parent thread subject, and author.
#### Reacts
- When a previously unresolved post is now resolved, the script will add a :white_check_box: react to it's respective notification on the slack channel.
- When a currently unresolved post has a number of upvotes > 0, the script will add a :eyes: react to it's respective notification on the slack channel.


