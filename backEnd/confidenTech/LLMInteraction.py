from openai import OpenAI

API_KEY = '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'
URL = 'https://api.groq.com/openai/v1'

client = OpenAI(api_key=API_KEY, base_url=URL)


'''
This method takes in a user question and the response from the LLM, then forms a query to search
the web and returns it as a string
'''
def form_query(question, LLMResponse):
    prompt = """You are a helpful assistant that analyzes a question asked by the user
    and the response a LLM gave them. From the answer and response to be provided,
    form one single search query to find websites allowing the user to fact check the response the
    LLM produced. Respond with only the formed search query and nothing else."""

    combinedContent = "User's question: " + question + ". LLM's response: " + LLMResponse 

    response = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[{"role": "system", "content": prompt},
                  {"role": "user", "content": combinedContent}],
        temperature=0.7,
    )

    return response.choices[0].message.content


'''
This method takes in a user question and gets a response answer from an LLM, then returns this response as a string
'''
def form_answer(question):
    prompt = "You are a helpful and knowledgeable assistant that answers questions clearly"

    response = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[{"role": "system", "content": prompt},
                  {"role": "user", "content": question}],
        temperature = 0.7
    )

    return response.choices[0].message.content

'''
This method takes in a user's prompt, the LLM answer to that prompt,
and the scraped textual content of a related website then summarizes
relevant parts for fact checking purposes
'''
def summarize_web_page(prompt, answer, webContent):
    # Give directions to GPT
    basePrompt = "You are a helpful assistant that summarizes webpage content relevant to fact checking" \
    " the question and answer provided by the user. Keep response under 200 words."

    # Trim webpage content
    if len(webContent) > 5000:
        webContent = webContent[:5000]

    # Form user prompt for GPT
    userPrompt = f"User's question: {prompt}\n" \
    f"LLM's response: {answer}\n" \
    f"Webpage content: {webContent}"

    response = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[{"role": "system", "content": basePrompt},
                  {"role": "user", "content": userPrompt}],
        temperature = 0.7
    )

    return response.choices[0].message.content