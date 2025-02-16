from groq import Groq
import os

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

def get_memory_response(name,relation,memory):
    messages=[
        {"role":"assistant", "content":"You're a friendly assistant helping an elder with Alzheimers remember people in their life. Given the format of someone from their life: name| their relation to the elder | their favourite memory, help the elder remember who they are. Be specific but keep it around 5 sentences. Be more confident in your answer"},
        {"role": "user", "content": f"{name}|{relation}|{memory}"}
    ]
    completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            max_tokens=300
        )

    return completion.choices[0].message.content.strip()

print(get_memory_response("connie","sister","eating ice cream by the beach with you"))


def generate_story(people, url):
    client = Groq()
    completion = client.chat.completions.create(
        model="llama-3.2-11b-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Pretend you are {people}, tell the user a story what you did throughout the day. Pretend you are telling an elder loved one who has alzheiemer what you did through your day based on the image. Keep it under 10 sentences."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"{url}"
                        }
                    }
                ]
            }
        ],
        temperature=1,
        max_completion_tokens=2048,
        top_p=1,
        stream=False,
        stop=None,
    )

    print(completion.choices[0].message)

print(generate_story("sophie","https://media.istockphoto.com/id/1319453854/photo/beautiful-asian-woman-eating-ice-cream-on-the-street-emotional-hipster-wearing-casual.jpg?s=612x612&w=0&k=20&c=nbTKzEMEfVMGX0w3F4LG0LCBujQpFhwG0EnUthj7T8Q="))