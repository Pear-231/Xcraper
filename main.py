import asyncio
from post_quoters_tool.post_quoters_tool import PostQuotersTool
from user_posts_tool.user_posts_compiler import UserPostsTool
from post_reposters_tool.post_reposters_compiler import PostRepostersTool
from twikit_utilities.twikit_client import TwikitClient

async def main():
    client = await TwikitClient.initialise_client()

    screen_name = "DavidLammy"
    start_date = "05/07/2024"
    end_date = "07/11/2024"

    user_posts_data = await UserPostsTool.compile_user_posts_data(client, screen_name, start_date, end_date)
    await PostQuotersTool.compile_quoters_data(client, user_posts_data, screen_name)
    await PostRepostersTool.compile_reposters_data(client, user_posts_data, screen_name)

if __name__ == "__main__":
    asyncio.run(main())