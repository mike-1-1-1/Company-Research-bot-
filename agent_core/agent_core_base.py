
import asyncio
from http.client import NOT_FOUND
from linecache import cache
from random import randint
from typing import Any, Dict, Optional
from openai import OpenAI, OpenAIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dotenv import load_dotenv
from diskcache import Cache # TODO: make cache key construction more robust to be more insenstive to whitespace and punctuation differences in the input message

class AgentCoreBase:
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None, base_model: Optional[str] = "gpt-4o-mini", instructions: Optional[str] = "", max_tokens: Optional[int] = 100):
        self.name = name
        self.config = config or {}
        self.base_model = base_model
        self.instructions = instructions
        self.max_tokens = max_tokens
        self.state: Dict[str, Any] = {}
        self.cache = Cache(self.config.get('CACHE_DIR', f'./agent_core_cache_dir'))  # Default cache directory
        self.client = OpenAI(api_key=self.config.get('OPEN_AI_API_KEY', ''))

        #self.state['message_history'] = []

    # def cleanupIfNecessary(self):
    #     if(len(self.state['message_history']) > 10):
    #         self.state['message_history'] = self.state['message_history'][2:]

    # def append_user_message(self, message: str):
    #     self.state['message_history'].append({
    #         'type': 'user',
    #         'content': message,
    #         'timestamp': asyncio.get_event_loop().time()
    #     })

    # def append_reply_message(self, message: str):
    #     self.state['message_history'].append({
    #         'type': 'agent',
    #         'content': message,
    #         'timestamp': asyncio.get_event_loop().time()
    #     })

    def try_get_from_cache(self, message: str) -> Optional[str]:
        NOT_FOUND = object()

        # Single disk lookup: attempts to get the value, falls back to the sentinel
        value = self.cache.get(message, default=NOT_FOUND)

        if value is NOT_FOUND:
            return None
        else:
            return value

    # Define a robust retry strategy:
    # - Retries only if it's an OpenAI API error (like rate limits or server blips)
    # - Stops trying after 3 attempts
    # - Exponentially backoff (wait 2s, then 4s,...) so you OPENAI endpoint is not overwhelmed
    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=4),
        retry=retry_if_exception_type(OpenAIError)
    )
    def get_reply_from_openai(self, message: str, temperature: float = 0.5, web_search: bool = False) -> str:        
        cache_value  = self.try_get_from_cache(message)

        if(cache_value is not None):
            print("✅ Cache hit for message:", message, "Returning cached response:", cache_value)
            return cache_value

        try:

            if(web_search):
                print("🔍 Performing query with web search for message:", message)
                response = self.client.responses.create(
                    model=self.base_model,
                    tools=[{"type": "web_search_preview"}],
                    input=message,
                    temperature=temperature,
                    max_output_tokens=self.max_tokens,
                    instructions=self.instructions)
                ai_message = response.output_text
                try:
                    print(f"\n📊 [Tokens Used - Prompt: {response.usage.input_tokens}, Completion: {response.usage.output_tokens}, Total tokens: {response.usage.total_tokens}]")
                except AttributeError:
                    print("⚠️ Wasn't able to exact token usage information from the response.")
            else:
                print("💬 Performing query without web search for message:", message)
                response = self.client.chat.completions.create(
                    model=self.base_model, 
                    messages=[
                        {
                            "role": "system", 
                            "content": self.instructions
                        },
                        {
                            "role": "user", 
                            "content": message
                        }
                    ],
                    temperature=temperature,
                    max_tokens=self.max_tokens
                )
                
                # Extract and print the generated text output
                ai_message = response.choices[0].message.content
                try:
                    print(f"\n📊 [Tokens Used - Prompt: {response.usage.input_tokens}, Completion: {response.usage.output_tokens}]")
                except AttributeError:
                    print("⚠️ Wasn't able to exact token usage information from the response.")
            print("🤖 AI Response:\n", ai_message)
            
            # Optional: Print token usage information

            self.cache.set(message, ai_message, expire = 86400)  # Cache the response for future requests, with an expiration time of 1 day (i.e. 86400 seconds)

            return ai_message
        except Exception as e:
            print(f"❌ An error occurred: {e}")

        return "error: Unable to get a response from OpenAI."    

    async def get_reply(self, message: str) -> str:
        print(f"[{self.name}] Received message: {message}")

        # self.append_user_message(message)

        reply = self.get_reply_from_openai(message)

        #self.append_reply_message(reply)

        # self.cleanupIfNecessary()

        return reply