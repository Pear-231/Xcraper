import asyncio
import os
from compilers.user_posts_compiler import UserPostsCompiler
from compilers.post_quotes_compiler import PostQuotesCompiler
from compilers.post_reposters_compiler import PostRepostersCompiler
from compilers.post_replies_compiler import PostRepliesCompiler
from core.utilities.file_processing import FileProcessing
from twikit_utilities.twikit_client import TwikitClient

async def main():
    client = await TwikitClient.initialise_client()

    screen_name = "screen_name"
    start_date = "05/07/2024"
    end_date = "08/11/2024"

    # Specify the file paths if they already exist to continue processing from the most recent post in those files.
    # This is to accommodate any errors / connection issues causing processing to stop.
    user_posts_file = "C:/Path/To/posts.csv"
    quotes_file = "C:/Path/To/quotes.csv"
    reposters_file = "C:/Path/To/reposters.csv"
    replies_file = "C:/Path/To/replies.csv"

    if os.path.exists(user_posts_file):
        user_posts_data = FileProcessing.import_from_csv(user_posts_file)
    else:
        user_posts_data = await UserPostsCompiler.compile_user_posts_data(client, screen_name, start_date, end_date)

    await PostQuotesCompiler.compile_quotes_data(client, user_posts_data, screen_name, quotes_file)
    await PostRepostersCompiler.compile_reposters_data(client, user_posts_data, screen_name, reposters_file)
    await PostRepliesCompiler.compile_replies_data(client, user_posts_data, screen_name, replies_file)

if __name__ == "__main__":
    asyncio.run(main())