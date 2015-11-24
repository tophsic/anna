from will.plugin import WillPlugin
from will import settings
from will.decorators import require_settings
from will.decorators import respond_to
from will.storage.redis_storage import RedisStorage

from mixins import ExtendedStorageMixin
from mixins import QuestionsMixin
from mixins import Question

import threading
import datetime


class ServicesPlugin(WillPlugin, ExtendedStorageMixin, QuestionsMixin):



    REDIS_KEY = "services"
    REDIS_LOCK_KEY = "services_locked"



    # Add service {{{
    @respond_to("^Add service (?P<service>.*)", acl=['service_managers'])
    def add_service(self, message, service=None):
        """Add service ____: add a new service."""

        self.bootstrap_extended_storage()

        if not service:
            self.say("Sorry, you didn't say what service to add.", message=message)
            return

        services = self._services()

        if service in services:
            self.say("Sorry, service `%s` already exists." % service, message=message)
            return

        self.say("Ok. Adding service `%s`." % service, message=message)
        self.push(self.REDIS_KEY, service)
    # }}}



    # Remove service {{{
    @respond_to("^Remove service (?P<service>.*)", acl=['service_managers'])
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

        self.say("@%s, are you sure you want to remove service %s?" % (message.sender.name, service), message=message)

        arguments = dict()
        arguments['service'] = service
        question = Question(message=message, yes_callback=self._remove_service, no_callback=self._no_remove_service, arguments=arguments)
        self.add_question(question)

    def _remove_service(self, question, message, arguments):
        if not arguments.has_key('service'):
            return

        self.say("Ok @%s. Removing service `%s`." % (message.sender.name, arguments['service']), message=message)
        self.trim(self.REDIS_KEY, argument['service'])

    def _no_remove_service(self, question, message, arguments):
        if not arguments.has_key('service'):
            return

        self.say("Ok @%s. I am not removing service `%s`." % (message.sender.name, arguments['service']), message=message)
    # }}}



    # Give me {{{
    @respond_to("^(Give me )?all services")
    def list_services(self, message):
        """Give me all services: list defined services."""
        self.bootstrap_extended_storage()

        services = self._services()

        self.say("%d services are defined:\n"
                 "%s" % (len(services), ", ".join(services)), message=message)



    @respond_to("^(Give me )?locked services")
    def list_locked_services(self, message):
        """Give me all locked services: list locked services."""
        self.bootstrap_extended_storage()

        services = self._locked_services()

        self.say("%d services are locked:\n"
                 "%s" % (len(services), ", ".join(services)), message=message)
    # }}}



    @respond_to("^Redis\?")
    def is_redis_here(self, message):
        """Redis?: is Redis available?"""
        self.bootstrap_extended_storage()

        self.say("Redis is available", message=message)



    # Lock a service {{{
    @require_settings("SERVICE_LOCK_DELAY",)
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

        self.say("Hey @all, @%s wants to lock service %s, is that ok for you?" % (message.sender.name, service), message=message)

        arguments = dict()
        arguments['service'] = service
        question = LockServiceQuestion(
            message=message,
            no_callback=self._no_lock_service,
            yes_callback=self._lock_service,
            arguments=arguments,
            receiver='all'
            )
        self.add_question(question)

    def _lock_service(self, question, message, arguments):
        if not arguments.has_key('service'):
            return

        self.say("Sure @%s, you can take service %s" % (message.sender.name, arguments['service']), message=message)
        self.push(self.REDIS_LOCK_KEY, arguments['service'])

    def _no_lock_service(self, question, message, arguments):
        if not arguments.has_key('service'):
            return

        self.say("@%s, you can not take service %s, see @%s" % (question.message.sender.name, arguments['service'], message.sender.name), message=message)



    @respond_to("^(I )?unlock (?P<service>.*)")
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
            self.say("Sorry, service `%s` is not locked." % service, message=message)
            return

        self.say("@all, @%s unlock service %s" % (message.sender.name, service), message=message)
        self.trim(self.REDIS_LOCK_KEY, service)
    # }}}




    def _services(self):
        return self.range(self.REDIS_KEY, 0, -1)



    def _locked_services(self):
        return self.range(self.REDIS_LOCK_KEY, 0, -1)






class LockServiceQuestion(Question):

    STATUS_PENDING = "pending"
    STATUS_NO = "no"
    STATUS_END = "end"

    def __init__(self, message, arguments, yes_callback=None, no_callback=None, receiver=None):
        Question.__init__(self, message, arguments, yes_callback, no_callback, receiver)

        self.status = self.STATUS_PENDING

        thread = threading.Thread(target=self.waiting)
        thread.start()

    def answer(self, caller, message, answer):
        callback = None

        if self.status == self.STATUS_END:
            return

        if answer == 'no' and self.no_callback:
            self.status = self.STATUS_NO
            callback = self.no_callback

        if callback:
            callback(self, message, self.arguments)

    def waiting(self):

        startTime = datetime.datetime.now()

        while self.status != self.STATUS_NO and self.status != self.STATUS_END:
            time = datetime.datetime.now()
            delta = time - startTime

            if delta.total_seconds() > settings.SERVICE_LOCK_DELAY:
                self.status = self.STATUS_END

        if self.status == self.STATUS_END and self.yes_callback:
            self.yes_callback(self, self.message, self.arguments)


        for pop_callback in self.pop_callbacks:
            pop_callback(self.receiver)
