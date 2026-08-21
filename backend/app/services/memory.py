class ConversationMemory:

    def __init__(self):
        self.history = []

    def add(self, question, answer):

        self.history.append({
            "question": question,
            "answer": answer
        })

    def get_context(self):

        context = ""

        for chat in self.history[-5:]:

            context += f"""
User: {chat['question']}

Assistant: {chat['answer']}

"""

        return context

    def clear(self):
        self.history.clear()