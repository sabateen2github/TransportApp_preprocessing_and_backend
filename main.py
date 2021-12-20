from flask import Flask
from flask import request
from google.cloud import storage
import zipfile
import json

import os

# version = 20201101t003650

app = Flask(__name__)


def getPath(tree, toId):
    found = None

    path = []

    queue = []
    queue.append(tree)

    while len(queue) > 0:
        print(len(queue))

        value = queue.pop(0)
        if "checked" in value:
            continue

        if "receivedAt" not in value:
            value["receivedAt"] = []

        if value["node"] == toId:
            while "parent" in value:
                path.append({"id": value["node"], "receive": value["receivedAt"]})
                value = value["parent"]
            path.append({"id": value["node"], "receive": value["receivedAt"]})
            break
        if "children" in value:
            for item in value["children"]:
                item["parent"] = value
                queue.append(item)
        value["checked"] = True

    path.reverse()

    if len(path) > 0:
        found = path
    return found


@app.route('/')
def hello():
    try:
        fromID = int(request.args.get("from"))
        toID = int(request.args.get("to"))

        if fromID == toID:
            return json.dumps({"error": "same id", "code": 1})

        storage_client = storage.Client()

        bucket_name = "new-age-192017.appspot.com"
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob("generated_trees_zip/{}.json.zip".format(fromID))

        if not os.path.isdir("/tmp/"):
            os.mkdir("/tmp")

        blob.download_to_filename("/tmp/{}.json.zip".format(fromID))

        archive = zipfile.ZipFile("/tmp/{}.json.zip".format(fromID), "r")
        file = archive.open("Users/alaa2/OneDrive/Desktop/point_to_point/generated_trees/{}.json".format(fromID))
        st = json.load(file)
        archive.close()

        path = getPath(st, toID)
        if path is None:
            return json.dumps({"error": "no Path", "code": 2})
        else:
            return json.dumps(path)
    except Exception as e:
        return str(e)

    return json.dumps({"welcome": "Hello World!"})


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python38_app]
