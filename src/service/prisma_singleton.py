# prisma_singleton.py
from prisma import Prisma

class PrismaSingleton:
    _instance = None

    @staticmethod
    def get_instance():
        if PrismaSingleton._instance is None:
            PrismaSingleton._instance = Prisma()
            PrismaSingleton._instance.connect()
        return PrismaSingleton._instance

    @staticmethod
    def disconnect():
        if PrismaSingleton._instance is not None:
            PrismaSingleton._instance.disconnect()
            PrismaSingleton._instance = None