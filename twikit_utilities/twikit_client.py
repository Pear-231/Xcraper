import asyncio
import os
from twikit import Client
from datetime import datetime, timedelta
from core.credentials import USERNAME, EMAIL, PASSWORD
from core.directories import Directories

class TwikitClient:
    # https://github.com/d60/twikit/blob/main/ratelimits.md
    # Where there is no rate limit I've set it to 99999.
    RATE_LIMITS = {
        "add_members_to_group": 99999,
        "block_user": 187,
        "get_user_verified_followers": 500,
        "get_bookmarks": 500,
        "delete_all_bookmarks": 99999,
        "change_group_name": 900,
        "get_group_dm_history": 900,
        "get_dm_history": 900,
        "bookmark_tweet": 99999,
        "create_poll": 99999,
        "follow_user": 15,
        "create_list": 99999,
        "retweet": 99999,
        "create_scheduled_tweet": 99999,
        "create_tweet": 99999,
        "delete_bookmark": 99999,
        "delete_dm": 99999,
        "delete_list_banner": 99999,
        "delete_retweet": 99999,
        "delete_scheduled_tweet": 99999,
        "delete_tweet": 99999,
        "unfollow_user": 187,
        "edit_list_banner": 99999,
        "get_favoriters": 500,
        "favorite_tweet": 99999,
        "get_scheduled_tweets": 500,
        "get_user_followers": 50,
        "get_user_followers_you_know": 500,
        "get_user_following": 500,
        "get_guest_token": 99999,
        "get_latest_timeline": 500,
        "get_timeline": 500,
        "dm_inbox_initial_state": 450,
        "add_list_member": 99999,
        "get_list": 500,
        "get_list_tweets": 500,
        "get_lists": 500,
        "get_list_members": 500,
        "remove_list_member": 99999,
        "get_list_subscribers": 500,
        "logout": 187,
        "add_reaction_to_message": 99999,
        "remove_reaction_from_message": 99999,
        "mute_user": 187,
        "get_notifications_all": 180,
        "get_notifications_mentions": 180,
        "get_notifications_verified": 180,
        "get_retweeters": 500,
        "search_tweet": 50,
        "search_user": 50,
        "send_dm": 187,
        "user_id": 99999,
        "get_trends": 20000,
        "get_tweet_by_id": 150,
        "unblock_user": 187,
        "unfavorite_tweet": 99999,
        "unmute_user": 187,
        "edit_list": 99999,
        "upload_media": 99999,
        "get_user_by_id": 500,
        "get_user_by_screen_name": 95,
        "get_user_tweets_likes": 500,
        "get_user_tweets_media": 500,
        "get_user_tweets": 50,
        "get_user_tweets_replies": 50,
        "vote": 99999,
    }

    CALL_INTERVALS = {func: (15 * 60) / (limit - 1) for func, limit in RATE_LIMITS.items()}
    LAST_CALL_TIMES = {}

    def __init__(self, locale='en-UK'):
        self.client = Client(locale)
        self.CALL_INTERVALS = {func: (15 * 60) / (limit - 1) for func, limit in self.RATE_LIMITS.items()}
        self.LAST_CALL_TIMES = {}

    async def initialise_client(self):
        cookies_file = f"{Directories.COOKIES_PATH}{USERNAME}_cookies.json"
        if not os.path.exists(cookies_file):
            await self.client.login(
                auth_info_1=USERNAME,
                auth_info_2=EMAIL,
                password=PASSWORD
            )
            self.client.save_cookies(cookies_file)
        else:
            self.client.load_cookies(path=cookies_file)

    async def make_rate_limited_call(self, function_name, *args, **kwargs):
        now = datetime.now()
        last_call = self.LAST_CALL_TIMES.get(function_name, now - timedelta(seconds=self.CALL_INTERVALS[function_name]))
        time_since_last_call = (now - last_call).total_seconds()
        sleep_time = max(0, self.CALL_INTERVALS[function_name] - time_since_last_call)

        if sleep_time > 0:
            print(f"Sleeping for {sleep_time:.2f} seconds for {function_name} to respect rate limit.")
            await asyncio.sleep(sleep_time)

        self.LAST_CALL_TIMES[function_name] = datetime.now()
        try:
            method = getattr(self.client, function_name)
            result = await method(*args, **kwargs)
            return result
        except AttributeError:
            print(f"Function '{function_name}' not found in client.")
            return None
        except Exception as e:
            print(f"An error occurred in {function_name}: {e}")
            return None