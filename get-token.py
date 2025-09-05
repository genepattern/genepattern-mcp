#!/usr/bin/env python

import os
import requests
from optparse import OptionParser
import sys


def get_auth_token(gp_url, username, password):
    """
    Authenticates with a GenePattern server's OAuth2 endpoint to get a token.

    This implementation sends credentials as query parameters in a POST request,
    matching the specific requirements of some GenePattern server versions.

    Args:
        gp_url (str): The base URL of the GenePattern server (e.g., http://127.0.0.1:8080/gp).
        username (str): The GenePattern username.
        password (str): The GenePattern password.

    Returns:
        The access token as a string, or None if authentication fails.
    """
    token_url = f"{gp_url.rstrip('/')}/rest/v1/oauth2/token"

    # Parameters are sent in the query string, not the POST body
    params = {
        'grant_type': 'password',
        'username': username,
        'password': password,
        'client_id': f'GenePatternMCP-{username}'
    }

    headers = {
        'Accept': 'application/json'
    }

    try:
        # The request body is empty, as shown in the example (data=b'')
        response = requests.post(token_url, params=params, headers=headers, data=b'')
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        token_data = response.json()
        access_token = token_data.get('access_token')

        if not access_token:
            print("Error: 'access_token' not found in the server response.", file=sys.stderr)
            return None

        return access_token

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP Error: {http_err.response.status_code} - {http_err.response.text}", file=sys.stderr)
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Request Exception: Could not connect to {token_url}. Error: {req_err}", file=sys.stderr)
        return None
    except ValueError:  # Catches json.JSONDecodeError in Python 3.5+
        print("Error: Failed to decode JSON from server response.", file=sys.stderr)
        return None


def main():
    """Main function to parse arguments and execute the token retrieval."""
    parser = OptionParser(usage="usage: %prog -s SERVER_URL -u USERNAME -p PASSWORD")
    parser.add_option("-s", "--server", dest="server_url", default="https://cloud.genepattern.org/gp",
                      help="The URL of the GenePattern server.")
    parser.add_option("-u", "--username", dest="username",
                      help="Your GenePattern username.")
    parser.add_option("-p", "--password", dest="password",
                      help="Your GenePattern password.")

    (options, args) = parser.parse_args()

    if not all([options.server_url, options.username, options.password]):
        parser.print_help()
        sys.exit(1)

    if not all([options.server_url, options.username, options.password]):
        parser.print_help()
        sys.exit(1)

    print(f"Requesting token for user '{options.username}'...", file=sys.stderr)

    token = get_auth_token(options.server_url, options.username, options.password)

    if token:
        print("Token retrieved successfully.", file=sys.stderr)

        # Print the export command to standard output for the shell to evaluate
        print('Please run the following command to set the token in your environment:\n')
        print(f'export GENEPATTERN_KEY="{token}\n"')
    else:
        print("\nFailed to retrieve token.", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()