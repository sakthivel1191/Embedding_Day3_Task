import os
import json
import hashlib
def get_file_hash(file_path):
    sha = hashlib.sha256()
    with open(file_path, "rb") as file:
        sha.update(file.read())
    return sha.hexdigest()
def should_process(file_path):
    current_hash = get_file_hash(file_path)
    if os.path.exists("file_hashes.json"):
        with open("file_hashes.json", "r") as file:
            hashes = json.load(file)
    else:
        hashes = {}
    file_name = os.path.basename(file_path)
    if hashes.get(file_name) == current_hash:
        print("File not changed. Skipping.")
        return False
    hashes[file_name] = current_hash
    with open("file_hashes.json", "w") as file:
        json.dump(hashes, file, indent=4)
    print("File changed. Processing.")
    return True
if should_process("policy.txt"):
    print("Start indexing...")
    