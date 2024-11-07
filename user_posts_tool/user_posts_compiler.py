from datetime import datetime
from core.directories import Directories
from core.utilities.data_compiler_helpers import DataCompilerHelpers
from core.utilities.file_processing import FileProcessing
from twikit_utilities.twikit_client import TwikitClient

class UserPostsTool:
    def __init__(self, user_screen_name, start_date_str, end_date_str):
        self.user_screen_name = user_screen_name
        self.start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
        self.end_date = datetime.strptime(end_date_str, "%d/%m/%Y")
        self.file_path = f"{Directories.POSTS_DIRECTORY}{user_screen_name}_posts.csv"
        self.twikit_client = TwikitClient()

    async def compile_user_posts_data(self):
        await self.twikit_client.initialise_client()
        user_posts_data = await self.get_user_posts_data()
        FileProcessing.export_to_csv(self.file_path, user_posts_data)
        return user_posts_data

    async def get_user_posts_data(self):
        posts_data = []
        is_start_date_reached = False

        user = await self.twikit_client.make_rate_limited_call("get_user_by_screen_name", self.user_screen_name)
        twikit_posts_data = await self.twikit_client.make_rate_limited_call("get_user_tweets", user.id, "Tweets")

        while not is_start_date_reached:
            print(f"Collecting data between {self.start_date.strftime('%d/%m/%Y')} and {self.end_date.strftime('%d/%m/%Y')}.")
            for twikit_post_data in twikit_posts_data:
                post_date = twikit_post_data.created_at_datetime.replace(tzinfo=None)
                if post_date <= self.end_date:
                    if post_date <= self.start_date:
                        print("Start date reached. Ending post data collection.")
                        is_start_date_reached = True
                        break

                    post_data = self.extract_post_data(twikit_post_data)
                    posts_data.append(post_data)

                    print(f"\n==================== POST DATA FOR [{self.user_screen_name}_posts.csv] ====================\n")
                    print(post_data)

            if is_start_date_reached:
                break

            # Collect the next batch of posts
            more_tweets = await self.twikit_client.make_rate_limited_call(
                "get_user_tweets", user.id, "Tweets", cursor=twikit_posts_data.next_cursor
            )
            if more_tweets:
                twikit_posts_data = more_tweets
            else:
                break

        return posts_data

    def extract_post_data(self, twikit_post_data):
        """Extracts and formats a post's data into a dictionary."""
        return {
            "Published": twikit_post_data.created_at,
            "Post_URL": DataCompilerHelpers.get_post_link(twikit_post_data),
            "Username": twikit_post_data.user.screen_name,
            "Name": twikit_post_data.user.name,
            "Text": DataCompilerHelpers.get_post_text(twikit_post_data),
            "Text Without Links": DataCompilerHelpers.get_post_text_without_links(DataCompilerHelpers.get_post_text(twikit_post_data)),
            "Impressions": twikit_post_data.view_count,
            "Replies": twikit_post_data.reply_count,
            "Reposts": twikit_post_data.retweet_count,
            "Quote Reposts": twikit_post_data.quote_count,
            "Likes": twikit_post_data.favorite_count,
            "Bookmarks": twikit_post_data._data["legacy"]["bookmark_count"],
            "Total Engagement": (
                twikit_post_data.reply_count
                + twikit_post_data.retweet_count
                + twikit_post_data.quote_count
                + twikit_post_data.favorite_count
                + twikit_post_data._data["legacy"]["bookmark_count"]
            ),
            "Hashtags": DataCompilerHelpers.get_hashtags(twikit_post_data),
            "Post_Content_URLs": DataCompilerHelpers.get_links(DataCompilerHelpers.get_post_text(twikit_post_data)),
            "Is Quote": twikit_post_data.is_quote_status,
            "Is Repost": DataCompilerHelpers.is_repost(twikit_post_data),
            "Media Type": DataCompilerHelpers.get_media_type(twikit_post_data),
            "Photo Count": DataCompilerHelpers.get_photo_count(twikit_post_data),
            "Video Count": DataCompilerHelpers.get_video_count(twikit_post_data)
        }