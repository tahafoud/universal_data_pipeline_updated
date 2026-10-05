from pymongo import MongoClient


class MongoStore:
    def __init__(self, uri, database):
        self.client = MongoClient(uri)
        self.db = self.client[database]

    def save(self, df, collection):
        records = df.to_dict(orient="records")

        if not records:
            return 0

        self.db[collection].delete_many({})
        self.db[collection].insert_many(records)
        return len(records)

    def close(self):
        self.client.close()
