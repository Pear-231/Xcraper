import asyncio
from user_posts_tool.user_posts_compiler import UserPostsTool

async def main():
    user_post_data_tool = UserPostsTool("some_user_screen_name", "05/11/2024", "07/11/2024")
    user_posts_data = await user_post_data_tool.compile_user_posts_data()

if __name__ == "__main__":
    asyncio.run(main())