import asyncio
from compilers.user_posts_compiler import UserPostsCompiler
from compilers.post_quotes_compiler import PostQuotesCompiler
from compilers.post_reposters_compiler import PostRepostersCompiler
from compilers.post_replies_compiler import PostRepliesCompiler
from twikit_utilities.twikit_client import TwikitClient

async def main():
    client = await TwikitClient.initialise_client()

    screen_name = "screename"
    start_date = "05/11/2024"
    end_date = "07/11/2024"

    user_posts_data = await UserPostsCompiler.compile_user_posts_data(client, screen_name, start_date, end_date)
    await PostQuotesCompiler.compile_quotes_data(client, user_posts_data, screen_name)
    await PostRepostersCompiler.compile_reposters_data(client, user_posts_data, screen_name)
    await PostRepliesCompiler.compile_replies_data(client, user_posts_data, screen_name)

if __name__ == "__main__":
    asyncio.run(main())