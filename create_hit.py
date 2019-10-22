import boto3
# from boto.mturk.connection import MTurkConnection
# from boto.mturk.question import HTMLQuestion
import numpy as np

from mturk_html import html_start, html_end, test, real


bad_names = ["bad-LJ001-0015", "bad-LJ001-0051", "bad-LJ001-0063", "bad-LJ001-0072", "bad-LJ001-0079", "bad-LJ001-0094"]
good_names = ["GT-LJ001-0063", "GT-LJ001-0072", "GT-LJ001-0096", "GT-LJ001-0102", "GT-LJ001-0173"]
sandbox_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'

keyid = None
key = None
with open("aws.csv", "r") as fp:
    for i, line in enumerate(fp):
        if i == 0:
            keyid = str(line).split("=")[1].strip()
        else:
            key = str(line).split("=")[1].strip()

print(keyid, key)
def post_question(question_html_value):

    # Create your connection to MTurk
    mtc = boto3.client('mturk',
                        aws_access_key_id=keyid,
                        aws_secret_access_key=key,
                        region_name='us-east-1',
                        # endpoint_url = sandbox_url
                        )

    # The first parameter is the HTML content
    # The second is the height of the frame it will be shown in
    # Check out the documentation on HTMLQuestion for more details
    # html_question = HTMLQuestion(question_html_value, 0)
    # These parameters define the HIT that will be created
    # question is what we defined above
    # max_assignments is the # of unique Workers you're requesting
    # title, description, and keywords help Workers find your HIT
    # duration is the # of seconds Workers have to complete your HIT
    # reward is what Workers will be paid when you approve their work
    # Check out the documentation on CreateHIT for more details
    response = mtc.create_hit(
                              MaxAssignments=150,
                              AutoApprovalDelayInSeconds=604800,
                            LifetimeInSeconds=604800,
                            AssignmentDurationInSeconds=3000,
                            Reward='0.05',
                            Title='How natural (i.e. human-sounding) is this recording?',
                            Keywords='audio, naturalness, rating',
                            Description='How natural (i.e. human-sounding) is this recording?',
                            Question=question_html_value)

    # The response included several fields that will be helpful later
    hit_type_id = response['HIT']['HITGroupId']
    hit_id = response['HIT']['HITId']
    print("Your HIT has been created. You can see it at this link:")
    print("https://workersandbox.mturk.com/mturk/preview?groupId={}".format(hit_type_id))
    print("Your HIT ID is: {}".format(hit_id))
    return hit_id


def creat_quesiton(expname, fname):
    alreay_used = set()
    alreay_used.add(fname[-2:])

    modified_good_names = [name for name in good_names if name[-2:] not in alreay_used]

    divs = []

    goods = np.random.choice(modified_good_names, size=2, replace=False)
    divs.append(test.format(testname=goods[0]))
    divs.append(test.format(testname=goods[1]))
    alreay_used.add(goods[0][-2:])
    alreay_used.add(goods[1][-2:])

    modified_bad_names = [name for name in bad_names if name[-2:] not in alreay_used]
    bads = np.random.choice(modified_bad_names, size=2, replace=False)
    divs.append(test.format(testname=bads[0]))
    divs.append(test.format(testname=bads[1]))

    divs.append(real.format(realexp=expname, realname=fname))

    np.random.shuffle(divs)

    question_html_value = html_start + divs[0] + divs[1] + divs[2] + divs[3] + divs[4] + html_end

    return question_html_value


audio_names = [
"LJ001-0051", "LJ001-0063", "LJ001-0072", "LJ001-0079", "LJ001-0094", "LJ001-0096", "LJ001-0102", 
                "LJ001-0153", 
                "LJ001-0173"]

for audio in audio_names:
    expname = "allinone"
    q = creat_quesiton(expname, audio)
    hit_id = post_question(q)
    with open("posted-{}.txt".format(expname), "a") as fp:
        fp.write(expname + "," + audio + "," + hit_id + "\n")


