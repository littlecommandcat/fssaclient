import asyncio
import json

from client import AsyncClient

async def main() -> dict:
    async with AsyncClient() as client:
        results = {}

        results["announcements"] = [
            item.to_dict() for item in await client.get_announcements()
        ]
        results["events"] = [item.to_dict() for item in await client.get_events()]
        results["documents"] = [item.to_dict() for item in await client.get_documents()]

        results["log_size"] = await client.get_log_size()
        results["log_stats"] = (await client.get_log_stats()).to_dict()
        results["log_keys"] = [item.to_dict() for item in await client.get_log_keys()]
        results["log_entries"] = [
            item.to_dict() for item in await client.get_log_entries(from_index=1, limit=10)
        ]
        results["log_consistency"] = await client.get_log_consistency(
            from_size=1, to_size=10
        )
        results["log_inclusion"] = (
            await client.get_log_inclusion(idx=1, tree_size=10)
        ).to_dict()

        return results


if __name__ == "__main__":
    data = asyncio.run(main())
    print(json.dumps(data, ensure_ascii=False, indent=4))
