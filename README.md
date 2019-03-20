# reddit_scraper_2019
A new way to get all the posts from a subreddit after being limited to 1000 posts by the reddit api. Creates a JSON file where replies are nested to maintain the structure of every reddit post.

Make sure all dependencies are installed

## Example of the layout in txt
![alt text](https://github.com/aherrmannca/reddit_scraper_2019/blob/master/example_snippet.png)
NOTE: Title and score are placed below replies despite being created before replies for whatever reason.

## How to modify

### Choosing your subreddit
Line 77: Change string to the subreddit name (case sensitive)

### Choosing your date range
Line 79: Change Timedelta to how long ago you wish to scrape posts.

### Making sure you actually scrape all posts
Line 82: I suggest just keeping the number of days small, perhaps even smaller on larger subreddits.

### Setting up your client
Lines 95-100: Provide a username, client_id, client_secret, and user_agent.
To get this information:
1. Use your own reddit username
2. Set up your own client, to do this view this short tutorial (you only need to read up to registering a bot):
  [I'm an inline-style link](https://progur.com/2016/09/how-to-create-reddit-bot-using-praw4.html)
3. Google a list of common user agents and just use any

### Run the code and you're set!

### NOTE: if you want the text to be easily readable, run beautifier.py
### I suggest using VSCode to open large text files and going to view > Toggle Word Wrap for the file to be as easily readable as possible
  
