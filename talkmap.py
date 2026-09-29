# Leaflet cluster map of talk locations
#
# Run this from the repository root. This scrapes the location YAML field from
# each .md file in _talks/, geolocates it with geopy/Nominatim, and writes the
# marker data to talkmap/org-locations.js.
#
# Only the data file is regenerated. getorg's output_html_cluster_map would
# also overwrite talkmap/map.html and talkmap/leaflet_dist/ with its outdated
# template (Leaflet 1.0.0-beta.2, http tiles); those files are hand-maintained
# and must not be touched.
import frontmatter
import glob
import getorg
from geopy import Nominatim
from geopy.exc import GeocoderTimedOut

# Set the default timeout, in seconds
TIMEOUT = 5

# Collect the Markdown files
g = glob.glob("_talks/*.md")
if not g:
    raise SystemExit("No _talks/*.md files found; run this from the repository root.")

# Prepare to geolocate
geocoder = Nominatim(user_agent="academicpages.github.io")
location_dict = {}
location = ""
permalink = ""
title = ""

# Perform geolocation
for file in g:
    # Read the file
    data = frontmatter.load(file)
    data = data.to_dict()

    # Press on if the location is not present
    if 'location' not in data:
        continue

    # Prepare the description
    title = data['title'].strip()
    venue = data['venue'].strip()
    location = data['location'].strip()
    description = f"{title}<br />{venue}; {location}"

    # Geocode the location and report the status
    try:
        location_dict[description] = geocoder.geocode(location, timeout=TIMEOUT)
        print(description, location_dict[description])
    except ValueError as ex:
        print(f"Error: geocode failed on input {location} with message {ex}")
    except GeocoderTimedOut as ex:
        print(f"Error: geocode timed out on input {location} with message {ex}")
    except Exception as ex:
        print(f"An unhandled exception occurred while processing input {location} with message {ex}")

# Save the marker data, leaving the hand-edited map page and Leaflet files alone
getorg.orgmap.location_dict_to_jsvar(location_dict, "talkmap/org-locations.js", hashed_usernames=False)
