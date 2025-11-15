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

'''
This method analyzes the AI output sentence by sentence and identifies which sentences
align with the sources (green) and which conflict (red).
@param question: The user's question
@param aiAnswer: The AI's response to the question
@param references: A list of tuples where each tuple contains (title, link, snippet)
@returns A dictionary with 'aligned' and 'conflicting' lists containing sentence indices
'''
def analyze_sentence_alignment(question, aiAnswer, references):
    import json
    import re
    
    if not references or len(references) == 0:
        return {"aligned": [], "conflicting": [], "sentences": []}
    
    # Split AI answer into sentences
    sentences = re.split(r'(?<=[.!?])\s+', aiAnswer.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return {"aligned": [], "conflicting": [], "sentences": []}
    
    basePrompt = """You are a helpful assistant that analyzes AI-generated answers sentence by sentence
    and compares them with retrieved sources. For each sentence in the AI output, determine if it:
    - ALIGNS with the sources (supported by evidence)
    - CONFLICTS with the sources (contradicts or differs significantly)
    - NEUTRAL (cannot be verified or is not addressed in sources)
    
    Return your response as a JSON object with this exact format:
    {
        "sentences": [
            {"index": 0, "text": "first sentence", "status": "aligned"},
            {"index": 1, "text": "second sentence", "status": "conflicting"},
            {"index": 2, "text": "third sentence", "status": "neutral"}
        ]
    }
    
    Only use "aligned" or "conflicting" status. Use "neutral" only if the sentence cannot be verified.
    Be strict: only mark as "aligned" if sources clearly support it, and "conflicting" if sources contradict it."""
    
    referencesText = ""
    for i, ref in enumerate(references, 1):
        title = ref[0] if len(ref) > 0 else "Untitled"
        snippet = ref[2] if len(ref) > 2 else "No description available"
        referencesText += f"\nReference {i}: {title}\nDescription: {snippet}\n"
    
    sentencesText = ""
    for i, sentence in enumerate(sentences):
        sentencesText += f"Sentence {i}: {sentence}\n"
    
    userPrompt = f"User's question: {question}\n\n" \
                 f"AI's response sentences:\n{sentencesText}\n\n" \
                 f"Retrieved sources:\n{referencesText}\n\n" \
                 f"Analyze each sentence and return the JSON object with alignment status."
    
    try:
        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[{"role": "system", "content": basePrompt},
                      {"role": "user", "content": userPrompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        aligned_indices = []
        conflicting_indices = []
        
        if "sentences" in result:
            for item in result["sentences"]:
                index = item.get("index", -1)
                status = item.get("status", "").lower()
                if status == "aligned" and 0 <= index < len(sentences):
                    aligned_indices.append(index)
                elif status == "conflicting" and 0 <= index < len(sentences):
                    conflicting_indices.append(index)
        
        return {
            "aligned": aligned_indices,
            "conflicting": conflicting_indices,
            "sentences": sentences
        }
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return {"aligned": [], "conflicting": [], "sentences": sentences}
    except Exception as e:
        print(f"Error analyzing sentence alignment: {e}")
        return {"aligned": [], "conflicting": [], "sentences": sentences}