import boto3
from pprint import pprint

mturk = boto3.client('mturk',
   aws_access_key_id = "AKIAJYVCF5ROSO5YZNJQ",
   aws_secret_access_key = "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",
   region_name='us-east-1',
   #endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
)
#pprint(mturk.list_hits())
#exit()
# You will need the following library
# to help parse the XML answers supplied from MTurk
# Install it in your local environment with
# pip install xmltodict
import xmltodict
# Use the hit_id previously created
#hit_id = '3MVY4USGB6GWVM0U779VQCTHN5XISC'

hit_ids = {}
with open("posted-dwsplit.txt", "r") as hitFile:
    for line in hitFile:
        experiment, audio, hit_id = [c.strip() for c in line.split(",")]
        if experiment not in hit_ids:
            hit_ids[experiment] = {}
        hit_ids[experiment][audio] = hit_id

def get_answers(experiment):
    exp_hit_ids = hit_ids[experiment]
    for audio, hit_id in exp_hit_ids.items():
        # We are only publishing this task to one Worker
        # So we will get back an array with one item if it has
        # been completed

        paginator = mturk.get_paginator('list_assignments_for_hit')
        response_iterator = paginator.paginate(
            HITId=hit_id,
            AssignmentStatuses=['Submitted'],
            PaginationConfig={
                'MaxItems': 150,
                'PageSize': 10,
                #'StartingToken': ''
            }
        )
        all_results = [] 
        for r in list(response_iterator):
            all_results += r["Assignments"]
        #worker_results = mturk.list_assignments_for_hit(
        #        HITId=hit_id,
        #        MaxResults=100,
        #        AssignmentStatuses=['Submitted'])

        all_answers = []
        for assignment in all_results:
            xml_doc = xmltodict.parse(assignment['Answer'])

            # Multiple fields in HIT layout
            assert type(xml_doc['QuestionFormAnswers']['Answer']) is list
            answers = {}
            for answer_field in xml_doc['QuestionFormAnswers']['Answer']:
                question = answer_field['QuestionIdentifier']
                answers[question] = answer_field['FreeText']
            assert(experiment in [k[:len(experiment)] for k in answers.keys()])
            all_answers.append(answers)
        print(audio, len(all_answers))

    return all_answers


for experiment in hit_ids:
    get_answers(experiment)
"""
        else:
            print("OPTION 2")
            # One field found in HIT layout
            print("For input field: " + xml_doc['QuestionFormAnswers']['Answer']['QuestionIdentifier'])
            print("Submitted answer: " + xml_doc['QuestionFormAnswers']['Answer']['FreeText'])
"""
