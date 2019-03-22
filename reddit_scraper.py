import math
import json
import requests
import itertools
import numpy as np
import time
from datetime import datetime, timedelta
import praw
import json
import pout
import os

def make_request(uri, max_retries = 5):
    def fire_away(uri):
        response = requests.get(uri)
        assert response.status_code == 200
        return json.loads(response.content)
    current_tries = 1
    while current_tries < max_retries:
        try:
            time.sleep(1)
            response = fire_away(uri)
            return response
        except:
            time.sleep(1)
            current_tries += 1
    return fire_away(uri)


def pull_posts_for(subreddit, start_at, end_at):

    def map_posts(posts):
        return list(map(lambda post: {
            'id': post['id'],
            'created_utc': post['created_utc'],
            'prefix': 't4_'
        }, posts))

    SIZE = 500
    URI_TEMPLATE = r'https://api.pushshift.io/reddit/search/submission?subreddit={}&after={}&before={}&size={}'

    post_collections = map_posts( \
        make_request( \
            URI_TEMPLATE.format( \
                subreddit, start_at, end_at, SIZE))['data'])
    n = len(post_collections)
    while n == SIZE:
        last = post_collections[-1]
        new_start_at = last['created_utc'] - (10)

        more_posts = map_posts( \
            make_request( \
                URI_TEMPLATE.format( \
                    subreddit, new_start_at, end_at, SIZE))['data'])

        n = len(more_posts)
        post_collections.extend(more_posts)

    return post_collections


def give_me_intervals(start_at, number_of_days_per_interval = 3):

    end_at = math.ceil(datetime.utcnow().timestamp())

    ## 1 day = 86400,
    period = (86400 * number_of_days_per_interval)
    end = start_at + period
    yield (int(start_at), int(end))
    padding = 1
    while end <= end_at:
        start_at = end + padding
        end = (start_at - padding) + period
        yield int(start_at), int(end)


subreddit = 'PersonalFinanceCanada'
start_at = math.floor(\
    (datetime.utcnow() - timedelta(weeks=373)).timestamp())

posts = []
for interval in give_me_intervals(start_at, number_of_days_per_interval=3):
    pulled_posts = pull_posts_for(
        subreddit, interval[0], interval[1])

    posts.extend(pulled_posts)
    time.sleep(.500)

print('Length of total pulled posts:', len(posts))

num_posts = len(np.unique([ post['id'] for post in posts ]))
print('Length of unique pulled posts:', num_posts)


config = {
    "username" : "",
    "client_id" : "",
    "client_secret" : "",
    "user_agent" : ""
}

reddit = praw.Reddit(client_id = config['client_id'], \
                     client_secret = config['client_secret'], \
                     user_agent = config['user_agent'])

TIMEOUT_AFTER_COMMENT_IN_SECS = .350
posts_and_comments = []
count = 1
print('On submission {} out of {}'.format(count, num_posts))
for submission_id in np.unique([ post['id'] for post in posts ]):
    if count % 10 == 0:
        print('On submission {} out of {}'.format(count, num_posts))

    post_dict = {}

    submission = reddit.submission(id=submission_id)
    submission.comments.replace_more(limit=None)

    comment_queue = submission.comments[:]

    post_dict['title'] = submission.title
    post_dict['description'] = submission.selftext
    post_dict['link'] = submission.url
    post_dict['date'] = datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S')
    post_dict['num_comments'] = submission.num_comments
    post_dict['score'] = submission.score

    if comment_queue:
        post_dict['replies'] = [{}]
    else:
        post_dict['replies'] = []

    ref_nodes = [post_dict['replies']]
    depth = 0
    num_replies = [len(comment_queue)]
    parents = [post_dict]
    while comment_queue:
        comment = comment_queue.pop(0)
        ref_nodes[depth][-1]['comment'] = comment.body
        ref_nodes[depth][-1]['score'] = comment.score

        replies = comment.replies
        if replies:
            replies.replace_more(limit=None)
            replies = replies[:]
            comment_queue = list(replies) + comment_queue

            parents.append(ref_nodes[depth][-1])
            ref_nodes[depth][-1]['replies'] = [{}]
            ref_nodes.append([ref_nodes[depth][-1]['replies'][-1]])

            num_replies[depth] -= 1
            if num_replies[depth] > 0:
                parents[-2]['replies'].append({})
                ref_nodes[depth] = [parents[-2]['replies'][-1]]

            num_replies.append(len(replies))
            depth += 1
        else:
            ref_nodes[depth][-1]['replies'] = None

            num_replies[depth] -= 1
            if num_replies[depth] > 0:
                del ref_nodes[depth]
                parents[-1]['replies'].append({})
                ref_nodes.append([parents[-1]['replies'][-1]])
            else:
                while num_replies[depth] == 0:
                    del num_replies[depth]
                    if parents:
                        del parents[-1]

                    if depth == 0:
                        break
                    else:
                        del ref_nodes[depth]
                        depth -= 1

        if TIMEOUT_AFTER_COMMENT_IN_SECS > 0:
            time.sleep(TIMEOUT_AFTER_COMMENT_IN_SECS)

    posts_and_comments.append(post_dict)

    time.sleep(TIMEOUT_AFTER_COMMENT_IN_SECS)
    count += 1

with open(subreddit + '.json', 'w') as outfile:
    json_file = json.dump(posts_and_comments, outfile)
