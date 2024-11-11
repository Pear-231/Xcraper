import html
import re

class DataCompilerHelpers:
    @staticmethod
    def get_hashtags(post_data):
        if not post_data.hashtags:
            hashtags = ""
        else:
            hashtags = ", ".join(f"#{tag}" for tag in post_data.hashtags)
        return hashtags

    @staticmethod
    def get_post_text_without_links(post_text):
        url_pattern = r'\s*http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        text_without_links = re.sub(url_pattern, '', post_text)
        return text_without_links

    @staticmethod
    def get_post_text(post_data):
        post_text = ""
        if post_data.full_text is not None:
            post_text = post_data.full_text
        elif post_data.full_text is None:
            post_text = post_data.text
        post_text = html.unescape(post_text)
        return post_text

    @staticmethod
    def get_post_id_from_link(spike_post_data):
        link = spike_post_data["Link"]
        parts = link.split("/")
        post_id = parts[-1]
        return post_id

    @staticmethod
    def get_post_link(twikit_post_data):
        post_url = f"https://x.com/{twikit_post_data.user.screen_name}/status/{twikit_post_data.id}"
        return post_url

    @staticmethod
    def get_links(text):
        url_pattern = r"https?://\S+"
        links = re.findall(url_pattern, text)
        return links

    @staticmethod
    def get_photo_count(twikit_post_data):
        photo_count = 0
        if twikit_post_data.media is not None:
            for media in twikit_post_data.media:
                media_type = media.get("type")
                if media_type == "photo":
                    photo_count += 1
        return photo_count

    @staticmethod
    def get_video_count(twikit_post_data):
        video_count = 0
        if twikit_post_data.media is not None:
            for media in twikit_post_data.media:
                media_type = media.get("type")
                if media_type == "video":
                    video_count += 1
        return video_count

    @staticmethod
    def get_media_type(twikit_post_data):
        media_types = ["photo", "video", "animated_gif"]
        post_media_type = ""

        if DataCompilerHelpers.get_post_text(twikit_post_data) is not None:
            post_media_type += "text"

        if twikit_post_data.media:
            for media in twikit_post_data.media:
                media_type = media.get("type")
                if media_type in media_types:
                    if post_media_type:
                        post_media_type += ", "
                    post_media_type += media_type
                else:
                    if post_media_type:
                        post_media_type += ", "
                    post_media_type += "unknown"
                    break

        return post_media_type

    @staticmethod
    def is_repost(twikit_post_data):
        if twikit_post_data.retweeted_tweet and not twikit_post_data.is_quote_status:
            return True
        return False