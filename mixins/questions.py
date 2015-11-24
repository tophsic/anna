


from will.decorators import respond_to



class QuestionsMixin(object):

    def __init__(self):
        self.questions = dict()


    def add_question(self, question):
        receiver = question.receiver
        if not self.questions.has_key(receiver):
            self.questions[receiver] = list()

        question.onPop(self.pop)
        self.questions[receiver].append(question)


    @respond_to("(?P<answer>yes|no)")
    def listen(self, message, answer):
        author = message.sender.nick

        if not self.questions.has_key(author):
            return

        questions = self.questions[author]

        if len(questions) == 0:
            return

        question = questions[len(questions) - 1]
        question.answer(self, message, answer)



    @respond_to("@all (?P<answer>yes|no)")
    def listen_all(self, message, answer):
        author = message.sender.nick

        if not self.questions.has_key('all'):
            return

        questions = self.questions['all']

        if len(questions) == 0:
            return

        question = questions[len(questions) - 1]
        question.answer(self, message, answer)

    def pop(self, receiver):
        self.questions[receiver].pop()


class Question(object):

    def __init__(self, message, arguments, yes_callback=None, no_callback=None, receiver=None):
        self.message = message
        self.author = message.sender.name
        self.arguments = arguments
        self.yes_callback = yes_callback
        self.no_callback = no_callback
        self.receiver = receiver
        if not self.receiver:
            self.receiver = self.author
        self.pop_callbacks = list()

    def answer(self, caller, message, answer):
        callback = None

        if answer == 'yes' and self.yes_callback:
            callback = self.yes_callback

        if answer == 'no' and self.no_callback:
            callback = self.no_callback

        if callback:
            callback(self, message, self.arguments)

        for pop_callback in self.pop_callbacks:
            pop_callback(self.receiver)

    def onPop(self, callback):
        self.pop_callbacks.append(callback)
