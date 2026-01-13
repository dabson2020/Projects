## **ETL DATA PIPELINE WITH AWS S3, AWS LAMBDA AND AWS GLUE**

**INTRODUCTION**

This project is comprises of the storage, compute, ETL/Big data, Analytics and Permissions

**STORAGE**

Amazon S3: Used for scalable storage of raw and processed data, providing event-driven architecture capabilities with S3 even notifications. In this project, the raw_data bucket holds the csv files, the preprocessed_data_bucket holds that data that is preprocessed by the lambda functions and the final_data_bucket stored the transformed data by the glue job

**COMPUTE**

AWS Lambda: This service acts as a serverless compute layer, automatically triggered to preprocess and clean csv files upon uploas to S3

**ETL/BIG DATA**

AWS Glue provides ETL capabilities to extract, transform and load data into a usuable format for analysis

**ANALYTICS**

The final data in the S3 buscket is connected to a visualization tool which could be Power Bi, Tableau, Amazon Quicksight to visualize the data and provide insights for effective business decision.

**IAM ROLES AND POLICIES**

This service ensre secure access to S3, Lambda and AWS glue

The following steps are performed:
 - Setup and configuration of AWS services
 - Setup the IAM roles and policies:
 - Data Ingestion and preprocessing
 - Data Transformation with AWS Glue
 - Date visualization with Power BI

 The Architectual diagram of the project is seen below:


 - Raw CSV filed are uploaded to the csv_raw_data S3 bucket, initiating the pipeline
 - An AWS Lambda function is automatically trigeered to read and preprocess the uploaded CSV file
 - The lambda function filters/ format the data and stores clean files in the csv_preporcessed_data bucket
 - An AWS Glue crawler scans the processed data and identifies the schema for further processing
 - The crawler updates the AWS Glue Data Catalog, creating a structured table for ETL operation
 - Source-Transform-Store: An AWS Glue job extracts data from the table created in the Glue Data Catalog, transforms the data based on business requirements and loads the final data into the csv_final_data S3 bucket
 - The csv_finak_data S3 bucket is connected to Power BI for data insights

 **IAM ROLES AND POLICIES**
 
  These are created to ensure proper permissions are given to lambda and glue. 
  - An IAM role is created for lamdda function. The AWS Service use Case here is lambda. The Permission Policies selected here are S3FullAccess to enable access to the S3 buckets and GlueServiceRole to enable access to AWS 
  Glue.
  - An IAM Role is created for Use Case: Glue. Permission Policies  are also S3FullAccess to enable access to the S3 buckets and GlueServiceRole to enable access to AWS 
  Glue.

  The following Steps are the details of the creation of this project:

  **STEP 1: CREATE THE S3 BUCKETS**
  
  The 3 S3 buckets are created which are the csv_raw_data S3 bucket, csv_preporcessed_data bucket and the csv_final_data S3 bucket.

  **STEP 2: DATE INGESTION AND PREPROCESSING**
  
  AWS Lambda: Lets you run code without thinking about server provisions. 
  - The lambda function is created from the scratch as a python code. the Basic Information is provided, the runtime which is Python3.14 is selected, For permission, the existing role 'lambda-S3-glue-role is selected and then the function is created. a lambda_function.py file is opened when the function code is written. 

  - Deploy the function. after which you will see 'Successfully update the function"

  - Set up the S3 bucket to automatically trigger the lambda function whenever a new file is uploaded into the csv_raw_data S3 bucket. In the function, Add trigger -> Select Source -> Event Type -> select 'PUT" and 'All object create events" -> Prefix: raw/ (The folder inside the csv_raw_data bucket which the csv files are stored) -> suffix: .csv -> Acknowledge and Add.

  **STEP 3: DATA TRANSFORMATION WITH AWS GLUE**

  AWS Glue is a fully managed ETL service that helps to transform and move data between the storage layers. Here, the glue job is setup, we define the data catalog and execute transaformation on the preprocessed csv files.

  **AWS Glue** helps to automate data prepartion and transformation.

  **AWS Glue Data Catalog** is a centralized metadata repository that stores information about the datasets, making them easily searchable and accessible for analytics.

  In this step, we create the Glue Data Catalog and the Glue crawler
  - **Creating the Glue Data Catalog**: Add Database -> Give it a name and create. A Database is a logical container to organize the tables and metadata.
  - **Create the Glue Crawler**: The crawler automatically checks the data and create the metadata.
  Once the crawler is created, it will crawl data and create  a new crawler schema which will be available in the Glue Data Catalog.

  **STEP 4: CREATE THE CONFIGURE THE GLUE JOB**

  - Under the ETL jobs -> Select visual ETL -> cretae ETL job -> click visual ETL ->Select the  AWS Glue Data Catalog previously created-> select the database -> select the Table -> select the glue IAM Role.
  -  Add the transform layer: Add node -> Transforms -> Select the type of transformtion based on business requirements.
  - Add Target: Add node -> Targets -> Amazon S3 -> S3 Target location: csv_final_data -> format: csv -> compression type: GZIP-> Save -> Run.
  - The final data, after trasnformation, is loaded in the csv_final_data bucket.

  **STEP 5- DATA VISUALIZATION**

  The final data in the csv_final_data S3 bucket is connected to Power BI and visualized for insight

  
  



