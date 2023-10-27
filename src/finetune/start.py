import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")
"""res = openai.File.create(
  file=open("/home/melih/Desktop/personal/MapGPT/train.jsonl", "rb"),
  purpose='fine-tune'
)

print(res)"""

#openai.FineTuningJob.create(training_file="file-LRyuBZYIqYKq0HEDLhplJTdC", model="gpt-3.5-turbo")
# List 10 fine-tuning jobs
print(openai.FineTuningJob.list(limit=10))

#print(openai.FineTuningJob.retrieve("ftjob-lvaqie99akFbnqYlEcCdk6YL"))


