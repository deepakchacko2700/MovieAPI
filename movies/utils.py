import requests, os
from requests.auth import HTTPBasicAuth
from requests.exceptions import Timeout, RequestException
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, wait_fixed

# take environment variable from.env file
load_dotenv()


@retry(stop=stop_after_attempt(7), wait=wait_fixed(2))
def get_movies():
    """Get paginated list of movies from third party api"""
    api_url = 'https://demo.credy.in/api/v1/maya/movies/'
    try:
        username = os.getenv('username')
        password = os.getenv('password')
        auth = HTTPBasicAuth(username, password) # creating http basic auth    
        # get movies list from third party api
        response = requests.get(api_url, auth=auth, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx, 5xx)
        return response.json()  # Assuming the API returns JSON data
    except Timeout:
        print("Timeout error occurred while fetching data from the API.")
        raise Timeout("Request timed out, retrying...")
    except RequestException as e:
        print(f"Error occurred: {e}. Retrying...")
        raise RequestException("Request failed, retrying...")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise e 
