from core.directories import Directories
from core.utilities.file_processing import FileProcessing
from twikit_utilities.twikit_client import TwikitClient

class PostRepostersCompiler:
    @staticmethod
    async def compile_reposters_data(client, user_posts_data, user_screen_name, reposters_file):
        reposters_data = []

        last_processed_post_url = None
        is_processing_allowed = False

        if reposters_file is not None:
            reposters_data = FileProcessing.import_from_csv(reposters_file)
            last_processed_post_url = reposters_data[-1]["Reposted Post URL"]
            reposters_data = [reposter for reposter in reposters_data if reposter["Reposted Post URL"] != last_processed_post_url]

        file_path = f"{Directories.RESULTS_DIRECTORY}{user_screen_name}_reposters.csv"
        print("Getting reposters data.")

        for post_data in user_posts_data:
            post_url = post_data["Post URL"]

            if reposters_file is not None and is_processing_allowed == False:
                if post_url == last_processed_post_url:
                    is_processing_allowed = True
                else:
                    continue

            reposters = await TwikitClient.make_client_rate_limited_call(client, "get_retweeters", None, post_data["Post ID"])

            reposts_count = post_data["Reposts"]
            processed_reposters = 0

            while processed_reposters < reposts_count:
                for reposter in reposters:
                    reposter_data = await PostRepostersCompiler.extract_reposters_data(post_data, reposter)
                    reposters_data.append(reposter_data)

                    # Save file each time in case some error occurs to prevent data loss.
                    FileProcessing.export_to_csv(file_path, reposters_data)

                    print(f"\n==================== Repost post data for url: {post_data['Post URL']} from user: {post_data["Username"]} ====================\n")
                    print(reposter_data)

                    processed_reposters += 1
                    if processed_reposters >= reposts_count:
                        print(f"Ending collection of reposters data due to meeting to reposts_count.")
                        break

                if processed_reposters < reposts_count:
                    more_reposters = await TwikitClient.make_client_rate_limited_call(client, "get_retweeters", None, post_data["Post ID"], cursor=reposters.next_cursor)
                    if more_reposters:
                        reposters = more_reposters
                    else:
                        print(f"Ending collection of reposters data as there is no more data to collect.")
                        break

        return reposters_data

    @staticmethod
    async def extract_reposters_data(post_data, reposter):
        return {
            "Reposted Post URL": post_data["Post URL"],
            "Repost Time": reposter.created_at,
            "Name": reposter.name,
            "Screen Name": reposter.screen_name,
            "User ID": reposter.id,
            "Location": reposter.location,
            "Followers": reposter.followers_count,
            "Following": reposter.following_count,
            "Description": reposter.description,
        }