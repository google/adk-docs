### Create Database Objects

In order to run this Cloud Run Function, you should have created the AlloyDB side of things prior, for the database objects. 
Let’s create an AlloyDB cluster, instance and table where the ecommerce dataset will be loaded. 

#### Create a cluster and instance
1. Navigate the AlloyDB page in the Cloud Console.  An easy way to find most pages in Cloud Console is to search for them using the search bar of the console.

2. Select CREATE CLUSTER from that page:

3. You'll see a screen like the one below.  Create a cluster and instance with the following values (Make sure the values match in case you are cloning the application code from the repo):
cluster id: “vector-cluster”
password:  “alloydb”
PostgreSQL 15 / latest recommended
Region: “us-central1”
Networking: “default”

4. When you select the default network, you'll see a screen like the one below.  
Select SET UP CONNECTION.  

5. From there, select "Use an automatically allocated IP range" and Continue.  After reviewing the information, select CREATE CONNECTION. 

6. Once your network is set up, you can continue to create your cluster. Click CREATE CLUSTER to complete setting up of the cluster as shown below:
 
7. Make sure to change the instance id to vector-instance
If you cannot change it, remember to change the instance id in all the upcoming references.

Note that the Cluster creation will take around 10 minutes. Once it is successful, you should see a screen that shows the overview of your cluster you just created.

#### Data Ingestion
Now it's time to add a table with the data about the store.  Navigate to AlloyDB, select the primary cluster and then AlloyDB Studio.
1. You may need to wait for your instance to finish being created.  Once it is, sign into AlloyDB using the credentials you created when you created the cluster.  Use the following data for authenticating to PostgreSQL:

Username : “postgres”
Database : “postgres”
Password : “alloydb”

2. Once you have authenticated successfully into AlloyDB Studio, SQL commands are entered in the Editor.  You can add multiple Editor windows using the plus to the right of the last window.
Enable Extensions

For building this app, we will use the extensions pgvector and google_ml_integration. The pgvector extension allows you to store and search vector embeddings. The google_ml_integration extension provides functions you use to access Vertex AI prediction endpoints to get predictions in SQL. Enable these extensions by running the following DDLs:

CREATE EXTENSION IF NOT EXISTS google_ml_integration CASCADE;
CREATE EXTENSION IF NOT EXISTS vector;


3. If you would like to check the extensions that have been enabled on your database, run this SQL command:

select extname, extversion from pg_extension;


4. Create a table 
You can create a table using the DDL statement below in the AlloyDB Studio: 

CREATE TABLE patents_data ( id VARCHAR(25), type VARCHAR(25), number VARCHAR(20), country VARCHAR(2), date VARCHAR(20), abstract VARCHAR(300000), title VARCHAR(100000), kind VARCHAR(5), num_claims BIGINT, filename VARCHAR(100), withdrawn BIGINT, abstract_embeddings vector(768)) ;

The abstract_embeddings column will allow storage for the vector values of the text.

5. Grant Permission
Run the below statement to grant execute on the “embedding” function:

GRANT EXECUTE ON FUNCTION embedding TO postgres;

6. Grant Vertex AI User ROLE to the AlloyDB service account
   
From Google Cloud IAM console, grant the AlloyDB service account (that looks like this: service-<<PROJECT_NUMBER>>@gcp-sa-alloydb.iam.gserviceaccount.com) access to the role “Vertex AI User”. PROJECT_NUMBER will have your project number.

PROJECT_ID=$(gcloud config get-value project)

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:service-$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")@gcp-sa-alloydb.iam.gserviceaccount.com" \
--role="roles/aiplatform.user"

7. Load patent data into the database
The [Google Patents Public Datasets]([url](https://console.cloud.google.com/launcher/browse?q=google%20patents%20public%20datasets&filter=solution-type:dataset&_ga=2.179551075.-653757248.1714456172)) from BigQuery will be used as our dataset. Here is the link: https://console.cloud.google.com/launcher/browse?q=google%20patents%20public%20datasets&filter=solution-type:dataset&_ga=2.179551075.-653757248.1714456172

We will use the AlloyDB Studio to run our queries. The [alloydb-pgvector]([url](https://github.com/AbiramiSukumaran/alloydb-pgvector)) repository includes the
[insert_scripts.sql]([url](https://github.com/AbiramiSukumaran/alloydb-pgvector/blob/main/insert_scripts.sql)) script we will run to load the patent data:
https://github.com/AbiramiSukumaran/alloydb-pgvector/blob/main/insert_scripts.sql

a. In the Google Cloud console, open the AlloyDB page.
b. Select your newly created cluster and click the instance.
c. In the AlloyDB Navigation menu, click AlloyDB Studio. Sign in with your credentials.
d. Open a new tab by clicking the New tab icon on the right.
e. Copy the insert query statement from the insert_scripts.sql script mentioned above to the editor. You can copy 40-50 or even lesser insert statements for a quick demo of this use case.
f. Click Run. The results of your query appear in the Results table.

### Create Cloud Run Function

Ready for taking this data to Cloud Run Function? Follow the steps below:

1. Go to Cloud Run Functions in Google Cloud Console to CREATE a new Cloud Run Function or use the link: https://console.cloud.google.com/functions/add.

2. Select the Environment as "Cloud Run function". Provide Function Name "patent-search”  and choose Region as "us-central1". Set Authentication to "Allow unauthenticated invocations" and click NEXT. Choose Java 17 as runtime and Inline Editor for the source code.

3. By default it would set the Entry Point to "gcfv2.HelloHttpFunction". Replace the placeholder code in HelloHttpFunction.java and pom.xml of your Cloud Run Function with the code from “PatentSearch.java” and the “pom.xml” respectively. Change the name of the class file to PatentSearch.java.

4. Remember to change the ********* placeholder and the AlloyDB connection credentials with your values in the Java file. The AlloyDB credentials are the ones that we had used at the start of this codelab. If you have used different values, please modify the same in the Java file.

5. Click Deploy.

#### IMPORTANT STEP:

Once deployed, in order to allow the Cloud Function to access our AlloyDB database instance, we'll create the VPC connector.

Once you are set out for deployment, you should be able to see the functions in the Google Cloud Run Functions console. Search for the newly created function (patent-search), click on it, then click EDIT and change the following:

1. Go to Runtime, build, connections and security settings

2. Increase the timeout to 180 seconds

3. Go to the CONNECTIONS tab:
Under the Ingress settings, make sure "Allow all traffic" is selected.

Under the Egress settings, Click on the Network dropdown and select "Add New VPC Connector" option and follow the instructions you see on the dialog box that pops-up:

Provide a name for the VPC Connector and make sure the region is the same as your instance. Leave the Network value as default and set Subnet as Custom IP Range with the IP range of 10.8.0.0 or something similar that is available.

Expand SHOW SCALING SETTINGS and make sure you have the configuration set to exactly the following:
Minimum instances* 2
Maximum instances* 3
instance type* fi-micro

4. Click CREATE and this connector should be listed in the egress settings now.
   
6. Select the newly created connector.
   
8. Opt for all traffic to be routed through this VPC connector.
   
10. Click NEXT and then DEPLOY.

    Once the updated Cloud Function is deployed, you should see the endpoint generated. Copy that and replace in the following command:

    PROJECT_ID=$(gcloud config get-value project)

curl -X POST <<YOUR_ENDPOINT>> \
  -H 'Content-Type: application/json' \
  -d '{"search":"Sentiment Analysis"}' \
  | jq .

That's it! It is that simple to perform an advanced Contextual Similarity Vector Search using the Embeddings model on AlloyDB data.



