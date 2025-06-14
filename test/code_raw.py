
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
import logging
        

METHODS = {"GET": get,
           "POST": post}

@dataclass
class APIClientConfig:
    """Configuration class for API settings"""
    base_url="https://developer.spotify.com/documentation/web-api"
    name="Spotify"

    # OAuth 2.0 access token with appropriate scopes to authorize API calls. Used for authenticated requests.
    access_token: str = None

    # Your Spotify application's client ID, used for authentication during authorization flows.
    client_id: str = None

    # Your Spotify application's client secret, used for authentication during authorization flows.
    client_secret: str = None

    # The URL to redirect to after authentication, must match the one set in your Spotify app settings.
    redirect_uri: str = None

    # Optional ISO country code filter for content availability and market-specific data.
    market: str = None

    # Maximum number of items to return; default is 20, range typically from 1 to 50.
    limit: int = None

    # Index of the first result to return, used for pagination.
    offset: int = None

    # The Spotify ID of a playlist to retrieve or modify, consistent across endpoints.
    playlist_id: str = None

    # Comma-separated list of Spotify IDs used for bulk operations like checking presence or removing items.
    ids: str = None

    # The name of a playlist or item, used when creating or renaming.
    name: str = None

    # Boolean string indicating if the playlist is public ('true') or private ('false').
    public: str = None

    # Boolean string to set playlist as collaborative or not.
    collaborative: str = None

    # Playlist description or item description.
    description: str = None

    # ID of the device targeted for playback commands.
    device_id: str = None

    # Boolean indicator ('true'/'false') to start playback on the specified device.
    play: str = None

    # Spotify ID of the resource, such as an artist, album, show, or episode.
    id: str = None

    # Locale string for localization purposes, such as language codes.
    locale: str = None

    def get_oauth_params(self, method: str, url: str) -> dict[str, str]:
        return {}

    def validate(self):
        # Asserts here
        pass

    def authenticate(self):
        # For authentication done before calls, not during.
        pass

    def __init__(self): 
        self.validate()
        self.authenticate()

    def request(self, method: str, url: str, args_in_url: bool, data: dict) -> dict[str, any]:
        if args_in_url:
            url = url.format(**data)  # TODO: Take in-url args out of payload. Probably best with template string.

        response = METHODS[method](url, data=data)
        
        if response.status_code != 200:
            raise Exception(response.text)

        return json.loads(response.text)



class Add_Item_to_Playback_Queue(BaseFunction):
    """Endpoint to add an item (track or episode) to the user's current playback queue. Requires 'user-modify-playback-state' scope."""
    name = "Add Item to Playback Queue"
    url = "https://api.spotify.com/v1/me/player/queue"
    args_in_url = False
    method = "PUT"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="uri", param_type=ParameterType.STRING, required=True),  # The URI of the item to add to the queue. Must be a track or an episode URI, e.g., 'spotify:track:4iV5W9uYEdYUVa79Axb7Rh'.,
			Parameter(name="device_id", param_type=ParameterType.STRING, required=False),  # The ID of the device to target. If not specified, the currently active device will be used. Example: '0d1841b0976bae2a3a310dd74c0f3df354899bc8'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="status_code", param_type=OutputParameterType.INTEGER, is_array=False),  # HTTP response status code indicating the result of the request.,
			OutputParameter(name="response_message", param_type=OutputParameterType.STRING, is_array=False),  # Optional message associated with the response, such as error details.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Add_Item_to_Playback_Queue.method, 
                                          Add_Item_to_Playback_Queue.url,
                                          Add_Item_to_Playback_Queue.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Add_Item_to_Playback_Queue': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Several_Tracks(BaseFunction):
    """Endpoint to retrieve metadata for multiple tracks based on their Spotify IDs. Requires 'user-read-private' or 'user-read-email' scope."""
    name = "Get Several Tracks"
    url = "https://api.spotify.com/v1/tracks"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="market", param_type=ParameterType.STRING, required=False),  # An ISO 3166-1 alpha-2 country code to filter track availability. Example: 'ES'.,
			Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of Spotify track IDs. Maximum: 50 IDs. Example: '7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="tracks", param_type=OutputParameterType.OBJECT, is_array=True),  # An array of track objects, each containing details such as album, artists, duration, etc.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Several_Tracks.method, 
                                          Get_Several_Tracks.url,
                                          Get_Several_Tracks.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Several_Tracks': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Check_if_User_Follows_Playlist(BaseFunction):
    """Endpoint to check if the current user follows a specific playlist. Requires 'playlist-read-private' scope."""
    name = "Check if User Follows Playlist"
    url = "https://api.spotify.com/v1/playlists/{playlist_id}/followers/contains"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="playlist_id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the playlist. Example: '3cEYpjA9oz9GiPac4AsH4n'.,
			Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list containing the current user's Spotify username. Maximum 1 ID. Example: 'jmperezperez'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="follows", param_type=OutputParameterType.BOOLEAN, is_array=True),  # An array with a single boolean indicating whether the current user follows the playlist. Example: [true].
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Check_if_User_Follows_Playlist.method, 
                                          Check_if_User_Follows_Playlist.url,
                                          Check_if_User_Follows_Playlist.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Check_if_User_Follows_Playlist': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Unfollow_Artists_or_Users(BaseFunction):
    """Removes the current user as a follower of specified artists or users. Requires 'user-follow-modify' scope."""
    name = "Unfollow Artists or Users"
    url = "https://api.spotify.com/v1/me/followingtype"
    args_in_url = True
    method = "DELETE"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="type", param_type=ParameterType.STRING, required=True),  # The ID type: either 'artist' or 'user'. Allowed values: "artist", "user". This parameter should be included in the URL path.,
			Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of the artist or user Spotify IDs. A maximum of 50 IDs can be sent in one request. Example: '74ASZWbe4lXaubB36ztrGX,08td7MxkoHQkXnWAYD8d6Q'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="status_code", param_type=OutputParameterType.INTEGER, is_array=False),  # HTTP response status code. 204 indicates success; other codes indicate errors.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Unfollow_Artists_or_Users.method, 
                                          Unfollow_Artists_or_Users.url,
                                          Unfollow_Artists_or_Users.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Unfollow_Artists_or_Users': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Available_Genre_Seeds(BaseFunction):
    """Retrieves a list of available genre seed values for use in recommendations. This endpoint is deprecated."""
    name = "Get Available Genre Seeds"
    url = "https://api.spotify.com/documentation/web-api/reference/check-users-saved-shows"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="genres", param_type=OutputParameterType.STRING, is_array=True),  # A list of available genre seed parameter values for recommendations. Example: ['alternative','samba'].
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Available_Genre_Seeds.method, 
                                          Get_Available_Genre_Seeds.url,
                                          Get_Available_Genre_Seeds.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Available_Genre_Seeds': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Search_for_Item(BaseFunction):
    """Endpoint to search for items in Spotify's catalog, matching a keyword string with optional filters."""
    name = "Search for Item"
    url = "/search"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="q", param_type=ParameterType.STRING, required=True),  # Your search query. You can refine the search with field filters like `album`, `artist`, `track`, `year`, `upc`, `tag:hipster`, `tag:new`, `isrc`, and `genre`. Filters apply to specific result types. For example: `q=remaster%20track:Doxy%20artist:Miles%20Davis`.,
			Parameter(name="type", param_type=ParameterType.STRING, required=True),  # A comma-separated list of item types to search across. Allowed values: "album", "artist", "playlist", "track", "show", "episode", "audiobook".,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # An ISO 3166-1 alpha-2 country code to filter results to a specific market. If omitted, defaults to the user's country.,
			Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Maximum number of results to return. Default is 20. Range: 0-50.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # Index of the first result to return. Default is 0. Range: 0-1000.,
			Parameter(name="include_external", param_type=ParameterType.STRING, required=False),  # If set to 'audio', includes externally hosted audio content in the results.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="tracks", param_type=OutputParameterType.OBJECT, is_array=True),  # Object containing paginated list of search results for tracks, albums, artists, playlists, shows, episodes, or audiobooks based on the search.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Search_for_Item.method, 
                                          Search_for_Item.url,
                                          Search_for_Item.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Search_for_Item': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Playlist_Cover_Image(BaseFunction):
    """Get the current images associated with a specific playlist, specified by its Spotify ID."""
    name = "Get Playlist Cover Image"
    url = "/playlists/{playlist_id}/images"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
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
            out = self.api_config.request(Get_Playlist_Cover_Image.method, 
                                          Get_Playlist_Cover_Image.url,
                                          Get_Playlist_Cover_Image.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Playlist_Cover_Image': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Users_Saved_Episodes(BaseFunction):
    """Retrieves a list of episodes saved in the current Spotify user's library."""
    name = "Get User's Saved Episodes"
    url = "https://api.spotify.com/v1/me/episodes"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="market", param_type=ParameterType.STRING, required=False),  # An ISO 3166-1 alpha-2 country code. If specified, only content available in that market will be returned. If not provided, the user's country will take priority over this parameter.,
			Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Maximum number of items to return (default: 20, min: 1, max: 50).,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # The index of the first item to return (default: 0). Used with 'limit' to paginate results.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # A link to the Web API endpoint returning the full result of the request.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # Maximum number of items in the response.,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=False),  # URL to the next page of items, null if none.,
			OutputParameter(name="offset", param_type=OutputParameterType.INTEGER, is_array=False),  # Index of the first item in the response.,
			OutputParameter(name="previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to the previous page of items, null if none.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of items available.,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of saved episode objects.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Users_Saved_Episodes.method, 
                                          Get_Users_Saved_Episodes.url,
                                          Get_Users_Saved_Episodes.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Users_Saved_Episodes': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Check_if_Episodes_are_Saved(BaseFunction):
    """Checks if one or more episodes are already saved in the user's library."""
    name = "Check if Episodes are Saved"
    url = "https://api.spotify.com/v1/me/episodes/contains"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of Spotify episode IDs, with a maximum of 50 IDs.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="array_of_booleans", param_type=OutputParameterType.BOOLEAN, is_array=True),  # Array indicating for each ID whether it is saved (true) or not (false) in the user's library.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Check_if_Episodes_are_Saved.method, 
                                          Check_if_Episodes_are_Saved.url,
                                          Check_if_Episodes_are_Saved.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Check_if_Episodes_are_Saved': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Set_Playback_Volume(BaseFunction):
    """Sets the volume for the user's current playback device."""
    name = "Set Playback Volume"
    url = "https://api.spotify.com/v1/me/player/volume"
    args_in_url = False
    method = "PUT"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="volume_percent", param_type=ParameterType.INTEGER, required=True),  # The volume to set, from 0 to 100 inclusive.,
			Parameter(name="device_id", param_type=ParameterType.STRING, required=False),  # The ID of the device to target. If not specified, the currently active device is targeted.
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Set_Playback_Volume.method, 
                                          Set_Playback_Volume.url,
                                          Set_Playback_Volume.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Set_Playback_Volume': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Recommended_Tracks(BaseFunction):
    """Get a list of recommended tracks based on seed artists, genres, and tracks."""
    name = "Get Recommended Tracks"
    url = "https://api.spotify.com/v1/recommendations"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="seed_artists", param_type=ParameterType.STRING, required=False),  # A list of Spotify artist IDs. Up to 5 seed artists are allowed.,
			Parameter(name="seed_genres", param_type=ParameterType.STRING, required=False),  # A list of Spotify genres. Up to 5 seed genres are allowed.,
			Parameter(name="seed_tracks", param_type=ParameterType.STRING, required=False),  # A list of Spotify track IDs. Up to 5 seed tracks are allowed.,
			Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # The maximum number of recommended tracks to return (default: 20, max: 100).
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="tracks", param_type=OutputParameterType.OBJECT, is_array=True),  # A list of recommended tracks.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Recommended_Tracks.method, 
                                          Get_Recommended_Tracks.url,
                                          Get_Recommended_Tracks.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Recommended_Tracks': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Check_Users_Saved_Audiobooks(BaseFunction):
    """Checks if one or more audiobooks are already saved in the current Spotify user's library. Requires 'user-library-read' scope."""
    name = "Check User's Saved Audiobooks"
    url = "https://api.spotify.com/v1/me/audiobooks/contains"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of Spotify IDs for audiobooks. Maximum: 50 IDs. Example: '18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="result", param_type=OutputParameterType.BOOLEAN, is_array=True),  # Array of booleans indicating whether each audiobook ID is saved in the user's library.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Check_Users_Saved_Audiobooks.method, 
                                          Check_Users_Saved_Audiobooks.url,
                                          Check_Users_Saved_Audiobooks.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Check_Users_Saved_Audiobooks': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Remove_Users_Saved_Audiobooks(BaseFunction):
    """This endpoint deletes one or more audiobooks from the user's library. It requires a comma-separated list of Spotify IDs (max 50)."""
    name = "Remove User's Saved Audiobooks"
    url = "https://api.spotify.com/v1/me/audiobooks"
    args_in_url = False
    method = "DELETE"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of Spotify IDs (strings). Maximum: 50 IDs. Example: '18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ,7iHfbu1YPACw6oZPAFJtqe',
			Parameter(name="Authorization scopes", param_type=ParameterType.STRING, required=True),  # Requires scope 'user-library-modify' to manage saved content.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="status_code", param_type=OutputParameterType.STRING, is_array=False),  # HTTP status code indicating the result of the request: 200, 401, 403, 429
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Remove_Users_Saved_Audiobooks.method, 
                                          Remove_Users_Saved_Audiobooks.url,
                                          Remove_Users_Saved_Audiobooks.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Remove_Users_Saved_Audiobooks': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_New_Releases(BaseFunction):
    """Retrieves a list of new album releases featured in Spotify, with optional pagination."""
    name = "Get New Releases"
    url = "https://api.spotify.com/v1/browse/new-releases"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Maximum number of items to return. Default: 20. Range: 1-50.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # The index of the first item to return. Default: 0.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="albums", param_type=OutputParameterType.OBJECT, is_array=True),  # A paged set of albums with metadata such as href, limit, next, offset, previous, total, and items.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_New_Releases.method, 
                                          Get_New_Releases.url,
                                          Get_New_Releases.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_New_Releases': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Recommendations(BaseFunction):
    """Returns a set of recommended tracks based on seed entities and tunable track attributes."""
    name = "Get Recommendations"
    url = "https://api.spotify.com/v1/recommendations"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # The target size of the list of recommended tracks. Default is 20. Range: 1 - 100. Example: limit=10.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # A country code as per ISO 3166-1 alpha-2. Determines the market for content availability. Example: market=ES.,
			Parameter(name="seed_artists", param_type=ParameterType.STRING, required=False),  # Comma-separated list of Spotify IDs for seed artists. Up to 5 seed values. Used if seed_genres and seed_tracks are not set. Example: seed_artists=4NHQUGzhtTLFvgF5SZesLK.,
			Parameter(name="seed_genres", param_type=ParameterType.STRING, required=False),  # Comma-separated list of genres from available genre seeds. Up to 5 seed values. Used if seed_artists and seed_tracks are not set. Example: seed_genres=classical,country.,
			Parameter(name="seed_tracks", param_type=ParameterType.STRING, required=False),  # Comma-separated list of Spotify IDs for seed tracks. Up to 5 seed values. Used if seed_artists and seed_genres are not set. Example: seed_tracks=0c6xIDDpzE81m2q797ordA.,
			Parameter(name="min_acousticness", param_type=ParameterType.FLOAT, required=False),  # Minimum acousticness of tracks. Range: 0 - 1.,
			Parameter(name="max_acousticness", param_type=ParameterType.FLOAT, required=False),  # Maximum acousticness of tracks. Range: 0 - 1.,
			Parameter(name="target_acousticness", param_type=ParameterType.FLOAT, required=False),  # Target acousticness of tracks. Range: 0 - 1.,
			Parameter(name="min_danceability", param_type=ParameterType.FLOAT, required=False),  # Minimum danceability. Range: 0 - 1.,
			Parameter(name="max_danceability", param_type=ParameterType.FLOAT, required=False),  # Maximum danceability. Range: 0 - 1.,
			Parameter(name="target_danceability", param_type=ParameterType.FLOAT, required=False),  # Target danceability. Range: 0 - 1.,
			Parameter(name="min_duration_ms", param_type=ParameterType.INTEGER, required=False),  # Minimum duration in milliseconds.,
			Parameter(name="max_duration_ms", param_type=ParameterType.INTEGER, required=False),  # Maximum duration in milliseconds.,
			Parameter(name="target_duration_ms", param_type=ParameterType.INTEGER, required=False),  # Target duration in milliseconds.,
			Parameter(name="min_energy", param_type=ParameterType.FLOAT, required=False),  # Minimum energy. Range: 0 - 1.,
			Parameter(name="max_energy", param_type=ParameterType.FLOAT, required=False),  # Maximum energy. Range: 0 - 1.,
			Parameter(name="target_energy", param_type=ParameterType.FLOAT, required=False),  # Target energy. Range: 0 - 1.,
			Parameter(name="min_instrumentalness", param_type=ParameterType.FLOAT, required=False),  # Minimum instrumentalness. Range: 0 - 1.,
			Parameter(name="max_instrumentalness", param_type=ParameterType.FLOAT, required=False),  # Maximum instrumentalness. Range: 0 - 1.,
			Parameter(name="target_instrumentalness", param_type=ParameterType.FLOAT, required=False),  # Target instrumentalness. Range: 0 - 1.,
			Parameter(name="min_key", param_type=ParameterType.INTEGER, required=False),  # Minimum key. Range: 0 - 11.,
			Parameter(name="max_key", param_type=ParameterType.INTEGER, required=False),  # Maximum key. Range: 0 - 11.,
			Parameter(name="target_key", param_type=ParameterType.INTEGER, required=False),  # Target key. Range: 0 - 11.,
			Parameter(name="min_liveness", param_type=ParameterType.FLOAT, required=False),  # Minimum liveness. Range: 0 - 1.,
			Parameter(name="max_liveness", param_type=ParameterType.FLOAT, required=False),  # Maximum liveness. Range: 0 - 1.,
			Parameter(name="target_liveness", param_type=ParameterType.FLOAT, required=False),  # Target liveness. Range: 0 - 1.,
			Parameter(name="min_loudness", param_type=ParameterType.FLOAT, required=False),  # Minimum loudness in decibels.,
			Parameter(name="max_loudness", param_type=ParameterType.FLOAT, required=False),  # Maximum loudness in decibels.,
			Parameter(name="target_loudness", param_type=ParameterType.FLOAT, required=False),  # Target loudness in decibels.,
			Parameter(name="min_mode", param_type=ParameterType.INTEGER, required=False),  # Minimum mode (0 or 1).,
			Parameter(name="max_mode", param_type=ParameterType.INTEGER, required=False),  # Maximum mode (0 or 1).,
			Parameter(name="target_mode", param_type=ParameterType.INTEGER, required=False),  # Target mode (0 or 1).,
			Parameter(name="min_popularity", param_type=ParameterType.INTEGER, required=False),  # Minimum popularity (0-100).,
			Parameter(name="max_popularity", param_type=ParameterType.INTEGER, required=False),  # Maximum popularity (0-100).,
			Parameter(name="target_popularity", param_type=ParameterType.INTEGER, required=False),  # Target popularity (0-100).,
			Parameter(name="min_speechiness", param_type=ParameterType.FLOAT, required=False),  # Minimum speechiness. Range: 0 - 1.,
			Parameter(name="max_speechiness", param_type=ParameterType.FLOAT, required=False),  # Maximum speechiness. Range: 0 - 1.,
			Parameter(name="target_speechiness", param_type=ParameterType.FLOAT, required=False),  # Target speechiness. Range: 0 - 1.,
			Parameter(name="min_tempo", param_type=ParameterType.FLOAT, required=False),  # Minimum tempo in BPM.,
			Parameter(name="max_tempo", param_type=ParameterType.FLOAT, required=False),  # Maximum tempo in BPM.,
			Parameter(name="target_tempo", param_type=ParameterType.FLOAT, required=False),  # Target tempo in BPM.,
			Parameter(name="min_time_signature", param_type=ParameterType.INTEGER, required=False),  # Minimum time signature (1-11).,
			Parameter(name="max_time_signature", param_type=ParameterType.INTEGER, required=False),  # Maximum time signature (1-11).,
			Parameter(name="target_time_signature", param_type=ParameterType.INTEGER, required=False),  # Target time signature (1-11).,
			Parameter(name="min_valence", param_type=ParameterType.FLOAT, required=False),  # Minimum valence. Range: 0 - 1.,
			Parameter(name="max_valence", param_type=ParameterType.FLOAT, required=False),  # Maximum valence. Range: 0 - 1.,
			Parameter(name="target_valence", param_type=ParameterType.FLOAT, required=False),  # Target valence. Range: 0 - 1.
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Recommendations.method, 
                                          Get_Recommendations.url,
                                          Get_Recommendations.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Recommendations': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Display_your_Spotify_profile_data_in_a_web_app(BaseFunction):
    """Provides a schema to describe user profile data for web app display."""
    name = "Display your Spotify profile data in a web app"
    url = "https://developer.spotify.com/documentation/web-api/howtos/web-app-profile"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="profile", param_type=OutputParameterType.OBJECT, required=True),  # User profile data with fields: display_name, email, id, uri, href, images, external_urls, followers, product, type, uri.
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Display_your_Spotify_profile_data_in_a_web_app.method, 
                                          Display_your_Spotify_profile_data_in_a_web_app.url,
                                          Display_your_Spotify_profile_data_in_a_web_app.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Display_your_Spotify_profile_data_in_a_web_app': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Check_Users_Saved_Albums(BaseFunction):
    """Checks whether one or more albums are already saved in the user's library."""
    name = "Check User's Saved Albums"
    url = "https://api.spotify.com/v1/me/albums/contains"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # Comma-separated list of Spotify album IDs. Max 20. Example: ids=382ObEPsp2rxGrnsizN5TX,1A2GTWGtFfWp7KSQTwWOyo,2noRn2Aes5aoNVsU6iWThc.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="array", param_type=OutputParameterType.BOOLEAN, is_array=True),  # Array of booleans indicating if albums are saved (true) or not (false) in the current user's library. Example: [false,true].
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Check_Users_Saved_Albums.method, 
                                          Check_Users_Saved_Albums.url,
                                          Check_Users_Saved_Albums.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Check_Users_Saved_Albums': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Multiple_Shows(BaseFunction):
    """Retrieve information about multiple shows using their Spotify IDs."""
    name = "Get Multiple Shows"
    url = "https://api.spotify.com/v1/shows"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="market", param_type=ParameterType.STRING, required=False),  # An ISO 3166-1 alpha-2 country code. If specified, only content available in this market will be returned. If a user access token is provided, the user account's country will take priority. Example: 'ES'
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="shows", param_type=OutputParameterType.OBJECT, is_array=True),  # An array of show objects with their details.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Multiple_Shows.method, 
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
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the artist. Example: '0TnOYISbd1XYRBk9myaseg'.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # An ISO 3166-1 alpha-2 country code. The top tracks returned will be relevant to this market. If none is provided and the user has a valid access token, the user's country will be used. Example: 'ES'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="tracks", param_type=OutputParameterType.OBJECT, is_array=True),  # An array of track objects representing the artist's top tracks in the specified market.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Artists_Top_Tracks.method, 
                                          Get_Artists_Top_Tracks.url,
                                          Get_Artists_Top_Tracks.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Artists_Top_Tracks': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Change_Playlist_Details(BaseFunction):
    """Update the name, public/private status, collaborative status, or description of a playlist."""
    name = "Change Playlist Details"
    url = "https://api.spotify.com/v1/playlists/{playlist_id}"
    args_in_url = True
    method = "PUT"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="playlist_id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the playlist to update. Example: '3cEYpjA9oz9GiPac4AsH4n'.,
			Parameter(name="name", param_type=ParameterType.STRING, required=False),  # The new name for the playlist, e.g., 'My New Playlist Title'.,
			Parameter(name="public", param_type=ParameterType.BOOLEAN, required=False),  # Whether the playlist should be public (true), private (false), or leave unchanged (null).,
			Parameter(name="collaborative", param_type=ParameterType.BOOLEAN, required=False),  # Set to true to make the playlist collaborative, allowing others to modify it. Note: Only applicable to non-public playlists.,
			Parameter(name="description", param_type=ParameterType.STRING, required=False),  # A description for the playlist as displayed in Spotify clients and the Web API.
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Change_Playlist_Details.method, 
                                          Change_Playlist_Details.url,
                                          Change_Playlist_Details.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Change_Playlist_Details': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Follow_Playlist(BaseFunction):
    """Adds the current user as a follower of a playlist."""
    name = "Follow Playlist"
    url = "https://api.spotify.com/v1/playlists/{playlist_id}/followers"
    args_in_url = True
    method = "PUT"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="playlist_id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the playlist. Example: '3cEYpjA9oz9GiPac4AsH4n'.,
			Parameter(name="public", param_type=ParameterType.BOOLEAN, required=False),  # Defaults to true. If true, the playlist will be included in the user's public playlists. If false, it remains private.
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Follow_Playlist.method, 
                                          Follow_Playlist.url,
                                          Follow_Playlist.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Follow_Playlist': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Artists_Albums(BaseFunction):
    """Retrieves Spotify catalog information about an artist's albums."""
    name = "Get Artist's Albums"
    url = "https://api.spotify.com/v1/artists/{id}/albums"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the artist. Example: '0TnOYISbd1XYRBk9myaseg'.,
			Parameter(name="include_groups", param_type=ParameterType.STRING, required=False),  # Comma-separated list of album types to filter response. Valid values: 'album', 'single', 'appears_on', 'compilation'. For example: 'include_groups=single,appears_on'.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # ISO 3166-1 alpha-2 country code. Limits the data to the specified market.,
			Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Maximum number of items to return. Default: 20. Range: 1-50.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # Index of the first item to return. Default: 0.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the Web API endpoint returning the full result.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # Maximum number of items in the response.,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=False),  # URL to the next page of results, or null if none.,
			OutputParameter(name="offset", param_type=OutputParameterType.INTEGER, is_array=False),  # The offset of the returned items.,
			OutputParameter(name="previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to the previous page of results, or null if none.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of albums available.,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of album objects.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Artists_Albums.method, 
                                          Get_Artists_Albums.url,
                                          Get_Artists_Albums.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Artists_Albums': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Remove_Users_Saved_Albums(BaseFunction):
    """Removes one or more albums from the current user's 'Your Music' library."""
    name = "Remove User's Saved Albums"
    url = "https://api.spotify.com/v1/me/albums"
    args_in_url = False
    method = "DELETE"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of Spotify IDs for the albums. Max: 20 IDs. Example: '382ObEPsp2rxGrnsizN5TX,1A2GTWGtFfWp7KSQTwWOyo'.,
			Parameter(name="ids_array", param_type=ParameterType.STRING, required=False),  # A JSON array of Spotify IDs. Max: 50 IDs. Example: ['4iV5W9uYEdYUVa79Axb7Rh', '1301WleyT98MSxVHPZCA6M']. Note: if 'ids' parameter is present, this field is ignored.
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Remove_Users_Saved_Albums.method, 
                                          Remove_Users_Saved_Albums.url,
                                          Remove_Users_Saved_Albums.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Remove_Users_Saved_Albums': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Migration_from_Implicit_Grant_to_Authorization_Code_with_PKCE(BaseFunction):
    """Guide to migrate from Implicit Grant Flow to Authorization Code with PKCE flow, including code generation, handling redirects, and exchanging authorization codes for tokens."""
    name = "Migration from Implicit Grant to Authorization Code with PKCE"
    url = "https://developer.spotify.com/documentation/web-api/tutorials/migration-implicit-auth-code"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Migration_from_Implicit_Grant_to_Authorization_Code_with_PKCE.method, 
                                          Migration_from_Implicit_Grant_to_Authorization_Code_with_PKCE.url,
                                          Migration_from_Implicit_Grant_to_Authorization_Code_with_PKCE.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Migration_from_Implicit_Grant_to_Authorization_Code_with_PKCE': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Check_if_current_user_follows_artists_or_users(BaseFunction):
    """Checks whether the current user is following one or more artists or Spotify users."""
    name = "Check if current user follows artists or users"
    url = "https://api.spotify.com/v1/me/following/contains"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="type", param_type=ParameterType.STRING, required=True),  # The ID type: either 'artist' or 'user'. Allowed values: 'artist', 'user'.,
			Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of Spotify IDs to check, maximum of 50 IDs. Example: '2CIMQHirSU0MQqyYHq0eOx,57dN52uHvrHOxijzpIgu3E'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="response", param_type=OutputParameterType.BOOLEAN, is_array=True),  # Array of booleans indicating follow status for each ID. Example: [false,true].
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Check_if_current_user_follows_artists_or_users.method, 
                                          Check_if_current_user_follows_artists_or_users.url,
                                          Check_if_current_user_follows_artists_or_users.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Check_if_current_user_follows_artists_or_users': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Skip_to_previous_track_in_users_playback(BaseFunction):
    """Skips to the previous track in the user's playback on a specified device."""
    name = "Skip to previous track in user's playback"
    url = "https://api.spotify.com/v1/me/player/previous"
    args_in_url = False
    method = "PUT"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="device_id", param_type=ParameterType.STRING, required=False),  # The ID of the device to target. If not supplied, the user's currently active device is used. Example: '0d1841b0976bae2a3a310dd74c0f3df354899bc8'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="status_code", param_type=OutputParameterType.INTEGER, is_array=False),  # HTTP status codes: 204 (No Content), 401, 403, 429.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Skip_to_previous_track_in_users_playback.method, 
                                          Skip_to_previous_track_in_users_playback.url,
                                          Skip_to_previous_track_in_users_playback.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Skip_to_previous_track_in_users_playback': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Transfer_playback_to_a_new_device(BaseFunction):
    """Transfers playback to a new device and optionally begins playback."""
    name = "Transfer playback to a new device"
    url = "https://api.spotify.com/v1/me/player"
    args_in_url = False
    method = "PUT"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="device_ids", param_type=ParameterType.STRING, required=True),  # An array of device IDs on which playback should be transferred. Although an array is supported, only a single device ID is currently supported. Example: ['74ASZWbe4lXaubB36ztrGX'].,
			Parameter(name="play", param_type=ParameterType.BOOLEAN, required=False),  # Ensures playback begins on the new device if true. Default is false or not provided, maintaining current playback state.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="status_code", param_type=OutputParameterType.INTEGER, is_array=False),  # HTTP status codes: 204 (No Content), 401, 403, 429.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Transfer_playback_to_a_new_device.method, 
                                          Transfer_playback_to_a_new_device.url,
                                          Transfer_playback_to_a_new_device.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Transfer_playback_to_a_new_device': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Pause_playback_on_users_account(BaseFunction):
    """Pauses playback on the user's active device."""
    name = "Pause playback on user's account"
    url = "https://api.spotify.com/v1/me/player/pause"
    args_in_url = False
    method = "PUT"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="device_id", param_type=ParameterType.STRING, required=False),  # The ID of the device on which to pause playback. If not supplied, the currently active device is used. Example: '0d1841b0976bae2a3a310dd74c0f3df354899bc8'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="status_code", param_type=OutputParameterType.INTEGER, is_array=False),  # HTTP status codes: 204 (No Content), 401, 403, 429.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Pause_playback_on_users_account.method, 
                                          Pause_playback_on_users_account.url,
                                          Pause_playback_on_users_account.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Pause_playback_on_users_account': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_a_Users_Available_Devices(BaseFunction):
    """Retrieve the current user's available Spotify Connect devices. Requires 'user-read-playback-state' scope."""
    name = "Get a User's Available Devices"
    url = "https://api.spotify.com/v1/me/player/devices"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="devices", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of DeviceObject, containing information about each device.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_a_Users_Available_Devices.method, 
                                          Get_a_Users_Available_Devices.url,
                                          Get_a_Users_Available_Devices.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_a_Users_Available_Devices': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Artists_Related_Artists(BaseFunction):
    """Fetch artists related to the given artist ID. Requires 'artist-read-related-artists' scope."""
    name = "Get Artist's Related Artists"
    url = "https://api.spotify.com/v1/artists/{id}/related-artists"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the artist.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="artists", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of ArtistObject, representing related artists.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Artists_Related_Artists.method, 
                                          Get_Artists_Related_Artists.url,
                                          Get_Artists_Related_Artists.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Artists_Related_Artists': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Several_Tracks_Audio_Features(BaseFunction):
    """Retrieve audio features for multiple tracks by their Spotify IDs. Requires 'audio-read' scope."""
    name = "Get Several Tracks' Audio Features"
    url = "https://api.spotify.com/v1/audio-features"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # Comma-separated list of Spotify track IDs; maximum 100 IDs.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="audio_features", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of AudioFeaturesObject, each representing audio features for a track.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Several_Tracks_Audio_Features.method, 
                                          Get_Several_Tracks_Audio_Features.url,
                                          Get_Several_Tracks_Audio_Features.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Several_Tracks_Audio_Features': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Create_a_Playlist_for_a_User(BaseFunction):
    """Create a new playlist under the specified user. Requires 'playlist-modify-public' or 'playlist-modify-private' scope."""
    name = "Create a Playlist for a User"
    url = "https://api.spotify.com/v1/users/{user_id}/playlists"
    args_in_url = True
    method = "PUT"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="user_id", param_type=ParameterType.STRING, required=True),  # The Spotify User ID.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="collaborative", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Indicates if the playlist is collaborative.,
			OutputParameter(name="description", param_type=OutputParameterType.STRING, is_array=False),  # The playlist description.,
			OutputParameter(name="external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # Known external URLs for this playlist.,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the Web API endpoint for full playlist details.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # Spotify ID for the new playlist.,
			OutputParameter(name="images", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of ImageObject for playlist images.,
			OutputParameter(name="name", param_type=OutputParameterType.STRING, is_array=False),  # The name of the playlist.,
			OutputParameter(name="owner", param_type=OutputParameterType.OBJECT, is_array=False),  # User who owns the playlist.,
			OutputParameter(name="public", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Indicates if the playlist is public.,
			OutputParameter(name="snapshot_id", param_type=OutputParameterType.STRING, is_array=False),  # Version identifier for the playlist.,
			OutputParameter(name="tracks", param_type=OutputParameterType.OBJECT, is_array=False),  # Tracks object of the playlist.,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI for the playlist.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Create_a_Playlist_for_a_User.method, 
                                          Create_a_Playlist_for_a_User.url,
                                          Create_a_Playlist_for_a_User.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Create_a_Playlist_for_a_User': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Current_Users_Saved_Albums(BaseFunction):
    """Allows the client to save one or more albums to the current user's 'Your Music' library. Requires 'user-library-modify' scope."""
    name = "Get Current User's Saved Albums"
    url = "https://api.spotify.com/v1/me/albums"
    args_in_url = False
    method = "PUT"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of Spotify album IDs. Maximum: 20 IDs. Example: '382ObEPsp2rxGrnsizN5TX,1A2GTWGtFfWp7KSQTwWOyo,2noRn2Aes5aoNVsU6iWThc'.,
			Parameter(name="ids_array", param_type=OutputParameterType.OBJECT, required=False),  # A JSON array of Spotify album IDs, e.g., ['4iV5W9uYEdYUVa79Axb7Rh','1301WleyT98MSxVHPZCA6M']. A maximum of 50 IDs can be specified.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="status_code", param_type=OutputParameterType.INTEGER, is_array=False),  # HTTP response status code indicating success or failure.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Current_Users_Saved_Albums.method, 
                                          Get_Current_Users_Saved_Albums.url,
                                          Get_Current_Users_Saved_Albums.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Current_Users_Saved_Albums': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Artist_by_ID(BaseFunction):
    """Retrieves detailed information about an artist by Spotify ID. Requires 'artist-read' scope."""
    name = "Get Artist by ID"
    url = "https://api.spotify.com/v1/artists/{id}"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the artist. Example: '0TnOYISbd1XYRBk9myaseg'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # Known external URLs for the artist, including 'spotify' link.,
			OutputParameter(name="followers", param_type=OutputParameterType.OBJECT, is_array=False),  # Information about the artist's followers, including total count.,
			OutputParameter(name="genres", param_type=OutputParameterType.STRING, is_array=True),  # List of genres associated with the artist, e.g., ['Prog rock','Grunge'].,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the Web API endpoint providing full details of the artist.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # The Spotify ID of the artist.,
			OutputParameter(name="images", param_type=OutputParameterType.OBJECT, is_array=True),  # Images of the artist in various sizes.,
			OutputParameter(name="name", param_type=OutputParameterType.STRING, is_array=False),  # Name of the artist.,
			OutputParameter(name="popularity", param_type=OutputParameterType.INTEGER, is_array=False),  # Popularity score between 0 and 100.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, always 'artist'.,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI of the artist.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Artist_by_ID.method, 
                                          Get_Artist_by_ID.url,
                                          Get_Artist_by_ID.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Artist_by_ID': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Playlist_details(BaseFunction):
    """Retrieves detailed information about a specific playlist by its Spotify ID. Requires appropriate scopes."""
    name = "Get Playlist details"
    url = "https://api.spotify.com/v1/playlists/{playlist_id}"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="playlist_id", param_type=ParameterType.STRING, required=True),  # The Spotify ID for the playlist.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="collaborative", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Whether the playlist is collaborative.,
			OutputParameter(name="description", param_type=OutputParameterType.STRING, is_array=False),  # The playlist description.,
			OutputParameter(name="followers", param_type=OutputParameterType.OBJECT, is_array=False),  # Information about the followers of the playlist.,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the Web API endpoint for the playlist.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # The Spotify ID of the playlist.,
			OutputParameter(name="images", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of images associated with the playlist.,
			OutputParameter(name="name", param_type=OutputParameterType.STRING, is_array=False),  # Name of the playlist.,
			OutputParameter(name="owner", param_type=OutputParameterType.OBJECT, is_array=False),  # User who owns the playlist.,
			OutputParameter(name="public", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Whether the playlist is public.,
			OutputParameter(name="snapshot_id", param_type=OutputParameterType.STRING, is_array=False),  # Snapshot ID of the playlist for version control.,
			OutputParameter(name="tracks", param_type=OutputParameterType.OBJECT, is_array=False),  # Tracks contained in the playlist.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, always 'playlist'.,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI of the playlist.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Playlist_details.method, 
                                          Get_Playlist_details.url,
                                          Get_Playlist_details.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Playlist_details': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Set_Repeat_Mode_on_Users_Playback(BaseFunction):
    """Sets the repeat mode for the user's playback. Note: This API requires the 'user-modify-playback-state' scope. It only works for users with Spotify Premium. The order of execution is not guaranteed when used with other Player API endpoints."""
    name = "Set Repeat Mode on User's Playback"
    url = "https://api.spotify.com/v1/me/player/repeat"
    args_in_url = False
    method = "PUT"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="state", param_type=ParameterType.STRING, required=True),  # The repeat mode. Must be one of: 'track', 'context', or 'off'. 'track' will repeat the current track, 'context' will repeat the current context, and 'off' will turn repeat off.,
			Parameter(name="device_id", param_type=ParameterType.STRING, required=False),  # The ID of the device this command is targeting. If not provided, the user's currently active device will be targeted. Example: '0d1841b0976bae2a3a310dd74c0f3df354899bc8'.
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Set_Repeat_Mode_on_Users_Playback.method, 
                                          Set_Repeat_Mode_on_Users_Playback.url,
                                          Set_Repeat_Mode_on_Users_Playback.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Set_Repeat_Mode_on_Users_Playback': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_the_Users_Queue(BaseFunction):
    """Retrieves the list of objects that make up the user's playback queue. This API requires the 'user-read-playback-state' scope. It only works for users with Spotify Premium. The response includes a 'currently_playing' object (which can be null) and a 'queue' array containing track or episode objects."""
    name = "Get the User's Queue"
    url = "https://api.spotify.com/v1/me/player/queue"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_the_Users_Queue.method, 
                                          Get_the_Users_Queue.url,
                                          Get_the_Users_Queue.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_the_Users_Queue': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Available_Markets(BaseFunction):
    """Returns a list of countries/markets where Spotify is available. This endpoint requires OAuth 2.0 authentication."""
    name = "Get Available Markets"
    url = "https://api.spotify.com/v1/markets"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="markets", param_type=OutputParameterType.STRING, is_array=True),  # An array of country codes (ISO 3166-1 alpha-2) where Spotify is available. Example: ['CA', 'BR', 'IT'].
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Available_Markets.method, 
                                          Get_Available_Markets.url,
                                          Get_Available_Markets.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Available_Markets': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_a_Category(BaseFunction):
    """Retrieve detailed information about a specific Spotify category by its ID."""
    name = "Get a Category"
    url = "https://api.spotify.com/v1/browse/categories/{category_id}"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="category_id", param_type=ParameterType.STRING, required=True),  # The Spotify category ID for the category. Example: 'dinner'.,
			Parameter(name="locale", param_type=ParameterType.STRING, required=False),  # The desired language, consisting of an ISO 639-1 language code and an ISO 3166-1 alpha-2 country code, joined by an underscore. For example: 'sv_SE'. Provide this parameter to get category strings in a particular language. If not supplied or unavailable, defaults to English.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # A link to the Web API endpoint returning full details of the category.,
			OutputParameter(name="icons", param_type=OutputParameterType.OBJECT, is_array=True),  # The category icon in various sizes.,
			OutputParameter(name="url", param_type=OutputParameterType.STRING, is_array=False),  # The source URL of the image.,
			OutputParameter(name="height", param_type=OutputParameterType.INTEGER, is_array=False),  # The image height in pixels. Nullable.,
			OutputParameter(name="width", param_type=OutputParameterType.INTEGER, is_array=False),  # The image width in pixels. Nullable.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # The Spotify category ID.,
			OutputParameter(name="name", param_type=OutputParameterType.STRING, is_array=False),  # The name of the category.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_a_Category.method, 
                                          Get_a_Category.url,
                                          Get_a_Category.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_a_Category': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Show_Episodes(BaseFunction):
    """Retrieve a list of episodes for a show, with optional pagination."""
    name = "Get Show Episodes"
    url = "https://api.spotify.com/v1/shows/{id}/episodes"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.STRING, required=True),  # The Spotify ID for the show. Example: '38bS44xjbVVZ3No3ByF1dJ'.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # An ISO 3166-1 alpha-2 country code to specify the market. If a user access token is provided, the user's country will take priority. If neither the market nor user country are provided, content is considered unavailable.,
			Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Maximum number of items to return. Default: 20. Range: 1-50.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # Index of the first item to return. Default: 0.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the full result of the request.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # Maximum number of items in the response.,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=False),  # URL to the next page of items. Null if none.,
			OutputParameter(name="offset", param_type=OutputParameterType.INTEGER, is_array=False),  # The offset of the returned items.,
			OutputParameter(name="previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to the previous page of items. Null if none.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of items available.,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of episode objects.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Show_Episodes.method, 
                                          Get_Show_Episodes.url,
                                          Get_Show_Episodes.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Show_Episodes': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Seek_to_Position_in_Currently_Playing_Track(BaseFunction):
    """Seek to a position in the currently playing track for a user who has Spotify Premium."""
    name = "Seek to Position in Currently Playing Track"
    url = "https://api.spotify.com/v1/me/player/seek?position_ms={position_ms}&device_id={device_id}"
    args_in_url = True
    method = "PUT"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="position_ms", param_type=ParameterType.INTEGER, required=True),  # The position in milliseconds to seek to. Must be positive. If greater than track length, plays next track.,
			Parameter(name="device_id", param_type=ParameterType.STRING, required=False),  # Target device ID. If not supplied, the user's currently active device is targeted.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="response_code", param_type=OutputParameterType.INTEGER, is_array=False),  # HTTP response code indicating success or error.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Seek_to_Position_in_Currently_Playing_Track.method, 
                                          Seek_to_Position_in_Currently_Playing_Track.url,
                                          Seek_to_Position_in_Currently_Playing_Track.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Seek_to_Position_in_Currently_Playing_Track': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_the_Users_Currently_Playing_Track(BaseFunction):
    """Retrieve the current playback state of the user."""
    name = "Get the Users' Currently Playing Track"
    url = "https://api.spotify.com/v1/me/player/currently-playing"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="market", param_type=ParameterType.STRING, required=False),  # An ISO 3166-1 alpha-2 country code. If specified, only content available in this market will be returned. If omitted, the user's country from account settings takes precedence. Example: 'ES'.,
			Parameter(name="additional_types", param_type=ParameterType.STRING, required=False),  # A comma-separated list of item types supported besides 'track'. Valid values: 'track', 'episode'. Note: this parameter may be deprecated in future.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="device", param_type=OutputParameterType.OBJECT, is_array=False),  # The device currently active.,
			OutputParameter(name="device.id", param_type=OutputParameterType.STRING, is_array=False),  # The device ID. Nullable, unique, but not guaranteed. Cache should be refreshed periodically.,
			OutputParameter(name="device.is_active", param_type=OutputParameterType.BOOLEAN, is_array=False),  # True if this device is the current active device.,
			OutputParameter(name="device.is_private_session", param_type=OutputParameterType.BOOLEAN, is_array=False),  # True if the device is in a private session.,
			OutputParameter(name="device.is_restricted", param_type=OutputParameterType.BOOLEAN, is_array=False),  # True if control of this device is restricted; no Web API commands will be accepted.,
			OutputParameter(name="device.name", param_type=OutputParameterType.STRING, is_array=False),  # Human-readable device name, configurable by user or default.,
			OutputParameter(name="device.type", param_type=OutputParameterType.STRING, is_array=False),  # Device type, e.g., 'computer', 'smartphone', 'speaker'.,
			OutputParameter(name="device.volume_percent", param_type=OutputParameterType.INTEGER, is_array=False),  # Current volume in percent (0-100). Nullable.,
			OutputParameter(name="device.supports_volume", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Indicates if this device can be used to set volume.,
			OutputParameter(name="repeat_state", param_type=OutputParameterType.STRING, is_array=False),  # Playback repeat state. Allowed values: 'off', 'track', 'context'.,
			OutputParameter(name="shuffle_state", param_type=OutputParameterType.BOOLEAN, is_array=False),  # True if shuffle is enabled.,
			OutputParameter(name="context", param_type=OutputParameterType.OBJECT, is_array=False),  # The context in which playback is occurring.,
			OutputParameter(name="context.type", param_type=OutputParameterType.STRING, is_array=False),  # Type of context, e.g., 'artist', 'playlist', 'album', 'show'.,
			OutputParameter(name="context.href", param_type=OutputParameterType.STRING, is_array=False),  # A link to the Web API endpoint providing details of the context.,
			OutputParameter(name="context.external_urls.spotify", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URL for the context.,
			OutputParameter(name="context.uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI for the context.,
			OutputParameter(name="timestamp", param_type=OutputParameterType.INTEGER, is_array=False),  # Unix Millisecond timestamp when playback status was last changed.,
			OutputParameter(name="progress_ms", param_type=OutputParameterType.INTEGER, is_array=False),  # Progress into the currently playing track or episode in milliseconds. Nullable.,
			OutputParameter(name="is_playing", param_type=OutputParameterType.BOOLEAN, is_array=False),  # True if something is currently playing.,
			OutputParameter(name="item", param_type=OutputParameterType.OBJECT, is_array=False),  # The currently playing track or episode. Can be null.,
			OutputParameter(name="item.album", param_type=OutputParameterType.OBJECT, is_array=False),  # Album on which the track appears.,
			OutputParameter(name="item.album.album_type", param_type=OutputParameterType.STRING, is_array=False),  # Type of album. Allowed: 'album', 'single', 'chapter', 'compilation'.,
			OutputParameter(name="item.album.total_tracks", param_type=OutputParameterType.INTEGER, is_array=False),  # Number of tracks in the album.,
			OutputParameter(name="item.album.available_markets", param_type=OutputParameterType.STRING, is_array=True),  # Markets where the album/track is available. ISO 3166-1 alpha-2 codes.,
			OutputParameter(name="item.album.external_urls.spotify", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URL for the album.,
			OutputParameter(name="item.album.href", param_type=OutputParameterType.STRING, is_array=False),  # API endpoint for full album details.,
			OutputParameter(name="item.album.id", param_type=OutputParameterType.STRING, is_array=False),  # Spotify ID for the album.,
			OutputParameter(name="item.album.images", param_type=OutputParameterType.OBJECT, is_array=True),  # Cover art images.,
			OutputParameter(name="item.album.images.url", param_type=OutputParameterType.STRING, is_array=False),  # Source URL of the image.,
			OutputParameter(name="item.album.images.height", param_type=OutputParameterType.INTEGER, is_array=False),  # Image height in pixels. Nullable.,
			OutputParameter(name="item.album.images.width", param_type=OutputParameterType.INTEGER, is_array=False),  # Image width in pixels. Nullable.,
			OutputParameter(name="item.album.name", param_type=OutputParameterType.STRING, is_array=False),  # Album name.,
			OutputParameter(name="item.album.release_date", param_type=OutputParameterType.STRING, is_array=False),  # First release date of the album. Format varies, e.g., '1981-12'.,
			OutputParameter(name="item.album.release_date_precision", param_type=OutputParameterType.STRING, is_array=False),  # Precision of release date. Allowed: 'year', 'month', 'day'.,
			OutputParameter(name="item.album.restrictions", param_type=OutputParameterType.OBJECT, is_array=False),  # Content restrictions, if any.,
			OutputParameter(name="item.album.restrictions.reason", param_type=OutputParameterType.STRING, is_array=False),  # Reason for restriction. Allowed: 'market', 'product', 'explicit'.,
			OutputParameter(name="item.album.type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, e.g., 'album'.,
			OutputParameter(name="item.album.uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI for the album.,
			OutputParameter(name="item.artists", param_type=OutputParameterType.OBJECT, is_array=True),  # Artists of the track or album.,
			OutputParameter(name="item.artists.external_urls.spotify", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URL for the artist.,
			OutputParameter(name="item.artists.href", param_type=OutputParameterType.STRING, is_array=False),  # API endpoint for artist details.,
			OutputParameter(name="item.artists.id", param_type=OutputParameterType.STRING, is_array=False),  # Spotify ID for the artist.,
			OutputParameter(name="item.artists.name", param_type=OutputParameterType.STRING, is_array=False),  # Artist name.,
			OutputParameter(name="item.artists.type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, e.g., 'artist'.,
			OutputParameter(name="item.artists.uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI for the artist.,
			OutputParameter(name="item.available_markets", param_type=OutputParameterType.STRING, is_array=True),  # Markets where the track is available. ISO 3166-1 alpha-2.,
			OutputParameter(name="item.disc_number", param_type=OutputParameterType.INTEGER, is_array=False),  # Disc number, usually 1 unless multi-disc album.,
			OutputParameter(name="item.duration_ms", param_type=OutputParameterType.INTEGER, is_array=False),  # Track length in milliseconds.,
			OutputParameter(name="item.explicit", param_type=OutputParameterType.BOOLEAN, is_array=False),  # True if explicit lyrics.,
			OutputParameter(name="item.external_ids", param_type=OutputParameterType.OBJECT, is_array=False),  # External IDs for the track.,
			OutputParameter(name="item.external_ids.isrc", param_type=OutputParameterType.STRING, is_array=False),  # International Standard Recording Code.,
			OutputParameter(name="item.external_ids.ean", param_type=OutputParameterType.STRING, is_array=False),  # International Article Number.,
			OutputParameter(name="item.external_ids.upc", param_type=OutputParameterType.STRING, is_array=False),  # Universal Product Code.,
			OutputParameter(name="item.external_urls.spotify", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URL for the track.,
			OutputParameter(name="item.href", param_type=OutputParameterType.STRING, is_array=False),  # API endpoint for full track details.,
			OutputParameter(name="item.id", param_type=OutputParameterType.STRING, is_array=False),  # Spotify ID for the track.,
			OutputParameter(name="item.is_playable", param_type=OutputParameterType.BOOLEAN, is_array=False),  # True if the track is playable in current market.,
			OutputParameter(name="item.linked_from", param_type=OutputParameterType.OBJECT, is_array=False),  # Original track info if relinked.,
			OutputParameter(name="item.restrictions", param_type=OutputParameterType.OBJECT, is_array=False),  # Content restrictions.,
			OutputParameter(name="item.restrictions.reason", param_type=OutputParameterType.STRING, is_array=False),  # Restriction reason.,
			OutputParameter(name="item.name", param_type=OutputParameterType.STRING, is_array=False),  # Track name.,
			OutputParameter(name="item.popularity", param_type=OutputParameterType.INTEGER, is_array=False),  # Popularity score (0-100).,
			OutputParameter(name="item.preview_url", param_type=OutputParameterType.STRING, is_array=False),  # URL to 30s preview, nullable.,
			OutputParameter(name="item.track_number", param_type=OutputParameterType.INTEGER, is_array=False),  # Track number in album/disc.,
			OutputParameter(name="item.type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, e.g., 'track'.,
			OutputParameter(name="item.uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI for the track.,
			OutputParameter(name="item.is_local", param_type=OutputParameterType.BOOLEAN, is_array=False),  # True if local file.,
			OutputParameter(name="currently_playing_type", param_type=OutputParameterType.STRING, is_array=False),  # Type of the currently playing item. Allowed: 'track', 'episode', 'ad', 'unknown'.,
			OutputParameter(name="actions", param_type=OutputParameterType.OBJECT, is_array=False),  # Available playback actions.,
			OutputParameter(name="actions.interrupting_playback", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Can playback be interrupted?,
			OutputParameter(name="actions.pausing", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Can playback be paused?,
			OutputParameter(name="actions.resuming", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Can playback be resumed?,
			OutputParameter(name="actions.seeking", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Can seek operations be performed.,
			OutputParameter(name="actions.skipping_next", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Can skip to next.,
			OutputParameter(name="actions.skipping_prev", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Can skip to previous.,
			OutputParameter(name="actions.toggling_repeat_context", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Can toggle repeat context.,
			OutputParameter(name="actions.toggling_shuffle", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Can toggle shuffle.,
			OutputParameter(name="actions.toggling_repeat_track", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Can toggle repeat on track.,
			OutputParameter(name="actions.transferring_playback", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Can transfer playback.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_the_Users_Currently_Playing_Track.method, 
                                          Get_the_Users_Currently_Playing_Track.url,
                                          Get_the_Users_Currently_Playing_Track.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_the_Users_Currently_Playing_Track': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Save_Tracks_for_Current_User(BaseFunction):
    """This endpoint allows the user to save one or multiple tracks to their 'Your Music' library. The 'ids' parameter can be provided as a comma-separated string or as a JSON array of strings."""
    name = "Save Tracks for Current User"
    url = "https://api.spotify.com/v1/me/tracks"
    args_in_url = False
    method = "PUT"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of the Spotify IDs of the tracks to save. Maximum: 50 IDs. Example: '7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B',
			Parameter(name="ids", param_type=OutputParameterType.OBJECT, required=True),  # A JSON array of Spotify track IDs. Maximum 50 items. Example: ['4iV5W9uYEdYUVa79Axb7Rh', '1301WleyT98MSxVHPZCA6M'].
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Save_Tracks_for_Current_User.method, 
                                          Save_Tracks_for_Current_User.url,
                                          Save_Tracks_for_Current_User.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Save_Tracks_for_Current_User': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Skip_To_Next_Track(BaseFunction):
    """Skips to the next track in the user's current playback queue. This API only works for users with Spotify Premium. If 'device_id' is provided, the command targets that device; otherwise, the user's active device is used."""
    name = "Skip To Next Track"
    url = "https://api.spotify.com/v1/me/player/next"
    args_in_url = True
    method = "PUT"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="device_id", param_type=ParameterType.STRING, required=False),  # The ID of the device this command is targeting. If not provided, the currently active device of the user will be targeted. Example: '0d1841b0976bae2a3a310dd74c0f3df354899bc8'
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Skip_To_Next_Track.method, 
                                          Skip_To_Next_Track.url,
                                          Skip_To_Next_Track.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Skip_To_Next_Track': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_an_Audiobook(BaseFunction):
    """API endpoints related to various Spotify content, including saving tracks, skipping playback, and retrieving audiobook details, with parameters and response structures detailed for each."""
    name = "Get an Audiobook"
    url = "https://api.spotify.com/v1/audiobooks/{id}"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the audiobook. Example: '7iHfbu1YPACw6oZPAFJtqe'.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # An ISO 3166-1 alpha-2 country code to specify the market. If not provided, the market will be determined by the user token or defaults.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="authors", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of author objects for the audiobook.,
			OutputParameter(name="available_markets", param_type=OutputParameterType.STRING, is_array=True),  # List of countries where the audiobook is available, identified by ISO 3166-1 alpha-2 codes.,
			OutputParameter(name="copyrights", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of copyright objects.,
			OutputParameter(name="description", param_type=OutputParameterType.STRING, is_array=False),  # Plain text description of the audiobook.,
			OutputParameter(name="html_description", param_type=OutputParameterType.STRING, is_array=False),  # HTML formatted description of the audiobook.,
			OutputParameter(name="edition", param_type=OutputParameterType.STRING, is_array=False),  # Edition of the audiobook, e.g., 'Unabridged'.,
			OutputParameter(name="explicit", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Indicates if the audiobook has explicit content.,
			OutputParameter(name="external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # External URLs object.,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # URL to the full details of the audiobook in the Web API.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # Spotify ID of the audiobook.,
			OutputParameter(name="images", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of image objects for cover art.,
			OutputParameter(name="languages", param_type=OutputParameterType.STRING, is_array=True),  # List of ISO 639-1 language codes used in the audiobook.,
			OutputParameter(name="media_type", param_type=OutputParameterType.STRING, is_array=False),  # Media type of the audiobook.,
			OutputParameter(name="name", param_type=OutputParameterType.STRING, is_array=False),  # Name of the audiobook.,
			OutputParameter(name="narrators", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of narrator objects.,
			OutputParameter(name="publisher", param_type=OutputParameterType.STRING, is_array=False),  # Publisher of the audiobook.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # The object type, always 'audiobook'.,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI for the audiobook.,
			OutputParameter(name="total_chapters", param_type=OutputParameterType.INTEGER, is_array=False),  # Number of chapters in the audiobook.,
			OutputParameter(name="chapters", param_type=OutputParameterType.OBJECT, is_array=False),  # Object containing pagination and items for chapters.,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the API endpoint returning full chapter results.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # Maximum number of chapters returned per page.,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=True),  # URL to next page of results, null if none.,
			OutputParameter(name="offset", param_type=OutputParameterType.INTEGER, is_array=False),  # Offset of the current page.,
			OutputParameter(name="previous", param_type=OutputParameterType.STRING, is_array=True),  # URL to previous page, null if none.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of chapters available.,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of chapter objects.,
			OutputParameter(name="audio_preview_url", param_type=OutputParameterType.STRING, is_array=False),  # URL to a 30 second preview MP3 of the chapter, nullable.,
			OutputParameter(name="available_markets", param_type=OutputParameterType.STRING, is_array=True),  # Countries where the chapter can be played.,
			OutputParameter(name="chapter_number", param_type=OutputParameterType.INTEGER, is_array=False),  # The number of the chapter.,
			OutputParameter(name="description", param_type=OutputParameterType.STRING, is_array=False),  # Description of the chapter.,
			OutputParameter(name="html_description", param_type=OutputParameterType.STRING, is_array=False),  # HTML formatted description of the chapter.,
			OutputParameter(name="duration_ms", param_type=OutputParameterType.INTEGER, is_array=False),  # Length of the chapter in milliseconds.,
			OutputParameter(name="explicit", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Whether the chapter has explicit content.,
			OutputParameter(name="external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # External URLs object.,
			OutputParameter(name="spotify", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URL for the chapter.,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the Web API endpoint for this chapter.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # Spotify ID for the chapter.,
			OutputParameter(name="images", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of images for chapter cover art.,
			OutputParameter(name="url", param_type=OutputParameterType.STRING, is_array=False),  # Image URL.,
			OutputParameter(name="height", param_type=OutputParameterType.INTEGER, is_array=True),  # Height of the image in pixels, nullable.,
			OutputParameter(name="width", param_type=OutputParameterType.INTEGER, is_array=True),  # Width of the image in pixels, nullable.,
			OutputParameter(name="is_playable", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Indicates if the chapter is playable in the market.,
			OutputParameter(name="languages", param_type=OutputParameterType.STRING, is_array=True),  # List of ISO 639-1 language codes in the chapter.,
			OutputParameter(name="name", param_type=OutputParameterType.STRING, is_array=False),  # Chapter name.,
			OutputParameter(name="release_date", param_type=OutputParameterType.STRING, is_array=False),  # Release date, format 'YYYY-MM-DD'.,
			OutputParameter(name="release_date_precision", param_type=OutputParameterType.STRING, is_array=False),  # Precision of the release date: 'year', 'month', 'day'.,
			OutputParameter(name="resume_point", param_type=OutputParameterType.OBJECT, is_array=False),  # Object with user's playback position in the chapter.,
			OutputParameter(name="fully_played", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Whether the chapter has been fully played.,
			OutputParameter(name="resume_position_ms", param_type=OutputParameterType.INTEGER, is_array=False),  # Recent position in milliseconds.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, always 'episode'.,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI of the chapter.,
			OutputParameter(name="restrictions", param_type=OutputParameterType.OBJECT, is_array=False),  # Restrictions applied to the content.,
			OutputParameter(name="reason", param_type=OutputParameterType.STRING, is_array=False),  # Reason for restriction, e.g., 'market', 'product', 'explicit', 'payment_required'.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_an_Audiobook.method, 
                                          Get_an_Audiobook.url,
                                          Get_an_Audiobook.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_an_Audiobook': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Audio_Analysis_for_a_Track(BaseFunction):
    """This endpoint provides a detailed audio analysis of a track, describing its structure, rhythm, pitch, timbre, and other musical content."""
    name = "Get Audio Analysis for a Track"
    url = "https://api.spotify.com/v1/audio-analysis/{id}"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.STRING, required=True),  # The Spotify ID for the track. Example: '11dFghVXANMlKmJXsNCbNl'
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="meta", param_type=OutputParameterType.OBJECT, is_array=False),  # Metadata about the analysis including version, platform, status, timestamp, analysis time, and input process.,
			OutputParameter(name="track", param_type=OutputParameterType.OBJECT, is_array=False),  # Track-specific analysis data including samples, duration, loudness, tempo, key, mode, segments, bars, beats, sections, tatums, and various analysis features.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Audio_Analysis_for_a_Track.method, 
                                          Get_Audio_Analysis_for_a_Track.url,
                                          Get_Audio_Analysis_for_a_Track.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Audio_Analysis_for_a_Track': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Several_Episodes(BaseFunction):
    """Retrieve multiple episodes' information based on given Spotify IDs, including metadata, images, content restrictions, and show details."""
    name = "Get Several Episodes"
    url = "https://api.spotify.com/v1/episodes"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of Spotify IDs for the episodes. Maximum: 50. Example: '77o6BIVlYM3msb4MMIL1jH,0Q86acNRm6V9GYx55SXKwf'.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # An ISO 3166-1 alpha-2 country code to specify the market. Example: 'ES'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="episodes", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of episode objects containing details such as preview URL, description, duration, explicit content indicator, external URLs, id, images, availability, language, name, release date, resume point, type, uri, restrictions, and show information.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Several_Episodes.method, 
                                          Get_Several_Episodes.url,
                                          Get_Several_Episodes.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Several_Episodes': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_a_list_of_available_genre_seeds(BaseFunction):
    """Fetch a list of available genres that can be used as seed genres for generating recommendations."""
    name = "Get a list of available genre seeds"
    url = "https://api.spotify.com/v1/recommendations/available-genre-seeds"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="genres", param_type=OutputParameterType.STRING, is_array=True),  # List of available genres for recommendations, e.g., 'rock', 'pop', 'jazz', etc.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_a_list_of_available_genre_seeds.method, 
                                          Get_a_list_of_available_genre_seeds.url,
                                          Get_a_list_of_available_genre_seeds.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_a_list_of_available_genre_seeds': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_available_markets(BaseFunction):
    """Retrieve a list of markets (countries) where Spotify content and features are available."""
    name = "Get available markets"
    url = "https://api.spotify.com/v1/markets"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="markets", param_type=OutputParameterType.STRING, is_array=True),  # List of ISO 3166-1 alpha-2 country codes where Spotify is available, e.g., 'US', 'SE', 'DE', etc.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_available_markets.method, 
                                          Get_available_markets.url,
                                          Get_available_markets.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_available_markets': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Recently_Played_Tracks(BaseFunction):
    """Retrieve the current user's recently played tracks. Note: Does not support podcast episodes."""
    name = "Get Recently Played Tracks"
    url = "https://api.spotify.com/v1/me/player/recently-played"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # The maximum number of items to return. Default: 20. Minimum: 1. Maximum: 50. Default: `limit=20`. Range: `0` - `50`. Example: `limit=10`.,
			Parameter(name="after", param_type=ParameterType.INTEGER, required=False),  # A Unix timestamp in milliseconds. Returns all items after (but not including) this cursor position. If `after` is specified, `before` must not be specified. Example: `after=1484811043508`.,
			Parameter(name="before", param_type=ParameterType.INTEGER, required=False),  # A Unix timestamp in milliseconds. Returns all items before (but not including) this cursor position. If `before` is specified, `after` must not be specified.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # A link to the Web API endpoint returning the full result of the request.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # The maximum number of items in the response (as set in the query or by default).,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=False),  # URL to the next page of items. (`null` if none),
			OutputParameter(name="cursors", param_type=OutputParameterType.OBJECT, is_array=False),  # The cursors used to find the next set of items.,
			OutputParameter(name="cursors.after", param_type=OutputParameterType.STRING, is_array=False),  # The cursor to use as key to find the next page of items.,
			OutputParameter(name="cursors.before", param_type=OutputParameterType.STRING, is_array=False),  # The cursor to use as key to find the previous page of items.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # The total number of items available to return.,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # A paged set of tracks
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Recently_Played_Tracks.method, 
                                          Get_Recently_Played_Tracks.url,
                                          Get_Recently_Played_Tracks.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Recently_Played_Tracks': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_a_Show(BaseFunction):
    """Retrieve information about the current user's playback state, including track or episode, progress, and active device."""
    name = "Get a Show"
    url = "https://api.spotify.com/v1/shows/{id}"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="market", param_type=ParameterType.STRING, required=False),  # An [ISO 3166-1 alpha-2 country code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2). If specified, only content available in this market will be returned. If a user access token is provided, the user's country takes priority. Example: `market=ES`.,
			Parameter(name="id", param_type=ParameterType.STRING, required=True),  # The [Spotify ID](https://en.wikipedia.org/wiki/Spotify_URI_scheme#Spotify_IDs) for the show. Example: `38bS44xjbVVZ3No3ByF1dJ`.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="available_markets", param_type=OutputParameterType.STRING, is_array=True),  # List of countries where the show can be played, identified by ISO 3166-1 alpha-2 codes.,
			OutputParameter(name="copyrights", param_type=OutputParameterType.OBJECT, is_array=True),  # Copyright statements of the show.,
			OutputParameter(name="copyrights.text", param_type=OutputParameterType.STRING, is_array=False),  # The copyright text.,
			OutputParameter(name="copyrights.type", param_type=OutputParameterType.STRING, is_array=False),  # The type of copyright: `C` or `P`.,
			OutputParameter(name="description", param_type=OutputParameterType.STRING, is_array=False),  # Description of the show with HTML tags stripped.,
			OutputParameter(name="html_description", param_type=OutputParameterType.STRING, is_array=False),  # Description of the show, may contain HTML tags.,
			OutputParameter(name="explicit", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Indicates if the show has explicit content.,
			OutputParameter(name="external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # External URLs for the show.,
			OutputParameter(name="external_urls.spotify", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URL for the show.,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to Web API endpoint for full show details.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # Spotify ID for the show.,
			OutputParameter(name="images", param_type=OutputParameterType.OBJECT, is_array=True),  # Cover art images.,
			OutputParameter(name="images.url", param_type=OutputParameterType.STRING, is_array=False),  # Image source URL.,
			OutputParameter(name="images.height", param_type=OutputParameterType.INTEGER, is_array=False),  # Image height in pixels. Nullable.,
			OutputParameter(name="images.width", param_type=OutputParameterType.INTEGER, is_array=False),  # Image width in pixels. Nullable.,
			OutputParameter(name="is_externally_hosted", param_type=OutputParameterType.BOOLEAN, is_array=False),  # True if all episodes are hosted outside Spotify's CDN.,
			OutputParameter(name="languages", param_type=OutputParameterType.STRING, is_array=True),  # List of ISO 639 codes for languages used.,
			OutputParameter(name="media_type", param_type=OutputParameterType.STRING, is_array=False),  # Media type of the show.,
			OutputParameter(name="name", param_type=OutputParameterType.STRING, is_array=False),  # Name of the show.,
			OutputParameter(name="publisher", param_type=OutputParameterType.STRING, is_array=False),  # Publisher of the show.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, e.g., `show`.,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI for the show.,
			OutputParameter(name="total_episodes", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of episodes in the show.,
			OutputParameter(name="episodes", param_type=OutputParameterType.OBJECT, is_array=False),  # Episodes of the show.,
			OutputParameter(name="episodes.href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the endpoint returning full episodes.,
			OutputParameter(name="episodes.limit", param_type=OutputParameterType.INTEGER, is_array=False),  # Maximum number of episodes returned.,
			OutputParameter(name="episodes.next", param_type=OutputParameterType.STRING, is_array=False),  # URL to next page of episodes or `null`.,
			OutputParameter(name="episodes.offset", param_type=OutputParameterType.INTEGER, is_array=False),  # Offset of the episodes returned.,
			OutputParameter(name="episodes.previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to previous page or `null`.,
			OutputParameter(name="episodes.total", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of episodes.,
			OutputParameter(name="episodes.items", param_type=OutputParameterType.OBJECT, is_array=True),  # List of episode objects.,
			OutputParameter(name="episodes.items.audio_preview_url", param_type=OutputParameterType.STRING, is_array=False),  # Nullable URL to a 30s preview. Deprecated. Nullable.,
			OutputParameter(name="episodes.items.description", param_type=OutputParameterType.STRING, is_array=False),  # Description with HTML tags stripped.,
			OutputParameter(name="episodes.items.html_description", param_type=OutputParameterType.STRING, is_array=False),  # Description may contain HTML tags.,
			OutputParameter(name="episodes.items.duration_ms", param_type=OutputParameterType.INTEGER, is_array=False),  # Length of episode in milliseconds.,
			OutputParameter(name="episodes.items.explicit", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Whether the episode has explicit content.,
			OutputParameter(name="episodes.items.external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # External URLs.,
			OutputParameter(name="episodes.items.external_urls.spotify", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URL.,
			OutputParameter(name="episodes.items.href", param_type=OutputParameterType.STRING, is_array=False),  # API endpoint for episode details.,
			OutputParameter(name="episodes.items.id", param_type=OutputParameterType.STRING, is_array=False),  # Spotify ID of the episode.,
			OutputParameter(name="episodes.items.images", param_type=OutputParameterType.OBJECT, is_array=True),  # Cover art images.,
			OutputParameter(name="episodes.items.images.url", param_type=OutputParameterType.STRING, is_array=False),  # Image URL.,
			OutputParameter(name="episodes.items.images.height", param_type=OutputParameterType.INTEGER, is_array=False),  # Nullable height in pixels.,
			OutputParameter(name="episodes.items.images.width", param_type=OutputParameterType.INTEGER, is_array=False),  # Nullable width in pixels.,
			OutputParameter(name="episodes.items.is_externally_hosted", param_type=OutputParameterType.BOOLEAN, is_array=False),  # True if hosted outside Spotify.,
			OutputParameter(name="episodes.items.is_playable", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Is playable in current market.,
			OutputParameter(name="episodes.items.language", param_type=OutputParameterType.STRING, is_array=False),  # Deprecated. ISO 639 code of episode language.,
			OutputParameter(name="episodes.items.languages", param_type=OutputParameterType.STRING, is_array=True),  # List of ISO 639 codes for languages used.,
			OutputParameter(name="episodes.items.name", param_type=OutputParameterType.STRING, is_array=False),  # Name of the episode.,
			OutputParameter(name="episodes.items.release_date", param_type=OutputParameterType.STRING, is_array=False),  # First release date, format: `YYYY-MM-DD` or partial.,
			OutputParameter(name="episodes.items.release_date_precision", param_type=OutputParameterType.STRING, is_array=False),  # Precision of release date: `year`, `month`, or `day`.,
			OutputParameter(name="episodes.items.resume_point", param_type=OutputParameterType.OBJECT, is_array=False),  # User's most recent position in the episode.,
			OutputParameter(name="episodes.items.resume_point.fully_played", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Whether the episode has been fully played.,
			OutputParameter(name="episodes.items.resume_point.resume_position_ms", param_type=OutputParameterType.INTEGER, is_array=False),  # Most recent position in milliseconds.,
			OutputParameter(name="episodes.items.type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, e.g., `episode`.,
			OutputParameter(name="episodes.items.uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI for the episode.,
			OutputParameter(name="episodes.items.restrictions", param_type=OutputParameterType.OBJECT, is_array=False),  # Content restrictions.,
			OutputParameter(name="episodes.items.restrictions.reason", param_type=OutputParameterType.STRING, is_array=False),  # Reason for restriction: `market`, `product`, or `explicit`.,
			OutputParameter(name="show", param_type=OutputParameterType.OBJECT, is_array=False),  # Show object the episode belongs to.,
			OutputParameter(name="show.available_markets", param_type=OutputParameterType.STRING, is_array=True),  # Countries where show can be played.,
			OutputParameter(name="show.copyrights", param_type=OutputParameterType.OBJECT, is_array=True),  # Copyrights of the show.,
			OutputParameter(name="show.copyrights.text", param_type=OutputParameterType.STRING, is_array=False),  # Copyright text.,
			OutputParameter(name="show.copyrights.type", param_type=OutputParameterType.STRING, is_array=False),  # Type of copyright (`C` or `P`).,
			OutputParameter(name="show.description", param_type=OutputParameterType.STRING, is_array=False),  # Description of the show without HTML tags.,
			OutputParameter(name="show.html_description", param_type=OutputParameterType.STRING, is_array=False),  # Description of the show may contain HTML tags.,
			OutputParameter(name="show.explicit", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Whether the show has explicit content.,
			OutputParameter(name="show.external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # External URLs for the show.,
			OutputParameter(name="show.external_urls.spotify", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URL for the show.,
			OutputParameter(name="show.href", param_type=OutputParameterType.STRING, is_array=False),  # API link for show details.,
			OutputParameter(name="show.id", param_type=OutputParameterType.STRING, is_array=False),  # Spotify ID for the show.,
			OutputParameter(name="show.images", param_type=OutputParameterType.OBJECT, is_array=True),  # Cover art images.,
			OutputParameter(name="show.images.url", param_type=OutputParameterType.STRING, is_array=False),  # Image URL.,
			OutputParameter(name="show.images.height", param_type=OutputParameterType.INTEGER, is_array=False),  # Nullable height.,
			OutputParameter(name="show.images.width", param_type=OutputParameterType.INTEGER, is_array=False),  # Nullable width.,
			OutputParameter(name="show.is_externally_hosted", param_type=OutputParameterType.BOOLEAN, is_array=False),  # True if episodes are hosted outside Spotify.,
			OutputParameter(name="show.languages", param_type=OutputParameterType.STRING, is_array=True),  # List of ISO 639 language codes.,
			OutputParameter(name="show.media_type", param_type=OutputParameterType.STRING, is_array=False),  # Media type of the show.,
			OutputParameter(name="show.name", param_type=OutputParameterType.STRING, is_array=False),  # Name of the show.,
			OutputParameter(name="show.publisher", param_type=OutputParameterType.STRING, is_array=False),  # Publisher of the show.,
			OutputParameter(name="show.type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, e.g., `show`.,
			OutputParameter(name="show.uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI for the show.,
			OutputParameter(name="show.total_episodes", param_type=OutputParameterType.INTEGER, is_array=False),  # Total episodes in the show.,
			OutputParameter(name="currently_playing_type", param_type=OutputParameterType.STRING, is_array=False),  # Type of the currently playing item: `track`, `episode`, `ad`, or `unknown`.,
			OutputParameter(name="actions", param_type=OutputParameterType.OBJECT, is_array=False),  # Playback actions available.,
			OutputParameter(name="actions.interrupting_playback", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Interrupting playback available.,
			OutputParameter(name="actions.pausing", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Pausing available.,
			OutputParameter(name="actions.resuming", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Resuming available.,
			OutputParameter(name="actions.seeking", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Seeking possible.,
			OutputParameter(name="actions.skipping_next", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Next track skipping available.,
			OutputParameter(name="actions.skipping_prev", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Previous track skipping available.,
			OutputParameter(name="actions.toggling_repeat_context", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Toggle repeat context.,
			OutputParameter(name="actions.toggling_shuffle", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Toggle shuffle.,
			OutputParameter(name="actions.toggling_repeat_track", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Toggle repeat track.,
			OutputParameter(name="actions.transferring_playback", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Transfer playback available.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_a_Show.method, 
                                          Get_a_Show.url,
                                          Get_a_Show.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_a_Show': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_a_Playlists_Items(BaseFunction):
    """Retrieve the current playlist tracks, with optional field selection, pagination, and market filtering."""
    name = "Get a Playlist’s Items"
    url = "https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="playlist_id", param_type=ParameterType.STRING, required=True),  # The Spotify ID for the playlist.,
			Parameter(name="fields", param_type=ParameterType.STRING, required=False),  # Selector to narrow down the fields returned. Default: null.,
			Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Maximum number of items to return. Default: 100.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # The index of the first item to return. Default: 0.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # An ISO 3166-1 alpha-2 country code. The market of the user if not specified.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # A link to the Web API endpoint returning the full result of the request.,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # The playlist tracks.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # The maximum number of items in the response.,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=False),  # URL to the next page of items, or null if none.,
			OutputParameter(name="offset", param_type=OutputParameterType.INTEGER, is_array=False),  # The offset of the items returned.,
			OutputParameter(name="previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to the previous page of items, or null if none.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # The total number of tracks in the playlist.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_a_Playlists_Items.method, 
                                          Get_a_Playlists_Items.url,
                                          Get_a_Playlists_Items.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_a_Playlists_Items': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Create_a_Playlist(BaseFunction):
    """Create a new playlist for a Spotify user."""
    name = "Create a Playlist"
    url = "https://api.spotify.com/v1/users/{user_id}/playlists"
    args_in_url = True
    method = "INSERT"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="user_id", param_type=ParameterType.STRING, required=True),  # The Spotify user ID for the user.,
			Parameter(name="name", param_type=ParameterType.STRING, required=True),  # The name of the new playlist.,
			Parameter(name="public", param_type=ParameterType.BOOLEAN, required=False),  # Whether the playlist is public. Default: true.,
			Parameter(name="collaborative", param_type=ParameterType.BOOLEAN, required=False),  # Whether the playlist is collaborative. Default: false.,
			Parameter(name="description", param_type=ParameterType.STRING, required=False),  # The playlist description.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # The Spotify ID for the new playlist.,
			OutputParameter(name="name", param_type=OutputParameterType.STRING, is_array=False),  # The name of the playlist.,
			OutputParameter(name="public", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Whether the playlist is public.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Create_a_Playlist.method, 
                                          Create_a_Playlist.url,
                                          Create_a_Playlist.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Create_a_Playlist': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Add_Items_to_a_Playlist(BaseFunction):
    """Add one or more tracks to a playlist."""
    name = "Add Items to a Playlist"
    url = "https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    args_in_url = True
    method = "PUT"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="playlist_id", param_type=ParameterType.STRING, required=True),  # The Spotify ID for the playlist.,
			Parameter(name="uris", param_type=ParameterType.STRING, required=True),  # A comma-separated list of Spotify URIs to add. Max: 100 per request.,
			Parameter(name="position", param_type=ParameterType.INTEGER, required=False),  # The position to insert the items in the playlist. Default: 0.
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Add_Items_to_a_Playlist.method, 
                                          Add_Items_to_a_Playlist.url,
                                          Add_Items_to_a_Playlist.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Add_Items_to_a_Playlist': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Follow_a_Playlist(BaseFunction):
    """Add the current user as a follower of a playlist."""
    name = "Follow a Playlist"
    url = "https://api.spotify.com/v1/me/playlists/\{playlist_id\}/followers"
    args_in_url = True
    method = "PUT"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="playlist_id", param_type=ParameterType.STRING, required=True),  # The Spotify ID for the playlist.
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Follow_a_Playlist.method, 
                                          Follow_a_Playlist.url,
                                          Follow_a_Playlist.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Follow_a_Playlist': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Unfollow_a_Playlist(BaseFunction):
    """Remove the current user as a follower of a playlist."""
    name = "Unfollow a Playlist"
    url = "https://api.spotify.com/v1/me/playlists/\{playlist_id\}/followers"
    args_in_url = True
    method = "DELETE"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="playlist_id", param_type=ParameterType.STRING, required=True),  # The Spotify ID for the playlist.
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Unfollow_a_Playlist.method, 
                                          Unfollow_a_Playlist.url,
                                          Unfollow_a_Playlist.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Unfollow_a_Playlist': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_a_Playlist_Cover_Image(BaseFunction):
    """Get the cover image for a playlist."""
    name = "Get a Playlist Cover Image"
    url = "https://api.spotify.com/v1/playlists/{playlist_id}/images"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="playlist_id", param_type=ParameterType.STRING, required=True),  # The Spotify ID for the playlist.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="images", param_type=OutputParameterType.OBJECT, is_array=True),  # The playlist images.,
			OutputParameter(name="url", param_type=OutputParameterType.STRING, is_array=False),  # The source URL of the image.,
			OutputParameter(name="height", param_type=OutputParameterType.INTEGER, is_array=False),  # The height of the image in pixels.,
			OutputParameter(name="width", param_type=OutputParameterType.INTEGER, is_array=False),  # The width of the image in pixels.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_a_Playlist_Cover_Image.method, 
                                          Get_a_Playlist_Cover_Image.url,
                                          Get_a_Playlist_Cover_Image.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_a_Playlist_Cover_Image': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Save_Episodes_for_Current_User(BaseFunction):
    """Endpoint to save one or more episodes to the current user's library. Requires 'user-library-modify' scope."""
    name = "Save Episodes for Current User"
    url = "https://api.spotify.com/v1/me/episodes"
    args_in_url = False
    method = "PUT"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of Spotify IDs to save. Maximum of 50 IDs. Example: `ids=77o6BIVlYM3msb4MMIL1jH,0Q86acNRm6V9GYx55SXKwf`.,
			Parameter(name="body", param_type=OutputParameterType.OBJECT, required=False),  # Supports additional optional properties, including 'ids' as an array of strings (overrides query parameter if both are present).
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="status_code", param_type=OutputParameterType.INTEGER, is_array=False),  # HTTP status code indicating success or failure.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Save_Episodes_for_Current_User.method, 
                                          Save_Episodes_for_Current_User.url,
                                          Save_Episodes_for_Current_User.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Save_Episodes_for_Current_User': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_an_Episode(BaseFunction):
    """Endpoint to retrieve detailed information about a specific episode identified by its Spotify ID."""
    name = "Get an Episode"
    url = "https://api.spotify.com/v1/episodes/{id}"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.STRING, required=True),  # The Spotify ID for the episode. Example: `512ojhOuo1ktJprKbVcKyQ`.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # An ISO 3166-1 alpha-2 country code to filter content availability. If not specified, defaults to user country if access token is provided. Example: `ES`.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="audio_preview_url", param_type=OutputParameterType.STRING, is_array=False),  # URL to a 30-second MP3 preview of the episode. Nullable; may be null if not available.,
			OutputParameter(name="description", param_type=OutputParameterType.STRING, is_array=False),  # Plain text description of the episode with HTML tags stripped.,
			OutputParameter(name="html_description", param_type=OutputParameterType.STRING, is_array=False),  # HTML-formatted description of the episode.,
			OutputParameter(name="duration_ms", param_type=OutputParameterType.INTEGER, is_array=False),  # Length of the episode in milliseconds. Example: 1686230.,
			OutputParameter(name="explicit", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Indicates if the episode has explicit content.,
			OutputParameter(name="external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # External URLs for this episode, including the Spotify URL.,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the Web API endpoint providing full details.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # Spotify ID for the episode.,
			OutputParameter(name="images", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of image objects representing cover art.,
			OutputParameter(name="is_playable", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Whether the episode is playable in the given market.,
			OutputParameter(name="languages", param_type=OutputParameterType.STRING, is_array=True),  # List of ISO 639-1 language codes used in the episode.,
			OutputParameter(name="name", param_type=OutputParameterType.STRING, is_array=False),  # Name of the episode.,
			OutputParameter(name="release_date", param_type=OutputParameterType.STRING, is_array=False),  # Release date in 'YYYY-MM-DD' format.,
			OutputParameter(name="release_date_precision", param_type=OutputParameterType.STRING, is_array=False),  # Precision of release date: 'year', 'month', or 'day'.,
			OutputParameter(name="resume_point", param_type=OutputParameterType.OBJECT, is_array=False),  # User's most recent position in the episode, if scope allows.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, always 'episode'.,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # The Spotify URI for the episode.,
			OutputParameter(name="restrictions", param_type=OutputParameterType.OBJECT, is_array=False),  # Content restrictions applied, if any.,
			OutputParameter(name="show", param_type=OutputParameterType.OBJECT, is_array=False),  # The show to which this episode belongs.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_an_Episode.method, 
                                          Get_an_Episode.url,
                                          Get_an_Episode.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_an_Episode': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_a_Chapter(BaseFunction):
    """Endpoint to fetch details about a specific audiobook chapter by its Spotify ID."""
    name = "Get a Chapter"
    url = "https://api.spotify.com/v1/chapters/{id}"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.STRING, required=True),  # The Spotify ID for the chapter. Example: `0D5wENdkdwbqlrHoaJ9g29`.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # ISO 3166-1 alpha-2 country code to filter content. If not specified, defaults to user country if access token is provided. Example: `ES`.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="audio_preview_url", param_type=OutputParameterType.STRING, is_array=False),  # URL to a 30-second MP3 preview of the chapter. Nullable; may be null if not available.,
			OutputParameter(name="available_markets", param_type=OutputParameterType.STRING, is_array=True),  # Markets where the chapter can be played, specified as ISO 3166-1 alpha-2 codes.,
			OutputParameter(name="chapter_number", param_type=OutputParameterType.INTEGER, is_array=False),  # Number of the chapter in the audiobook.,
			OutputParameter(name="description", param_type=OutputParameterType.STRING, is_array=False),  # Plain text description with HTML tags stripped.,
			OutputParameter(name="html_description", param_type=OutputParameterType.STRING, is_array=False),  # HTML-formatted description of the chapter.,
			OutputParameter(name="duration_ms", param_type=OutputParameterType.INTEGER, is_array=False),  # Length of the chapter in milliseconds.,
			OutputParameter(name="explicit", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Whether the chapter contains explicit content.,
			OutputParameter(name="external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # External URLs including the Spotify link.,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the Web API endpoint for full details.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # Spotify ID for the chapter.,
			OutputParameter(name="images", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of images representing cover art.,
			OutputParameter(name="is_playable", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Whether the chapter is playable in the current market.,
			OutputParameter(name="languages", param_type=OutputParameterType.STRING, is_array=True),  # List of ISO 639-1 language codes used in the chapter.,
			OutputParameter(name="name", param_type=OutputParameterType.STRING, is_array=False),  # Name of the chapter.,
			OutputParameter(name="release_date", param_type=OutputParameterType.STRING, is_array=False),  # Release date in 'YYYY-MM-DD' format.,
			OutputParameter(name="release_date_precision", param_type=OutputParameterType.STRING, is_array=False),  # Precision: 'year', 'month', or 'day'.,
			OutputParameter(name="resume_point", param_type=OutputParameterType.OBJECT, is_array=False),  # User's most recent position in the chapter.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, always 'episode'.,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI of the chapter.,
			OutputParameter(name="restrictions", param_type=OutputParameterType.OBJECT, is_array=False),  # Content restrictions, if any.,
			OutputParameter(name="audiobook", param_type=OutputParameterType.OBJECT, is_array=False),  # The audiobook to which this chapter belongs.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_a_Chapter.method, 
                                          Get_a_Chapter.url,
                                          Get_a_Chapter.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_a_Chapter': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Followed_Artists(BaseFunction):
    """Endpoint to get the current user's followed artists, supports pagination."""
    name = "Get Followed Artists"
    url = "https://api.spotify.com/v1/me/following"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="type", param_type=ParameterType.STRING, required=True),  # The ID type to fetch. Currently, only 'artist' is supported. Example: `type=artist`.,
			Parameter(name="after", param_type=ParameterType.STRING, required=False),  # The last artist ID retrieved from the previous request, for pagination. Example: `after=0I2XqVXqHScXjHhk6AYYRe`.,
			Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Maximum number of items to return. Default 20, min 1, max 50. Example: `limit=10`.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="artists", param_type=OutputParameterType.OBJECT, is_array=False),  # Paged set of followed artists.,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to full result endpoint.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # Maximum number of items in response.,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=False),  # URL to next page, or null.,
			OutputParameter(name="cursors", param_type=OutputParameterType.OBJECT, is_array=True),  # Pagination cursors.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # Total followed artists.,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of artist objects.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Followed_Artists.method, 
                                          Get_Followed_Artists.url,
                                          Get_Followed_Artists.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Followed_Artists': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Featured_Playlists(BaseFunction):
    """Retrieves a list of Spotify's featured playlists with pagination and localization options."""
    name = "Get Featured Playlists"
    url = "https://api.spotify.com/v1/browse/featured-playlists"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="locale", param_type=ParameterType.STRING, required=False),  # The desired language, consisting of an ISO 639-1 language code and an ISO 3166-1 alpha-2 country code, joined by an underscore. For example: 'es_MX'. If not supplied or unavailable, defaults to English.,
			Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Maximum number of items to return. Default: 20. Range: 1-50.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # Index of the first item to return. Default: 0.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="message", param_type=OutputParameterType.STRING, is_array=False),  # The localized message of a playlist, e.g., 'Popular Playlists'.,
			OutputParameter(name="playlists", param_type=OutputParameterType.OBJECT, is_array=False),  # An object containing details of the playlists, including links, pagination info, and items.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Featured_Playlists.method, 
                                          Get_Featured_Playlists.url,
                                          Get_Featured_Playlists.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Featured_Playlists': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Current_Users_Profile(BaseFunction):
    """Retrieves detailed profile information about the current user, including settings and images."""
    name = "Get Current User's Profile"
    url = "https://api.spotify.com/v1/me"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="country", param_type=OutputParameterType.STRING, is_array=False),  # User's country code as set in their profile; ISO 3166-1 alpha-2 code.,
			OutputParameter(name="display_name", param_type=OutputParameterType.STRING, is_array=False),  # Display name of the user, or null if not available.,
			OutputParameter(name="email", param_type=OutputParameterType.STRING, is_array=False),  # User's email address, unverified, as entered during account creation.,
			OutputParameter(name="explicit_content", param_type=OutputParameterType.OBJECT, is_array=False),  # Content restrictions and explicit content settings.,
			OutputParameter(name="external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # Known external URLs for the user.,
			OutputParameter(name="followers", param_type=OutputParameterType.OBJECT, is_array=False),  # Information about user followers.,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to Web API endpoint for this user.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # Spotify's user ID.,
			OutputParameter(name="images", param_type=OutputParameterType.OBJECT, is_array=True),  # Profile images of the user.,
			OutputParameter(name="product", param_type=OutputParameterType.STRING, is_array=False),  # Subscription level, e.g., 'premium' or 'free'.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, always 'user'.,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI for the user.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Current_Users_Profile.method, 
                                          Get_Current_Users_Profile.url,
                                          Get_Current_Users_Profile.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Current_Users_Profile': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Users_Saved_Albums(BaseFunction):
    """Fetches a paginated list of albums saved in the user's library, with optional market filtering."""
    name = "Get User's Saved Albums"
    url = "https://api.spotify.com/v1/me/albums"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Maximum number of items to return. Default: 20. Range: 1-50.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # The index of the first item to return. Default: 0.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # ISO 3166-1 alpha-2 country code to filter content available in that market. If unspecified, user's market is used if available.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the full result set.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # Maximum number of items returned.,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=True),  # URL to the next page of items, or null if none.,
			OutputParameter(name="offset", param_type=OutputParameterType.INTEGER, is_array=False),  # Starting index of the returned items.,
			OutputParameter(name="previous", param_type=OutputParameterType.STRING, is_array=True),  # URL to the previous page of items, or null if none.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of saved albums.,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of saved album objects, including added date and album info.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Users_Saved_Albums.method, 
                                          Get_Users_Saved_Albums.url,
                                          Get_Users_Saved_Albums.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Users_Saved_Albums': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Album(BaseFunction):
    """Retrieve detailed information about a specific album by its Spotify ID."""
    name = "Get Album"
    url = "https://api.spotify.com/v1/albums/{id}"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the album. Example: '4aawyAB9vmqN3uQ7FjRGTy'.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # An ISO 3166-1 alpha-2 country code to specify the market for album availability. Example: 'ES'. If not provided, defaults to the country associated with the user or request.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="album_type", param_type=OutputParameterType.STRING, is_array=False),  # Required. The type of the album. Allowed values: 'album', 'single', 'compilation'.,
			OutputParameter(name="total_tracks", param_type=OutputParameterType.INTEGER, is_array=False),  # Required. The number of tracks in the album.,
			OutputParameter(name="available_markets", param_type=OutputParameterType.STRING, is_array=True),  # Required. List of markets where the album is available. ISO 3166-1 alpha-2 country codes. Example: ['CA','BR','IT'].,
			OutputParameter(name="external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # Required. External URLs for the album, including 'spotify'.,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the Web API endpoint providing full details of the album.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # Spotify ID for the album. Example: '2up3OPMp9Tb4dAKM2erWXQ'.,
			OutputParameter(name="images", param_type=OutputParameterType.OBJECT, is_array=True),  # Album cover images in various sizes.,
			OutputParameter(name="name", param_type=OutputParameterType.STRING, is_array=False),  # The name of the album.,
			OutputParameter(name="release_date", param_type=OutputParameterType.STRING, is_array=False),  # The date the album was first released. Example: '1981-12'.,
			OutputParameter(name="release_date_precision", param_type=OutputParameterType.STRING, is_array=False),  # The precision of the release date. Allowed values: 'year', 'month', 'day'.,
			OutputParameter(name="restrictions", param_type=OutputParameterType.OBJECT, is_array=False),  # Content restrictions applied to the album.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # Object type. Allowed value: 'album'.,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI for the album. Example: 'spotify:album:...'.,
			OutputParameter(name="artists", param_type=OutputParameterType.OBJECT, is_array=True),  # List of artists of the album.,
			OutputParameter(name="tracks", param_type=OutputParameterType.OBJECT, is_array=False),  # Tracks in the album, includes paging information and list of track objects.,
			OutputParameter(name="copyrights", param_type=OutputParameterType.OBJECT, is_array=True),  # Copyright statements of the album.,
			OutputParameter(name="external_ids", param_type=OutputParameterType.OBJECT, is_array=False),  # External IDs such as ISRC, EAN, UPC.,
			OutputParameter(name="genres", param_type=OutputParameterType.STRING, is_array=True),  # (Deprecated) This field is always empty.,
			OutputParameter(name="label", param_type=OutputParameterType.STRING, is_array=False),  # The label of the album.,
			OutputParameter(name="popularity", param_type=OutputParameterType.INTEGER, is_array=False),  # The popularity of the album, a value between 0 and 100.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Album.method, 
                                          Get_Album.url,
                                          Get_Album.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Album': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Update_Playlist_Items(BaseFunction):
    """Reorder or replace items in a playlist depending on parameters provided."""
    name = "Update Playlist Items"
    url = "https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    args_in_url = True
    method = "PUT"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="playlist_id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the playlist. Example: '3cEYpjA9oz9GiPac4AsH4n'.,
			Parameter(name="uris", param_type=ParameterType.STRING, required=False),  # A comma-separated list of Spotify URIs to set in the playlist (either tracks or episodes). Example: 'spotify:track:...,spotify:episode:...'. Max 100 items.,
			Parameter(name="body", param_type=OutputParameterType.OBJECT, required=False),  # Request body containing 'uris' as an array of strings, 'range_start' as integer, 'insert_before' as integer, 'range_length' as integer, 'snapshot_id' as string. Supports reordering or replacing playlist items.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="snapshot_id", param_type=OutputParameterType.STRING, is_array=False),  # A snapshot ID for the playlist after changes. Example: 'abc'.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Update_Playlist_Items.method, 
                                          Update_Playlist_Items.url,
                                          Update_Playlist_Items.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Update_Playlist_Items': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Spotify_URIs_and_IDs(BaseFunction):
    """Different resource identifiers and URLs used within Spotify's API for various resources."""
    name = "Spotify URIs and IDs"
    url = "https://developer.spotify.com/documentation/web-api/concepts/spotify-uris-ids"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="spotify_uri", param_type=OutputParameterType.STRING, is_array=False),  # The resource identifier of an artist, album, or track. Example: 'spotify:track:6rqhFgbbKwnb9MLmUQDhG6'.,
			OutputParameter(name="spotify_id", param_type=OutputParameterType.STRING, is_array=False),  # The base-62 identifier found at the end of a Spotify URI. Example: '6rqhFgbbKwnb9MLmUQDhG6'.,
			OutputParameter(name="spotify_category_id", param_type=OutputParameterType.STRING, is_array=False),  # The unique string for a Spotify category. Example: 'party'.,
			OutputParameter(name="spotify_user_id", param_type=OutputParameterType.STRING, is_array=False),  # The Spotify user ID. Example: 'wizzler'.,
			OutputParameter(name="spotify_url", param_type=OutputParameterType.STRING, is_array=False),  # A URL that opens in the Spotify client or web player. Example: 'http://open.spotify.com/track/...'.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Spotify_URIs_and_IDs.method, 
                                          Spotify_URIs_and_IDs.url,
                                          Spotify_URIs_and_IDs.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Spotify_URIs_and_IDs': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Playlist(BaseFunction):
    """Get detailed information about a specific playlist by its ID."""
    name = "Get Playlist"
    url = "https://api.spotify.com/v1/playlists/{playlist_id}"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="playlist_id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the playlist. Example: `3cEYpjA9oz9GiPac4AsH4n`,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # ISO 3166-1 alpha-2 country code. If specified, only content available in that market will be returned. If a user access token is provided, the user's country is used instead. Example: `ES`,
			Parameter(name="fields", param_type=ParameterType.STRING, required=False),  # Comma-separated list of fields to return. Supports nested fields with dot notation and parentheses, e.g., `tracks.items(added_at,added_by.id)`. Use '!' prefix to exclude fields, e.g., `tracks.items(track(name,href))`. Example: `items(added_by.id,track(name,href))`,
			Parameter(name="additional_types", param_type=ParameterType.STRING, required=False),  # Comma-separated list of item types supporting besides 'track' and 'episode', e.g., `track,episode`. Note: this parameter might be deprecated.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="collaborative", param_type=OutputParameterType.BOOLEAN, is_array=False),  # True if owners allow other users to modify the playlist.,
			OutputParameter(name="description", param_type=OutputParameterType.STRING, is_array=False),  # The playlist description, nullable. Only returned for modified, verified playlists; otherwise null.,
			OutputParameter(name="external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # Known external URLs for the playlist, e.g., Spotify URL.,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to Web API endpoint providing full playlist details.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # The Spotify ID for the playlist.,
			OutputParameter(name="images", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of image objects for the playlist, up to three images, sorted by size descending.,
			OutputParameter(name="name", param_type=OutputParameterType.STRING, is_array=False),  # Name of the playlist.,
			OutputParameter(name="owner", param_type=OutputParameterType.OBJECT, is_array=False),  # The owner of the playlist, including external URLs, href, id, type, uri, display name.,
			OutputParameter(name="public", param_type=OutputParameterType.BOOLEAN, is_array=False),  # The playlist's public/private status; true if public, false if private, null if not relevant.,
			OutputParameter(name="snapshot_id", param_type=OutputParameterType.STRING, is_array=False),  # Snapshot ID of the playlist for version control.,
			OutputParameter(name="tracks", param_type=OutputParameterType.OBJECT, is_array=False),  # Object containing playlist tracks, including href, limit, next, offset, previous, total, and items array.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # The object type: 'playlist'.,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # The Spotify URI for the playlist.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Playlist.method, 
                                          Get_Playlist.url,
                                          Get_Playlist.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Playlist': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Add_Tracks_to_Playlist(BaseFunction):
    """Add one or more tracks or episodes to a playlist at optional position."""
    name = "Add Tracks to Playlist"
    url = "https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    args_in_url = True
    method = "PUT"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="playlist_id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the playlist to add tracks to. Example: `3cEYpjA9oz9GiPac4AsH4n`,
			Parameter(name="position", param_type=ParameterType.INTEGER, required=False),  # The position to insert the items, zero-based index. Defaults to appending at the end if omitted. Example: `0`.,
			Parameter(name="uris", param_type=ParameterType.STRING, required=False),  # Comma-separated list of Spotify URIs (track or episode) to add, e.g., `spotify:track:4iV5W9uYEdYUVa79Axb7Rh`. Max 100 items. Note: for large sets, pass as JSON array in request body.,
			Parameter(name="body", param_type=OutputParameterType.OBJECT, required=False),  # Request body supporting 'uris' as an array of strings and optional 'position'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="snapshot_id", param_type=OutputParameterType.STRING, is_array=False),  # Snapshot ID of the playlist after modification.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Add_Tracks_to_Playlist.method, 
                                          Add_Tracks_to_Playlist.url,
                                          Add_Tracks_to_Playlist.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Add_Tracks_to_Playlist': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Follow_Artists_or_Users(BaseFunction):
    """Add current user as follower of specified artists or other Spotify users."""
    name = "Follow Artists or Users"
    url = "https://api.spotify.com/v1/me/following?type={type}"
    args_in_url = True
    method = "PUT"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="type", param_type=ParameterType.STRING, required=True),  # The ID type: 'artist' or 'user'.,
			Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # Comma-separated list of Spotify IDs (max 50) of artists or users to follow. Example: `2CIMQHirSU0MQqyYHq0eOx,57dN52uHvrHOxijzpIgu3E`,
			Parameter(name="body", param_type=OutputParameterType.OBJECT, required=False),  # Request body supporting 'ids' as an array of strings of Spotify IDs, maximum 50, e.g., `{'ids': ['id1', 'id2']}`.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="status", param_type=OutputParameterType.STRING, is_array=False),  # Empty response on success, status codes indicate the result.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Follow_Artists_or_Users.method, 
                                          Follow_Artists_or_Users.url,
                                          Follow_Artists_or_Users.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Follow_Artists_or_Users': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Remove_Users_Saved_Tracks(BaseFunction):
    """Removes one or more tracks from the current user's 'Your Music' library."""
    name = "Remove User's Saved Tracks"
    url = "https://api.spotify.com/v1/me/tracks"
    args_in_url = False
    method = "DELETE"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of the Spotify IDs for the tracks to remove. For example: '4iV5W9uYEdYUVa79Axb7Rh,1301WleyT98MSxVHPZCA6M'. Maximum: 50 IDs.,
			Parameter(name="ids", param_type=ParameterType.STRING, required=False),  # An array of strings representing Spotify IDs. For example: ['7ouMYWpwJ422jRcDASZB7P', '4VqPOruhp5EdPBeR92t6lQ']. A maximum of 50 items can be specified in one request. If both 'ids' query parameter and this body property are present, the body property will be ignored.
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Remove_Users_Saved_Tracks.method, 
                                          Remove_Users_Saved_Tracks.url,
                                          Remove_Users_Saved_Tracks.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Remove_Users_Saved_Tracks': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Tracks_Audio_Features(BaseFunction):
    """Get audio feature information for a single track identified by its Spotify ID."""
    name = "Get Track's Audio Features"
    url = "https://api.spotify.com/v1/audio-features/{id}"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.STRING, required=True),  # The Spotify ID for the track. Example: '11dFghVXANMlKmJXsNCbNl'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="acousticness", param_type=OutputParameterType.FLOAT, is_array=False),  # A confidence measure from 0.0 to 1.0 of whether the track is acoustic. 1.0 represents high confidence the track is acoustic.,
			OutputParameter(name="analysis_url", param_type=OutputParameterType.STRING, is_array=False),  # A URL to access the full audio analysis of this track. An access token is required to access this data.,
			OutputParameter(name="danceability", param_type=OutputParameterType.FLOAT, is_array=False),  # Danceability describes how suitable a track is for dancing based on a combination of musical elements, ranging from 0.0 to 1.0.,
			OutputParameter(name="duration_ms", param_type=OutputParameterType.INTEGER, is_array=False),  # The duration of the track in milliseconds.,
			OutputParameter(name="energy", param_type=OutputParameterType.FLOAT, is_array=False),  # A measure from 0.0 to 1.0 of perceptual measure of intensity and activity.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # The Spotify ID for the track.,
			OutputParameter(name="instrumentalness", param_type=OutputParameterType.FLOAT, is_array=False),  # Predicts whether a track contains no vocals, with values closer to 1.0 indicating a higher likelihood of being purely instrumental.,
			OutputParameter(name="key", param_type=OutputParameterType.INTEGER, is_array=False),  # The key the track is in, represented as an integer from -1 to 11, following the Pitch Class notation.,
			OutputParameter(name="liveness", param_type=OutputParameterType.FLOAT, is_array=False),  # Detects the presence of an audience in the recording, with higher values indicating a higher probability that the track was performed live.,
			OutputParameter(name="loudness", param_type=OutputParameterType.FLOAT, is_array=False),  # The overall loudness of the track in decibels (dB). Usually between -60 and 0.,
			OutputParameter(name="mode", param_type=OutputParameterType.INTEGER, is_array=False),  # The modality (major or minor) of the track, 1 for major, 0 for minor.,
			OutputParameter(name="speechiness", param_type=OutputParameterType.FLOAT, is_array=False),  # Detects the presence of spoken words in a track, with values above 0.66 indicating likely speech content.,
			OutputParameter(name="tempo", param_type=OutputParameterType.FLOAT, is_array=False),  # The estimated tempo of the track in beats per minute (BPM).,
			OutputParameter(name="time_signature", param_type=OutputParameterType.INTEGER, is_array=False),  # An estimated time signature, range from 3 to 7.,
			OutputParameter(name="track_href", param_type=OutputParameterType.STRING, is_array=False),  # A URL to access full details of the track via the Web API.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # The object type, always 'audio_features'.,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # The Spotify URI for the track.,
			OutputParameter(name="valence", param_type=OutputParameterType.FLOAT, is_array=False),  # A measure from 0.0 to 1.0 representing the musical positiveness conveyed by the track.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Tracks_Audio_Features.method, 
                                          Get_Tracks_Audio_Features.url,
                                          Get_Tracks_Audio_Features.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Tracks_Audio_Features': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Users_Top_Items(BaseFunction):
    """Get the current user's top artists or tracks based on affinity over a specified time frame."""
    name = "Get User's Top Items"
    url = "https://api.spotify.com/v1/me/top/{type}"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="type", param_type=ParameterType.STRING, required=True),  # The type of item to return. Valid values: 'artists' or 'tracks'.,
			Parameter(name="time_range", param_type=ParameterType.STRING, required=False),  # Over what time period the affinities are computed. Valid values: 'long_term', 'medium_term', 'short_term'. Default: 'medium_term'.,
			Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Maximum number of items to return. Default: 20, min: 1, max: 50.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # The index of the first item to return. Default: 0.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # A link to the API endpoint returning the full result of the request.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # Maximum number of items returned.,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=False),  # URL to the next page of items, or null.,
			OutputParameter(name="offset", param_type=OutputParameterType.INTEGER, is_array=False),  # The offset of the items returned.,
			OutputParameter(name="previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to the previous page of items, or null.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # The total number of items available.,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # An array of artist or track objects, each with their own detailed schema.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Users_Top_Items.method, 
                                          Get_Users_Top_Items.url,
                                          Get_Users_Top_Items.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Users_Top_Items': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_a_Chapter(BaseFunction):
    """Retrieve information about one or multiple audiobook chapters, with optional filtering by market and pagination."""
    name = "Get a Chapter"
    url = "/audiobooks/{id}/chapters"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the audiobook chapter. Example: '7iHfbu1YPACw6oZPAFJtqe'.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # ISO 3166-1 alpha-2 country code. If specified, only content available in that market will be returned. Example: 'ES'.,
			Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Maximum number of items to return. Default: 20. Min: 1. Max: 50.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # Index of the first item to return. Default: 0.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the Web API endpoint returning the full result.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # Maximum number of items in the response.,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=False),  # URL to the next page of items, or null if none.,
			OutputParameter(name="offset", param_type=OutputParameterType.INTEGER, is_array=False),  # Offset of the items returned.,
			OutputParameter(name="previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to the previous page of items, or null if none.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of items available.,
			OutputParameter(name="chapters", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of chapter objects.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_a_Chapter.method, 
                                          Get_a_Chapter.url,
                                          Get_a_Chapter.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_a_Chapter': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Several_Chapters(BaseFunction):
    """Retrieve multiple chapters by their Spotify IDs, up to a maximum of 50."""
    name = "Get Several Chapters"
    url = "/chapters"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # Comma-separated list of Spotify IDs for chapters. Max 50 IDs. Example: '0IsXVP0JmcB2adSE338GkK,3ZXb8FKZGU0EHALYX6uCzU'.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # ISO 3166-1 alpha-2 country code. Content is available within specified markets.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="chapters", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of chapter objects.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Several_Chapters.method, 
                                          Get_Several_Chapters.url,
                                          Get_Several_Chapters.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Several_Chapters': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Upload_Custom_Playlist_Cover_Image(BaseFunction):
    """Replace the playlist's cover image with a new one, provided as Base64 encoded JPEG."""
    name = "Upload Custom Playlist Cover Image"
    url = "/playlists/{playlist_id}/images"
    args_in_url = True
    method = "PUT"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="playlist_id", param_type=ParameterType.STRING, required=True),  # Spotify ID of the playlist. Example: '3cEYpjA9oz9GiPac4AsH4n'.,
			Parameter(name="image_data", param_type=ParameterType.STRING, required=True),  # Base64 encoded JPEG image data, max 256 KB. Example: '/9j/...'
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="status_code", param_type=OutputParameterType.INTEGER, is_array=False),  # HTTP status code indicating success or failure.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Upload_Custom_Playlist_Cover_Image.method, 
                                          Upload_Custom_Playlist_Cover_Image.url,
                                          Upload_Custom_Playlist_Cover_Image.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Upload_Custom_Playlist_Cover_Image': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Toggle_Playback_Shuffle(BaseFunction):
    """Control playback shuffle state for user's current device."""
    name = "Toggle Playback Shuffle"
    url = "https://api.spotify.com/v1/me/player/shuffle"
    args_in_url = False
    method = "PUT"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="state", param_type=ParameterType.BOOLEAN, required=True),  # Required. True to shuffle user's playback; false to disable shuffle. Example: true.,
			Parameter(name="device_id", param_type=ParameterType.STRING, required=False),  # Optional. The id of the device this command is targeting. If not supplied, the user's currently active device is used. Example: '0d1841b0976bae2a3a310dd74c0f3df354899bc8'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="status_code", param_type=OutputParameterType.INTEGER, is_array=False),  # HTTP response status code. 204 indicates success.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Toggle_Playback_Shuffle.method, 
                                          Toggle_Playback_Shuffle.url,
                                          Toggle_Playback_Shuffle.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Toggle_Playback_Shuffle': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Several_Browse_Categories(BaseFunction):
    """Retrieve a list of available categories used to tag items in Spotify."""
    name = "Get Several Browse Categories"
    url = "https://api.spotify.com/v1/browse/categories"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="locale", param_type=ParameterType.STRING, required=False),  # Optional. The desired language, consisting of an ISO 639-1 language code and an ISO 3166-1 alpha-2 country code, joined by an underscore. Example: 'sv_SE'.,
			Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Optional. Maximum number of items to return. Default: 20. Range: 1-50. Example: 10.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # Optional. The index of the first item to return. Default: 0. Example: 5.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="categories", param_type=OutputParameterType.OBJECT, is_array=True),  # A paged set of categories.,
			OutputParameter(name="categories.href", param_type=OutputParameterType.STRING, is_array=False),  # A link to the Web API endpoint returning full results.,
			OutputParameter(name="categories.limit", param_type=OutputParameterType.INTEGER, is_array=False),  # The maximum number of items in the response.,
			OutputParameter(name="categories.next", param_type=OutputParameterType.STRING, is_array=False),  # URL to next page, or null if none.,
			OutputParameter(name="categories.offset", param_type=OutputParameterType.INTEGER, is_array=False),  # The offset of the first item in the response.,
			OutputParameter(name="categories.previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to previous page, or null if none.,
			OutputParameter(name="categories.total", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of categories available.,
			OutputParameter(name="categories.items", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of category objects.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Several_Browse_Categories.method, 
                                          Get_Several_Browse_Categories.url,
                                          Get_Several_Browse_Categories.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Several_Browse_Categories': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Track(BaseFunction):
    """Retrieve detailed information about a specific track by its Spotify ID."""
    name = "Get Track"
    url = "https://api.spotify.com/v1/tracks/{id}"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="id", param_type=ParameterType.STRING, required=True),  # Required. The Spotify ID of the track. Example: '11dFghVXANMlKmJXsNCbNl'.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # Optional. An ISO 3166-1 alpha-2 country code. If specified, limits the content to that market. If user access token's country is available, it takes priority. Example: 'ES'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="album", param_type=OutputParameterType.OBJECT, is_array=False),  # The album on which the track appears.,
			OutputParameter(name="album.album_type", param_type=OutputParameterType.STRING, is_array=False),  # Required. The type of the album. Allowed values: 'album', 'single', 'compilation'. Example: 'compilation'.,
			OutputParameter(name="album.total_tracks", param_type=OutputParameterType.INTEGER, is_array=False),  # Required. Total number of tracks in the album. Example: 9.,
			OutputParameter(name="album.available_markets", param_type=OutputParameterType.STRING, is_array=True),  # Markets where the album is available, identified by ISO 3166-1 alpha-2 codes. Example: ['CA','BR','IT'].,
			OutputParameter(name="album.external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # External URLs for the album.,
			OutputParameter(name="album.external_urls.spotify", param_type=OutputParameterType.STRING, is_array=False),  # The Spotify URL of the album.,
			OutputParameter(name="album.href", param_type=OutputParameterType.STRING, is_array=False),  # Link to API endpoint for full album details.,
			OutputParameter(name="album.id", param_type=OutputParameterType.STRING, is_array=False),  # Spotify ID of the album.,
			OutputParameter(name="album.images", param_type=OutputParameterType.OBJECT, is_array=True),  # Album cover images in various sizes.,
			OutputParameter(name="album.images.url", param_type=OutputParameterType.STRING, is_array=False),  # Source URL of the image.,
			OutputParameter(name="album.images.height", param_type=OutputParameterType.INTEGER, is_array=False),  # Nullable. Image height in pixels.,
			OutputParameter(name="album.images.width", param_type=OutputParameterType.INTEGER, is_array=False),  # Nullable. Image width in pixels.,
			OutputParameter(name="album.name", param_type=OutputParameterType.STRING, is_array=False),  # The name of the album.,
			OutputParameter(name="album.release_date", param_type=OutputParameterType.STRING, is_array=False),  # The release date of the album. Example: '1981-12'.,
			OutputParameter(name="album.release_date_precision", param_type=OutputParameterType.STRING, is_array=False),  # The precision of the release date. Allowed: 'year', 'month', 'day'.,
			OutputParameter(name="album.restrictions", param_type=OutputParameterType.OBJECT, is_array=False),  # Content restrictions if any.,
			OutputParameter(name="album.restrictions.reason", param_type=OutputParameterType.STRING, is_array=False),  # Reason for restriction. Allowed: 'market', 'product', 'explicit'.,
			OutputParameter(name="album.type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, typically 'album'.,
			OutputParameter(name="album.uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI of the album.,
			OutputParameter(name="artists", param_type=OutputParameterType.OBJECT, is_array=True),  # Artists of the track.,
			OutputParameter(name="artists.external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # External URLs for the artist.,
			OutputParameter(name="artists.external_urls.spotify", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URL for the artist.,
			OutputParameter(name="artists.href", param_type=OutputParameterType.STRING, is_array=False),  # API link to artist details.,
			OutputParameter(name="artists.id", param_type=OutputParameterType.STRING, is_array=False),  # Spotify ID of the artist.,
			OutputParameter(name="artists.name", param_type=OutputParameterType.STRING, is_array=False),  # Artist's name.,
			OutputParameter(name="artists.type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, e.g., 'artist'.,
			OutputParameter(name="artists.uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI for the artist.,
			OutputParameter(name="available_markets", param_type=OutputParameterType.STRING, is_array=True),  # Markets where the track is available, identified by ISO 3166-1 alpha-2 codes.,
			OutputParameter(name="disc_number", param_type=OutputParameterType.INTEGER, is_array=False),  # Disc number, usually 1.,
			OutputParameter(name="duration_ms", param_type=OutputParameterType.INTEGER, is_array=False),  # Length of the track in milliseconds.,
			OutputParameter(name="explicit", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Whether the track has explicit lyrics.,
			OutputParameter(name="external_ids", param_type=OutputParameterType.OBJECT, is_array=False),  # External IDs for the track.,
			OutputParameter(name="external_ids.isrc", param_type=OutputParameterType.STRING, is_array=False),  # International Standard Recording Code.,
			OutputParameter(name="external_ids.ean", param_type=OutputParameterType.STRING, is_array=False),  # European Article Number.,
			OutputParameter(name="external_ids.upc", param_type=OutputParameterType.STRING, is_array=False),  # Universal Product Code.,
			OutputParameter(name="external_urls", param_type=OutputParameterType.OBJECT, is_array=False),  # External URLs for the track.,
			OutputParameter(name="external_urls.spotify", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URL of the track.,
			OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to API endpoint for track details.,
			OutputParameter(name="id", param_type=OutputParameterType.STRING, is_array=False),  # Spotify ID of the track.,
			OutputParameter(name="is_playable", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Indicates if the track is playable in the given market.,
			OutputParameter(name="linked_from", param_type=OutputParameterType.OBJECT, is_array=False),  # Contains information if track is relinked to another track.,
			OutputParameter(name="restrictions", param_type=OutputParameterType.OBJECT, is_array=False),  # Restrictions if any.,
			OutputParameter(name="restrictions.reason", param_type=OutputParameterType.STRING, is_array=False),  # Reason for restriction: 'market', 'product', or 'explicit'.,
			OutputParameter(name="name", param_type=OutputParameterType.STRING, is_array=False),  # Track name.,
			OutputParameter(name="popularity", param_type=OutputParameterType.INTEGER, is_array=False),  # Track's popularity score (0-100).,
			OutputParameter(name="preview_url", param_type=OutputParameterType.STRING, is_array=False),  # URL to a 30-second preview of the track.,
			OutputParameter(name="track_number", param_type=OutputParameterType.INTEGER, is_array=False),  # Track's position in the album.,
			OutputParameter(name="type", param_type=OutputParameterType.STRING, is_array=False),  # Object type, typically 'track'.,
			OutputParameter(name="uri", param_type=OutputParameterType.STRING, is_array=False),  # Spotify URI of the track.,
			OutputParameter(name="is_local", param_type=OutputParameterType.BOOLEAN, is_array=False),  # Whether the track is from a local file.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Track.method, 
                                          Get_Track.url,
                                          Get_Track.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Track': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Playlist_Items(BaseFunction):
    """Retrieve the items (tracks or episodes) of a specified playlist, with optional filtering and pagination."""
    name = "Get Playlist Items"
    url = "https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="playlist_id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the playlist. This is a unique identifier for the playlist, e.g., '3cEYpjA9oz9GiPac4AsH4n'.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # A Spotify country code (ISO 3166-1 alpha-2). If specified, only content available in that market will be returned. Example: 'ES'.,
			Parameter(name="fields", param_type=ParameterType.STRING, required=False),  # A comma-separated list of the fields to include in the response. Supports nested object fields using parentheses. Example: 'items(added_at,track(name,href,album(name,href)))'.,
			Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Maximum number of items to return. Default is 20. Range: 1-50. Example: 10.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # The index of the first item to return. Default is 0. Example: 5.,
			Parameter(name="additional_types", param_type=ParameterType.STRING, required=False),  # A comma-separated list of item types supported besides 'track'. Valid types include 'track' and 'episode'. Used to support multiple content types.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # Link to the Web API endpoint returning the full result of the request.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # Maximum number of items in the response.,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=False),  # URL to the next page of items. Null if there is no next page.,
			OutputParameter(name="offset", param_type=OutputParameterType.INTEGER, is_array=False),  # The offset of the items returned.,
			OutputParameter(name="previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to the previous page of items. Null if there is no previous page.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of items available.,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of playlist track objects.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Playlist_Items.method, 
                                          Get_Playlist_Items.url,
                                          Get_Playlist_Items.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Playlist_Items': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Several_Audiobooks(BaseFunction):
    """Retrieve information for multiple audiobooks by their Spotify IDs, limited to certain markets."""
    name = "Get Several Audiobooks"
    url = "https://api.spotify.com/v1/audiobooks"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of Spotify IDs for the audiobooks. Maximum 50 IDs. Example: '18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ'.,
			Parameter(name="market", param_type=ParameterType.STRING, required=False),  # A country code (ISO 3166-1 alpha-2). If specified, only content available in that market will be returned. Example: 'ES'.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="audiobooks", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of audiobook objects, null items indicate unavailable audiobooks.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Several_Audiobooks.method, 
                                          Get_Several_Audiobooks.url,
                                          Get_Several_Audiobooks.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Several_Audiobooks': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Save_Shows_for_Current_User(BaseFunction):
    """Adds one or more shows to the current user's library. Requires 'user-library-modify' scope."""
    name = "Save Shows for Current User"
    url = "https://api.spotify.com/v1/me/shows"
    args_in_url = False
    method = "PUT"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of the Spotify IDs for the shows to be saved. Must include no more than 50 IDs. Example: '5CfCWKI5pZ28U0uOzXkDHe,5as3aKmN2k11yfDDDSrvaZ'.
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Save_Shows_for_Current_User.method, 
                                          Save_Shows_for_Current_User.url,
                                          Save_Shows_for_Current_User.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Save_Shows_for_Current_User': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Current_Users_Playlists(BaseFunction):
    """Retrieves the current user's playlists. Requires 'playlist-read-private' scope."""
    name = "Get Current User's Playlists"
    url = "https://api.spotify.com/v1/me/playlists"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # The maximum number of playlists to return. Default is 20. Min is 1, max is 50.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # The index of the first playlist to return. Default is 0.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # A link to the Web API endpoint returning the full result of the request.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # The maximum number of items in the response set.,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=False),  # URL to the next page of the result set, or null if none.,
			OutputParameter(name="offset", param_type=OutputParameterType.INTEGER, is_array=False),  # The offset of the Playlist objects returned.,
			OutputParameter(name="previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to the previous page of the result set, or null if none.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # The total number of playlists available.,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of playlist objects, each containing details like name, owner, images, tracks, etc.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Current_Users_Playlists.method, 
                                          Get_Current_Users_Playlists.url,
                                          Get_Current_Users_Playlists.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Current_Users_Playlists': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Unfollow_Playlist(BaseFunction):
    """Removes the current user as a follower of a playlist. Requires 'playlist-modify-public' or 'playlist-modify-private' scope."""
    name = "Unfollow Playlist"
    url = "https://api.spotify.com/v1/playlists/{playlist_id}/followers"
    args_in_url = True
    method = "DELETE"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="playlist_id", param_type=ParameterType.STRING, required=True),  # The Spotify ID of the playlist to unfollow.
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Unfollow_Playlist.method, 
                                          Unfollow_Playlist.url,
                                          Unfollow_Playlist.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Unfollow_Playlist': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Remove_Users_Saved_Episodes(BaseFunction):
    """Removes one or more episodes from the current user's library. Requires 'user-library-modify' scope."""
    name = "Remove User's Saved Episodes"
    url = "https://api.spotify.com/v1/me/episodes"
    args_in_url = False
    method = "DELETE"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="ids", param_type=ParameterType.STRING, required=True),  # A comma-separated list of the Spotify IDs of episodes to remove, with a maximum of 50 IDs. Example: '4iV5W9uYEdYUVa79Axb7Rh,1301WleyT98MSxVHPZCA6M'.,
			Parameter(name="ids_array", param_type=OutputParameterType.OBJECT, required=False),  # An array of Spotify IDs of episodes to remove, maximum 50 items. The body of the request supports either 'ids' parameter or 'ids_array'.
        ]

    def get_output_schema(self):
        return [
            
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Remove_Users_Saved_Episodes.method, 
                                          Remove_Users_Saved_Episodes.url,
                                          Remove_Users_Saved_Episodes.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Remove_Users_Saved_Episodes': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Client_Credentials_Flow_Token(BaseFunction):
    """Obtains an access token using the Client Credentials flow for server-to-server authentication. Does not access user data."""
    name = "Client Credentials Flow Token"
    url = "https://accounts.spotify.com/api/token"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="grant_type", param_type=ParameterType.STRING, required=True),  # Set to 'client_credentials'.,
			Parameter(name="client_id", param_type=ParameterType.STRING, required=True),  # Your Spotify application's client ID.,
			Parameter(name="client_secret", param_type=ParameterType.STRING, required=True),  # Your Spotify application's client secret.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="access_token", param_type=OutputParameterType.STRING, is_array=False),  # A token that can be used in subsequent requests to the Spotify API.,
			OutputParameter(name="token_type", param_type=OutputParameterType.STRING, is_array=False),  # Type of the token, always 'Bearer'.,
			OutputParameter(name="expires_in", param_type=OutputParameterType.INTEGER, is_array=False),  # The time in seconds before the token expires.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Client_Credentials_Flow_Token.method, 
                                          Client_Credentials_Flow_Token.url,
                                          Client_Credentials_Flow_Token.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Client_Credentials_Flow_Token': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Users_Saved_Audiobooks(BaseFunction):
    """Retrieve a list of audiobooks saved in the current Spotify user's library."""
    name = "Get User's Saved Audiobooks"
    url = "https://api.spotify.com/v1/me/audiobooks"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # The maximum number of items to return. Default: 20. Range: 1 - 50.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # The index of the first item to return. Default: 0.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # A link to the Web API endpoint returning the full result of the request.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # The maximum number of items in the response.,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=False),  # URL to the next page of items, or null if none.,
			OutputParameter(name="offset", param_type=OutputParameterType.INTEGER, is_array=False),  # The offset of the items returned.,
			OutputParameter(name="previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to the previous page of items, or null if none.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # The total number of items available.,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of saved audiobook objects.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Users_Saved_Audiobooks.method, 
                                          Get_Users_Saved_Audiobooks.url,
                                          Get_Users_Saved_Audiobooks.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Users_Saved_Audiobooks': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class StartResume_a_Users_Playback(BaseFunction):
    """Start or resume current playback on the user's device."""
    name = "Start/Resume a User's Playback"
    url = "https://api.spotify.com/v1/me/player/play"
    args_in_url = True
    method = "PUT"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="device_id", param_type=ParameterType.STRING, required=False),  # The ID of the device to target. If not specified, the active device is used.,
			Parameter(name="body", param_type=OutputParameterType.OBJECT, required=True),  # JSON body with options for playback.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="status_code", param_type=OutputParameterType.INTEGER, is_array=False),  # HTTP status code indicating success (204) or errors like 401, 403, 429.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(StartResume_a_Users_Playback.method, 
                                          StartResume_a_Users_Playback.url,
                                          StartResume_a_Users_Playback.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'StartResume_a_Users_Playback': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Users_Saved_Tracks(BaseFunction):
    """Retrieve a list of songs saved in the current user's library."""
    name = "Get User's Saved Tracks"
    url = "https://api.spotify.com/v1/me/tracks"
    args_in_url = False
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="market", param_type=ParameterType.STRING, required=False),  # ISO 3166-1 alpha-2 country code to filter content available in that market.,
			Parameter(name="limit", param_type=ParameterType.INTEGER, required=False),  # Maximum number of items to return. Default: 20. Range: 1 - 50.,
			Parameter(name="offset", param_type=ParameterType.INTEGER, required=False),  # The index of the first item to return. Default: 0.
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # A link to the Web API endpoint returning the full result.,
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # The maximum number of items in the response.,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=False),  # URL to the next page of items, or null if none.,
			OutputParameter(name="offset", param_type=OutputParameterType.INTEGER, is_array=False),  # The offset of the items returned.,
			OutputParameter(name="previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to the previous page of items, or null if none.,
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # The total number of saved tracks.,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # Array of saved track objects.
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Users_Saved_Tracks.method, 
                                          Get_Users_Saved_Tracks.url,
                                          Get_Users_Saved_Tracks.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Users_Saved_Tracks': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)



class Get_Users_Playlists(BaseFunction):
    """Retrieves a list of playlists owned or followed by a specific Spotify user."""
    name = "Get User's Playlists"
    url = "https://api.spotify.com/v1/users/{user_id}/playlists"
    args_in_url = True
    method = "GET"

    def __init__(self):
        self.api_config = APIClientConfig()
    
    def get_parameter_schema(self):
        return [
            Parameter(name="user_id", param_type=ParameterType.STRING, required=True),  # The Spotify user ID of the user whose playlists are to be retrieved. Example: 'smedjan'
        ]

    def get_output_schema(self):
        return [
            OutputParameter(name="href", param_type=OutputParameterType.STRING, is_array=False),  # A link to the Web API endpoint returning the full result of the request. Example: 'https://api.spotify.com/v1/me/shows?offset=0&limit=20',
			OutputParameter(name="limit", param_type=OutputParameterType.INTEGER, is_array=False),  # The maximum number of items in the response (as set in the query or by default). Example: 20,
			OutputParameter(name="next", param_type=OutputParameterType.STRING, is_array=False),  # URL to the next page of items. ('null' if none). Example: 'https://api.spotify.com/v1/me/shows?offset=1&limit=1',
			OutputParameter(name="offset", param_type=OutputParameterType.INTEGER, is_array=False),  # The offset of the items returned (as set in the query or by default). Example: 0,
			OutputParameter(name="previous", param_type=OutputParameterType.STRING, is_array=False),  # URL to the previous page of items. ('null' if none). Example: 'https://api.spotify.com/v1/me/shows?offset=1&limit=1',
			OutputParameter(name="total", param_type=OutputParameterType.INTEGER, is_array=False),  # Total number of items available to return. Example: 4,
			OutputParameter(name="items", param_type=OutputParameterType.OBJECT, is_array=True),  # An array of playlist objects
        ]
    
    def process(self, input_data: StandardInput) -> StandardOutput:
        try:
            out = self.api_config.request(Get_Users_Playlists.method, 
                                          Get_Users_Playlists.url,
                                          Get_Users_Playlists.args_in_url,
                                          input_data.validated_data)
            return StandardOutput(out, self.get_output_schema())
        except Exception as e:
            error_msg = f"Error running function 'Get_Users_Playlists': {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)

