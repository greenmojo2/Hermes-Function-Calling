# Import SonarrAPI Class
from pyarr import SonarrAPI

# Set Host URL and API-Key
host_url = 'http://tower.tail44b475.ts.net:8989'

# You can find your API key in Settings > General.
api_key = '4da58ee293464875982816e46d40a193'

# Instantiate SonarrAPI Object
sonarr = SonarrAPI(host_url, api_key)

# Get and print TV Shows
print(sonarr.get_series())