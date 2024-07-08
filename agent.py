from openai import OpenAI

client = OpenAI()
import re
from utils import normalize_answer
from prompt import (
    SYSTEM_MESSAGE, 
    INSIGHTS,
    FEWSHOTS
)

def make_message(role, content):
    return {"role": role, "content": content}

def gpt_agent(messages, message, model):
    messages.append(message)
    try:
        response = client.chat.completions.create(model=model,
        messages=messages,
        stop = ["\n", "\n\n"])
        return response.choices[0].message.content.strip().replace(message['content'], "")
    except Exception as e:
        return str(e)

def log_message(messages):
    print(messages[-1]['content'])
    return messages[-1]['content']

class ReactAgent():
    def __init__(self, dataset, df, wiki_index, explorer, model, max_step):
        self.dataset = dataset
        self.df = df
        self.wiki_index = wiki_index
        self.explorer = explorer
        self.model = model
        self.max_step = max_step

    def get_topk(self, argument, k=5):
        top_k = self.explorer.similarity_search(argument, k=k)
        documents = [doc.page_content for doc in top_k]
        return documents

    def get_search(self, argument):
        document = self.explorer.similarity_search(argument, k=1)[0].page_content
        document_content = " ".join(self.wiki_index[document])
        return document_content


    def eval_hotpotqa(self, index):
        thought_id = 1
        messages = []
        message_logs = []
        search_documents = []
        data = self.dataset.iloc[index]
        supporting_facts = ", ".join(data['supporting_facts']['title'])
        fewshots_content = "\n".join(FEWSHOTS)

        messages.append(make_message("system", SYSTEM_MESSAGE))
        messages.append(make_message("system", f'You may take maximum of {self.max_step} steps\nHere are some examples:\n\n{fewshots_content}\n\n(END OF EXAMPLES)\n\n'))
        messages.append(make_message("system", f'The following are some experience you gather on a similar task of question answering using Wikipedia. Use these as references to help you perform this task:\n{INSIGHTS}\n\n'))
        messages.append(make_message("user", f"Now it's your turn!\nQuestion: {data.question}\n"))
        messages.append(make_message("user", f'You can found supporting facts of answer in following documents: {supporting_facts}\n'))
        message_logs.append(log_message(messages))

        while(thought_id <= self.max_step):
            thought_message = make_message("assistant", f"Thought {thought_id}: ")
            thought_content = gpt_agent(messages, thought_message, self.model)
            messages.append(make_message("assistant", f"Thought {thought_id}: {thought_content}\n"))
            message_logs.append(log_message(messages))
            if thought_id == self.max_step:
                action_message = make_message("assistant", f"this time you must use Finish[answer] at Action 10\nAction {thought_id}: ")
            else:
                action_message = make_message("assistant", f"Action {thought_id}: ")
            action_content = gpt_agent(messages, action_message, self.model)
            match_search = re.findall(r"Search\[(.*?)\]", action_content)
            match_finish = re.findall(r"Finish\[(.*?)\]", action_content)
            if len(match_search)>0:
                matches = match_search[0]
                messages.append(make_message("assistant", f"Action {thought_id}: Search[{matches}]\n"))
                message_logs.append(log_message(messages))
                documents = self.get_topk(matches)
                if matches.lower() == documents[0].lower():
                    search_documents.append(documents[0])
                    messages.append(make_message("assistant", f"Observation {thought_id}: {self.get_search(documents[0])}\n"))
                    message_logs.append(log_message(messages))
                else:
                    similar = ", ".join(documents)
                    messages.append(make_message("assistant", f"Observation {thought_id}: Could not find [{matches}]. Similar: [{similar}]\n"))
                    message_logs.append(log_message(messages))
                thought_id+=1
            elif len(match_finish)>0:
                predict = match_finish[0]
                self.df.iloc[index]['search_documents'] = search_documents
                self.df.iloc[index]['predict'] = predict
                messages.append(make_message("assistant", f"Action {thought_id}: Finish[{predict}]\n"))
                message_logs.append(log_message(messages))
                if normalize_answer(predict) == normalize_answer(data.answer):
                    messages.append(make_message("assistant", f"Observation {thought_id}: Answer is CORRECT\n"))
                    message_logs.append(log_message(messages))
                    return (message_logs, self.df)
                else:
                    messages.append(make_message("assistant", f"Observation {thought_id}: Answer is INCORRECT, the Answer was {data.answer}\n"))
                    message_logs.append(log_message(messages))
                    return (message_logs, self.df)
            else:
                thought_id+=1
        return (message_logs, self.df)



