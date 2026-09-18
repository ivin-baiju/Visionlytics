import os

from huggingface_hub import HfApi

api = HfApi(token=os.environ["HF_TOKEN"])
repo_id = "ivin-baiju/Visionlytics"

print("Uploading to HF Spaces...")
api.upload_folder(
    folder_path=".",
    repo_id=repo_id,
    repo_type="space",
    ignore_patterns=[".git*", ".venv*", "__pycache__", ".pytest_cache", ".DS_Store", "outputs/*"],
)
print("Done!")
