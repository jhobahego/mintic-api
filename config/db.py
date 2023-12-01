import motor.motor_asyncio

from decouple import config

client = motor.motor_asyncio.AsyncIOMotorClient(config("MONGODB_URL"))
conn = client.misiontic
