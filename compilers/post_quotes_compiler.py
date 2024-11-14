import os
from core.directories import Directories
from core.utilities.data_compiler_helpers import DataCompilerHelpers
from core.utilities.file_processing import FileProcessing
from twikit_utilities.twikit_client import TwikitClient

class PostQuotesCompiler:
    @staticmethod
    async def compile_quotes_data(client, user_posts_data, user_screen_name, quotes_file):
        quotes_data = []

        last_processed_post_url = None
        is_processing_allowed = False
        # Define this here to prevent it being updated after the file is created later in the process.
        does_quotes_file_exist = os.path.exists(quotes_file)

        if does_quotes_file_exist:
            quotes_data = FileProcessing.import_from_csv(quotes_file)
            last_processed_post_url = quotes_data[-1]["Quoting Post URL"]
            quotes_data = [quote for quote in quotes_data if quote["Quoting Post URL"] != last_processed_post_url]

        file_path = quotes_file or f"{Directories.RESULTS_DIRECTORY}{user_screen_name}_quotes.csv"
        print("Getting quotes data.")

        for post_data in user_posts_data:
            post_url = post_data["Post URL"]

            if does_quotes_file_exist and is_processing_allowed == False:
                if post_url == last_processed_post_url:
                    is_processing_allowed = True
                    print("Processing quotes data from file.")
                else:
                    continue

            query_post_url = f"{user_screen_name}/Status/{post_data["Post ID"]}"
            quotes = await TwikitClient.make_client_rate_limited_call(client, "search_tweet", None, query_post_url, "Top")

            processed_quotes = 0

            if not quotes:
                print("No quotes found for this post.")
                continue

            while quotes:
                for quote in quotes:
                    if post_data["Post URL"] != DataCompilerHelpers.get_post_link(quote):
                        quote_data = PostQuotesCompiler.extract_quotes_data(post_data, quote)
                        quotes_data.append(quote_data)

                        FileProcessing.export_to_csv(file_path, quotes_data)

                        print(f"\n==================== Quote post data for url: {post_data['Post URL']} from user: {post_data['Username']} ====================\n")
                        print(quote_data)

                        processed_quotes += 1

                more_quoters = await TwikitClient.make_client_rate_limited_call(client, "search_tweet", None, query_post_url, "Top", cursor=quotes.next_cursor)
                if more_quoters:
                    quotes = more_quoters
                else:
                    print("Ending collection of quote post data as there is no more data to collect.")
                    break

        return quotes_data

    @staticmethod
    def extract_quotes_data(post_data, quote):
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