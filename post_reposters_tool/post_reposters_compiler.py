from core.directories import Directories
from core.utilities.file_processing import FileProcessing
from twikit_utilities.twikit_client import TwikitClient

class PostRepostersTool:
    @staticmethod
    async  def compile_likers_data(client, user_posts_data, user_screen_name):
        file_path = f"{Directories.RESULTS_DIRECTORY}{user_screen_name}_reposters.csv"
        reposters_data = await PostRepostersTool.get_likers_data(client, user_posts_data)
        FileProcessing.export_to_csv(file_path, reposters_data)
        return reposters_data

    @staticmethod
    async def get_likers_data(client, user_posts_data):
        reposters_data = []

        print("Getting Likers data.")
        for post_data in user_posts_data:
            post_reposters = await TwikitClient.make_client_rate_limited_call(client, "get_retweeters", None, post_data["Post ID"])

            reposters_count = post_data["Reposters Count"]
            processed_reposters = 0

            while processed_reposters < reposters_count:
                for reposter in post_reposters:
                    reposter_data = await PostRepostersTool.extract_reposters_data(post_data, reposter)
                    reposters_data.append(reposter_data)

                    print(f"\n==================== REPOSTER DATA FOR POST {post_data['Post URL']} ====================\n")
                    print(reposter_data)

                    processed_reposters += 1
                    if processed_reposters >= reposters_count:
                        print(f"Ending collection of reposters data due to meeting to reposters_count.")
                        break

                if processed_reposters < reposters_count:
                    more_reposters = await TwikitClient.make_client_rate_limited_call(client, "get_retweeters", None, post_data["Post ID"], cursor=post_reposters.next_cursor)
                    if more_reposters:
                        post_reposters = more_reposters
                    else:
                        print(f"Ending collection of reposters data as there is no more data to collect.")
                        break

        return reposters_data

    @staticmethod
    async def extract_reposters_data(post_data, reposter):
        reposter_data = {
            "Post URL": post_data["Post URL"],
            "Published": reposter.created_at,
            "Name": reposter.name,
            "Screen Name": reposter.screen_name,
            "ID" : reposter.id,
            "Location": reposter.location,
            "Followers": reposter.followers_count,
            "Following" : reposter.following_count,
            "Description" : reposter.description,
        }
        return reposter_data