from datetime import datetime
from core.directories import Directories
from core.utilities.data_compiler_helpers import DataCompilerHelpers
from core.utilities.file_processing import FileProcessing
from twikit_utilities.twikit_client import TwikitClient

class UserPostsTool:
    @staticmethod
    async def compile_user_posts_data(client, user_screen_name, start_date_str, end_date_str):
        start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
        end_date = datetime.strptime(end_date_str, "%d/%m/%Y")
        file_path = f"{Directories.RESULTS_DIRECTORY}{user_screen_name}_posts.csv"

        user_posts_data = await UserPostsTool.get_user_posts_data(client, user_screen_name, start_date, end_date)
        FileProcessing.export_to_csv(file_path, user_posts_data)
        return user_posts_data

    @staticmethod
    async def get_user_posts_data(client, user_screen_name, start_date, end_date):
        posts_data = []
        is_start_date_reached = False

        user = await TwikitClient.make_client_rate_limited_call(client, "get_user_by_screen_name", None, user_screen_name)
        twikit_posts_data = await TwikitClient.make_client_rate_limited_call(client, "get_user_tweets", None, user.id, "Tweets")

        while not is_start_date_reached:
            print(f"Collecting data between {start_date.strftime('%d/%m/%Y')} and {end_date.strftime('%d/%m/%Y')}.")
            for twikit_post_data in twikit_posts_data:
                post_date = twikit_post_data.created_at_datetime.replace(tzinfo=None)
                if post_date <= end_date:
                    if post_date <= start_date:
                        print("Start date reached. Ending post data collection.")
                        is_start_date_reached = True
                        break

                    post_data = UserPostsTool.extract_post_data(twikit_post_data)
                    posts_data.append(post_data)

                    print(f"\n==================== POST DATA FOR [{user_screen_name}_posts.csv] ====================\n")
                    print(post_data)

            if is_start_date_reached:
                break

            more_tweets = await TwikitClient.make_client_rate_limited_call(client,"get_user_tweets", None, user.id, "Tweets", cursor=twikit_posts_data.next_cursor)
            if more_tweets:
                twikit_posts_data = more_tweets
            else:
                break

        return posts_data

    @staticmethod
    def extract_post_data(twikit_post_data):
        return {
            "Published": twikit_post_data.created_at,
            "Post URL": DataCompilerHelpers.get_post_link(twikit_post_data),
            "Post ID": twikit_post_data.id,
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