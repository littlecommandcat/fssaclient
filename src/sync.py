import json

from client import SyncClient

def main() -> dict:
    with SyncClient() as client:
        results = {}

        results["announcements"] = [
            item.to_dict() for item in client.get_announcements()
        ]
        results["events"] = [item.to_dict() for item in client.get_events()]
        results["documents"] = [item.to_dict() for item in client.get_documents()]

        results["log_size"] = client.get_log_size()
        results["log_stats"] = client.get_log_stats().to_dict()
        results["log_keys"] = [item.to_dict() for item in client.get_log_keys()]
        results["log_entries"] = [
            item.to_dict() for item in client.get_log_entries(from_index=1, limit=10)
        ]
        results["log_consistency"] = client.get_log_consistency(from_size=1, to_size=10)
        results["log_inclusion"] = client.get_log_inclusion(idx=1, tree_size=10).to_dict()

        return results


if __name__ == "__main__":
    print(json.dumps(main(), ensure_ascii=False, indent=4))
