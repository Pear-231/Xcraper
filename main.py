import asyncio
import os
from twikit import Client
from core.directories import Directories
from core.credentials import USERNAME, EMAIL, PASSWORD
from post_quoters_tool.post_quoters_tool import PostQuotersTool
from user_posts_tool.user_posts_compiler import UserPostsTool
from post_reposters_tool.post_reposters_compiler import PostRepostersTool

async def initialise_client():
    cookies_file = f"{Directories.COOKIES_PATH}{USERNAME}_cookies.json"
    client = Client("en-UK")
    if not os.path.exists(cookies_file):
        await client.login(
            auth_info_1=USERNAME,
            auth_info_2=EMAIL,
            password=PASSWORD
        )
        client.save_cookies(cookies_file)
    else:
        client.load_cookies(path=cookies_file)
    return client

async def main():
    client = await initialise_client()

    screen_name = "DavidLammy"
    start_date = "05/07/2024"
    end_date = "07/11/2024"

    user_posts_data = await UserPostsTool.compile_user_posts_data(client, screen_name, start_date, end_date)
    await PostQuotersTool.compile_quoters_data(client, user_posts_data, screen_name)
    await PostRepostersTool.compile_reposters_data(client, user_posts_data, screen_name)

if __name__ == "__main__":
    asyncio.run(main())