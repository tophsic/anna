from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
from will.storage.redis_storage import RedisStorage

from mixins import ExtendedStorageMixin

import logging


class ServicesPlugin(WillPlugin, ExtendedStorageMixin):



    REDIS_KEY = "services"



    @respond_to("^Add service (?P<service>.*)", admin_only=True)
    def add_service(self, message, service=None):
        self.bootstrap_extended_storage()

        if not service:
            self.say("Sorry, you didn't say what service to add.", message=message)
            return

        services = self.range(self.REDIS_KEY, 0, -1)

        if service in services:
            self.say("Sorry, service `%`s already exists." % service, message=message)
            return

        self.say("Ok. Adding service `%s.`" % service, message=message)
        self.push(self.REDIS_KEY, service)



    @respond_to("^Remove service (?P<service>.*)", admin_only=True)
    def remove_service(self, message, service=None):
        self.bootstrap_extended_storage()

        if not service:
            self.say("Sorry, you didn't say what service to add.", message=message)
            return

        services = self.range(self.REDIS_KEY, 0, -1)

        if not service in services:
            self.say("Sorry, service `%s` does not exist." % service, message=message)
            return

        self.say("Ok. Removing service `%s`." % service, message=message)
        self.trim(self.REDIS_KEY, service)



    @respond_to("^Give me all services")
    def list_services(self, message):
        self.bootstrap_extended_storage()

        servicesLen = self.len(self.REDIS_KEY)
        services = self.range(self.REDIS_KEY, 0, -1)

        self.say("%d services are defined:\n"
                 "%s" % (servicesLen, ", ".join(services)), message=message)



    @respond_to("^Redis?")
    def is_redis_here(self, message, admin_only=True):
        self.bootstrap_extended_storage()

        self.say("Redis is available", message=message)
