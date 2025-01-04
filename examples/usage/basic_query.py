from ai_agent.core.query_handler import QueryHandler

async def main():
    handler = QueryHandler()
    try:
        # Basic file search
        response = await handler.process_query("find nginx configuration files")
        print(response)

        # Configuration check
        response = await handler.process_query("check server status and configurations")
        print(response)
    finally:
        await handler.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
