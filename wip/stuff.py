from twikit_utilities.twikit_client import *

async def get_likers_data(post_data, post_id):
    likers = []
    likers_data = []

    likes = post_data.favorite_count
    initial_likers = await client.get_favoriters(post_id)
    likers.extend(initial_likers)

    while len(likers) != likes:
        more_likers = initial_likers.next()
        likers.extend(more_likers)
        print(len(likers))

    for liker in likers:
        liker_data = {
            "Published": liker.created_at,
            "Name": liker.name,
            "Screen Name": liker.screen_name,
            "Location": liker.location,
            "Followers": liker.followers_count
        }
        likers_data.append(liker_data)

    return likers_data