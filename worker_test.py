from flask import Flask, render_template, request, redirect, url_for, flash, make_response
import boto3
import json
# from github import Github
import os, os.path
import time
import pymongo
from pymongo import MongoClient
from pprint import pprint
from bson import Regex
import gridfs
from bson.objectid import ObjectId
import codecs
from bson import json_util, ObjectId
from flask import jsonify


# import re


def get_key():
    with open("D:/Sandy/Course/2nd semester/IST 402_Crowdsourcing and Crowd AI/Assignments/Final project/rootkey.csv", "r") as infile:
        data = [line.strip().split("=")[1] for line in infile]
        access_key = data[0]
        secret_key = data[1]
        print(access_key, secret_key)
    return access_key, secret_key

def get_client():
    region_name = 'us-east-1'
    aws_access_key_id, aws_secret_access_key = get_key()
    endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'

    # Uncomment this line to use in production
    #endpoint_url = 'https://mturk-requester.us-east-1.amazonaws.com'

    client = boto3.client(
      'mturk',
      endpoint_url=endpoint_url,
      region_name=region_name,
      aws_access_key_id=aws_access_key_id,
      aws_secret_access_key=aws_secret_access_key,
    )

    # This will return $10,000.00 in the MTurk Developer Sandbox
    print(client.get_account_balance()['AvailableBalance'])
    return client


def send_hit(client, setting=None):
    if setting is None:
        with open("setting.xml", 'r') as infile:
            setting = infile.read()

    response = client.create_hit(
        MaxAssignments=5,
        LifetimeInSeconds=60*60*60,
        AssignmentDurationInSeconds=60*10,
        Reward='0.05',
        Title='Extracting Story Characters',
        Keywords='Story,Characters',
        Description= "Given a short story, you will need to find the all characters for it.",
        Question=setting,
        QualificationRequirements=[
            {
                "QualificationTypeId": "000000000000000000L0",
                "Comparator": "GreaterThanOrEqualTo",
                "IntegerValues": [
                    98
                ],
                "ActionsGuarded": "Accept"
            },
            {
                "QualificationTypeId": "00000000000000000060",
                "Comparator": "EqualTo",
                "IntegerValues": [
                    1
                ],
                "ActionsGuarded": "Accept"
            }
        ],
    )

    return response

# def get_github():
#     with open("/home/appleternity/workspace/lab/github.key", 'r') as infile:
#         data = [line.strip() for line in infile]
#     g = Github(data[0], data[1])
#     return g

def generate_html(task_id, img_src, city, region, postal_code, country):
    
    dir_path = "D:/Sandy/Course/2nd semester/IST 402_Crowdsourcing and Crowd AI/Assignments/Final project/Project/templates"
    with open(os.path.join(dir_path, "worker_1.html"), 'r', encoding='utf-8') as infile:
        template = infile.read()

    result = template.replace("{{img_src}}", img_src).replace("{{city}}", city).replace("{{region}}", region).replace("{{postal_code}}", postal_code).replace("{{country}}", country)
    # result = template.replace("{{img_src}}", "{{url_for('get_image', imgId={})}}".format(img_src))
    
    with open(os.path.join(dir_path, "{}.html".format(task_id)), 'w', encoding='utf-8') as outfile:
        outfile.write(result)

    return os.path.join(dir_path, "{}.html".format(task_id)), result


def task_manager():

    client = pymongo.MongoClient("mongodb+srv://User:a0933591611@cluster0-eufp8.gcp.mongodb.net/test?retryWrites=true&w=majority")
    db = client.test
    db = client["MealMatch"]
    fs = gridfs.GridFS(db)
    
    client = get_client()
    with open("template_setting.xml", 'r') as infile:
        template_setting = infile.read()


    while True:
        # check task
        information = db.information.find({"status":"active"})
        
        # print(results)
        for info in information:            
            filename, content = generate_html(task_id=str(info["_id"]), img_src= str(info["fields"]), city=str(info["city"]), region=str(info["region"]), postal_code=str(info["postal_code"]), country=str(info["country"]))
            
            # db.images.update_one({
            #     "_id":res["_id"]
            # }, {
            #     "$set": {
            #         "status":"processing",
            #         "hit_id":hit_info["HIT"]["HITId"],
            #         "results":[]
            #     }
            # })
            # github.create_file(filename, "create html file for worker", content)

            # url = "https://appleternity.github.io/CrayonSearch/{}".format(filename)
            # print(url)
            # setting = template_setting.format(url)
            # hit_info = send_hit(client, setting)
            # mongo.query.update_one({
            #     "_id":res["_id"]
            # }, {
            #     "$set": {
            #         "status":"processing",
            #         "hit_id":hit_info["HIT"]["HITId"],
            #         "results":[]
            #     }
            # })
        
        # check result
        # results = mongo.query.find({"status":"processing"})
        # for res in results:
        #     hit_id = res["hit_id"]
        #     results = extract_result(hit_id, client)
        #     if results:
        #         print("getting {} results for {}".format(len(results), hit_id))
        #         mongo.query.update_one({
        #             "_id":res["_id"]
        #         }, {
        #             "$push": {
        #                 "results": {
        #                     "$each": results
        #                 }
        #             }
        #         })

        # sleep
        # time.sleep(30)

def test_mturk():
    client = get_client()
    
    with open("setting.xml", 'r') as infile:
        template_setting = infile.read()
    setting = template_setting.format("https://SandyKuan.github.io/Assignment_2_fix.html")

    hit_info = send_hit(client, setting)
    pprint(hit_info) 
    # print(hit_info["HIT"]["HITId"]) 

def main():
    task_manager() 
    #test_mturk()

if __name__ == "__main__":
    main()