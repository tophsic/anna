


from will.mixins import StorageMixin
from will.storage.redis_storage import RedisStorage



class ExtendedStorageMixin(object):



    def bootstrap_extended_storage(self):
        if not isinstance(self, StorageMixin):
            raise Exception("%s object should be an insance of StorageMixin" % str(self))

        self.bootstrap_storage()

        if not isinstance(self.storage, RedisStorage):
            raise Exception("Only Redis storage is supported")



    def len(self, key):
        if not self.storage.redis.exists(key):
            return 0

        return self.storage.redis.llen(key)



    def range(self, key, start, stop):
        return self.storage.redis.lrange(self.REDIS_KEY, start, stop)



    def push(self, key, value):
        self.storage.redis.lpush(key, value)



    def trim(self, key, value):
        self.storage.redis.lrem(key, value, 0)
