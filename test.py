import json


with open("data/datasets/AnsweredQuestions/dataset_code_public.json", "r", encoding="utf-8") as file:
	data = json.load(file)

print(type(data))
print(data.keys())
