import os
from sentinelhub import SHConfig, SentinelHubRequest, BBox, CRS, DataCollection, MimeType
from dotenv import load_dotenv

load_dotenv()

config = SHConfig()

# Map YOUR variable names:
config.sh_client_id = os.getenv("SENTINEL_CLIENT_ID")
config.sh_client_secret = os.getenv("SENTINEL_CLIENT_SECRET")

instance_id = os.getenv("SENTINEL_INSTANCE_ID")
if instance_id:
    config.instance_id = instance_id

print("Testing SentinelHub Credentials...")
print("Client ID:", config.sh_client_id)
print("Client Secret:", "YES" if config.sh_client_secret else "NO")

if not config.sh_client_id or not config.sh_client_secret:
    print("❌ ERROR: Missing CLIENT_ID or CLIENT_SECRET in .env")
    exit()

# small bbox to test API access
bbox = BBox([14.505, 46.05, 14.51, 46.055], crs=CRS.WGS84)

request = SentinelHubRequest(
    data_folder="./test_output",
    evalscript="""
    function setup() {
        return {
            input: ["B02"],
            output: { id: "default", bands: 1, sampleType: "FLOAT32" }
        };
    }
    function evaluatePixel(sample) {
        return [sample.B02];
    }
    """,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L2A
        )
    ],
    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
    bbox=bbox,
    size=(20, 20),
    config=config
)

try:
    print("Sending request to SentinelHub...")
    data = request.get_data(save_data=True)
    print("✅ SUCCESS: Credentials validated")
    print("Output saved at ./test_output/")
except Exception as e:
    print("❌ FAILED: SentinelHub rejected your request")
    print("Error:", e)
