import boto3
import json
import sys
import time
from dotenv import load_dotenv
import logging


class AwsParserClientAsync:
    def __init__(self, role, bucket, document):
        load_dotenv()
        self.logger = logging.getLogger(__name__)
        self.roleArn = role
        self.bucket = bucket
        self.document = document
        self.textract = boto3.client("textract")
        self.sqs = boto3.client("sqs")
        self.sns = boto3.client("sns")

    def ProcessDocument(
        self,
        save_local_path: str = None,
        feature_types: list[str] = ["TABLES", "FORMS"],
    ):
        jobFound = False

        # select which features you want to obtain with the FeatureTypes argument
        response = self.textract.start_document_analysis(
            DocumentLocation={
                "S3Object": {"Bucket": self.bucket, "Name": self.document}
            },
            FeatureTypes=feature_types,
            NotificationChannel={
                "RoleArn": self.roleArn,
                "SNSTopicArn": self.snsTopicArn,
            },
        )
        self.logger.info("Start Job Id: %s", response["JobId"])

        dotLine = 0
        max_attempts = 20
        while jobFound == False and max_attempts > 0:
            max_attempts -= 1
            sqsResponse = self.sqs.receive_message(
                QueueUrl=self.sqsQueueUrl,
                MessageAttributeNames=["ALL"],
                MaxNumberOfMessages=10,
            )

            if sqsResponse:
                if "Messages" not in sqsResponse:
                    if dotLine < 40:
                        print(".", end="")
                        dotLine = dotLine + 1
                    else:
                        print()
                        dotLine = 0
                    sys.stdout.flush()
                    time.sleep(5)
                    continue

                for message in sqsResponse["Messages"]:
                    notification = json.loads(message["Body"])
                    textMessage = json.loads(notification["Message"])
                    print(textMessage["JobId"])
                    print(textMessage["Status"])
                    if str(textMessage["JobId"]) == response["JobId"]:
                        print("Matching Job Found:" + textMessage["JobId"])
                        jobFound = True
                        self.GetResults(textMessage["JobId"], save_local_path)
                        self.sqs.delete_message(
                            QueueUrl=self.sqsQueueUrl,
                            ReceiptHandle=message["ReceiptHandle"],
                        )
                    else:
                        print(
                            "Job didn't match:"
                            + str(textMessage["JobId"])
                            + " : "
                            + str(response["JobId"])
                        )
                    # Delete the unknown message. Consider sending to dead letter queue
                    self.sqs.delete_message(
                        QueueUrl=self.sqsQueueUrl,
                        ReceiptHandle=message["ReceiptHandle"],
                    )
        if max_attempts == 0:
            self.logger.warning("Max attempts reached. Job not found. Still attempts to acquire the job.")
            self.GetResults(response["JobId"], save_local_path)
        else:
            self.logger.info("Done!")

    def CreateTopicandQueue(self):
        """
        Create SNS topic and SQS queue dynamically to receive notifications.
        """

        millis = str(int(round(time.time() * 1000)))

        # Create SNS topic
        snsTopicName = "AmazonTextractTopic" + millis

        topicResponse = self.sns.create_topic(Name=snsTopicName)
        self.snsTopicArn = topicResponse["TopicArn"]

        # create SQS queue
        sqsQueueName = "AmazonTextractQueue" + millis
        self.sqs.create_queue(QueueName=sqsQueueName)
        self.sqsQueueUrl = self.sqs.get_queue_url(QueueName=sqsQueueName)["QueueUrl"]

        attribs = self.sqs.get_queue_attributes(
            QueueUrl=self.sqsQueueUrl, AttributeNames=["QueueArn"]
        )["Attributes"]

        sqsQueueArn = attribs["QueueArn"]

        # Subscribe SQS queue to SNS topic
        self.sns.subscribe(
            TopicArn=self.snsTopicArn, Protocol="sqs", Endpoint=sqsQueueArn
        )

        # Authorize SNS to write SQS queue
        policy = """{{
"Version": "2012-10-17",		 	 	 
"Statement":[
    {{
    "Sid":"MyPolicy",
    "Effect":"Allow",
    "Principal" : {{"AWS" : "*"}},
    "Action":"SQS:SendMessage",
    "Resource": "{}",
    "Condition":{{
        "ArnEquals":{{
        "aws:SourceArn": "{}"
        }}
    }}
    }}
]
}}""".format(
            sqsQueueArn, self.snsTopicArn
        )

        self.sqs.set_queue_attributes(
            QueueUrl=self.sqsQueueUrl, Attributes={"Policy": policy}
        )

    def DeleteTopicandQueue(self):
        self.sqs.delete_queue(QueueUrl=self.sqsQueueUrl)
        self.sns.delete_topic(TopicArn=self.snsTopicArn)

    # Display information about a block
    def DisplayBlockInfo(self, block):

        print("Block Id: " + block["Id"])
        print("Type: " + block["BlockType"])
        if "EntityTypes" in block:
            print("EntityTypes: {}".format(block["EntityTypes"]))

        if "Text" in block:
            print("Text: " + block["Text"])

        if block["BlockType"] != "PAGE" and "Confidence" in str(block["BlockType"]):
            print("Confidence: " + "{:.2f}".format(block["Confidence"]) + "%")

        print("Page: {}".format(block["Page"]))

        if block["BlockType"] == "CELL":
            print("Cell Information")
            print("\tColumn: {} ".format(block["ColumnIndex"]))
            print("\tRow: {}".format(block["RowIndex"]))
            print("\tColumn span: {} ".format(block["ColumnSpan"]))
            print("\tRow span: {}".format(block["RowSpan"]))

            if "Relationships" in block:
                print("\tRelationships: {}".format(block["Relationships"]))

        if ("Geometry") in str(block):
            print("Geometry")
            print("\tBounding Box: {}".format(block["Geometry"]["BoundingBox"]))
            print("\tPolygon: {}".format(block["Geometry"]["Polygon"]))

        if block["BlockType"] == "SELECTION_ELEMENT":
            print("    Selection element detected: ", end="")
            if block["SelectionStatus"] == "SELECTED":
                print("Selected")
            else:
                print("Not selected")

        if block["BlockType"] == "QUERY":
            print("Query info:")
            print(block["Query"])

        if block["BlockType"] == "QUERY_RESULT":
            print("Query answer:")
            print(block["Text"])

    def GetResults(self, jobId, save_local_path: str = None):
        maxResults = 1000
        paginationToken = None
        finished = False

        while finished == False:

            response = None

            if paginationToken == None:
                response = self.textract.get_document_analysis(
                    JobId=jobId, MaxResults=maxResults
                )
            else:
                response = self.textract.get_document_analysis(
                    JobId=jobId, MaxResults=maxResults, NextToken=paginationToken
                )

            self.logger.info(json.dumps(response, indent=2))
            # Save to local.
            if save_local_path is not None:
                with open(save_local_path, "w", encoding="utf-8") as json_file:
                    json.dump(response, json_file, indent=2, ensure_ascii=False)

            blocks = response["Blocks"]
            self.logger.info("Detected Document Text")
            print("Pages: {}".format(response["DocumentMetadata"]["Pages"]))

            # Display block information
            for block in blocks:
                self.DisplayBlockInfo(block)
                print()
                print()

            if "NextToken" in response:
                paginationToken = response["NextToken"]
            else:
                finished = True

    def GetResultsDocumentAnalysis(self, jobId):
        maxResults = 1000
        paginationToken = None
        finished = False

        while finished == False:

            response = None
            if paginationToken == None:
                response = self.textract.get_document_analysis(
                    JobId=jobId, MaxResults=maxResults
                )
            else:
                response = self.textract.get_document_analysis(
                    JobId=jobId, MaxResults=maxResults, NextToken=paginationToken
                )

            # Get the text blocks
            self.logger.info(json.dumps(response, indent=2))
            blocks = response["Blocks"]
            print("Analyzed Document Text")
            print("Pages: {}".format(response["DocumentMetadata"]["Pages"]))
            # Display block information
            for block in blocks:
                self.DisplayBlockInfo(block)
                print()
                print()

                if "NextToken" in response:
                    paginationToken = response["NextToken"]
                else:
                    finished = True
