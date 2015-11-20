


from will.decorators import respond_to



class QuestionsMixin(object):

    def __init__(self):
        self.questions = list()


    def add_question(self, question):
        self.questions.append(question)


    @respond_to("(?P<answer>yes|no)",)
    def listen(self, message, answer):
        if len(self.questions) == 0:
            return

        question = self.questions.pop()
        question.resolve(self, message, answer)




class Question(object):

    def __init__(self, message, callback, item):
        self.message = message
        self.callback = callback
        self.item = item

    def resolve(self, caller, message, answer):
        if answer == 'yes':
            self.callback(message, self.item)
            return

        caller.say("Ok. I did nothing", message=message)
