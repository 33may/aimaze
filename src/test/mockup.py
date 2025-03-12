import requests
from urllib.parse import urlencode

def request_authorisation(
    client_id,
    redirect_uri,
    state,
    response_type="code",
    scope=None,
    reauthenticate=None,
    hint=None
):
    """
    Request authorisation from the Companies House Identity Service.
    Returns the URL to redirect the user to.
    """
    base_url = "https://identity.company-information.service.gov.uk/oauth2/authorise"

    # Build query parameters
    params = {
        "response_type": response_type,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": state
    }

    # Add optional parameters if provided
    if scope:
        params["scope"] = scope
    if reauthenticate is not None:
        params["reauthenticate"] = str(reauthenticate).lower()
    if hint:
        params["hint"] = hint

    # Construct the full URL
    authorisation_url = f"{base_url}?{urlencode(params)}"

    return authorisation_url
