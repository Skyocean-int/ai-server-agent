from ai_agent.tools.file_cache_service import FileReader

async def main():
    reader = FileReader()
    await reader.initialize()
    try:
        # Search for config files
        files = await reader.search_files("config")
        for file in files:
            print(f"Found: {file['path']} on {file['server']}")
            
        # Search documentation
        docs = await reader.search_documentation(["configuration", "setup"])
        print("\nRelevant documentation:", docs)
    finally:
        await reader.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
