"""Some utils related to testing"""

class FakeBackgroundTask:
    """A fake background task to avoid running background tasks during tests"""

    def __init__(self):
        self.tasks = []

    def add_task(self, fn, *args, **kwargs):
        self.tasks.append((fn, args, kwargs))

    async def run(self):
        while self.tasks:
            fn, args, kwargs = self.tasks.pop()
            await fn(*args, **kwargs)


async def clean_neo4j_db(neo4j):
    """Delete all nodes and relations in the database"""
    async with neo4j.session() as session:
        query = "MATCH (n) DETACH DELETE n"
        await session.run(query)
        # list all indexes and drop them
        query = """
            SHOW INDEXES
            YIELD name AS idxname
            RETURN idxname
        """
        indexes = await session.run(query)
        for index in await indexes.values():
            query = f"DROP INDEX {index[0]} IF EXISTS"
            await session.run(query)