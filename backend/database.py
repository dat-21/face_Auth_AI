from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/testAI")
DB_NAME = "testAI"

class Database:
    client: AsyncIOMotorClient = None
    db = None

    async def connect(self):
        self.client = AsyncIOMotorClient(MONGO_URL)
        self.db = self.client[DB_NAME]
        # Create unique index for user_id if needed
        await self.db.users.create_index("user_id", unique=True)
        print("Connected to MongoDB")

    async def close(self):
        if self.client:
            self.client.close()
            print("Disconnected from MongoDB")

db = Database()
