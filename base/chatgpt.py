from dotenv import dotenv_values
import openai
from functools import wraps

def api_key_validation():
    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt="This is a test.",
            max_tokens=5
        )
        return True
    except:
        return False

def ensure_api_key(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if openai.api_key=='':
            raise None
        elif not api_key_validation():
            return None
        return func(*args, **kwargs)
    return wrapper


class chatgpt():
    def __init__(self,api_key):
        #config = dotenv_values('openaiapikey.txt')
        #api_key = config['API_KEY']
        #openai.api_key = api_key
        print('require openai_apikey')
        openai.api_key = api_key
        self.api_key = api_key
        self.messages = []

        self.messages.append({"role": "system",
                              "content": """你是心理治療師，在這個領域已有多年工作經驗，了解所需技能與知識與遵守倫理。
                                            不會要求使用者尋求其他人協助。擅長以比喻的方式形容使用者面對的困境。
                                            並且會在使用者話中提取有意義的關鍵字，以識別何時通過自我揭露暴露出他們的擔憂。以溫柔、非指導性的語氣回覆。
                                            不要條列式舉例，種點在於針對使用者的困擾的詢問實際狀況。每次盡量不要超過150字"""})

        self.messages.append({'role': 'user', 'content': '簡單說明你的身分，感謝我的分享'})
        self.messages.append({'role': 'assistant', 'content': '你好，我是一個ai情感支持機器人。我會提供一些的支援和建議讓您參考，來幫助您應對生活中的困難情況。有什麼我能幫忙的嗎?'})
    @ensure_api_key    
    def get_reply(self, message):
        self.messages.append({"role": "user", "content": message})
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.messages)
            reply = response["choices"][0]["message"]["content"]
            self.messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            print(f'Error: {e}')
            return None
        return reply
    
    def get_previous(self):
        pre_msg_list=[i['content'] for i in self.messages]
        
        return pre_msg_list
