from core.directories import Directories
from core.utilities.data_compiler_helpers import DataCompilerHelpers
from core.utilities.file_processing import FileProcessing
from twikit_utilities.twikit_client import TwikitClient

class PostQuotersTool:
    @staticmethod
    async  def compile_quoters_data(client, user_posts_data, user_screen_name):
        file_path = f"{Directories.RESULTS_DIRECTORY}{user_screen_name}_quoters.csv"
        quoters_data = await PostQuotersTool.get_quoters_data(client, user_posts_data, file_path)
        return quoters_data

    @staticmethod
    async def get_quoters_data(client, user_posts_data, file_path):
        quoters_data = []
        print("Getting quoters data.")

        for post_data in user_posts_data:
            query_post_url = DataCompilerHelpers.convert_url_from_x_to_twitter(post_data["Post URL"])
            post_quoters_data = await TwikitClient.make_client_rate_limited_call(client, "search_tweet", None, query_post_url, "Top")

            quotes_count = post_data["Quote Reposts"]
            processed_quoters = 0

            while processed_quoters < quotes_count:
                for quote_post in post_quoters_data:
                    quote_post_data = await PostQuotersTool.extract_quoters_data(post_data, quote_post)
                    quoters_data.append(quote_post_data)

                    # Save file each time in case some error occurs to prevent data loss.
                    FileProcessing.export_to_csv(file_path, quoters_data)

                    print(f"\n==================== Quote post data for url: {post_data['Post URL']} from user: {post_data["Username"]} ====================\n")
                    print(quote_post_data)

                    processed_quoters += 1
                    if processed_quoters >= quotes_count:
                        print(f"Ending collection of quote post data due to meeting to quotes_count.")
                        break

                if processed_quoters < quotes_count:
                    more_quoters = await TwikitClient.make_client_rate_limited_call(client, "search_tweet", None, query_post_url, "Top", cursor=post_quoters_data.next_cursor)
                    if more_quoters:
                        post_quoters_data = more_quoters
                    else:
                        print(f"Ending collection of quote post data as there is no more data to collect.")
                        break

        return quoters_data

    @staticmethod
    async def extract_quoters_data(post_data, quote_post_data):
        return {
            "Quoted Post URL": post_data["Post URL"],
            "Quoted Username": post_data["Username"],
            "Quoter Username": quote_post_data.user.screen_name,
            "Quoter Name": quote_post_data.user.name,
            "Quoter ID": quote_post_data.user.id,
            "Quoter Location": quote_post_data.user.location,
            "Quoter Followers": quote_post_data.user.followers_count,
            "Quoter Following": quote_post_data.user.following_count,
            "Quoter Description": quote_post_data.user.description,
            "Post Time": quote_post_data.created_at,
            "Post URL": DataCompilerHelpers.get_post_link(quote_post_data),
            "Text": DataCompilerHelpers.get_post_text(quote_post_data),
            "Text Without Links": DataCompilerHelpers.get_post_text_without_links(DataCompilerHelpers.get_post_text(quote_post_data)),
            "Impressions": quote_post_data.view_count,
            "Replies": quote_post_data.reply_count,
            "Reposts": quote_post_data.retweet_count,
            "Quote Reposts": quote_post_data.quote_count,
            "Likes": quote_post_data.favorite_count,
            "Bookmarks": quote_post_data._data["legacy"]["bookmark_count"],
            "Total Engagement": (
                    quote_post_data.reply_count
                    + quote_post_data.retweet_count
                    + quote_post_data.quote_count
                    + quote_post_data.favorite_count
                    + quote_post_data._data["legacy"]["bookmark_count"]
            ),
            "Hashtags": DataCompilerHelpers.get_hashtags(quote_post_data),
            "Post_Content_URLs": DataCompilerHelpers.get_links(DataCompilerHelpers.get_post_text(quote_post_data)),
            "Is Quote": quote_post_data.is_quote_status,
            "Is Repost": DataCompilerHelpers.is_repost(quote_post_data),
            "Media Type": DataCompilerHelpers.get_media_type(quote_post_data),
            "Photo Count": DataCompilerHelpers.get_photo_count(quote_post_data),
            "Video Count": DataCompilerHelpers.get_video_count(quote_post_data),
            "Language": quote_post_data.lang,
            "Place": quote_post_data.place,
            "Has Community Notes": quote_post_data.has_community_notes
        }