import os
from core.directories import Directories
from core.utilities.data_compiler_helpers import DataCompilerHelpers
from core.utilities.file_processing import FileProcessing
from twikit_utilities.twikit_client import TwikitClient

class PostRepliesCompiler:
    @staticmethod
    async def compile_replies_data(client, user_posts_data, user_screen_name, replies_file):
        replies_cursor = {}
        replies_data = []

        last_processed_post_url = None
        is_processing_allowed = False
        # Define this here to prevent it being updated after the file is created later in the process.
        does_replies_file_exist = os.path.exists(replies_file)

        if does_replies_file_exist:
            replies_data = FileProcessing.import_from_csv(replies_file)
            last_processed_post_url = replies_data[-1]["Replying to Post URL"]
            replies_data = [reply for reply in replies_data if reply["Replying to Post URL"] != last_processed_post_url]

        file_path = f"{Directories.RESULTS_DIRECTORY}{user_screen_name}_replies.csv"
        print("Getting replies data.")

        for post_data in user_posts_data:
            post_url = post_data["Post URL"]

            if does_replies_file_exist and is_processing_allowed == False:
                if post_url == last_processed_post_url:
                    is_processing_allowed = True
                    print("Processing replies data from file.")
                else:
                    continue

            tweet_id = post_data["Post ID"]
            post = await TwikitClient.make_client_rate_limited_call(client, "get_tweet_by_id", None, tweet_id)
            replies = post.replies

            replies_count = post_data["Replies"]
            processed_replies = 0

            while processed_replies < replies_count:
                for reply in replies:
                    reply_data = await PostRepliesCompiler.extract_replies_data(post_data, reply)
                    replies_data.append(reply_data)

                    # Save file each time in case some error occurs to prevent data loss.
                    FileProcessing.export_to_csv(file_path, replies_data)

                    print(f"\n==================== Reply data for url: {post_data['Post URL']} from user: {post_data["Username"]} ====================\n")
                    print(reply_data)

                    processed_replies += 1
                    if processed_replies >= replies_count:
                        print(f"Ending collection of replies data due to meeting to replies_count.")
                        break

                replies_cursor[tweet_id] = replies.next_cursor
                if not replies.next_cursor:
                    break

                # There is no bespoke API call for getting replies so assume it has the same rate limit as get_tweet_by_id and sleep accordingly.
                await TwikitClient.sleep_for_rate_limit("get_tweet_by_id")
                TwikitClient.update_last_call_time("get_tweet_by_id")

                replies = await replies.next()

    @staticmethod
    async def extract_replies_data(post_data, reply):
        return {
            "Replying to Post URL": post_data["Post URL"],
            "Replying to Username": post_data["Username"],
            "Replier Username": reply.user.screen_name,
            "Replier Name": reply.user.name,
            "Replier ID": reply.user.id,
            "Replier Location": reply.user.location,
            "Replier Followers": reply.user.followers_count,
            "Replier Following": reply.user.following_count,
            "Replier Description": reply.user.description,
            "Post Time": reply.created_at,
            "Post URL": DataCompilerHelpers.get_post_link(reply),
            "Text": DataCompilerHelpers.get_post_text(reply),
            "Text Without Links": DataCompilerHelpers.get_post_text_without_links(DataCompilerHelpers.get_post_text(reply)),
            "Impressions": reply.view_count,
            "Replies": reply.reply_count,
            "Reposts": reply.retweet_count,
            "Quote Reposts": reply.quote_count,
            "Likes": reply.favorite_count,
            "Bookmarks": reply._data["legacy"]["bookmark_count"],
            "Total Engagement": (
                    reply.reply_count
                    + reply.retweet_count
                    + reply.quote_count
                    + reply.favorite_count
                    + reply._data["legacy"]["bookmark_count"]
            ),
            "Hashtags": DataCompilerHelpers.get_hashtags(reply),
            "Post_Content_URLs": DataCompilerHelpers.get_links(DataCompilerHelpers.get_post_text(reply)),
            "Is Quote": reply.is_quote_status,
            "Is Repost": DataCompilerHelpers.is_repost(reply),
            "Media Type": DataCompilerHelpers.get_media_type(reply),
            "Photo Count": DataCompilerHelpers.get_photo_count(reply),
            "Video Count": DataCompilerHelpers.get_video_count(reply),
            "Language": reply.lang,
            "Place": reply.place,
            "Has Community Notes": reply.has_community_notes
        }