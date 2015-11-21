


from will.decorators import respond_to



class QuestionsMixin(object):

    def __init__(self):
        self.questions = dict()


    def add_question(self, question):
        author = question.author

        if not self.questions.has_key(author):
            self.questions[author] = list()

        self.questions[author].append(question)


    @respond_to("(?P<answer>yes|no)",)
    def listen(self, message, answer):
        author = message.sender.nick

        if not self.questions.has_key(author):
            return

        questions = self.questions[author]

        if len(questions) == 0:
            return

        question = questions.pop()
        question.resolve(self, message, answer)




class Question(object):

    def __init__(self, message, callback, item):
        self.message = message
        self.author = message.sender.nick
        self.callback = callback
        self.item = item

    def resolve(self, caller, message, answer):
        if answer == 'yes':
            self.callback(message, self.item)
            return

        caller.say("Ok. I did nothing", message=message)
