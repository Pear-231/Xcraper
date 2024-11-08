import asyncio
from compilers.user_posts_compiler import UserPostsCompiler
from compilers.post_quoters_compiler import PostQuotersCompiler
from compilers.post_reposters_compiler import PostRepostersCompiler
from twikit_utilities.twikit_client import TwikitClient

async def main():
    client = await TwikitClient.initialise_client()

    screen_name = "DavidLammy"
    start_date = "05/07/2024"
    end_date = "07/11/2024"

    user_posts_data = await UserPostsCompiler.compile_user_posts_data(client, screen_name, start_date, end_date)
    await PostQuotersCompiler.compile_quoters_data(client, user_posts_data, screen_name)
    await PostRepostersCompiler.compile_reposters_data(client, user_posts_data, screen_name)

if __name__ == "__main__":
    asyncio.run(main())