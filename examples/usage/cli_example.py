import argparse
import asyncio
from ai_agent.core.query_handler import QueryHandler

async def main(args):
    handler = QueryHandler()
    try:
        if args.command == "query":
            response = await handler.process_query(args.query)
            print(response)
        elif args.command == "search":
            files = await handler.search_files(args.query)
            for file in files:
                print(f"Found: {file['path']}")
    finally:
        await handler.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["query", "search"])
    parser.add_argument("query", help="Query string")
    args = parser.parse_args()
    asyncio.run(main(args))
