from core.directories import Directories
from core.utilities.data_compiler_helpers import DataCompilerHelpers
from core.utilities.file_processing import FileProcessing
from twikit_utilities.twikit_client import TwikitClient

class PostQuotesCompiler:
    @staticmethod
    async def compile_quotes_data(client, user_posts_data, user_screen_name):
        quotes_data = []

        file_path = f"{Directories.RESULTS_DIRECTORY}{user_screen_name}_quoters.csv"
        print("Getting quotes data.")

        for post_data in user_posts_data:
            query_post_url = DataCompilerHelpers.convert_url_from_x_to_twitter(post_data["Post URL"])
            quotes = await TwikitClient.make_client_rate_limited_call(client, "search_tweet", None, query_post_url, "Top")

            quotes_count = post_data["Quote Reposts"]
            processed_quotes = 0

            while processed_quotes < quotes_count:
                for quote in quotes:
                    quote_data = await PostQuotesCompiler.extract_quotes_data(post_data, quote)
                    quotes_data.append(quote_data)

                    # Save file each time in case some error occurs to prevent data loss.
                    FileProcessing.export_to_csv(file_path, quotes_data)

                    print(f"\n==================== Quote post data for url: {post_data['Post URL']} from user: {post_data["Username"]} ====================\n")
                    print(quote_data)

                    processed_quotes += 1
                    if processed_quotes >= quotes_count:
                        print(f"Ending collection of quote post data due to meeting to quotes_count.")
                        break

                if processed_quotes < quotes_count:
                    more_quoters = await TwikitClient.make_client_rate_limited_call(client, "search_tweet", None, query_post_url, "Top", cursor=quotes.next_cursor)
                    if more_quoters:
                        quotes = more_quoters
                    else:
                        print(f"Ending collection of quote post data as there is no more data to collect.")
                        break

        return quotes_data

    @staticmethod
    async def extract_quotes_data(post_data, quote):
        return {
            "Quoting Post URL": post_data["Post URL"],
            "Quoting Username": post_data["Username"],
            "Quoter Username": quote.user.screen_name,
            "Quoter Name": quote.user.name,
            "Quoter ID": quote.user.id,
            "Quoter Location": quote.user.location,
            "Quoter Followers": quote.user.followers_count,
            "Quoter Following": quote.user.following_count,
            "Quoter Description": quote.user.description,
            "Post Time": quote.created_at,
            "Post URL": DataCompilerHelpers.get_post_link(quote),
            "Text": DataCompilerHelpers.get_post_text(quote),
            "Text Without Links": DataCompilerHelpers.get_post_text_without_links(DataCompilerHelpers.get_post_text(quote)),
            "Impressions": quote.view_count,
            "Replies": quote.reply_count,
            "Reposts": quote.retweet_count,
            "Quote Reposts": quote.quote_count,
            "Likes": quote.favorite_count,
            "Bookmarks": quote._data["legacy"]["bookmark_count"],
            "Total Engagement": (
                    quote.reply_count
                    + quote.retweet_count
                    + quote.quote_count
                    + quote.favorite_count
                    + quote._data["legacy"]["bookmark_count"]
            ),
            "Hashtags": DataCompilerHelpers.get_hashtags(quote),
            "Post_Content_URLs": DataCompilerHelpers.get_links(DataCompilerHelpers.get_post_text(quote)),
            "Is Quote": quote.is_quote_status,
            "Is Repost": DataCompilerHelpers.is_repost(quote),
            "Media Type": DataCompilerHelpers.get_media_type(quote),
            "Photo Count": DataCompilerHelpers.get_photo_count(quote),
            "Video Count": DataCompilerHelpers.get_video_count(quote),
            "Language": quote.lang,
            "Place": quote.place,
            "Has Community Notes": quote.has_community_notes
        }