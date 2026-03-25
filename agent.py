from dotenv import load_dotenv
load_dotenv()

import anthropic
import datetime
from database import search_chunks, save_message, load_conversation_by_user_id
from rag import search

client = anthropic.Anthropic()

def search_documents(query):
    result = str(search(query))
    return result

ia_tools = [
                {
                    "name": "search_documents",
                    "description": "Rechercher les informations les plus proches du prompt utilisateur dans un document ",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Le prompt de l'utilisateur a comparer avec les donnees des documents"
                            }
                        },
                        "required": ["query"],
                    }
                },
            ]

def chat(user_message, user_id):
    conversation = load_conversation_by_user_id(user_id)
    save_message(user_id, "user", user_message)
    conversation.append({"role": "user", "content": user_message})
    response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=1000,
    system="Tu es un assistant logistique. Réponds uniquement en te basant sur les documents fournis via l'outil search_documents. Si l'information n'est pas dans les documents, dis-le clairement.",
    tools=ia_tools,
    messages=conversation
    )


    while response.stop_reason == "tool_use":
        tool_block = next(b for b in response.content if b.type == "tool_use")
        if tool_block.name == "search_documents":
            tool_result = str(search_documents(tool_block.input["query"]))

        conversation.append({"role": "assistant", "content": response.content})

        conversation.append({
            "role": "user",
            "content": [{
                "type": "tool_result",
                "tool_use_id": tool_block.id,
                "content": tool_result
            }]
        })

        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1000,
            tools=ia_tools,
            system="Tu es un assistant logistique. Réponds uniquement en te basant sur les documents fournis via l'outil search_documents. Si l'information n'est pas dans les documents, dis-le clairement.",
            messages=conversation
        )
    
    ia_text = response.content[0].text
    ia_message = {"role": "assistant", "content": ia_text}
    save_message(user_id, "assistant", ia_text)
    conversation.append(ia_message)

    return ia_text
    

    
    
    
