from dotenv import load_dotenv
import motor.motor_asyncio
import os
from os.path import join, dirname

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

client = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get("MONGODB_URL"))
conn = client.misiontic