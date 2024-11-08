from datetime import datetime
from core.directories import Directories
from core.utilities.data_compiler_helpers import DataCompilerHelpers
from core.utilities.file_processing import FileProcessing
from twikit_utilities.twikit_client import TwikitClient

class UserPostsCompiler:
    @staticmethod
    async def compile_user_posts_data(client, user_screen_name, start_date_str, end_date_str):
        posts_data = []
        is_start_date_reached = False

        start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
        end_date = datetime.strptime(end_date_str, "%d/%m/%Y")
        file_path = f"{Directories.RESULTS_DIRECTORY}{user_screen_name}_posts.csv"

        user = await TwikitClient.make_client_rate_limited_call(client, "get_user_by_screen_name", None, user_screen_name)
        posts = await TwikitClient.make_client_rate_limited_call(client, "get_user_tweets", None, user.id, "Tweets")
        print(f"Collecting data between {start_date.strftime('%d/%m/%Y')} and {end_date.strftime('%d/%m/%Y')}.")

        while not is_start_date_reached:
            for post in posts:
                post_date = post.created_at_datetime.replace(tzinfo=None)
                if post_date <= end_date:
                    if post_date <= start_date:
                        print("Start date reached. Ending post data collection.")
                        is_start_date_reached = True
                        break

                    post_data = UserPostsCompiler.extract_post_data(post)
                    posts_data.append(post_data)

                    # Save file each time in case some error occurs to prevent data loss.
                    FileProcessing.export_to_csv(file_path, posts_data)

                    print(f"\n==================== Post data for user: {user_screen_name} ====================\n")
                    print(post_data)

            if is_start_date_reached:
                break

            more_tweets = await TwikitClient.make_client_rate_limited_call(client,"get_user_tweets", None, user.id, "Tweets", cursor=posts.next_cursor)
            if more_tweets:
                posts = more_tweets
            else:
                break

        return posts_data

    @staticmethod
    def extract_post_data(post):
        return {
            "Post Time": post.created_at,
            "Post URL": DataCompilerHelpers.get_post_link(post),
            "Post ID": post.id,
            "Username": post.user.screen_name,
            "Name": post.user.name,
            "User ID": post.user.id,
            "Text": DataCompilerHelpers.get_post_text(post),
            "Text Without Links": DataCompilerHelpers.get_post_text_without_links(DataCompilerHelpers.get_post_text(post)),
            "Impressions": post.view_count,
            "Replies": post.reply_count,
            "Reposts": post.retweet_count,
            "Quote Reposts": post.quote_count,
            "Likes": post.favorite_count,
            "Bookmarks": post._data["legacy"]["bookmark_count"],
            "Total Engagement": (
                    post.reply_count
                    + post.retweet_count
                    + post.quote_count
                    + post.favorite_count
                    + post._data["legacy"]["bookmark_count"]
            ),
            "Hashtags": DataCompilerHelpers.get_hashtags(post),
            "Post_Content_URLs": DataCompilerHelpers.get_links(DataCompilerHelpers.get_post_text(post)),
            "Is Quote": post.is_quote_status,
            "Is Repost": DataCompilerHelpers.is_repost(post),
            "Media Type": DataCompilerHelpers.get_media_type(post),
            "Photo Count": DataCompilerHelpers.get_photo_count(post),
            "Video Count": DataCompilerHelpers.get_video_count(post),
            "Language": post.lang,
            "Place": post.place,
            "Has Community Notes": post.has_community_notes
        }