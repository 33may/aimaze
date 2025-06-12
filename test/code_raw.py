
from FunctionClass import BaseFunction
from ParameterClass import Parameter, ParameterType
from OutputParameterClass import OutputParameter, OutputParameterType
from InputClass import StandardInput
from OutputClass import StandardOutput
from BaseClass import APIWrapper

# from shared.FunctionClass import BaseFunction
# from shared.ParameterClass import Parameter, ParameterType
# from shared.OutputParameterClass import OutputParameter, OutputParameterType
# from shared.InputClass import StandardInput
# from shared.OutputClass import StandardOutput
# from shared.BaseClass import APIWrapper, AuthType

from dataclasses import dataclass
        

@dataclass
class APIClientConfig:
    """Configuration class for API settings"""
    type: str = None,  # Must be either `artist`, `user`, or `'user'` depending on context; specify object type.
    ids: str = None,  # Comma-separated list of Spotify IDs used for various endpoints, with a maximum count of 50, to identify artists, tracks, shows, or users.
    limit: int = "20",  # Number of items to return per request, with typical range from 1 to 100 or 50 depending on endpoint.
    market: str = None,  # ISO 3166-1 alpha-2 country code to filter content or specify market, defaulting to user's country if not provided.
    seed_artists: str = None,  # Comma-separated list of Spotify artist IDs to seed recommendations.
    seed_genres: str = None,  # Comma-separated list of genres to seed recommendations.
    seed_tracks: str = None,  # Comma-separated list of Spotify track IDs to seed recommendations.
    device_id: str = None,  # ID of the device to target for playback operations; optional.
    locale: str = None,  # Locale string in ISO 639-1 and ISO 3166-1 alpha-2 for language-specific responses.
    id: str = None,  # The Spotify ID of a specific resource such as track, album, show, or category.
    offset: int = "0",  # Index of the first item to return, used for pagination.
    position_ms: int = None,  # Position in milliseconds to seek to within the current track.
    category_id: str = None,  # Identifier for specific category; used in category-related endpoints.
    country: str = None,  # ISO 3166-1 alpha-2 country code indicating user's country, used for regional content filtering.
    display_name: str = None,  # User's display name; null if not available.
    email: str = None,  # User's email address; available only if scope is granted.
    explicit_content: int = None,  # Explicit content settings object or flag.
    external_urls: str = None,  # External URLs associated with the user.
    followers_total: int = "0",  # Number of followers the user has.
    href: str = None,  # API link to the user's profile.
    images_url: str = None,  # URL of the user's profile image.
    product: str = None,  # Subscription level: e.g., premium, free.
    uri: str = None,  # Spotify URI for the user or resource.
    state: int = None,  # Boolean as integer indicating shuffle state; true (1) to shuffle, false (0) to not.
    playlist_id: str = None,  # Spotify ID of the playlist to fetch items from.
    fields: str = None,  # Specific data fields to include in the response.
    additional_types: str = None,  # Additional content types supported besides 'track', such as 'episode'.
    category_id: str = None,  # Identifier for a category, used to fetch related playlists or items.
    body: str = None,  # JSON payload, such as list of IDs for batch operations.

    def get_oauth_params(self, method: str, url: str) -> Dict[str, str]:
        return {}

    def validate(self):
        # Asserts here
        pass

    def __init__(self):  # Validation on init.
        self.validate()

api_wrapper = APIWrapper(APIClientConfig(), base_url="https://developer.spotify.com/documentation/web-api", name="Spotify")
    


class Add_Item_to_Playback_Queue(BaseFunction):
    """Adds an item (track or episode) to the user's playback queue. Requires 'user-modify-playback-state' scope."""
    name = "Add Item to Playback Queue"
    url = "https://api.spotify.com/v1/me/player/queue"
    args_in_url = False
    method = "PUT"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="uri", param_type=ParameterType.STRING, required=True),  # The URI of the item to add to the queue. Must be a track or an episode URI. Example: 'spotify:track:4iV5W9uYEdYUVa79Axb7Rh',
			Parameter(name="device_id", param_type=ParameterType.STRING, required=False),  # The ID of the device to target. If not provided, the currently active device will be used. Example: '0d1841b0976bae2a3a310dd74c0f3df354899bc8'
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Add_Item_to_Playback_Queue.method, 
                                           Add_Item_to_Playback_Queue.url,
                                           Add_Item_to_Playback_Queue.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Add_Item_to_Playback_Queue': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Several_Tracks(BaseFunction):
    """Retrieves information for multiple tracks based on their Spotify IDs. Requires 'user-read-private' or 'user-read-email' scope."""
    name = "Get Several Tracks"
    url = "https://api.spotify.com/v1/tracks"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="market", param_type=ParameterType.STRING, required=False),  # An ISO 3166-1 alpha-2 country code to filter tracks available in that market. Example: 'ES',
			Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of Spotify IDs for the tracks. Maximum: 50 IDs. Example: '7ouMYWpwJ422jRcDASZB7P,1301WleyT98MSxVHPZCA6M'
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="tracks", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of track objects, each containing detailed information about a track.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_Several_Tracks.method, 
                                           Get_Several_Tracks.url,
                                           Get_Several_Tracks.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Several_Tracks': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Check_if_User_Follows_Playlist(BaseFunction):
    """Checks if the current user is following the specified playlist. Requires 'playlist-read-private' scope."""
    name = "Check if User Follows Playlist"
    url = "https://api.spotify.com/v1/playlists/{playlist_id}/followers/contains"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="playlist_id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the playlist. Example: '3cEYpjA9oz9GiPac4AsH4n',
			Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list containing the Spotify Username of the current user. Maximum: 1 ID. Example: 'jmperezperez'
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="follows", param_type=OutputParameterType.BOOLEAN, is_array=True),  # An array containing a single boolean indicating if the user follows the playlist.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Check_if_User_Follows_Playlist.method, 
                                           Check_if_User_Follows_Playlist.url,
                                           Check_if_User_Follows_Playlist.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Check_if_User_Follows_Playlist': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Unfollow_Artists_or_Users(BaseFunction):
    """Remove the current user as a follower of one or more artists or other Spotify users."""
    name = "Unfollow Artists or Users"
    url = "https://api.spotify.com/v1/me/followingtype"
    args_in_url = False
    method = "DELETE"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="type", param_type=ParameterType.STRING, required=True),  # The ID type: either `artist` or `user`. Allowed values: "artist", "user".,
			Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of the artist or user Spotify IDs. Example: `ids=74ASZWbe4lXaubB36ztrGX,08td7MxkoHQkXnWAYD8d6Q`. Max of 50 IDs.,
			Parameter(name="body", param_type=OutputParameterType.OBJECT, required=False),  # Request body supporting a JSON array of IDs.
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Unfollow_Artists_or_Users.method, 
                                           Unfollow_Artists_or_Users.url,
                                           Unfollow_Artists_or_Users.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Unfollow_Artists_or_Users': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Available_Genre_Seeds(BaseFunction):
    """Retrieve a list of available genre seed parameter values for recommendations, deprecated."""
    name = "Get Available Genre Seeds"
    url = "https://api.spotify.com/documentation/web-api/reference/check-users-saved-shows"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="genres", param_type=OutputParameterType.STRING, is_array=True),  # An array of available genre seed parameter values for recommendations.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_Available_Genre_Seeds.method, 
                                           Get_Available_Genre_Seeds.url,
                                           Get_Available_Genre_Seeds.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Available_Genre_Seeds': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Search_for_Item(BaseFunction):
    """Performs a search across Spotify catalogs, matching the provided query string with specified item types."""
    name = "Search for Item"
    url = "https://api.spotify.com/v1/search"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="q", param_type=ParameterType.STRING, required=True),  # Your search query. Use field filters to narrow down your search. Available filters include 'album', 'artist', 'track', 'year', 'upc', 'tag:hipster', 'tag:new', 'isrc', and 'genre'. The query supports URL encoding.,
			Parameter(name="type", param_type=ParameterType.STRING, required=True),  # A comma-separated list of item types to search across. Allowed values: "album", "artist", "playlist", "track", "show", "episode", "audiobook".,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # An ISO 3166-1 alpha-2 country code to filter results by market. If not provided, default market or user’s country setting is used.,
			Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Maximum number of results to return per item type. Default is 20. Range: 0-50.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # Index of the first result to return. Useful for paging. Default is 0. Range: 0-1000.,
			Parameter(name="include_external", param_type=ParameterType.STRING, required=False),  # Set to 'audio' to include externally hosted audio content in the results. Allowed value: "audio".
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="tracks", param_type=OutputParameterType.OBJECT, is_array=False),  # The result object containing search hits for various item types.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Search_for_Item.method, 
                                           Search_for_Item.url,
                                           Search_for_Item.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Search_for_Item': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Playlist_Cover_Image(BaseFunction):
    """Retrieves the current images associated with a specific playlist, such as cover art."""
    name = "Get Playlist Cover Image"
    url = "https://api.spotify.com/v1/playlists/{playlist_id}/images"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="playlist_id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the playlist. Example: '3cEYpjA9oz9GiPac4AsH4n'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="images", param_type=OutputParameterType.OBJECT, is_array=True),  # An array of image objects representing the playlist's cover images.,
			OutputParameter(name="url", param_type=OutputParameterType.STRING, is_array=False),  # The source URL of the image. Example: 'https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228'.,
			OutputParameter(name="height", param_type=OutputParameterType.INTEGER, is_array=False),  # The height of the image in pixels. Nullable. Example: 300.,
			OutputParameter(name="width", param_type=OutputParameterType.INTEGER, is_array=False),  # The width of the image in pixels. Nullable. Example: 300.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_Playlist_Cover_Image.method, 
                                           Get_Playlist_Cover_Image.url,
                                           Get_Playlist_Cover_Image.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Playlist_Cover_Image': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_users_saved_episodes(BaseFunction):
    """Retrieves a list of episodes saved in the current user's library."""
    name = "Get user's saved episodes"
    url = "https://api.spotify.com/v1/me/episodes"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="market", param_type=ParameterType.STRING, required=False),  # An ISO 3166-1 alpha-2 country code, e.g., 'ES'. If specified, only content available in that market is returned. If omitted, defaults to user's country.,
			Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Maximum number of items to return. Default is 20. Range: 1-50.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # The index of the first item to return. Default is 0.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the Web API endpoint returning the full result.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # Maximum number of items in the response.,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=False),  # URL to the next page of results or null if none.,
			OutputParameter(name="offset", param_type=OutputParameterType.INTEGER, is_array=False),  # Offset of the items returned.,
			OutputParameter(name="previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to the previous page or null if none.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of saved episodes available.,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of saved episode objects.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_users_saved_episodes.method, 
                                           Get_users_saved_episodes.url,
                                           Get_users_saved_episodes.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_users_saved_episodes': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Check_if_episodes_are_saved_in_users_library(BaseFunction):
    """Checks if one or more episodes are saved in the current user's library."""
    name = "Check if episodes are saved in user's library"
    url = "https://api.spotify.com/v1/me/episodes/contains"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # Comma-separated list of Spotify episode IDs, maximum 50. Example: '77o6BIVlYM3msb4MMIL1jH,0Q86acNRm6V9GYx55SXKwf'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="", param_type=OutputParameterType.BOOLEAN, is_array=True),  # Array of booleans indicating if each episode ID is saved (true) or not (false).
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Check_if_episodes_are_saved_in_users_library.method, 
                                           Check_if_episodes_are_saved_in_users_library.url,
                                           Check_if_episodes_are_saved_in_users_library.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Check_if_episodes_are_saved_in_users_library': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Set_volume_for_users_current_playback_device(BaseFunction):
    """Sets the volume for the user's current playback device. Works only for Spotify Premium users."""
    name = "Set volume for user's current playback device"
    url = "https://api.spotify.com/v1/me/player/volume"
    args_in_url = False
    method = "PUT"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="volume_percent", param_type=ParameterType.INTEGER, required=True),  # Volume to set, range 0-100.,
			Parameter(name="device_id", param_type=ParameterType.STRING, required=False),  # ID of the target device. If omitted, the currently active device is used.
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Set_volume_for_users_current_playback_device.method, 
                                           Set_volume_for_users_current_playback_device.url,
                                           Set_volume_for_users_current_playback_device.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Set_volume_for_users_current_playback_device': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Check_Users_Saved_Audiobooks_GET_meaudiobookscontains(BaseFunction):
    """Checks if one or more audiobooks are saved in the current user's library. Requires 'user-library-read' scope."""
    name = "Check User's Saved Audiobooks (GET /me/audiobooks/contains)"
    url = "https://api.spotify.com/v1/me/audiobooks/contains"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of Spotify IDs for audiobooks. Maximum: 50 IDs. Example: '18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ',
			Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Number of items to return (default 20, min 1, max 50).
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="response", param_type=OutputParameterType.BOOLEAN, is_array=True),  # An array of booleans indicating if each audiobooks ID is saved in the user's library. Example: [false,true]
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Check_Users_Saved_Audiobooks_GET_meaudiobookscontains.method, 
                                           Check_Users_Saved_Audiobooks_GET_meaudiobookscontains.url,
                                           Check_Users_Saved_Audiobooks_GET_meaudiobookscontains.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Check_Users_Saved_Audiobooks_GET_meaudiobookscontains': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Users_Saved_Shows_GET_meshows(BaseFunction):
    """Retrieves a list of shows saved in the current user's library. Requires 'user-library-read' scope."""
    name = "Get User's Saved Shows (GET /me/shows)"
    url = "https://api.spotify.com/v1/me/shows"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Maximum number of items to return. Default 20, min 1, max 50.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # The index of the first item to return. Default 0.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the Web API endpoint returning full result.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # Maximum number of items in response.,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=False),  # URL to next page of items, or null.,
			OutputParameter(name="offset", param_type=OutputParameterType.INTEGER, is_array=False),  # The offset of the items returned.,
			OutputParameter(name="previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to previous page, or null.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of saved shows.,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of saved show objects.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_Users_Saved_Shows_GET_meshows.method, 
                                           Get_Users_Saved_Shows_GET_meshows.url,
                                           Get_Users_Saved_Shows_GET_meshows.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Users_Saved_Shows_GET_meshows': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Remove_Users_Saved_Shows_DELETE_meshows(BaseFunction):
    """Deletes one or more shows from the current user's library. Requires 'user-library-modify' scope."""
    name = "Remove User's Saved Shows (DELETE /me/shows)"
    url = "https://api.spotify.com/v1/me/shows"
    args_in_url = False
    method = "DELETE"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of Spotify IDs for shows to remove. Maximum: 50 IDs. Example: '5CfCWKI5pZ28U0uOzXkDHe,5as3aKmN2k11yfDDDSrvaZ',
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # ISO 3166-1 alpha-2 country code to specify the market. If not provided, user country will be used.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="response", param_type=OutputParameterType.OBJECT, is_array=False),  # Empty response body indicates successful removal.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Remove_Users_Saved_Shows_DELETE_meshows.method, 
                                           Remove_Users_Saved_Shows_DELETE_meshows.url,
                                           Remove_Users_Saved_Shows_DELETE_meshows.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Remove_Users_Saved_Shows_DELETE_meshows': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Users_Saved_Albums_GET_mealbums(BaseFunction):
    """Retrieves a list of albums saved in the current user's library. Requires 'user-library-read' scope."""
    name = "Get User's Saved Albums (GET /me/albums)"
    url = "https://api.spotify.com/v1/me/albums"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Maximum number of items to return. Default 20, min 1, max 50.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # The index of the first item to return. Default 0.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the full result.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # Maximum number of items in response.,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=False),  # URL to next page, or null.,
			OutputParameter(name="offset", param_type=OutputParameterType.INTEGER, is_array=False),  # The index of the first item in response.,
			OutputParameter(name="previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to previous page, or null.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of saved albums.,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of saved album objects.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_Users_Saved_Albums_GET_mealbums.method, 
                                           Get_Users_Saved_Albums_GET_mealbums.url,
                                           Get_Users_Saved_Albums_GET_mealbums.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Users_Saved_Albums_GET_mealbums': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Save_Albums_for_Current_User_PUT_mealbums(BaseFunction):
    """Saves one or more albums to the current user's library. Requires 'user-library-modify' scope."""
    name = "Save Albums for Current User (PUT /me/albums)"
    url = "https://api.spotify.com/v1/me/albums"
    args_in_url = False
    method = "PUT"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # Comma-separated list of Spotify album IDs to save. Maximum: 20.
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Save_Albums_for_Current_User_PUT_mealbums.method, 
                                           Save_Albums_for_Current_User_PUT_mealbums.url,
                                           Save_Albums_for_Current_User_PUT_mealbums.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Save_Albums_for_Current_User_PUT_mealbums': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Remove_Users_Saved_Audiobooks(BaseFunction):
    """Deletes one or more audiobooks from the Spotify user's library using their Spotify IDs. Requires 'user-library-modify' scope."""
    name = "Remove User's Saved Audiobooks"
    url = "https://api.spotify.com/v1/me/audiobooks"
    args_in_url = False
    method = "DELETE"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of Spotify IDs for the audiobooks to remove from the user's library. Maximum: 50 IDs. Example: '18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="status_code", param_type=OutputParameterType.INTEGER, is_array=False),  # HTTP response status code indicating the result of the operation.,
			OutputParameter(name="response_message", param_type=OutputParameterType.STRING, is_array=False),  # Message indicating the outcome, e.g., 'Audiobooks have been removed from the library'.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Remove_Users_Saved_Audiobooks.method, 
                                           Remove_Users_Saved_Audiobooks.url,
                                           Remove_Users_Saved_Audiobooks.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Remove_Users_Saved_Audiobooks': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_New_Releases(BaseFunction):
    """Retrieves a list of new album releases featured in Spotify. Supports optional paging via 'limit' and 'offset' query parameters."""
    name = "Get New Releases"
    url = "https://api.spotify.com/v1/browse/new-releases"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Maximum number of items to return. Default is 20. Min 1, Max 50. Example: 10.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # The index of the first item to return. Default is 0. Used for paging. Example: 5.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="albums", param_type=OutputParameterType.OBJECT, is_array=False),  # A paged set of album objects, containing details about the new releases. The object includes fields like 'href', 'limit', 'next', 'offset', 'previous', 'total', and 'items'.,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # A link to the Web API endpoint returning the full result set.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # Maximum number of items returned in this response.,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=False),  # URL to the next page of items, or null if none.,
			OutputParameter(name="offset", param_type=OutputParameterType.INTEGER, is_array=False),  # The starting index of the items returned.,
			OutputParameter(name="previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to the previous page of items, or null if none.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of new album releases available.,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of album objects representing the new releases. Each album object includes fields like 'album_type', 'total_tracks', 'available_markets', 'external_urls', 'href', 'id', 'images', 'name', 'release_date', 'release_date_precision', 'restrictions', 'type', 'uri', and 'artists'.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_New_Releases.method, 
                                           Get_New_Releases.url,
                                           Get_New_Releases.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_New_Releases': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Recommendations(BaseFunction):
    """This endpoint generates track recommendations based on seed entities and optional tuning parameters."""
    name = "Get Recommendations"
    url = "https://api.spotify.com/v1/recommendations"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # The target size of the list of recommended tracks. Default: 20. Range: 1 - 100. Example: 10.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # An ISO 3166-1 alpha-2 country code to limit content to a specific market. Example: ES.,
			Parameter(name="seed_artists", param_type=ParameterType.STRING, required=False),  # Comma-separated list of Spotify IDs for seed artists (up to 5). Required if seed_genres and seed_tracks are not set. Example: 4NHQUGzhtTLFvgF5SZesLK.,
			Parameter(name="seed_genres", param_type=ParameterType.STRING, required=False),  # Comma-separated list of genres (up to 5). Required if seed_artists and seed_tracks are not set. Example: classical,country.,
			Parameter(name="seed_tracks", param_type=ParameterType.STRING, required=False),  # Comma-separated list of Spotify IDs for seed tracks (up to 5). Required if seed_artists and seed_genres are not set. Example: 0c6xIDDpzE81m2q797ordA.,
			Parameter(name="min_acousticness", param_type=ParameterType.FLOAT, required=False),  # Minimum acousticness (0.0 - 1.0). Example: 0.2.,
			Parameter(name="max_acousticness", param_type=ParameterType.FLOAT, required=False),  # Maximum acousticness (0.0 - 1.0). Example: 0.8.,
			Parameter(name="target_acousticness", param_type=ParameterType.FLOAT, required=False),  # Target acousticness (0.0 - 1.0). Example: 0.5.,
			Parameter(name="min_danceability", param_type=ParameterType.FLOAT, required=False),  # Minimum danceability (0.0 - 1.0). Example: 0.3.,
			Parameter(name="max_danceability", param_type=ParameterType.FLOAT, required=False),  # Maximum danceability (0.0 - 1.0). Example: 0.9.,
			Parameter(name="target_danceability", param_type=ParameterType.FLOAT, required=False),  # Target danceability (0.0 - 1.0). Example: 0.6.,
			Parameter(name="min_duration_ms", param_type=ParameterType.INTEGER, required=False),  # Minimum duration in milliseconds. Example: 180000.,
			Parameter(name="max_duration_ms", param_type=ParameterType.INTEGER, required=False),  # Maximum duration in milliseconds. Example: 300000.,
			Parameter(name="target_duration_ms", param_type=ParameterType.INTEGER, required=False),  # Target duration in milliseconds. Example: 240000.,
			Parameter(name="min_energy", param_type=ParameterType.FLOAT, required=False),  # Minimum energy (0.0 - 1.0). Example: 0.4.,
			Parameter(name="max_energy", param_type=ParameterType.FLOAT, required=False),  # Maximum energy (0.0 - 1.0). Example: 0.8.,
			Parameter(name="target_energy", param_type=ParameterType.FLOAT, required=False),  # Target energy (0.0 - 1.0). Example: 0.6.,
			Parameter(name="min_instrumentalness", param_type=ParameterType.FLOAT, required=False),  # Minimum instrumentalness (0.0 - 1.0). Example: 0.1.,
			Parameter(name="max_instrumentalness", param_type=ParameterType.FLOAT, required=False),  # Maximum instrumentalness (0.0 - 1.0). Example: 0.9.,
			Parameter(name="target_instrumentalness", param_type=ParameterType.FLOAT, required=False),  # Target instrumentalness (0.0 - 1.0). Example: 0.5.,
			Parameter(name="min_key", param_type=ParameterType.INTEGER, required=False),  # Minimum key (0 - 11). Example: 0.,
			Parameter(name="max_key", param_type=ParameterType.INTEGER, required=False),  # Maximum key (0 - 11). Example: 5.,
			Parameter(name="target_key", param_type=ParameterType.INTEGER, required=False),  # Target key (0 - 11). Example: 2.,
			Parameter(name="min_liveness", param_type=ParameterType.FLOAT, required=False),  # Minimum liveness (0.0 - 1.0). Example: 0.2.,
			Parameter(name="max_liveness", param_type=ParameterType.FLOAT, required=False),  # Maximum liveness (0.0 - 1.0). Example: 0.8.,
			Parameter(name="target_liveness", param_type=ParameterType.FLOAT, required=False),  # Target liveness (0.0 - 1.0). Example: 0.5.,
			Parameter(name="min_loudness", param_type=ParameterType.FLOAT, required=False),  # Minimum loudness (0.0 - 1.0). Example: -0.6.,
			Parameter(name="max_loudness", param_type=ParameterType.FLOAT, required=False),  # Maximum loudness (0.0 - 1.0). Example: -0.2.,
			Parameter(name="target_loudness", param_type=ParameterType.FLOAT, required=False),  # Target loudness (0.0 - 1.0). Example: -0.4.,
			Parameter(name="min_mode", param_type=ParameterType.INTEGER, required=False),  # Minimum mode (0 or 1). Example: 1.,
			Parameter(name="max_mode", param_type=ParameterType.INTEGER, required=False),  # Maximum mode (0 or 1). Example: 1.,
			Parameter(name="target_mode", param_type=ParameterType.INTEGER, required=False),  # Target mode (0 or 1). Example: 1.,
			Parameter(name="min_popularity", param_type=ParameterType.INTEGER, required=False),  # Minimum popularity (0 - 100). Example: 50.,
			Parameter(name="max_popularity", param_type=ParameterType.INTEGER, required=False),  # Maximum popularity (0 - 100). Example: 80.,
			Parameter(name="target_popularity", param_type=ParameterType.INTEGER, required=False),  # Target popularity (0 - 100). Example: 60.,
			Parameter(name="min_speechiness", param_type=ParameterType.FLOAT, required=False),  # Minimum speechiness (0.0 - 1.0). Example: 0.1.,
			Parameter(name="max_speechiness", param_type=ParameterType.FLOAT, required=False),  # Maximum speechiness (0.0 - 1.0). Example: 0.9.,
			Parameter(name="target_speechiness", param_type=ParameterType.FLOAT, required=False),  # Target speechiness (0.0 - 1.0). Example: 0.5.,
			Parameter(name="min_tempo", param_type=ParameterType.FLOAT, required=False),  # Minimum tempo in BPM. Example: 100.,
			Parameter(name="max_tempo", param_type=ParameterType.FLOAT, required=False),  # Maximum tempo in BPM. Example: 140.,
			Parameter(name="target_tempo", param_type=ParameterType.FLOAT, required=False),  # Target tempo in BPM. Example: 120.,
			Parameter(name="min_time_signature", param_type=ParameterType.INTEGER, required=False),  # Minimum time signature (e.g., 3). Max: 11. Example: 4.,
			Parameter(name="max_time_signature", param_type=ParameterType.INTEGER, required=False),  # Maximum time signature. Max: 11. Example: 4.,
			Parameter(name="target_time_signature", param_type=ParameterType.INTEGER, required=False),  # Target time signature. Example: 4.,
			Parameter(name="min_valence", param_type=ParameterType.FLOAT, required=False),  # Minimum valence (0.0 - 1.0). Example: 0.2.,
			Parameter(name="max_valence", param_type=ParameterType.FLOAT, required=False),  # Maximum valence (0.0 - 1.0). Example: 0.8.,
			Parameter(name="target_valence", param_type=ParameterType.FLOAT, required=False),  # Target valence (0.0 - 1.0). Example: 0.5.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="seeds", param_type=OutputParameterType.OBJECT, is_array=True),  # An array of recommendation seed objects.,
			OutputParameter(name="tracks", param_type=OutputParameterType.OBJECT, is_array=True),  # An array of simplified track objects.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_Recommendations.method, 
                                           Get_Recommendations.url,
                                           Get_Recommendations.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Recommendations': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Display_your_Spotify_profile_data_in_a_web_app(BaseFunction):
    """Retrieve the current user's profile data."""
    name = "Display your Spotify profile data in a web app"
    url = "https://developer.spotify.com/documentation/web-api/reference/get-current-users-profile"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="country", param_type=OutputParameterType.STRING, is_array=False),  # The country of the user.,
			OutputParameter(name="display_name", param_type=OutputParameterType.STRING, is_array=False),  # The display name of the user.,
			OutputParameter(name="email", param_type=OutputParameterType.STRING, is_array=False),  # The email of the user.,
			OutputParameter(name="explicit_content", param_type=OutputParameterType.OBJECT, is_array=False),  # Object indicating whether explicit content is filtered.,
			OutputParameter(name="external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # Object with external URLs.,
			OutputParameter(name="followers", param_type=OutputParameterType.OBJECT, is_array=False),  # Object containing follower information.,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # URL to the Web API endpoint for this user.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # The Spotify ID for the user.,
			OutputParameter(name="images", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of profile images.,
			OutputParameter(name="product", param_type=OutputParameterType.STRING, is_array=False),  # Spotify product type.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # Object type.,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Display_your_Spotify_profile_data_in_a_web_app.method, 
                                           Display_your_Spotify_profile_data_in_a_web_app.url,
                                           Display_your_Spotify_profile_data_in_a_web_app.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Display_your_Spotify_profile_data_in_a_web_app': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Check_Users_Saved_Albums(BaseFunction):
    """Check if one or more albums are saved in the user's library."""
    name = "Check User's Saved Albums"
    url = "https://api.spotify.com/v1/me/albums/contains"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # Comma-separated list of Spotify IDs for albums (max 20). Example: 382ObEPsp2rxGrnsizN5TX,1A2GTWGtFfWp7KSQTwWOyo.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="0", param_type=OutputParameterType.BOOLEAN, is_array=True),  # Boolean indicating whether each album is saved in the user's library.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Check_Users_Saved_Albums.method, 
                                           Check_Users_Saved_Albums.url,
                                           Check_Users_Saved_Albums.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Check_Users_Saved_Albums': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Multiple_Shows(BaseFunction):
    """Retrieve information about multiple shows by their Spotify IDs."""
    name = "Get Multiple Shows"
    url = "https://api.spotify.com/v1/shows"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="market", param_type=ParameterType.STRING, required=False),  # An ISO 3166-1 alpha-2 country code. If specified, only content available in that market will be returned. If a user access token is provided, the user's country will take priority. If neither is provided, the content is considered unavailable. Example: 'ES'.,
			Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of Spotify IDs for the shows. Maximum: 50 IDs. Example: '5CfCWKI5pZ28U0uOzXkDHe,5as3aKmN2k11yfDDDSrvaZ'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="shows", param_type=OutputParameterType.OBJECT, is_array=True),  # An array of show objects, each with details about the show including available markets, copyrights, description, images, and more.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_Multiple_Shows.method, 
                                           Get_Multiple_Shows.url,
                                           Get_Multiple_Shows.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Multiple_Shows': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Artists_Top_Tracks(BaseFunction):
    """Get Spotify catalog information about an artist's top tracks by country."""
    name = "Get Artist's Top Tracks"
    url = "https://api.spotify.com/v1/artists/{id}/top-tracks"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the artist. Example: '0TnOYISbd1XYRBk9myaseg'.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # An ISO 3166-1 alpha-2 country code. If specified, only top tracks available in that market are returned. If a user access token is provided, the user's country takes priority. If neither is provided, content is considered unavailable. Example: 'ES'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="tracks", param_type=OutputParameterType.OBJECT, is_array=True),  # An array of track objects representing the artist's top tracks in the specified market.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_Artists_Top_Tracks.method, 
                                           Get_Artists_Top_Tracks.url,
                                           Get_Artists_Top_Tracks.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Artists_Top_Tracks': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Change_Playlist_Details(BaseFunction):
    """Update a playlist's name, public/private status, collaborative status, or description."""
    name = "Change Playlist Details"
    url = "https://api.spotify.com/v1/playlists/{playlist_id}"
    args_in_url = True
    method = "PUT"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="playlist_id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the playlist. Example: '3cEYpjA9oz9GiPac4AsH4n'.,
			Parameter(name="name", param_type=ParameterType.STRING, required=False),  # The new name for the playlist, e.g., 'My New Playlist Title'.,
			Parameter(name="public", param_type=ParameterType.BOOLEAN, required=False),  # The playlist's public/private status: true=public, false=private, null=not relevant.,
			Parameter(name="collaborative", param_type=ParameterType.BOOLEAN, required=False),  # If true, the playlist will become collaborative, allowing others to modify it. Note: only set to true on non-public playlists.,
			Parameter(name="description", param_type=ParameterType.STRING, required=False),  # The playlist description as displayed in Spotify clients and the Web API.
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Change_Playlist_Details.method, 
                                           Change_Playlist_Details.url,
                                           Change_Playlist_Details.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Change_Playlist_Details': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class follow_playlist(BaseFunction):
    """Add the current user as a follower of a playlist. Requires 'playlist-modify-public' or 'playlist-modify-private' scope."""
    name = "follow_playlist"
    url = "https://api.spotify.com/v1/playlists/{playlist_id}/followers"
    args_in_url = True
    method = "PUT"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="playlist_id", param_type=ParameterType.STRING, required=True),  # Spotify ID of the playlist to follow, e.g., '3cEYpjA9oz9GiPac4AsH4n'.,
			Parameter(name="public", param_type=ParameterType.BOOLEAN, required=False),  # If true, the playlist will be included in the user's public playlists; defaults to true. If false, the playlist remains private.
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(follow_playlist.method, 
                                           follow_playlist.url,
                                           follow_playlist.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'follow_playlist': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class get_an_artists_albums(BaseFunction):
    """Get Spotify catalog information about an artist's albums."""
    name = "get_an_artists_albums"
    url = "https://api.spotify.com/v1/artists/{id}/albums"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.STRING, required=True),  # Spotify Artist ID, e.g., '0TnOYISbd1XYRBk9myaseg'.,
			Parameter(name="include_groups", param_type=ParameterType.STRING, required=False),  # Comma-separated list of album types to filter, e.g., 'album,single,appears_on,compilation'.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # ISO 3166-1 alpha-2 country code to filter results by market, e.g., 'ES'.,
			Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Maximum number of items to return (1-50), default 20.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # Index of the first item to return, default 0.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to full API result.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # Number of items returned.,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=False),  # URL to next page of results or null.,
			OutputParameter(name="offset", param_type=OutputParameterType.INTEGER, is_array=False),  # Index of the first item returned.,
			OutputParameter(name="previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to previous page or null.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of albums available.,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # List of album objects, each with properties:,
			OutputParameter(name="album_type", param_type=OutputParameterType.STRING, is_array=False),  # Type of album. Allowed: 'album', 'single', 'compilation'.,
			OutputParameter(name="total_tracks", param_type=OutputParameterType.INTEGER, is_array=False),  # Number of tracks in the album.,
			OutputParameter(name="available_markets", param_type=OutputParameterType.STRING, is_array=True),  # Markets where the album is available, e.g., ['CA','BR','IT'].,
			OutputParameter(name="external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # Known external URLs for this album.,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the full album object.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # Spotify ID for the album.,
			OutputParameter(name="images", param_type=OutputParameterType.OBJECT, is_array=True),  # Album cover images with properties:,
			OutputParameter(name="url", param_type=OutputParameterType.STRING, is_array=False),  # Image URL.,
			OutputParameter(name="height", param_type=OutputParameterType.INTEGER, is_array=False),  # Image height in pixels, nullable.,
			OutputParameter(name="width", param_type=OutputParameterType.INTEGER, is_array=False),  # Image width in pixels, nullable.,
			OutputParameter(name="name", param_type=OutputParameterType.STRING, is_array=False),  # Name of the album.,
			OutputParameter(name="release_date", param_type=OutputParameterType.STRING, is_array=False),  # Release date of the album, e.g., '1981-12'.,
			OutputParameter(name="release_date_precision", param_type=OutputParameterType.STRING, is_array=False),  # Precision of release date. Allowed: 'year', 'month', 'day'.,
			OutputParameter(name="restrictions", param_type=OutputParameterType.OBJECT, is_array=False),  # Content restrictions, if any, with property 'reason' which can be 'market', 'product', or 'explicit'.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, must be 'album'.,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI for the album.,
			OutputParameter(name="artists", param_type=OutputParameterType.OBJECT, is_array=True),  # List of artist objects with properties:,
			OutputParameter(name="external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # External URLs for the artist.,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the artist object.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # Spotify ID for the artist.,
			OutputParameter(name="name", param_type=OutputParameterType.STRING, is_array=False),  # Artist name.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, 'artist'.,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI for the artist.,
			OutputParameter(name="album_group", param_type=OutputParameterType.STRING, is_array=False),  # Relationship of the artist to the album, e.g., 'album', 'single', 'compilation', 'appears_on'.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(get_an_artists_albums.method, 
                                           get_an_artists_albums.url,
                                           get_an_artists_albums.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'get_an_artists_albums': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class remove_albums_user(BaseFunction):
    """Remove one or more albums from the current user's 'Your Music' library. Requires 'user-library-modify' scope."""
    name = "remove_albums_user"
    url = "https://api.spotify.com/v1/me/albums"
    args_in_url = False
    method = "DELETE"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # Comma-separated list of Spotify album IDs to remove, e.g., '382ObEPsp2rxGrnsizN5TX,1A2GTWGtFfWp7KSQTwWOyo'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="snapshot_id", param_type=OutputParameterType.STRING, is_array=False),  # Snapshot ID of the user’s 'Your Music' library after removal, e.g., 'abc'.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(remove_albums_user.method, 
                                           remove_albums_user.url,
                                           remove_albums_user.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'remove_albums_user': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class migrate_from_implicit_auth_code(BaseFunction):
    """Guide on migrating from Implicit Grant Flow to Authorization Code with PKCE for Spotify Web API."""
    name = "migrate_from_implicit_auth_code"
    url = "https://developer.spotify.com/documentation/web-api/tutorials/migration-implicit-auth-code"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(migrate_from_implicit_auth_code.method, 
                                           migrate_from_implicit_auth_code.url,
                                           migrate_from_implicit_auth_code.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'migrate_from_implicit_auth_code': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Check_if_current_user_follows_Artists_or_Users(BaseFunction):
    """Checks if the current user follows one or more artists or Spotify users based on the specified IDs."""
    name = "Check if current user follows Artists or Users"
    url = "https://api.spotify.com/v1/me/following/contains"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="type", param_type=ParameterType.STRING, required=True),  # The ID type: either 'artist' or 'user'.,
			Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of the Spotify IDs to check. Maximum of 50 IDs. Example: '2CIMQHirSU0MQqyYHq0eOx,57dN52uHvrHOxijzpIgu3E'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="response", param_type=OutputParameterType.BOOLEAN, is_array=True),  # Array of booleans indicating whether the current user follows each ID in the 'ids' list. Example: [false, true].
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Check_if_current_user_follows_Artists_or_Users.method, 
                                           Check_if_current_user_follows_Artists_or_Users.url,
                                           Check_if_current_user_follows_Artists_or_Users.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Check_if_current_user_follows_Artists_or_Users': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Skip_to_previous_track_for_users_playback(BaseFunction):
    """Skips to the previous track in the user's playback. Only works for users with Spotify Premium."""
    name = "Skip to previous track for user's playback"
    url = "https://api.spotify.com/v1/me/player/previous"
    args_in_url = False
    method = "PUT"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="device_id", param_type=ParameterType.STRING, required=False),  # The ID of the device to control. If not provided, the current active device is used. Example: '0d1841b0976bae2a3a310dd74c0f3df354899bc8'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="response_code", param_type=OutputParameterType.INTEGER, is_array=False),  # HTTP status code indicating success (204) or error (401, 403, 429).
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Skip_to_previous_track_for_users_playback.method, 
                                           Skip_to_previous_track_for_users_playback.url,
                                           Skip_to_previous_track_for_users_playback.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Skip_to_previous_track_for_users_playback': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Transfer_playback_to_a_new_device(BaseFunction):
    """Transfers playback to the specified device(s). Only one device ID is supported at a time."""
    name = "Transfer playback to a new device"
    url = "https://api.spotify.com/v1/me/player"
    args_in_url = False
    method = "PUT"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="device_ids", param_type=ParameterType.STRING, required=True),  # A JSON array of device IDs to transfer playback to. Although an array is accepted, only a single device ID is supported currently. Example: '[
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="response_code", param_type=OutputParameterType.INTEGER, is_array=False),  # HTTP status code indicating success (204) or error (401, 403, 429).
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Transfer_playback_to_a_new_device.method, 
                                           Transfer_playback_to_a_new_device.url,
                                           Transfer_playback_to_a_new_device.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Transfer_playback_to_a_new_device': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_a_users_available_devices(BaseFunction):
    """Retrieves information about the user's available Spotify Connect devices."""
    name = "Get a user's available devices"
    url = "https://api.spotify.com/v1/me/player/devices"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="devices", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of DeviceObject representing the user's available Spotify Connect devices. Each device object includes the following fields:,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # The device ID, unique and persistent to some extent. Can be used to identify the device in subsequent requests.,
			OutputParameter(name="is_active", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Indicates whether this device is the currently active device.,
			OutputParameter(name="is_private_session", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Indicates whether this device is in a private session.,
			OutputParameter(name="is_restricted", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Indicates whether controlling this device is restricted; if true, no Web API commands will be accepted by this device.,
			OutputParameter(name="name", param_type=OutputParameterType.STRING, is_array=False),  # A human-readable name for the device, e.g., 'Kitchen speaker'.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # Device type, such as 'computer', 'smartphone', or 'speaker'.,
			OutputParameter(name="volume_percent", param_type=OutputParameterType.INTEGER, is_array=False),  # The current volume of the device in percentage (0-100). Can be null if not available.,
			OutputParameter(name="supports_volume", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Indicates whether this device supports volume control.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_a_users_available_devices.method, 
                                           Get_a_users_available_devices.url,
                                           Get_a_users_available_devices.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_a_users_available_devices': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Artists_Related_Artists(BaseFunction):
    """Fetches artists related to the specified artist ID, based on listening history."""
    name = "Get Artist's Related Artists"
    url = "https://api.spotify.com/v1/artists/{id}/related-artists"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the artist. This is a required parameter and should be provided in the URL path. Example: '0TnOYISbd1XYRBk9myaseg'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="artists", param_type=OutputParameterType.OBJECT, is_array=True),  # A list of artist objects related to the specified artist.,
			OutputParameter(name="external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # Known external URLs for the artist, including 'spotify' URL.,
			OutputParameter(name="followers", param_type=OutputParameterType.OBJECT, is_array=False),  # Information about the artist's followers, including total count.,
			OutputParameter(name="genres", param_type=OutputParameterType.STRING, is_array=True),  # List of genres associated with the artist.,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # A link to the Web API endpoint providing full details of the artist.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # The Spotify ID for the artist.,
			OutputParameter(name="images", param_type=OutputParameterType.OBJECT, is_array=True),  # Images of the artist in various sizes.,
			OutputParameter(name="name", param_type=OutputParameterType.STRING, is_array=False),  # Name of the artist.,
			OutputParameter(name="popularity", param_type=OutputParameterType.INTEGER, is_array=False),  # Artist's popularity score, from 0 to 100.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, always 'artist'.,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI for the artist.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_Artists_Related_Artists.method, 
                                           Get_Artists_Related_Artists.url,
                                           Get_Artists_Related_Artists.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Artists_Related_Artists': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Several_Tracks_Audio_Features(BaseFunction):
    """Retrieves audio features for multiple tracks based on their Spotify IDs."""
    name = "Get Several Tracks' Audio Features"
    url = "https://api.spotify.com/v1/audio-features"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # Comma-separated list of Spotify track IDs. Up to 100 IDs can be provided. Example: '7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="audio_features", param_type=OutputParameterType.OBJECT, is_array=True),  # An array of AudioFeaturesObject, each containing audio analysis for a track.,
			OutputParameter(name="acousticness", param_type=OutputParameterType.FLOAT, is_array=False),  # Confidence measure from 0.0 to 1.0 of whether the track is acoustic.,
			OutputParameter(name="analysis_url", param_type=OutputParameterType.STRING, is_array=False),  # URL to access the full audio analysis of the track.,
			OutputParameter(name="danceability", param_type=OutputParameterType.FLOAT, is_array=False),  # How suitable the track is for dancing, 0.0 to 1.0.,
			OutputParameter(name="duration_ms", param_type=OutputParameterType.INTEGER, is_array=False),  # Length of the track in milliseconds.,
			OutputParameter(name="energy", param_type=OutputParameterType.FLOAT, is_array=False),  # Perceptual measure of intensity, 0.0 to 1.0.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # Spotify ID of the track.,
			OutputParameter(name="instrumentalness", param_type=OutputParameterType.FLOAT, is_array=False),  # Likelihood the track contains no vocals, 0.0 to 1.0.,
			OutputParameter(name="key", param_type=OutputParameterType.INTEGER, is_array=False),  # Key the track is in, with -1 indicating no detection; 0-11 representing pitches.,
			OutputParameter(name="liveness", param_type=OutputParameterType.FLOAT, is_array=False),  # Presence of an audience, 0.0 to 1.0.,
			OutputParameter(name="loudness", param_type=OutputParameterType.FLOAT, is_array=False),  # Overall loudness in decibels.,
			OutputParameter(name="mode", param_type=OutputParameterType.INTEGER, is_array=False),  # Mode (major or minor), 1 or 0.,
			OutputParameter(name="speechiness", param_type=OutputParameterType.FLOAT, is_array=False),  # Presence of spoken words, 0.0 to 1.0.,
			OutputParameter(name="tempo", param_type=OutputParameterType.FLOAT, is_array=False),  # Estimated tempo in beats per minute.,
			OutputParameter(name="time_signature", param_type=OutputParameterType.INTEGER, is_array=False),  # Estimated time signature, 3 to 7.,
			OutputParameter(name="track_href", param_type=OutputParameterType.STRING, is_array=False),  # URL to the full details of the track.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, always 'audio_features'.,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI for the track.,
			OutputParameter(name="valence", param_type=OutputParameterType.FLOAT, is_array=False),  # Musical positiveness, 0.0 to 1.0.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_Several_Tracks_Audio_Features.method, 
                                           Get_Several_Tracks_Audio_Features.url,
                                           Get_Several_Tracks_Audio_Features.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Several_Tracks_Audio_Features': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Create_Playlist(BaseFunction):
    """Creates a new playlist for a user with specified details."""
    name = "Create Playlist"
    url = "https://api.spotify.com/v1/users/{user_id}/playlists"
    args_in_url = True
    method = "PUT"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="user_id", param_type=ParameterType.STRING, required=True),  # The Spotify user ID of the user for whom the playlist is being created. Example: 'smedjan'.,
			Parameter(name="name", param_type=ParameterType.STRING, required=True),  # The name for the new playlist, e.g., 'Your Coolest Playlist'.,
			Parameter(name="public", param_type=ParameterType.BOOLEAN, required=False),  # Whether the playlist is public. Defaults to true.,
			Parameter(name="collaborative", param_type=ParameterType.BOOLEAN, required=False),  # Whether the playlist is collaborative. Defaults to false.,
			Parameter(name="description", param_type=ParameterType.STRING, required=False),  # Description of the playlist, visible in Spotify clients.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="collaborative", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Indicates if the playlist owner allows others to modify the playlist.,
			OutputParameter(name="description", param_type=OutputParameterType.STRING, is_array=False),  # The playlist description, might be null if not set.,
			OutputParameter(name="external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # External URLs for the playlist, including Spotify URL.,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the Web API endpoint providing full details of the playlist.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # The Spotify ID for the playlist.,
			OutputParameter(name="images", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of images associated with the playlist, ordered by size.,
			OutputParameter(name="name", param_type=OutputParameterType.STRING, is_array=False),  # Name of the playlist.,
			OutputParameter(name="owner", param_type=OutputParameterType.OBJECT, is_array=False),  # The user who owns the playlist, with details including external URLs, href, id, images, name, and uri.,
			OutputParameter(name="public", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Whether the playlist is public.,
			OutputParameter(name="snapshot_id", param_type=OutputParameterType.STRING, is_array=False),  # The version identifier of the playlist.,
			OutputParameter(name="tracks", param_type=OutputParameterType.OBJECT, is_array=False),  # Object containing reference to tracks, with fields like href, limit, next, offset, previous, total, and items.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, always 'playlist'.,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI for the playlist.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Create_Playlist.method, 
                                           Create_Playlist.url,
                                           Create_Playlist.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Create_Playlist': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Save_Albums_for_Current_User(BaseFunction):
    """Endpoint to save one or more albums to the current user's 'Your Music' library."""
    name = "Save Albums for Current User"
    url = "https://api.spotify.com/v1/me/albums"
    args_in_url = False
    method = "PUT"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of Spotify album IDs. Maximum: 20 IDs. Example: '382ObEPsp2rxGrnsizN5TX,1A2GTWGtFfWp7KSQTwWOyo,2noRn2Aes5aoNVsU6iWThc'.,
			Parameter(name="ids_array", param_type=ParameterType.STRING, required=False),  # A JSON array of Spotify album IDs, e.g. ['4iV5W9uYEdYUVa79Axb7Rh', '1301WleyT98MSxVHPZCA6M']. A maximum of 50 items can be specified; this parameter is ignored if 'ids' in query string.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="response", param_type=OutputParameterType.STRING, is_array=False),  # Empty response body indicates success. Possible response status codes: 200, 401, 403, 429.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Save_Albums_for_Current_User.method, 
                                           Save_Albums_for_Current_User.url,
                                           Save_Albums_for_Current_User.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Save_Albums_for_Current_User': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_an_Artist(BaseFunction):
    """Retrieve Spotify catalog information for a single artist by their unique Spotify ID."""
    name = "Get an Artist"
    url = "https://api.spotify.com/v1/artists/{id}"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the artist. Example: '0TnOYISbd1XYRBk9myaseg'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # Known external URLs for this artist, e.g., Spotify URL.,
			OutputParameter(name="followers", param_type=OutputParameterType.OBJECT, is_array=False),  # Information about followers: 'href' (nullable string) always null, 'total' (integer) number of followers.,
			OutputParameter(name="genres", param_type=OutputParameterType.STRING, is_array=True),  # List of genres associated with the artist. Example: ['Prog rock','Grunge'].,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the Web API endpoint providing full artist details.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # The Spotify ID of the artist.,
			OutputParameter(name="images", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of images of various sizes for the artist.,
			OutputParameter(name="name", param_type=OutputParameterType.STRING, is_array=False),  # Name of the artist.,
			OutputParameter(name="popularity", param_type=OutputParameterType.INTEGER, is_array=False),  # Artist's popularity score between 0 and 100.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, always 'artist'.,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI for the artist.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_an_Artist.method, 
                                           Get_an_Artist.url,
                                           Get_an_Artist.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_an_Artist': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_a_Playlist(BaseFunction):
    """Retrieve the details of a specific playlist by its Spotify ID."""
    name = "Get a Playlist"
    url = "https://api.spotify.com/v1/playlists/{playlist_id}"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="playlist_id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the playlist.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="collaborative", param_type=OutputParameterType.BOOLEAN, is_array=False),  # If the playlist is collaborative.,
			OutputParameter(name="description", param_type=OutputParameterType.STRING, is_array=False),  # The playlist description.,
			OutputParameter(name="external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # External URLs object, including Spotify link.,
			OutputParameter(name="followers", param_type=OutputParameterType.OBJECT, is_array=False),  # Followers information.,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the Web API endpoint providing full playlist details.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # The Spotify ID of the playlist.,
			OutputParameter(name="images", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of images representing the playlist.,
			OutputParameter(name="name", param_type=OutputParameterType.STRING, is_array=False),  # Name of the playlist.,
			OutputParameter(name="owner", param_type=OutputParameterType.OBJECT, is_array=False),  # Object containing owner information.,
			OutputParameter(name="public", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Whether the playlist is public.,
			OutputParameter(name="snapshot_id", param_type=OutputParameterType.STRING, is_array=False),  # Snapshot ID for version control.,
			OutputParameter(name="tracks", param_type=OutputParameterType.OBJECT, is_array=False),  # Object containing playlist tracks.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, always 'playlist'.,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI for the playlist.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_a_Playlist.method, 
                                           Get_a_Playlist.url,
                                           Get_a_Playlist.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_a_Playlist': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Set_Repeat_Mode_on_Users_Playback(BaseFunction):
    """Set the repeat mode for the user's playback. Requires 'user-modify-playback-state' scope. Possible 'state' values: 'track', 'context', 'off'."""
    name = "Set Repeat Mode on User's Playback"
    url = "https://api.spotify.com/v1/me/player/repeat"
    args_in_url = False
    method = "PUT"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="state", param_type=ParameterType.STRING, required=True),  # Required. The string indicating the repeat mode. Allowed values: 'track' to repeat the current track, 'context' to repeat the current context (playlist or album), or 'off' to turn off repeat.,
			Parameter(name="device_id", param_type=ParameterType.STRING, required=False),  # Optional. The ID of the device this command is targeting. If not supplied, the currently active device is targeted.
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Set_Repeat_Mode_on_Users_Playback.method, 
                                           Set_Repeat_Mode_on_Users_Playback.url,
                                           Set_Repeat_Mode_on_Users_Playback.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Set_Repeat_Mode_on_Users_Playback': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_the_Users_Playback_Queue(BaseFunction):
    """Retrieve the current queue of tracks and episodes for the user. Requires 'user-read-playback-state' scope. The response includes 'currently_playing' item and 'queue' array with upcoming items."""
    name = "Get the User's Playback Queue"
    url = "https://api.spotify.com/v1/me/player/queue"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_the_Users_Playback_Queue.method, 
                                           Get_the_Users_Playback_Queue.url,
                                           Get_the_Users_Playback_Queue.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_the_Users_Playback_Queue': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Available_Markets(BaseFunction):
    """Retrieve the list of markets (countries) where Spotify is available. Authentication with OAuth 2.0 required."""
    name = "Get Available Markets"
    url = "https://api.spotify.com/v1/markets"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="markets", param_type=OutputParameterType.STRING, is_array=True),  # An array of country codes (ISO 3166-1 alpha-2) representing the markets where Spotify is available.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_Available_Markets.method, 
                                           Get_Available_Markets.url,
                                           Get_Available_Markets.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Available_Markets': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Track_Relinking__Get_a_Track_with_market(BaseFunction):
    """Retrieves information about a specific track, attempting relinking based on the market if necessary."""
    name = "Track Relinking - Get a Track (with market)"
    url = "https://api.spotify.com/v1/tracks/{id}"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the track.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # A country code (ISO 3166-1 alpha-2). If specified, the API attempts to return the track in the specified market, relinking if necessary.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="available_markets", param_type=OutputParameterType.STRING, is_array=True),  # List of markets where the track is available. (Note: this property is replaced by 'is_playable' when 'market' is used).,
			OutputParameter(name="disc_number", param_type=OutputParameterType.INTEGER, is_array=False),  # The disc number (usually 1 unless the album has multiple discs).,
			OutputParameter(name="duration_ms", param_type=OutputParameterType.INTEGER, is_array=False),  # The length of the track in milliseconds.,
			OutputParameter(name="explicit", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Whether the track has explicit lyrics.,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # A link to the Web API endpoint providing full details of the track.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # The Spotify ID for the track.,
			OutputParameter(name="is_playable", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Indicates if the track can be played in the market.,
			OutputParameter(name="linked_from", param_type=OutputParameterType.OBJECT, is_array=False),  # Contains information about the original track if relinked, including 'external_urls', 'href', 'id', 'type', and 'uri'.,
			OutputParameter(name="name", param_type=OutputParameterType.STRING, is_array=False),  # The name of the track.,
			OutputParameter(name="preview_url", param_type=OutputParameterType.STRING, is_array=False),  # A URL to a 30 second preview of the track.,
			OutputParameter(name="restrictions", param_type=OutputParameterType.OBJECT, is_array=False),  # Restrictions if the track is not available, including 'reason' (e.g., 'market').},{
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Track_Relinking__Get_a_Track_with_market.method, 
                                           Track_Relinking__Get_a_Track_with_market.url,
                                           Track_Relinking__Get_a_Track_with_market.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Track_Relinking__Get_a_Track_with_market': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_a_Category(BaseFunction):
    """Retrieves a single Spotify category used for tagging items."""
    name = "Get a Category"
    url = "https://api.spotify.com/v1/browse/categories/{category_id}"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="category_id", param_type=ParameterType.STRING, required=True),  # The Spotify category ID, e.g., 'dinner'.,
			Parameter(name="locale", param_type=ParameterType.STRING, required=False),  # Language and country code (ISO 639-1 and ISO 3166-1 alpha-2), e.g., 'es_MX'. If not provided, defaults to American English.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # A link to the Web API endpoint returning full details of the category.,
			OutputParameter(name="icons", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of image objects representing the category icon in various sizes.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # The Spotify category ID.,
			OutputParameter(name="name", param_type=OutputParameterType.STRING, is_array=False),  # The name of the category.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_a_Category.method, 
                                           Get_a_Category.url,
                                           Get_a_Category.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_a_Category': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Show_Episodes(BaseFunction):
    """Retrieves a list of episodes for a specific show, with optional pagination and market filtering."""
    name = "Get Show Episodes"
    url = "https://api.spotify.com/v1/shows/{id}/episodes"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the show.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # A country code (ISO 3166-1 alpha-2). If provided, only episodes available in this market are returned. If not, the user's country is used.,
			Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # The maximum number of episodes to return. Default: 20. Min: 1. Max: 50.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # The index of the first episode to return. Default: 0.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # A link to the full result of the request.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # Maximum number of items in the response.,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=False),  # URL to the next page of episodes, or null if none.,
			OutputParameter(name="offset", param_type=OutputParameterType.INTEGER, is_array=False),  # The offset of the items returned.,
			OutputParameter(name="previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to the previous page of episodes, or null if none.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of episodes available.,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of episode objects, including details like 'audio_preview_url', 'description', 'html_description', 'duration_ms', 'explicit', 'external_urls', 'href', 'id', 'images', 'is_externally_hosted', 'is_playable', 'language(s)', 'name', 'release_date', 'release_date_precision', 'resume_point', 'type', 'uri', and 'restrictions'.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_Show_Episodes.method, 
                                           Get_Show_Episodes.url,
                                           Get_Show_Episodes.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Show_Episodes': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_the_users_currently_playing_track(BaseFunction):
    """Retrieves information about the user's currently playing track or episode."""
    name = "Get the user's currently playing track"
    url = "https://api.spotify.com/v1/me/player/currently-playing"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="market", param_type=ParameterType.STRING, required=False),  # An ISO 3166-1 alpha-2 country code to restrict the content to a specific market. If omitted, the user's country setting will take priority. Example: 'ES'.,
			Parameter(name="additional_types", param_type=ParameterType.STRING, required=False),  # A comma-separated list of item types supported besides 'track'. Valid types are: 'track' and 'episode'. This parameter affects the returned item types.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="device", param_type=OutputParameterType.OBJECT, is_array=False),  # Information about the device currently active for playback.,
			OutputParameter(name="repeat_state", param_type=OutputParameterType.STRING, is_array=False),  # The current repeat mode. Possible values: 'off', 'track', 'context'.,
			OutputParameter(name="shuffle_state", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Whether shuffle mode is enabled.,
			OutputParameter(name="context", param_type=OutputParameterType.OBJECT, is_array=False),  # The context object for playback, such as playlist or album.,
			OutputParameter(name="timestamp", param_type=OutputParameterType.INTEGER, is_array=False),  # Unix timestamp indicating when the playback state was last changed.,
			OutputParameter(name="progress_ms", param_type=OutputParameterType.INTEGER, is_array=False),  # Progress into the current track or episode in milliseconds. Can be null.,
			OutputParameter(name="is_playing", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Indicates if something is currently playing.,
			OutputParameter(name="item", param_type=OutputParameterType.OBJECT, is_array=False),  # The currently playing track or episode, or null if nothing is playing.,
			OutputParameter(name="currently_playing_type", param_type=OutputParameterType.STRING, is_array=False),  # Object type of the currently playing item. Possible values: 'track', 'episode', 'ad', 'unknown'.,
			OutputParameter(name="actions", param_type=OutputParameterType.OBJECT, is_array=False),  # Available playback actions within the current context.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_the_users_currently_playing_track.method, 
                                           Get_the_users_currently_playing_track.url,
                                           Get_the_users_currently_playing_track.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_the_users_currently_playing_track': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Save_audiobooks_for_the_current_user(BaseFunction):
    """Saves one or more audiobooks to the current Spotify user's library."""
    name = "Save audiobooks for the current user"
    url = "https://api.spotify.com/v1/me/audiobooks"
    args_in_url = False
    method = "PUT"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of Spotify IDs for audiobooks to save. Maximum: 50 IDs. Example: '18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ'
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="", param_type=OutputParameterType.STRING, is_array=False),  # Empty response indicating success.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Save_audiobooks_for_the_current_user.method, 
                                           Save_audiobooks_for_the_current_user.url,
                                           Save_audiobooks_for_the_current_user.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Save_audiobooks_for_the_current_user': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Check_if_user_has_saved_specific_tracks(BaseFunction):
    """Checks if one or more tracks are already saved in the current user's 'Your Music' library."""
    name = "Check if user has saved specific tracks"
    url = "https://api.spotify.com/v1/me/tracks/contains"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of Spotify IDs for tracks to check. Maximum: 50 IDs. Example: '7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ'
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="", param_type=OutputParameterType.BOOLEAN, is_array=True),  # An array of booleans indicating whether each track is saved (true) or not (false).
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Check_if_user_has_saved_specific_tracks.method, 
                                           Check_if_user_has_saved_specific_tracks.url,
                                           Check_if_user_has_saved_specific_tracks.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Check_if_user_has_saved_specific_tracks': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Save_Tracks_for_Current_User(BaseFunction):
    """Endpoint to save one or more tracks to the current user's 'Your Music' library. Supports either a comma-separated string of IDs or an array of IDs in the request body."""
    name = "Save Tracks for Current User"
    url = "https://api.spotify.com/v1/me/tracks"
    args_in_url = False
    method = "PUT"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of the Spotify IDs of the tracks to save. Maximum: 50 IDs. Example: '7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B'.,
			Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # An array of track Spotify IDs. Maximum: 50 items. Example: ['4iV5W9uYEdYUVa79Axb7Rh','1301WleyT98MSxVHPZCA6M']. If 'ids' parameter is present in the query string, any IDs listed in the body will be ignored.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="status_code", param_type=OutputParameterType.STRING, is_array=False),  # HTTP status code indicating the result. Examples: '200' for success, '401' for Unauthorized, '403' for Forbidden, '429' for Too Many Requests.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Save_Tracks_for_Current_User.method, 
                                           Save_Tracks_for_Current_User.url,
                                           Save_Tracks_for_Current_User.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Save_Tracks_for_Current_User': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Skip_to_Next_Track(BaseFunction):
    """API to skip to the next track in the user's queue. Works only for users with Spotify Premium."""
    name = "Skip to Next Track"
    url = "https://api.spotify.com/v1/me/player/next"
    args_in_url = False
    method = "PUT"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="status_code", param_type=OutputParameterType.STRING, is_array=False),  # HTTP status code indicating the result. Examples: '204' No Content on success, '401' Unauthorized, '403' Forbidden, '429' Too Many Requests.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Skip_to_Next_Track.method, 
                                           Skip_to_Next_Track.url,
                                           Skip_to_Next_Track.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Skip_to_Next_Track': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_an_Audiobook(BaseFunction):
    """API endpoint to retrieve detailed information for a specific audiobook by its Spotify ID, possibly filtered by market."""
    name = "Get an Audiobook"
    url = "https://api.spotify.com/v1/audiobooks/{id}"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.STRING, required=True),  # The Spotify ID for the audiobook. Example: '7iHfbu1YPACw6oZPAFJtqe'.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # An ISO 3166-1 alpha-2 country code. If specified, only content available in that market will be returned. If the user has a valid access token, the country associated with the user account takes priority. Example: 'ES'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="authors", param_type=OutputParameterType.OBJECT, is_array=True),  # List of authors for the audiobook.,
			OutputParameter(name="available_markets", param_type=OutputParameterType.STRING, is_array=True),  # List of country codes where the audiobook can be played.,
			OutputParameter(name="copyrights", param_type=OutputParameterType.OBJECT, is_array=True),  # Copyright statements for the audiobook.,
			OutputParameter(name="description", param_type=OutputParameterType.STRING, is_array=False),  # Description of the audiobook with HTML tags stripped.,
			OutputParameter(name="html_description", param_type=OutputParameterType.STRING, is_array=False),  # Description of the audiobook which may contain HTML tags.,
			OutputParameter(name="edition", param_type=OutputParameterType.STRING, is_array=False),  # Edition of the audiobook, e.g., 'Unabridged'.,
			OutputParameter(name="explicit", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Indicates if the audiobook has explicit content.,
			OutputParameter(name="external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # External URLs related to the audiobook.,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # A link to the Web API endpoint providing full details of the audiobook.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # Spotify ID of the audiobook.,
			OutputParameter(name="images", param_type=OutputParameterType.OBJECT, is_array=True),  # Images of the audiobook's cover art.,
			OutputParameter(name="languages", param_type=OutputParameterType.STRING, is_array=True),  # Languages used in the audiobook.,
			OutputParameter(name="media_type", param_type=OutputParameterType.STRING, is_array=False),  # Media type of the audiobook.,
			OutputParameter(name="name", param_type=OutputParameterType.STRING, is_array=False),  # Name of the audiobook.,
			OutputParameter(name="narrators", param_type=OutputParameterType.OBJECT, is_array=True),  # List of narrators for the audiobook.,
			OutputParameter(name="publisher", param_type=OutputParameterType.STRING, is_array=False),  # Publisher of the audiobook.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, e.g., 'audiobook'.,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI of the audiobook.,
			OutputParameter(name="total_chapters", param_type=OutputParameterType.INTEGER, is_array=False),  # Number of chapters in the audiobook.,
			OutputParameter(name="chapters", param_type=OutputParameterType.OBJECT, is_array=False),  # Chapter information including pagination and items.,
			OutputParameter(name="is_playable", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Indicates if the chapter is playable in the current market.,
			OutputParameter(name="restrictions", param_type=OutputParameterType.OBJECT, is_array=False),  # Content restrictions applied to the audiobook.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_an_Audiobook.method, 
                                           Get_an_Audiobook.url,
                                           Get_an_Audiobook.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_an_Audiobook': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_a_single_tracks_audio_analysis(BaseFunction):
    """JSON schema for the response of retrieving a track's audio analysis, including metadata, track info, and detailed musical features."""
    name = "Get a single track's audio analysis"
    url = "https://api.spotify.com/v1/audio-analysis/{id}"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.STRING, required=True),  # The Spotify ID for the track. Example: `11dFghVXANMlKmJXsNCbNl`.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="meta", param_type=OutputParameterType.OBJECT, is_array=False),  # Metadata about the analysis, including analyzer version, platform, status codes, timestamp, analysis time, and input process.,
			OutputParameter(name="meta.analyzer_version", param_type=OutputParameterType.STRING, is_array=False),  # The version of the analyzer used to analyze this track. Example: "4.0.0".,
			OutputParameter(name="meta.platform", param_type=OutputParameterType.STRING, is_array=False),  # The platform used to read the track's audio data. Example: "Linux".,
			OutputParameter(name="meta.detailed_status", param_type=OutputParameterType.STRING, is_array=False),  # A detailed status code. Example: "OK".,
			OutputParameter(name="meta.status_code", param_type=OutputParameterType.INTEGER, is_array=False),  # Return code: 0 if successful.,
			OutputParameter(name="meta.timestamp", param_type=OutputParameterType.INTEGER, is_array=False),  # Unix timestamp when the track was analyzed. Example: 1495193577.,
			OutputParameter(name="meta.analysis_time", param_type=OutputParameterType.FLOAT, is_array=False),  # Time taken to analyze the track in seconds. Example: 6.93906.,
			OutputParameter(name="meta.input_process", param_type=OutputParameterType.STRING, is_array=False),  # The method used to read the track's audio data. Example: "libvorbisfile L+R 44100->22050".,
			OutputParameter(name="track", param_type=OutputParameterType.OBJECT, is_array=False),  # Track information including number of samples, duration, sample MD5, offset, window size, sample rate, channels, fade timings, loudness, tempo, key, mode, and codestrings.,
			OutputParameter(name="track.num_samples", param_type=OutputParameterType.INTEGER, is_array=False),  # Number of samples analyzed from this track. Example: 4585515.,
			OutputParameter(name="track.duration", param_type=OutputParameterType.FLOAT, is_array=False),  # Length of the track in seconds. Example: 207.95985.,
			OutputParameter(name="track.sample_md5", param_type=OutputParameterType.STRING, is_array=False),  # Always contains an empty string.,
			OutputParameter(name="track.offset_seconds", param_type=OutputParameterType.INTEGER, is_array=False),  # Offset to the start of the analysis region. Usually 0.,
			OutputParameter(name="track.window_seconds", param_type=OutputParameterType.INTEGER, is_array=False),  # Length of the analyzed region of the track, usually 0.,
			OutputParameter(name="track.analysis_sample_rate", param_type=OutputParameterType.INTEGER, is_array=False),  # Sample rate used for decoding and analysis. Example: 22050.,
			OutputParameter(name="track.analysis_channels", param_type=OutputParameterType.INTEGER, is_array=False),  # Number of channels used for analysis. Example: 1.,
			OutputParameter(name="track.end_of_fade_in", param_type=OutputParameterType.FLOAT, is_array=False),  # Seconds at which fade-in ends. Example: 0.,
			OutputParameter(name="track.start_of_fade_out", param_type=OutputParameterType.FLOAT, is_array=False),  # Seconds at which fade-out starts. Example: 201.13705.,
			OutputParameter(name="track.loudness", param_type=OutputParameterType.FLOAT, is_array=False),  # Overall loudness in decibels, range typically -60 to 0.,
			OutputParameter(name="track.tempo", param_type=OutputParameterType.FLOAT, is_array=False),  # Estimated tempo in BPM. Example: 118.211.,
			OutputParameter(name="track.tempo_confidence", param_type=OutputParameterType.FLOAT, is_array=False),  # Confidence in tempo estimation, between 0.0 and 1.0. Example: 0.73.,
			OutputParameter(name="track.time_signature", param_type=OutputParameterType.INTEGER, is_array=False),  # Estimated time signature, between 3 and 7. Example: 4.,
			OutputParameter(name="track.time_signature_confidence", param_type=OutputParameterType.FLOAT, is_array=False),  # Confidence in time signature, between 0.0 and 1.0. Example: 0.994.,
			OutputParameter(name="track.key", param_type=OutputParameterType.INTEGER, is_array=False),  # The key of the track, -1 if not detected. Values map to pitch classes. Example: 9.,
			OutputParameter(name="track.key_confidence", param_type=OutputParameterType.FLOAT, is_array=False),  # Confidence in key detection, between 0.0 and 1.0. Example: 0.408.,
			OutputParameter(name="track.mode", param_type=OutputParameterType.INTEGER, is_array=False),  # Mode: 0 (minor) or 1 (major). Example: 0.,
			OutputParameter(name="track.mode_confidence", param_type=OutputParameterType.FLOAT, is_array=False),  # Confidence in mode detection, 0.0 to 1.0. Example: 0.485.,
			OutputParameter(name="track.codestring", param_type=OutputParameterType.STRING, is_array=False),  # Echo Nest Musical Fingerprint codestring.,
			OutputParameter(name="track.code_version", param_type=OutputParameterType.FLOAT, is_array=False),  # Version number of the codestring format. Example: 3.15.,
			OutputParameter(name="track.echoprintstring", param_type=OutputParameterType.STRING, is_array=False),  # EchoPrint codestring.,
			OutputParameter(name="track.echoprint_version", param_type=OutputParameterType.FLOAT, is_array=False),  # Version of the EchoPrint format, e.g., 4.15.,
			OutputParameter(name="track.synchstring", param_type=OutputParameterType.STRING, is_array=False),  # Synchstring for the track.,
			OutputParameter(name="track.synch_version", param_type=OutputParameterType.INTEGER, is_array=False),  # Version of the Synchstring, usually 1.,
			OutputParameter(name="track.rhythmstring", param_type=OutputParameterType.STRING, is_array=False),  # Rhythmstring for the track.,
			OutputParameter(name="track.rhythm_version", param_type=OutputParameterType.INTEGER, is_array=False),  # Version number for Rhythmstring, usually 1.,
			OutputParameter(name="bars", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of bar objects, each with start, duration, and confidence.,
			OutputParameter(name="bars.start", param_type=OutputParameterType.FLOAT, is_array=False),  # Start time in seconds. Example: 0.49567.,
			OutputParameter(name="bars.duration", param_type=OutputParameterType.FLOAT, is_array=False),  # Duration in seconds. Example: 2.18749.,
			OutputParameter(name="bars.confidence", param_type=OutputParameterType.FLOAT, is_array=False),  # Confidence level, 0.0 to 1.0. Example: 0.925.,
			OutputParameter(name="beats", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of beat objects, each with start, duration, and confidence.,
			OutputParameter(name="beats.start", param_type=OutputParameterType.FLOAT, is_array=False),  # Start time in seconds. Example: 0.49567.,
			OutputParameter(name="beats.duration", param_type=OutputParameterType.FLOAT, is_array=False),  # Duration in seconds. Example: 2.18749.,
			OutputParameter(name="beats.confidence", param_type=OutputParameterType.FLOAT, is_array=False),  # Confidence level, 0.0 to 1.0. Example: 0.925.,
			OutputParameter(name="sections", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of section objects, each with start, duration, confidence, loudness, tempo, key, mode, and time signature.,
			OutputParameter(name="sections.start", param_type=OutputParameterType.FLOAT, is_array=False),  # Section start time in seconds.,
			OutputParameter(name="sections.duration", param_type=OutputParameterType.FLOAT, is_array=False),  # Duration of the section in seconds.,
			OutputParameter(name="sections.confidence", param_type=OutputParameterType.FLOAT, is_array=False),  # Confidence level, 0.0 to 1.0.,
			OutputParameter(name="sections.loudness", param_type=OutputParameterType.FLOAT, is_array=False),  # Loudness in decibels.,
			OutputParameter(name="sections.tempo", param_type=OutputParameterType.FLOAT, is_array=False),  # Tempo in BPM.,
			OutputParameter(name="sections.tempo_confidence", param_type=OutputParameterType.FLOAT, is_array=False),  # Confidence in tempo estimation.,
			OutputParameter(name="sections.key", param_type=OutputParameterType.INTEGER, is_array=False),  # Key of the section, -1 if undetected.,
			OutputParameter(name="sections.key_confidence", param_type=OutputParameterType.FLOAT, is_array=False),  # Confidence in key detection.,
			OutputParameter(name="sections.mode", param_type=OutputParameterType.INTEGER, is_array=False),  # Mode: 0 (minor), 1 (major), or -1 if no result.,
			OutputParameter(name="sections.mode_confidence", param_type=OutputParameterType.FLOAT, is_array=False),  # Confidence in mode detection.,
			OutputParameter(name="sections.time_signature", param_type=OutputParameterType.INTEGER, is_array=False),  # Time signature. Range 3-7.,
			OutputParameter(name="sections.time_signature_confidence", param_type=OutputParameterType.FLOAT, is_array=False),  # Confidence in time signature detection.,
			OutputParameter(name="segments", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of segment objects with detailed audio feature data.,
			OutputParameter(name="segments.start", param_type=OutputParameterType.FLOAT, is_array=False),  # Segment start time in seconds.,
			OutputParameter(name="segments.duration", param_type=OutputParameterType.FLOAT, is_array=False),  # Segment duration in seconds.,
			OutputParameter(name="segments.confidence", param_type=OutputParameterType.FLOAT, is_array=False),  # Confidence in segmentation.,
			OutputParameter(name="segments.loudness_start", param_type=OutputParameterType.FLOAT, is_array=False),  # Loudness at segment start in decibels.,
			OutputParameter(name="segments.loudness_max", param_type=OutputParameterType.FLOAT, is_array=False),  # Maximum loudness in decibels.,
			OutputParameter(name="segments.loudness_max_time", param_type=OutputParameterType.FLOAT, is_array=False),  # Time to reach maximum loudness within the segment.,
			OutputParameter(name="segments.loudness_end", param_type=OutputParameterType.FLOAT, is_array=False),  # Loudness at segment end in decibels.,
			OutputParameter(name="segments.pitches", param_type=OutputParameterType.FLOAT, is_array=True),  # Array of 12 pitch content values, each between 0 and 1.,
			OutputParameter(name="segments.timbre", param_type=OutputParameterType.FLOAT, is_array=True),  # Array of 12 timbre coefficients.,
			OutputParameter(name="tatums", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of tatum objects with start, duration, and confidence.,
			OutputParameter(name="tatums.start", param_type=OutputParameterType.FLOAT, is_array=False),  # Start time in seconds.,
			OutputParameter(name="tatums.duration", param_type=OutputParameterType.FLOAT, is_array=False),  # Duration in seconds.,
			OutputParameter(name="tatums.confidence", param_type=OutputParameterType.FLOAT, is_array=False),  # Confidence level, 0.0 to 1.0.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_a_single_tracks_audio_analysis.method, 
                                           Get_a_single_tracks_audio_analysis.url,
                                           Get_a_single_tracks_audio_analysis.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_a_single_tracks_audio_analysis': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Recently_Played_Tracks(BaseFunction):
    """"""
    name = "Get Recently Played Tracks"
    url = "https://api.spotify.com/v1/me/player/recently-played"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # The maximum number of items to return. Default: 20. Minimum: 1. Maximum: 50.,
			Parameter(name="after", param_type=ParameterType.INTEGER, required=False),  # A Unix timestamp in milliseconds. Returns all items after (but not including) this cursor position. If `after` is specified, `before` must not be specified.,
			Parameter(name="before", param_type=ParameterType.INTEGER, required=False),  # A Unix timestamp in milliseconds. Returns all items before (but not including) this cursor position. If `before` is specified, `after` must not be specified.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # A link to the Web API endpoint returning the full result of the request.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # The maximum number of items in the response (as set in the query or by default).,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=False),  # URL to the next page of items. ( `null` if none),
			OutputParameter(name="cursors", param_type=OutputParameterType.OBJECT, is_array=False),  # The cursors used to find the next set of items.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # The total number of items available to return.,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # A paged set of tracks containing Track and Played_at.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_Recently_Played_Tracks.method, 
                                           Get_Recently_Played_Tracks.url,
                                           Get_Recently_Played_Tracks.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Recently_Played_Tracks': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_a_Show(BaseFunction):
    """"""
    name = "Get a Show"
    url = "https://api.spotify.com/v1/shows/{id}"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="market", param_type=ParameterType.STRING, required=False),  # An [ISO 3166-1 alpha-2 country code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2). If a country code is specified, only content that is available in that market will be returned. The country associated with the user account will take priority over this parameter if a valid user access token is provided. Example: `market=ES`.,
			Parameter(name="id", param_type=ParameterType.STRING, required=True),  # The [Spotify ID] for the show. Example: `38bS44xjbVVZ3No3ByF1dJ`.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="available_markets", param_type=OutputParameterType.STRING, is_array=True),  # A list of the countries in which the show can be played, identified by their [ISO 3166-1 alpha-2](http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) code.,
			OutputParameter(name="copyrights", param_type=OutputParameterType.OBJECT, is_array=True),  # The copyright statements of the show.,
			OutputParameter(name="description", param_type=OutputParameterType.STRING, is_array=False),  # A description of the show. HTML tags are stripped away.,
			OutputParameter(name="html_description", param_type=OutputParameterType.STRING, is_array=False),  # A description of the show. This field may contain HTML tags.,
			OutputParameter(name="explicit", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Whether or not the show has explicit content.,
			OutputParameter(name="external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # External URLs for this show.,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # A link to the Web API endpoint providing full details of the show.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # The [Spotify ID] for the show.,
			OutputParameter(name="images", param_type=OutputParameterType.OBJECT, is_array=True),  # The cover art for the show in various sizes.,
			OutputParameter(name="is_externally_hosted", param_type=OutputParameterType.BOOLEAN, is_array=False),  # True if all episodes are hosted outside Spotify's CDN.,
			OutputParameter(name="languages", param_type=OutputParameterType.STRING, is_array=True),  # A list of the languages used in the show, identified by their ISO 639 codes.,
			OutputParameter(name="media_type", param_type=OutputParameterType.STRING, is_array=False),  # The media type of the show.,
			OutputParameter(name="name", param_type=OutputParameterType.STRING, is_array=False),  # The name of the show.,
			OutputParameter(name="publisher", param_type=OutputParameterType.STRING, is_array=False),  # The publisher of the show.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # The object type: "show".,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # The [Spotify URI] for the show.,
			OutputParameter(name="total_episodes", param_type=OutputParameterType.INTEGER, is_array=False),  # The total number of episodes in the show.,
			OutputParameter(name="episodes", param_type=OutputParameterType.OBJECT, is_array=False),  # The episodes of the show.,
			OutputParameter(name="currently_playing_type", param_type=OutputParameterType.STRING, is_array=False),  # The object type of the currently playing item. Can be `track`, `episode`, `ad`, or `unknown`.,
			OutputParameter(name="actions", param_type=OutputParameterType.OBJECT, is_array=False),  # Allows updating the user interface based on available playback actions.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_a_Show.method, 
                                           Get_a_Show.url,
                                           Get_a_Show.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_a_Show': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Playback_State(BaseFunction):
    """"""
    name = "Get Playback State"
    url = "https://api.spotify.com/v1/me/player"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="market", param_type=ParameterType.STRING, required=False),  # An [ISO 3166-1 alpha-2 country code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2). If specified, only content available in that market will be returned. The country associated with the user account will take priority if a valid user access token is provided.,
			Parameter(name="additional_types", param_type=ParameterType.STRING, required=False),  # A comma-separated list of item types supported besides `track` (e.g., `episode`).
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="device", param_type=OutputParameterType.OBJECT, is_array=False),  # The device currently active.,
			OutputParameter(name="repeat_state", param_type=OutputParameterType.STRING, is_array=False),  # The repeat state: 'off', 'track', or 'context'.,
			OutputParameter(name="shuffle_state", param_type=OutputParameterType.BOOLEAN, is_array=False),  # If shuffle is on or off.,
			OutputParameter(name="context", param_type=OutputParameterType.OBJECT, is_array=False),  # The context the track was played from.,
			OutputParameter(name="timestamp", param_type=OutputParameterType.INTEGER, is_array=False),  # Unix Millisecond Timestamp when playback state was last changed.,
			OutputParameter(name="progress_ms", param_type=OutputParameterType.INTEGER, is_array=False),  # Progress into the currently playing track or episode in milliseconds.,
			OutputParameter(name="is_playing", param_type=OutputParameterType.BOOLEAN, is_array=False),  # If something is currently playing.,
			OutputParameter(name="item", param_type=OutputParameterType.OBJECT, is_array=False),  # The currently playing track or episode, or null.,
			OutputParameter(name="currently_playing_type", param_type=OutputParameterType.STRING, is_array=False),  # The object type of the currently playing item: 'track', 'episode', 'ad', 'unknown'.,
			OutputParameter(name="actions", param_type=OutputParameterType.OBJECT, is_array=False),  # Actions that can be performed in the current context.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_Playback_State.method, 
                                           Get_Playback_State.url,
                                           Get_Playback_State.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Playback_State': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_a_Categorys_Playlists(BaseFunction):
    """Fetches Spotify playlists for a specific category."""
    name = "Get a Category's Playlists"
    url = "https://api.spotify.com/v1/browse/categories/{category_id}/playlists"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="category_id", param_type=ParameterType.STRING, required=True),  # The Spotify category ID, e.g. 'dinner'. This is a path parameter.,
			Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Maximum number of items to return. Default: 20. Range: 1-50.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # Index of the first item to return. Default: 0.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="message", param_type=OutputParameterType.STRING, is_array=False),  # The localized message of a playlist. Example: 'Popular Playlists'.,
			OutputParameter(name="playlists", param_type=OutputParameterType.OBJECT, is_array=False),  # A paged set of playlists.,
			OutputParameter(name="playlists.href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the Web API endpoint returning the full result of the request.,
			OutputParameter(name="playlists.limit", param_type=OutputParameterType.INTEGER, is_array=False),  # Maximum number of items in the response.,
			OutputParameter(name="playlists.next", param_type=OutputParameterType.STRING, is_array=False),  # URL to the next page of items. Null if none.,
			OutputParameter(name="playlists.offset", param_type=OutputParameterType.INTEGER, is_array=False),  # The offset of the items returned.,
			OutputParameter(name="playlists.previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to the previous page of items. Null if none.,
			OutputParameter(name="playlists.total", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of items available.,
			OutputParameter(name="playlists.items", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of playlist objects.,
			OutputParameter(name="items.collaborative", param_type=OutputParameterType.BOOLEAN, is_array=False),  # True if the owner allows modification.,
			OutputParameter(name="items.description", param_type=OutputParameterType.STRING, is_array=False),  # Playlist description. Null if not available.,
			OutputParameter(name="items.external_urls.spotify", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URL for the playlist.,
			OutputParameter(name="items.href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the Web API endpoint of the playlist.,
			OutputParameter(name="items.id", param_type=OutputParameterType.STRING, is_array=False),  # Spotify ID of the playlist.,
			OutputParameter(name="items.images", param_type=OutputParameterType.OBJECT, is_array=True),  # Images for the playlist.,
			OutputParameter(name="images.url", param_type=OutputParameterType.STRING, is_array=False),  # Source URL of the image.,
			OutputParameter(name="images.height", param_type=OutputParameterType.INTEGER, is_array=False),  # Height of the image in pixels.,
			OutputParameter(name="images.width", param_type=OutputParameterType.INTEGER, is_array=False),  # Width of the image in pixels.,
			OutputParameter(name="items.name", param_type=OutputParameterType.STRING, is_array=False),  # Name of the playlist.,
			OutputParameter(name="items.owner", param_type=OutputParameterType.OBJECT, is_array=False),  # Owner of the playlist.,
			OutputParameter(name="owner.external_urls.spotify", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URL for the owner.,
			OutputParameter(name="owner.href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the owner in Web API.,
			OutputParameter(name="owner.id", param_type=OutputParameterType.STRING, is_array=False),  # Spotify ID of the owner.,
			OutputParameter(name="owner.type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, e.g. 'user'.,
			OutputParameter(name="owner.uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI for the owner.,
			OutputParameter(name="owner.display_name", param_type=OutputParameterType.STRING, is_array=False),  # Display name of the owner.,
			OutputParameter(name="items.public", param_type=OutputParameterType.BOOLEAN, is_array=False),  # The playlist's public/private status.,
			OutputParameter(name="items.snapshot_id", param_type=OutputParameterType.STRING, is_array=False),  # Current version identifier of the playlist.,
			OutputParameter(name="items.tracks", param_type=OutputParameterType.OBJECT, is_array=False),  # Contains link and total number of tracks.,
			OutputParameter(name="tracks.href", param_type=OutputParameterType.STRING, is_array=False),  # Link to fetch playlist tracks.,
			OutputParameter(name="tracks.total", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of tracks.,
			OutputParameter(name="items.type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, e.g. 'playlist'.,
			OutputParameter(name="items.uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI for the playlist.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_a_Categorys_Playlists.method, 
                                           Get_a_Categorys_Playlists.url,
                                           Get_a_Categorys_Playlists.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_a_Categorys_Playlists': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Several_Albums(BaseFunction):
    """Fetches details for multiple albums using their Spotify IDs."""
    name = "Get Several Albums"
    url = "https://api.spotify.com/v1/albums"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # Comma-separated list of Spotify IDs. Maximum 20 IDs.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # ISO 3166-1 alpha-2 country code; determines market availability.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="albums", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of Album objects.,
			OutputParameter(name="albums.album_type", param_type=OutputParameterType.STRING, is_array=False),  # Type of the album. Allowed: 'album', 'single', 'compilation'.,
			OutputParameter(name="albums.total_tracks", param_type=OutputParameterType.INTEGER, is_array=False),  # Number of tracks in the album.,
			OutputParameter(name="albums.available_markets", param_type=OutputParameterType.STRING, is_array=True),  # Markets where the album is available, identified by ISO 3166-1 alpha-2 codes.,
			OutputParameter(name="albums.external_urls.spotify", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URL of the album.,
			OutputParameter(name="albums.href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the Web API endpoint of the album.,
			OutputParameter(name="albums.id", param_type=OutputParameterType.STRING, is_array=False),  # Spotify ID of the album.,
			OutputParameter(name="albums.images", param_type=OutputParameterType.OBJECT, is_array=True),  # Album cover images.,
			OutputParameter(name="images.url", param_type=OutputParameterType.STRING, is_array=False),  # Source URL of the image.,
			OutputParameter(name="images.height", param_type=OutputParameterType.INTEGER, is_array=False),  # Image height in pixels.,
			OutputParameter(name="images.width", param_type=OutputParameterType.INTEGER, is_array=False),  # Image width in pixels.,
			OutputParameter(name="albums.name", param_type=OutputParameterType.STRING, is_array=False),  # Album name.,
			OutputParameter(name="albums.release_date", param_type=OutputParameterType.STRING, is_array=False),  # Release date in ISO 8601 format, e.g. '1981-12'.,
			OutputParameter(name="albums.release_date_precision", param_type=OutputParameterType.STRING, is_array=False),  # Precision of release date. Allowed: 'year', 'month', 'day'.,
			OutputParameter(name="albums.restrictions.reason", param_type=OutputParameterType.STRING, is_array=False),  # Reason for restriction, e.g. 'market'.,
			OutputParameter(name="albums.type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, e.g. 'album'.,
			OutputParameter(name="albums.uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI of the album.,
			OutputParameter(name="albums.artists", param_type=OutputParameterType.OBJECT, is_array=True),  # Artists associated with the album.,
			OutputParameter(name="artists.external_urls.spotify", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URL for the artist.,
			OutputParameter(name="artists.href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the artist in Web API.,
			OutputParameter(name="artists.id", param_type=OutputParameterType.STRING, is_array=False),  # Spotify ID of the artist.,
			OutputParameter(name="artists.name", param_type=OutputParameterType.STRING, is_array=False),  # Name of the artist.,
			OutputParameter(name="artists.type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, e.g. 'artist'.,
			OutputParameter(name="artists.uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI for the artist.,
			OutputParameter(name="albums.tracks", param_type=OutputParameterType.OBJECT, is_array=True),  # Tracks of the album.,
			OutputParameter(name="tracks.href", param_type=OutputParameterType.STRING, is_array=False),  # Link to fetch tracks.,
			OutputParameter(name="tracks.limit", param_type=OutputParameterType.INTEGER, is_array=False),  # Maximum number of tracks in the response.,
			OutputParameter(name="tracks.next", param_type=OutputParameterType.STRING, is_array=False),  # URL to fetch next set of tracks; null if none.,
			OutputParameter(name="tracks.offset", param_type=OutputParameterType.INTEGER, is_array=False),  # Offset for tracks.,
			OutputParameter(name="tracks.previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to previous set of tracks; null if none.,
			OutputParameter(name="tracks.total", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of tracks in album.,
			OutputParameter(name="tracks.items", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of track objects.,
			OutputParameter(name="items.artists", param_type=OutputParameterType.OBJECT, is_array=True),  # Artists of the track.,
			OutputParameter(name="items.external_urls.spotify", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URL for the artist.,
			OutputParameter(name="items.href", param_type=OutputParameterType.STRING, is_array=False),  # Link to track in Web API.,
			OutputParameter(name="items.id", param_type=OutputParameterType.STRING, is_array=False),  # Spotify ID of the track.,
			OutputParameter(name="items.name", param_type=OutputParameterType.STRING, is_array=False),  # Track name.,
			OutputParameter(name="items.type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, e.g. 'track'.,
			OutputParameter(name="items.uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI of the track.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_Several_Albums.method, 
                                           Get_Several_Albums.url,
                                           Get_Several_Albums.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Several_Albums': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Save_Episodes_for_Current_User(BaseFunction):
    """Endpoint to save one or more episodes to the current user's library. Accepts either a comma-separated string in the 'ids' query parameter or a JSON array in the request body. The maximum number of IDs that can be sent in one request is 50."""
    name = "Save Episodes for Current User"
    url = "https://api.spotify.com/v1/me/episodes"
    args_in_url = False
    method = "PUT"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of the Spotify IDs. Maximum 50 IDs. Example: '77o6BIVlYM3msb4MMIL1jH,0Q86acNRm6V9GYx55SXKwf'.,
			Parameter(name="body", param_type=OutputParameterType.OBJECT, required=True),  # JSON object containing an array 'ids' of Spotify IDs, max 50 items.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="status_code", param_type=OutputParameterType.STRING, is_array=False),  # HTTP status code indicating the result (e.g., '200', '401', etc.).
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Save_Episodes_for_Current_User.method, 
                                           Save_Episodes_for_Current_User.url,
                                           Save_Episodes_for_Current_User.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Save_Episodes_for_Current_User': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_an_Episode(BaseFunction):
    """Retrieve detailed information about a specific episode by its Spotify ID, including metadata, images, and related show info."""
    name = "Get an Episode"
    url = "https://api.spotify.com/v1/episodes/{id}"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.STRING, required=True),  # The Spotify ID for the episode. Example: '5Xt5DXGzch68nYYamXrNxZ'.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # Optional country code (ISO 3166-1 alpha-2). Determines content availability based on market.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="audio_preview_url", param_type=OutputParameterType.STRING, is_array=False),  # A URL to a 30 second preview (MP3 format) of the episode. Nullable and deprecated. Example: 'https://p.scdn.co/mp3-preview/2f37da1d4221f40b9d1a98cd191f4d6f1646ad17'.,
			OutputParameter(name="description", param_type=OutputParameterType.STRING, is_array=False),  # A description of the episode with HTML tags stripped. Use 'html_description' if HTML content is needed.,
			OutputParameter(name="html_description", param_type=OutputParameterType.STRING, is_array=False),  # A description of the episode, can contain HTML tags.,
			OutputParameter(name="duration_ms", param_type=OutputParameterType.INTEGER, is_array=False),  # Length of the episode in milliseconds.,
			OutputParameter(name="explicit", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Indicates whether the episode has explicit content.,
			OutputParameter(name="external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # External URLs related to the episode, e.g., Spotify URL.,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # URL to the API endpoint providing full details of the episode.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # The Spotify ID of the episode.,
			OutputParameter(name="images", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of images representing the episode cover art.,
			OutputParameter(name="is_playable", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Indicates if the episode is playable in the given market.,
			OutputParameter(name="languages", param_type=OutputParameterType.STRING, is_array=True),  # List of ISO 639-1 codes representing the languages used in the episode.,
			OutputParameter(name="name", param_type=OutputParameterType.STRING, is_array=False),  # The name of the episode.,
			OutputParameter(name="release_date", param_type=OutputParameterType.STRING, is_array=False),  # The release date of the episode in 'YYYY-MM-DD' format.,
			OutputParameter(name="release_date_precision", param_type=OutputParameterType.STRING, is_array=False),  # Precision of the release date: 'year', 'month', or 'day'.,
			OutputParameter(name="resume_point", param_type=OutputParameterType.OBJECT, is_array=False),  # User's most recent playback position in the episode, if available.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, always 'episode'.,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # The Spotify URI for the episode.,
			OutputParameter(name="restrictions", param_type=OutputParameterType.OBJECT, is_array=False),  # Content restrictions if any, with reason.,
			OutputParameter(name="show", param_type=OutputParameterType.OBJECT, is_array=False),  # Object representing the show the episode belongs to.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_an_Episode.method, 
                                           Get_an_Episode.url,
                                           Get_an_Episode.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_an_Episode': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_the_current_users_profile(BaseFunction):
    """"""
    name = "Get the current user's profile"
    url = "https://api.spotify.com/v1/me"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="country", param_type=OutputParameterType.STRING, is_array=False),  # The country of the user, as set in the user's account profile. An ISO 3166-1 alpha-2 country code.,
			OutputParameter(name="display_name", param_type=OutputParameterType.STRING, is_array=False),  # The name displayed on the user's profile. null if not available.,
			OutputParameter(name="email", param_type=OutputParameterType.STRING, is_array=False),  # The user's email address, as entered by the user when creating their account. Important! This email address is unverified.,
			OutputParameter(name="explicit_content", param_type=OutputParameterType.OBJECT, is_array=False),  # The user's explicit content settings.,
			OutputParameter(name="external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # Known external URLs for this user.,
			OutputParameter(name="followers", param_type=OutputParameterType.OBJECT, is_array=False),  # Information about the followers of the user.,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # A link to the Web API endpoint for this user.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # The Spotify user ID for the user.,
			OutputParameter(name="images", param_type=OutputParameterType.OBJECT, is_array=True),  # The user's profile image.,
			OutputParameter(name="product", param_type=OutputParameterType.STRING, is_array=False),  # The user's Spotify subscription level: "premium", "free" etc.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # The object type: 'user'.,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # The Spotify URI for the user.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_the_current_users_profile.method, 
                                           Get_the_current_users_profile.url,
                                           Get_the_current_users_profile.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_the_current_users_profile': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_a_list_of_the_albums_saved_in_the_current_Spotify_users_Your_Music_library(BaseFunction):
    """"""
    name = "Get a list of the albums saved in the current Spotify user’s ‘Your Music’ library"
    url = "https://api.spotify.com/v1/me/albums"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Maximum number of items to return. Default: 20. Range: 1-50.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # The index of the first item to return. Default: 0.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # An ISO 3166-1 alpha-2 country code. If specified, only content available in that market is returned.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # A link to the Web API endpoint returning the full result of the request.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # Maximum number of items in the response.,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=False),  # URL to the next page of items. null if none.,
			OutputParameter(name="offset", param_type=OutputParameterType.INTEGER, is_array=False),  # The offset of the items returned.,
			OutputParameter(name="previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to previous page of items. null if none.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of items available.,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # An array of saved album objects.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_a_list_of_the_albums_saved_in_the_current_Spotify_users_Your_Music_library.method, 
                                           Get_a_list_of_the_albums_saved_in_the_current_Spotify_users_Your_Music_library.url,
                                           Get_a_list_of_the_albums_saved_in_the_current_Spotify_users_Your_Music_library.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_a_list_of_the_albums_saved_in_the_current_Spotify_users_Your_Music_library': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Spotifys_list_of_featured_playlists(BaseFunction):
    """"""
    name = "Get Spotify's list of featured playlists"
    url = "https://api.spotify.com/v1/browse/featured-playlists"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="locale", param_type=ParameterType.STRING, required=False),  # The desired language, ISO 639-1 code and ISO 3166-1 alpha-2 country code joined by an underscore, e.g., 'es_MX'. If not supplied, defaults to American English.,
			Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Maximum number of items to return. Default: 20. Range: 1-50.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # The index of the first item to return. Default: 0.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="message", param_type=OutputParameterType.STRING, is_array=False),  # The localized message of a playlist.,
			OutputParameter(name="playlists", param_type=OutputParameterType.OBJECT, is_array=False),  # A paged set of playlists.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_Spotifys_list_of_featured_playlists.method, 
                                           Get_Spotifys_list_of_featured_playlists.url,
                                           Get_Spotifys_list_of_featured_playlists.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Spotifys_list_of_featured_playlists': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Album(BaseFunction):
    """Get detailed information about a specific album by Spotify ID."""
    name = "Get Album"
    url = "https://api.spotify.com/v1/albums/{id}"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the album. Example: '4aawyAB9vmqN3uQ7FjRGTy'.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # An ISO 3166-1 alpha-2 country code. Specifies the market in which to return content. Example: 'ES'. If not provided, defaults to user's country if access token is provided.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="album_type", param_type=OutputParameterType.STRING, is_array=False),  # The type of the album. Allowed values: 'album', 'single', 'compilation'.,
			OutputParameter(name="total_tracks", param_type=OutputParameterType.INTEGER, is_array=False),  # The number of tracks in the album.,
			OutputParameter(name="available_markets", param_type=OutputParameterType.STRING, is_array=True),  # Markets where the album is available, specified by ISO 3166-1 alpha-2 codes. Example: ['CA','BR','IT'].,
			OutputParameter(name="external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # Known external URLs for this album, contains 'spotify' string.,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the Web API endpoint providing full details of the album.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # The Spotify ID of the album. Example: '2up3OPMp9Tb4dAKM2erWXQ'.,
			OutputParameter(name="images", param_type=OutputParameterType.OBJECT, is_array=True),  # The cover art in various sizes.,
			OutputParameter(name="name", param_type=OutputParameterType.STRING, is_array=False),  # The name of the album.,
			OutputParameter(name="release_date", param_type=OutputParameterType.STRING, is_array=False),  # The release date of the album. Format varies by 'release_date_precision'.,
			OutputParameter(name="release_date_precision", param_type=OutputParameterType.STRING, is_array=False),  # Precision of 'release_date'. Allowed values: 'year', 'month', 'day'.,
			OutputParameter(name="restrictions", param_type=OutputParameterType.OBJECT, is_array=False),  # Content restrictions, if any, includes 'reason' field.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # Object type: 'album'.,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI of the album, e.g., 'spotify:album:...'.,
			OutputParameter(name="artists", param_type=OutputParameterType.OBJECT, is_array=True),  # Artists of the album.,
			OutputParameter(name="tracks", param_type=OutputParameterType.OBJECT, is_array=False),  # Tracks in the album, with 'href', 'limit', 'next', 'offset', 'previous', 'total', 'items'.,
			OutputParameter(name="copyrights", param_type=OutputParameterType.OBJECT, is_array=True),  # Copyright statements.,
			OutputParameter(name="external_ids", param_type=OutputParameterType.OBJECT, is_array=False),  # External identifiers like ISRC, EAN, UPC.,
			OutputParameter(name="genres", param_type=OutputParameterType.STRING, is_array=True),  # (Deprecated) always empty array.,
			OutputParameter(name="label", param_type=OutputParameterType.STRING, is_array=False),  # Label associated with the album.,
			OutputParameter(name="popularity", param_type=OutputParameterType.INTEGER, is_array=False),  # Popularity score between 0 and 100.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_Album.method, 
                                           Get_Album.url,
                                           Get_Album.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Album': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Reorder_or_replace_playlist_tracks(BaseFunction):
    """Reorder or replace tracks in a playlist. Use 'uris' to replace tracks, or 'range_start', 'insert_before', and 'range_length' to reorder."""
    name = "Reorder or replace playlist tracks"
    url = "https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    args_in_url = True
    method = "PUT"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="playlist_id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the playlist. Example: '3cEYpjA9oz9GiPac4AsH4n'.,
			Parameter(name="uris", param_type=ParameterType.STRING, required=False),  # Comma-separated list of Spotify URIs to add (for replacing tracks). Example: 'spotify:track:...'. Max 100 items.,
			Parameter(name="range_start", param_type=ParameterType.INTEGER, required=False),  # Position of the first item to be reordered.,
			Parameter(name="insert_before", param_type=ParameterType.INTEGER, required=False),  # Position where the items should be inserted.,
			Parameter(name="range_length", param_type=ParameterType.INTEGER, required=False),  # Number of items to move starting from 'range_start'. Defaults to 1.,
			Parameter(name="snapshot_id", param_type=ParameterType.STRING, required=False),  # The playlist's snapshot ID for concurrency control.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="snapshot_id", param_type=OutputParameterType.STRING, is_array=False),  # A Snapshot ID for the playlist after the operation, e.g., 'abc'.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Reorder_or_replace_playlist_tracks.method, 
                                           Reorder_or_replace_playlist_tracks.url,
                                           Reorder_or_replace_playlist_tracks.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Reorder_or_replace_playlist_tracks': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Spotify_URIs_and_IDs(BaseFunction):
    """Provides the standard Spotify URIs and IDs for resources like tracks, artists, albums, categories, and users."""
    name = "Spotify URIs and IDs"
    url = "https://developer.spotify.com/documentation/web-api/concepts/spotify-uris-ids"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="spotify_uri", param_type=OutputParameterType.STRING, is_array=False),  # Resource identifier for entities like artist, album, or track. Example: 'spotify:track:6rqhFgbbKwnb9MLmUQDhG6'.,
			OutputParameter(name="spotify_id", param_type=OutputParameterType.STRING, is_array=False),  # Base62 identifier found at the end of the URI. Example: '6rqhFgbbKwnb9MLmUQDhG6'.,
			OutputParameter(name="spotify_category_id", param_type=OutputParameterType.STRING, is_array=False),  # Unique string for Spotify category. Example: 'party'.,
			OutputParameter(name="spotify_user_id", param_type=OutputParameterType.STRING, is_array=False),  # Unique string for Spotify user ID. Example: 'wizzler'.,
			OutputParameter(name="spotify_url", param_type=OutputParameterType.STRING, is_array=False),  # URL to open resource in Spotify client. Example: 'http://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6'.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Spotify_URIs_and_IDs.method, 
                                           Spotify_URIs_and_IDs.url,
                                           Spotify_URIs_and_IDs.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Spotify_URIs_and_IDs': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Playlist(BaseFunction):
    """Retrieve full details of a playlist owned by a Spotify user."""
    name = "Get Playlist"
    url = "https://api.spotify.com/v1/playlists/{playlist_id}"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="playlist_id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the playlist. Example: '3cEYpjA9oz9GiPac4AsH4n'.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # An ISO 3166-1 alpha-2 country code. Content available in this market will be returned. If a user access token is provided, the user's country takes priority. No value or null indicates content is unavailable.,
			Parameter(name="fields", param_type=ParameterType.STRING, required=False),  # Comma-separated list of fields to return, supports dot notation and parentheses for nested fields. Example: 'description,uri'.,
			Parameter(name="additional_types", param_type=ParameterType.STRING, required=False),  # Comma-separated list of item types besides 'track', valid values are 'track' and 'episode'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="collaborative", param_type=OutputParameterType.BOOLEAN, is_array=False),  # True if the owner allows other users to modify the playlist.,
			OutputParameter(name="description", param_type=OutputParameterType.STRING, is_array=False),  # The playlist description. Nullable; null if not available.,
			OutputParameter(name="external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # Known external URLs for the playlist. Contains 'spotify' string.,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the Web API endpoint for full playlist details.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # The Spotify ID for the playlist.,
			OutputParameter(name="images", param_type=OutputParameterType.OBJECT, is_array=True),  # Images for the playlist, up to three, ordered by size. Each contains 'url', 'height', and 'width'.,
			OutputParameter(name="name", param_type=OutputParameterType.STRING, is_array=False),  # The name of the playlist.,
			OutputParameter(name="owner", param_type=OutputParameterType.OBJECT, is_array=False),  # User who owns the playlist, contains 'external_urls', 'href', 'id', 'type', 'uri', 'display_name'.,
			OutputParameter(name="public", param_type=OutputParameterType.BOOLEAN, is_array=False),  # The playlist's public/private status; true, false, or null.,
			OutputParameter(name="snapshot_id", param_type=OutputParameterType.STRING, is_array=False),  # Playlist version identifier.,
			OutputParameter(name="tracks", param_type=OutputParameterType.OBJECT, is_array=False),  # Details about the tracks, including 'href', 'limit', 'next', 'offset', 'previous', 'total', 'items'.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # Object type: 'playlist'.,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # The Spotify URI for the playlist.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_Playlist.method, 
                                           Get_Playlist.url,
                                           Get_Playlist.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Playlist': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Add_Items_to_Playlist(BaseFunction):
    """Add one or more items to a user's playlist, responding with a snapshot ID."""
    name = "Add Items to Playlist"
    url = "https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    args_in_url = True
    method = "PUT"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="playlist_id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the playlist.,
			Parameter(name="position", param_type=ParameterType.INTEGER, required=False),  # Zero-based index to insert items at. Defaults to appending if omitted.,
			Parameter(name="uris", param_type=ParameterType.STRING, required=False),  # Comma-separated list of Spotify URIs to add, e.g., 'spotify:track:...' or 'spotify:episode:...'. Support up to 100 items; recommended to send as JSON array in body.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="snapshot_id", param_type=OutputParameterType.STRING, is_array=False),  # A snapshot ID for the playlist after addition.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Add_Items_to_Playlist.method, 
                                           Add_Items_to_Playlist.url,
                                           Add_Items_to_Playlist.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Add_Items_to_Playlist': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Follow_Artists_or_Users(BaseFunction):
    """Follow one or more artists or users, adding the current user as a follower, requiring 'user-follow-modify' scope."""
    name = "Follow Artists or Users"
    url = "https://api.spotify.com/v1/me/following?type={type}"
    args_in_url = False
    method = "PUT"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="type", param_type=ParameterType.STRING, required=True),  # The ID type. Allowed values: 'artist' or 'user'.,
			Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # Comma-separated list of Spotify IDs (max 50). Alternatively, provide JSON array in body.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="status", param_type=OutputParameterType.STRING, is_array=False),  # HTTP response status indicating success or failure.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Follow_Artists_or_Users.method, 
                                           Follow_Artists_or_Users.url,
                                           Follow_Artists_or_Users.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Follow_Artists_or_Users': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Remove_users_saved_tracks(BaseFunction):
    """Deletes one or more tracks from the current user's 'Your Music' library using either the comma-separated string or array format for IDs."""
    name = "Remove user's saved tracks"
    url = "https://api.spotify.com/v1/me/tracks"
    args_in_url = False
    method = "DELETE"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of Spotify IDs for the tracks to remove. Maximum: 50 IDs. Example: '7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ'.,
			Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # An array of Spotify track IDs, up to 50 items. Example: ['7ouMYWpwJ422jRcDASZB7P', '4VqPOruhp5EdPBeR92t6lQ']
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Remove_users_saved_tracks.method, 
                                           Remove_users_saved_tracks.url,
                                           Remove_users_saved_tracks.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Remove_users_saved_tracks': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_audio_features_for_a_track(BaseFunction):
    """Retrieves audio features for a specific track identified by its Spotify ID, providing a detailed audio analysis."""
    name = "Get audio features for a track"
    url = "https://api.spotify.com/v1/audio-features/{id}"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.STRING, required=True),  # The Spotify ID for the track. Example: '11dFghVXANMlKmJXsNCbNl'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="acousticness", param_type=OutputParameterType.FLOAT, is_array=False),  # Confidence measure from 0.0 to 1.0 of whether the track is acoustic. E.g., 0.00242.,
			OutputParameter(name="analysis_url", param_type=OutputParameterType.STRING, is_array=False),  # URL to access the full audio analysis, requires an access token. Example: 'https://api.spotify.com/v1/audio-analysis/2takcwOaAZWiXQijPHIx7B'.,
			OutputParameter(name="danceability", param_type=OutputParameterType.FLOAT, is_array=False),  # Describes how suitable the track is for dancing, from 0.0 (least danceable) to 1.0 (most danceable). Example: 0.585.,
			OutputParameter(name="duration_ms", param_type=OutputParameterType.INTEGER, is_array=False),  # Length of the track in milliseconds. Example: 237040.,
			OutputParameter(name="energy", param_type=OutputParameterType.FLOAT, is_array=False),  # Perceptual measure from 0.0 to 1.0 of intensity and activity. Example: 0.842.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # The Spotify ID for the track. Example: '2takcwOaAZWiXQijPHIx7B'.,
			OutputParameter(name="instrumentalness", param_type=OutputParameterType.FLOAT, is_array=False),  # Predicts likelihood of no vocals, from 0.0 to 1.0. Example: 0.00686.,
			OutputParameter(name="key", param_type=OutputParameterType.INTEGER, is_array=False),  # The key the track is in, from -1 (no key detected) to 11, using Pitch Class notation. Example: 9.,
			OutputParameter(name="liveness", param_type=OutputParameterType.FLOAT, is_array=False),  # Detects presence of audience, from 0.0 to 1.0. Example: 0.0866.,
			OutputParameter(name="loudness", param_type=OutputParameterType.FLOAT, is_array=False),  # Overall loudness in decibels. Example: -5.883.,
			OutputParameter(name="mode", param_type=OutputParameterType.INTEGER, is_array=False),  # Modal scale, 1 for major, 0 for minor. Example: 0.,
			OutputParameter(name="speechiness", param_type=OutputParameterType.FLOAT, is_array=False),  # Detects presence of spoken words, from 0.0 to 1.0. Example: 0.0556.,
			OutputParameter(name="tempo", param_type=OutputParameterType.FLOAT, is_array=False),  # Estimated tempo in beats per minute. Example: 118.211.,
			OutputParameter(name="time_signature", param_type=OutputParameterType.INTEGER, is_array=False),  # Estimated time signature, from 3 to 7. Example: 4.,
			OutputParameter(name="track_href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the Web API endpoint for full track details. Example: 'https://api.spotify.com/v1/tracks/2takcwOaAZWiXQijPHIx7B'.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, fixed value: 'audio_features'.,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI for the track. Example: 'spotify:track:2takcwOaAZWiXQijPHIx7B'.,
			OutputParameter(name="valence", param_type=OutputParameterType.FLOAT, is_array=False),  # Musical positiveness measure, from 0.0 (negative) to 1.0 (positive). Example: 0.428.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_audio_features_for_a_track.method, 
                                           Get_audio_features_for_a_track.url,
                                           Get_audio_features_for_a_track.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_audio_features_for_a_track': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_users_top_artists_or_tracks(BaseFunction):
    """Retrieves the current user's most played artists or tracks over a specified time period, limited to 50 items."""
    name = "Get user's top artists or tracks"
    url = "https://api.spotify.com/v1/me/top/{type}"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="type", param_type=ParameterType.STRING, required=True),  # The type of entity to return: 'artists' or 'tracks'. Allowed values: 'artists', 'tracks'.,
			Parameter(name="time_range", param_type=ParameterType.STRING, required=False),  # Time frame for the data: 'long_term', 'medium_term', 'short_term'. Defaults to 'medium_term'.,
			Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Maximum number of items to return, between 1 and 50. Default: 20.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # Index of the first item to return. Default: 0.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the full result set. Example: 'https://api.spotify.com/v1/me/shows?offset=0&limit=20'.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # Number of items in the response, as set in the query.,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=False),  # URL to next page, or null if none.,
			OutputParameter(name="offset", param_type=OutputParameterType.INTEGER, is_array=False),  # Index of the first item in the returned page.,
			OutputParameter(name="previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to previous page, or null if none.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of items available.,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of artist or track objects.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_users_top_artists_or_tracks.method, 
                                           Get_users_top_artists_or_tracks.url,
                                           Get_users_top_artists_or_tracks.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_users_top_artists_or_tracks': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Audiobook_Chapters(BaseFunction):
    """Retrieve audiobook chapters with pagination support."""
    name = "Get Audiobook Chapters"
    url = "https://api.spotify.com/v1/audiobooks/{id}/chapters"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the audiobook.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # ISO 3166-1 alpha-2 country code. If specified, only content available in that market will be returned.,
			Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Maximum number of items to return. Default is 20. Range: 1-50.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # Index of the first item to return. Default is 0.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the Web API endpoint returning full results.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # Maximum number of items in response.,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=False),  # URL to next page of items, or null if none.,
			OutputParameter(name="offset", param_type=OutputParameterType.INTEGER, is_array=False),  # Offset of the first item returned.,
			OutputParameter(name="previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to previous page of items, or null if none.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of items available.,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of chapter objects.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_Audiobook_Chapters.method, 
                                           Get_Audiobook_Chapters.url,
                                           Get_Audiobook_Chapters.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Audiobook_Chapters': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Several_Chapters(BaseFunction):
    """Retrieve multiple chapters by their Spotify IDs."""
    name = "Get Several Chapters"
    url = "https://api.spotify.com/v1/chapters"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # Comma-separated list of Spotify IDs for chapters. Max 50 IDs.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # ISO 3166-1 alpha-2 country code. Content availability depends on market.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="chapters", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of chapter objects.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_Several_Chapters.method, 
                                           Get_Several_Chapters.url,
                                           Get_Several_Chapters.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Several_Chapters': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Toggle_Playback_Shuffle(BaseFunction):
    """Controls whether shuffle is enabled or disabled on the user's playback."""
    name = "Toggle Playback Shuffle"
    url = "https://api.spotify.com/v1/me/player/shuffle"
    args_in_url = False
    method = "PUT"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="state", param_type=ParameterType.BOOLEAN, required=True),  # Required. true to shuffle user's playback; false to do not shuffle user's playback.,
			Parameter(name="device_id", param_type=ParameterType.STRING, required=False),  # Optional. The id of the device this command is targeting. If not supplied, the currently active device is the target.
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Toggle_Playback_Shuffle.method, 
                                           Toggle_Playback_Shuffle.url,
                                           Toggle_Playback_Shuffle.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Toggle_Playback_Shuffle': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Several_Browse_Categories(BaseFunction):
    """Retrieves a list of categories used to tag items in Spotify."""
    name = "Get Several Browse Categories"
    url = "https://api.spotify.com/v1/browse/categories"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="locale", param_type=ParameterType.STRING, required=False),  # Optional. The desired language, consisting of an ISO 639-1 language code and an ISO 3166-1 alpha-2 country code, joined by an underscore (e.g., 'es_MX'). This parameter specifies in which language the category strings should be returned.,
			Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Optional. The maximum number of items to return. Default is 20. Minimum is 1, maximum is 50.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # Optional. The index of the first item to return. Default is 0.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="categories", param_type=OutputParameterType.OBJECT, is_array=False),  # A paged set of categories.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_Several_Browse_Categories.method, 
                                           Get_Several_Browse_Categories.url,
                                           Get_Several_Browse_Categories.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Several_Browse_Categories': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Track(BaseFunction):
    """Retrieves detailed information about a specific track by its Spotify ID."""
    name = "Get Track"
    url = "https://api.spotify.com/v1/tracks/{id}"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.STRING, required=True),  # Required. The Spotify ID of the track.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # Optional. An ISO 3166-1 alpha-2 country code. If specified, only content available in that market will be returned. If a user access token is provided, the country of the user account will take priority. If neither market nor user country is provided, content is considered unavailable.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="album", param_type=OutputParameterType.OBJECT, is_array=False),  # The album on which the track appears. Contains details like album type, total tracks, available markets, external URLs, images, name, release date, restrictions, type, URI, and artists.,
			OutputParameter(name="artists", param_type=OutputParameterType.OBJECT, is_array=True),  # The artists of the track, each including external URLs, href, id, name, type, and uri.,
			OutputParameter(name="available_markets", param_type=OutputParameterType.STRING, is_array=True),  # List of countries where the track can be played, identified by ISO 3166-1 alpha-2 codes.,
			OutputParameter(name="disc_number", param_type=OutputParameterType.INTEGER, is_array=False),  # Disc number, usually 1 unless the album has multiple discs.,
			OutputParameter(name="duration_ms", param_type=OutputParameterType.INTEGER, is_array=False),  # Length of the track in milliseconds.,
			OutputParameter(name="explicit", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Indicates if the track has explicit lyrics.,
			OutputParameter(name="external_ids", param_type=OutputParameterType.OBJECT, is_array=False),  # External IDs for the track, such as ISRC, EAN, UPC.,
			OutputParameter(name="external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # External URLs for the track, including Spotify URL.,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the Web API endpoint for full details of the track.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # Spotify ID for the track.,
			OutputParameter(name="is_playable", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Part of response when track relinking is applied; indicates if the track is playable in the given market.,
			OutputParameter(name="linked_from", param_type=OutputParameterType.OBJECT, is_array=False),  # Contains information about the originally requested track if relinking has replaced it.,
			OutputParameter(name="restrictions", param_type=OutputParameterType.OBJECT, is_array=False),  # Restrictions applied to the content, including reason.,
			OutputParameter(name="name", param_type=OutputParameterType.STRING, is_array=False),  # Name of the track.,
			OutputParameter(name="popularity", param_type=OutputParameterType.INTEGER, is_array=False),  # Popularity of the track, between 0 and 100.,
			OutputParameter(name="preview_url", param_type=OutputParameterType.STRING, is_array=False),  # URL to a 30-second preview of the track, or null. Deprecated.,
			OutputParameter(name="track_number", param_type=OutputParameterType.INTEGER, is_array=False),  # Track number on the album.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, which is 'track'.,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI for the track.,
			OutputParameter(name="is_local", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Indicates if the track is from a local file.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_Track.method, 
                                           Get_Track.url,
                                           Get_Track.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Track': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Playlist_Items(BaseFunction):
    """Retrieves the tracks or episodes of a playlist, with support for pagination and filtering."""
    name = "Get Playlist Items"
    url = "https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="playlist_id", param_type=ParameterType.STRING, required=True),  # The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of the playlist.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # An [ISO 3166-1 alpha-2 country code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2). If a country code is specified, only content available in that market will be returned. Defaults to the user's country if a user access token is provided.,
			Parameter(name="fields", param_type=ParameterType.STRING, required=False),  # Filters for the query: a comma-separated list of the fields to return. If omitted, all fields are returned.,
			Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # The maximum number of items to return. Default: 20. Range: 1-50.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # The index of the first item to return. Default: 0.,
			Parameter(name="additional_types", param_type=ParameterType.STRING, required=False),  # A comma-separated list of item types supported besides 'track'. Valid types: 'track' and 'episode'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # A link to the Web API endpoint returning the full result of the request.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # The maximum number of items in the response.,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=False),  # URL to the next page of items, or null if none.,
			OutputParameter(name="offset", param_type=OutputParameterType.INTEGER, is_array=False),  # The offset of the items returned.,
			OutputParameter(name="previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to the previous page of items, or null if none.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # The total number of items available to return.,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # An array of PlaylistTrackObject. Each item includes details about added tracks or episodes.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_Playlist_Items.method, 
                                           Get_Playlist_Items.url,
                                           Get_Playlist_Items.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Playlist_Items': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Multiple_Audiobooks(BaseFunction):
    """Fetches information for multiple audiobooks by their Spotify IDs, taking into account market restrictions."""
    name = "Get Multiple Audiobooks"
    url = "https://api.spotify.com/v1/audiobooks"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of the [Spotify IDs](/documentation/web-api/concepts/spotify-uris-ids) of the audiobooks, max 50 IDs.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # An [ISO 3166-1 alpha-2 country code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2). If specified, only content available in that market will be returned.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="audiobooks", param_type=OutputParameterType.OBJECT, is_array=True),  # An array of AudiobookObject, each representing an audiobook or null if unavailable.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_Multiple_Audiobooks.method, 
                                           Get_Multiple_Audiobooks.url,
                                           Get_Multiple_Audiobooks.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Multiple_Audiobooks': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Save_Shows_for_Current_User(BaseFunction):
    """Endpoint to save one or multiple shows to the current Spotify user's library."""
    name = "Save Shows for Current User"
    url = "https://api.spotify.com/v1/me/shows"
    args_in_url = False
    method = "PUT"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of the Spotify IDs for the shows to save. Maximum of 50 IDs. Example: '5CfCWKI5pZ28U0uOzXkDHe,5as3aKmN2k11yfDDDSrvaZ'.
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Save_Shows_for_Current_User.method, 
                                           Save_Shows_for_Current_User.url,
                                           Save_Shows_for_Current_User.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Save_Shows_for_Current_User': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_a_List_of_Current_Users_Playlists(BaseFunction):
    """Endpoint to retrieve a paginated list of playlists owned or followed by the current user."""
    name = "Get a List of Current User's Playlists"
    url = "https://api.spotify.com/v1/me/playlists"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # The maximum number of items to return. Default: 20. Minimum: 1. Maximum: 50. Example: 10.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # The index of the first playlist to return. Default: 0. Example: 5.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # A link to the Web API endpoint returning the full result of the request.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # The maximum number of items in the response.,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=False),  # URL to the next page of items, or null if none.,
			OutputParameter(name="offset", param_type=OutputParameterType.INTEGER, is_array=False),  # The offset of the items returned.,
			OutputParameter(name="previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to the previous page of items, or null if none.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of playlists.,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of playlist objects.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_a_List_of_Current_Users_Playlists.method, 
                                           Get_a_List_of_Current_Users_Playlists.url,
                                           Get_a_List_of_Current_Users_Playlists.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_a_List_of_Current_Users_Playlists': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Unfollow_Playlist(BaseFunction):
    """Endpoint to remove the current user as a follower of a specific playlist."""
    name = "Unfollow Playlist"
    url = "https://api.spotify.com/v1/playlists/{playlist_id}/followers"
    args_in_url = True
    method = "DELETE"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="playlist_id", param_type=ParameterType.STRING, required=True),  # Spotify ID of the playlist to unfollow. Example: '3cEYpjA9oz9GiPac4AsH4n'.
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Unfollow_Playlist.method, 
                                           Unfollow_Playlist.url,
                                           Unfollow_Playlist.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Unfollow_Playlist': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Remove_Users_Saved_Episodes(BaseFunction):
    """Endpoint to remove episodes from the current user's library, accepting a list of episode IDs."""
    name = "Remove User's Saved Episodes"
    url = "https://api.spotify.com/v1/me/episodes"
    args_in_url = False
    method = "DELETE"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of Spotify IDs for the episodes to remove. Maximum of 50 IDs. Example: '7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B'.
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Remove_Users_Saved_Episodes.method, 
                                           Remove_Users_Saved_Episodes.url,
                                           Remove_Users_Saved_Episodes.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Remove_Users_Saved_Episodes': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Client_Credentials_Flow__Request_Token(BaseFunction):
    """Endpoint to obtain an access token using the client credentials flow for server-to-server authentication."""
    name = "Client Credentials Flow - Request Token"
    url = "https://accounts.spotify.com/api/token"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="grant_type", param_type=ParameterType.STRING, required=True),  # Must be set to 'client_credentials' to obtain an access token.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="access_token", param_type=OutputParameterType.STRING, is_array=False),  # An access token for making authenticated requests.,
			OutputParameter(name="token_type", param_type=OutputParameterType.STRING, is_array=False),  # Always 'Bearer'.,
			OutputParameter(name="expires_in", param_type=OutputParameterType.INTEGER, is_array=False),  # Token validity duration in seconds.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Client_Credentials_Flow__Request_Token.method, 
                                           Client_Credentials_Flow__Request_Token.url,
                                           Client_Credentials_Flow__Request_Token.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Client_Credentials_Flow__Request_Token': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Users_Saved_Audiobooks(BaseFunction):
    """Retrieve a list of audiobooks saved in the current user's library."""
    name = "Get User's Saved Audiobooks"
    url = "https://api.spotify.com/v1/me/audiobooks"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Maximum number of items to return. Default: 20. Range: 1 - 50.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # Index of the first item to return. Default: 0.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the endpoint returning the full result of the request.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # Maximum number of items in the response.,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=False),  # URL to the next page of items, or null if none.,
			OutputParameter(name="offset", param_type=OutputParameterType.INTEGER, is_array=False),  # The offset of the items returned.,
			OutputParameter(name="previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to the previous page of items, or null if none.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of items available.,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of saved audiobooks.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_Users_Saved_Audiobooks.method, 
                                           Get_Users_Saved_Audiobooks.url,
                                           Get_Users_Saved_Audiobooks.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Users_Saved_Audiobooks': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Users_Saved_Tracks(BaseFunction):
    """Retrieve a list of tracks saved in the current user's library."""
    name = "Get User's Saved Tracks"
    url = "https://api.spotify.com/v1/me/tracks"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="market", param_type=ParameterType.STRING, required=False),  # ISO 3166-1 alpha-2 country code. If specified, only content available in that market is returned. Example: 'ES'.,
			Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Maximum number of items to return. Default: 20. Range: 1 - 50.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # Index of the first item to return. Default: 0.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the endpoint returning the full result.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # Maximum number of items in the response.,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=False),  # URL to the next page, or null if none.,
			OutputParameter(name="offset", param_type=OutputParameterType.INTEGER, is_array=False),  # Offset of the items.,
			OutputParameter(name="previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to the previous page, or null if none.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of saved tracks.,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of saved track objects.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_Users_Saved_Tracks.method, 
                                           Get_Users_Saved_Tracks.url,
                                           Get_Users_Saved_Tracks.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Users_Saved_Tracks': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Users_Playlists(BaseFunction):
    """Retrieve a list of the playlists owned or followed by a Spotify user. Requires 'playlist-read-private' scope."""
    name = "Get User's Playlists"
    url = "https://api.spotify.com/v1/users/{user_id}/playlists"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_wrapper = api_wrapper
    
    def get_parameter_schema(self):
        return [
            Parameter(name="user_id", param_type=ParameterType.STRING, required=True),  # The Spotify user ID. Examples: 'smedjan'. This is a path parameter, part of the URL.,
			Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Maximum number of playlists to return. Default is 20. Allowed range: 1-50.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # Index of the first playlist to return. Default is 0. Allowed range: 0-100000.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # A link to the Web API endpoint returning the full result of the request.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # Maximum number of items in the response.,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=False),  # URL to the next page of items, or null if none.,
			OutputParameter(name="offset", param_type=OutputParameterType.INTEGER, is_array=False),  # The offset of the items returned.,
			OutputParameter(name="previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to the previous page of items, or null if none.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of playlists available.,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # An array of playlist objects.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_wrapper.request(Get_Users_Playlists.method, 
                                           Get_Users_Playlists.url,
                                           Get_Users_Playlists.args_in_url,
                                           input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Users_Playlists': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)

