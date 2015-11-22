from will.plugin import WillPlugin
from will.decorators import respond_to
from will.storage.redis_storage import RedisStorage

from mixins import ExtendedStorageMixin
from mixins import QuestionsMixin
from mixins import Question

import logging


class ServicesPlugin(WillPlugin, ExtendedStorageMixin, QuestionsMixin):



    REDIS_KEY = "services"
    REDIS_LOCK_KEY = "services_locked"



    @respond_to("^Add service (?P<service>.*)", admin_only=True)
    def add_service(self, message, service=None):
        """Add service ____: add a new service."""

        self.bootstrap_extended_storage()

        if not service:
            self.say("Sorry, you didn't say what service to add.", message=message)
            return

        services = self._services()

        if service in services:
            self.say("Sorry, service `%`s already exists." % service, message=message)
            return

        self.say("Ok. Adding service `%s`." % service, message=message)
        self.push(self.REDIS_KEY, service)



    @respond_to("^Remove service (?P<service>.*)", admin_only=True)
    def remove_service(self, message, service=None):
        """Remove service ____: remove an defined service."""

        self.bootstrap_extended_storage()

        if not service:
            self.say("Sorry, you didn't say what service to add.", message=message)
            return

        services = self.range(self.REDIS_KEY, 0, -1)

        if not service in services:
            self.say("Sorry, service `%s` does not exist." % service, message=message)
            return

        self.say("Are you sure you want to remove service %s?" %service, message=message)

        self.add_question(Question(message=message, callback=self._remove_service, item=service))

    def _remove_service(self, message, item):
        self.say("Ok. Removing service `%s`." % item, message=message)
        self.trim(self.REDIS_KEY, item)



    @respond_to("^Give me all services")
    def list_services(self, message):
        """Give me all services: list defined services."""
        self.bootstrap_extended_storage()

        services = self._services()

        self.say("%d services are defined:\n"
                 "%s" % (len(services), ", ".join(services)), message=message)



    @respond_to("^Give me all locked services")
    def list_locked_services(self, message):
        """Give me all locked services: list locked services."""
        self.bootstrap_extended_storage()

        services = self._locked_services()

        self.say("%d services are locked:\n"
                 "%s" % (len(services), ", ".join(services)), message=message)



    @respond_to("^Redis\?")
    def is_redis_here(self, message, admin_only=True):
        """Redis?: is Redis available?"""
        self.bootstrap_extended_storage()

        self.say("Redis is available", message=message)



    @respond_to("^Can I take (?P<service>.*)\?$")
    def can_i_take(self, message, service=None):
        """Can I take ____?: lock a service"""
        self.bootstrap_extended_storage()

        if not service:
            self.say("Sorry, you didn't say what service to add.", message=message)
            return

        services = self._services()

        if not service in services:
            self.say("Sorry, service `%s` does not exist." % service, message=message)
            return

        locked_services = self._locked_services()

        if service in locked_services:
            self.say("Sorry, service `%s` is already locked." % service, message=message)
            return

        self.say("Sure @%s, you can take service %s" % (message.sender.nick, service), message=message)
        self.push(self.REDIS_LOCK_KEY, service)




    @respond_to("^I unlock (?P<service>.*)")
    def unlock_service(self, message, service=None):
        """I unlock ____?: unlock a service"""
        self.bootstrap_extended_storage()

        if not service:
            self.say("Sorry, you didn't say what service to add.", message=message)
            return

        services = self._services()

        if not service in services:
            self.say("Sorry, service `%s` does not exist." % service, message=message)
            return

        locked_services = self._locked_services()

        if not service in locked_services:
            self.say("Sorry, service `%s` is not already." % service, message=message)
            return

        self.say("@all, @%s unlock service %s" % (message.sender.nick, service), message=message)
        self.trim(self.REDIS_LOCK_KEY, service)




    def _services(self):
        return self.range(self.REDIS_KEY, 0, -1)



    def _locked_services(self):
        return self.range(self.REDIS_LOCK_KEY, 0, -1)
