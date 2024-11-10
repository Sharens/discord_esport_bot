import ollama
response = ollama.chat(model='llama3.1', messages=[
  {
    'role': 'user',
    'content': 'wygeneruj mi kod w pythonie który narysuje trójkąt który zostanie wyprintowany w formie tekstu',
  },
])
print(response['message']['content'])