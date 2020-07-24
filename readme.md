# Demo pipeline

This repository is a short tutorial/demo on how to create a simple pipeline using Iterum. For this demo, we will perform an experiment  where the eyes of cats will be detected using edge detection and a hough transform. We start with a dataset consisting of 10 cat images. The pipeline then consists of the following steps:

1. Split the dataset into separate fragments
1. Perform edge detection on the images
1. Perform the hough transform for circles on the edges
1. Store the results

![pipeline](images/pipeline.png)

## 1. Creating a versioned dataset

To run this experiment using Iterum we first have to version the dataset. The images themselves are stored in the *images* subfolder of this repository.

#### 1.1. Initializing a dataset
```
iterum init
```
Follow the instructions on what name the dataset should have. You can for example use the name `cats-dataset` for the dataset.


#### 1.2. Creating *idv-config.yaml*
Then we have to create the `idv-config.yaml` file in the newly created folder. 
```
touch idv-config.yaml
```
Edit this file such that it contains the following text:
```
name:
  cats-dataset
daemon:
  "http://localhost:3000/"
backend:
  Local
credentials:
  path:
    "/localStorage/"
```
Be sure to replace the name of the dataset (`cats-dataset`) with the name you picked in the previous step.

#### 1.3. Syncing with the daemon
You now have to sync the dataset with the daemon, such that the daemon is aware that this dataset exists. This can be done using the following command:
```
iterum setup
```

#### 1.4. Adding and committing the cat photos
Now the cats can be added and committed to the dataset. Run the following command:
```
iterum add -r ../cats_subset
```
Followed by
```
iterum commit "10-cats" "Added 10 cats"
```
#### 1.5. Retrieving the commit hash
You have now added a new version to the dataset. Before you can run the pipeline, you need to retrieve the correct commit hash. This can be done using the following command:
```
iterum ls -c
```
This hash can now be copied to be placed in a pipeline deployment file.


## 2. Build and push the images to a container registry available to your cluster
This step depends a bit on your specific Kubernetes implementation. If a local registry does not work for you, you can always use the public Dockerhub registry for this step. Be sure to replace `<YOUR-REGISTRY>` with the url of your actual registry.

#### 2.1 Run the following commands to build the images:
```
docker build -t <YOUR-REGISTRY>/demo-fragmenter:v1.0 ./0_fragmenter
docker build -t <YOUR-REGISTRY>/demo-edge-detection:v1.0 ./1_edge_detection
docker build -t <YOUR-REGISTRY>/demo-hough-transform:v1.0 ./2_hough_transform
```
#### 2.2 Run the following commands to push the images to your registry:
```
docker push <YOUR-REGISTRY>/demo-fragmenter:v1.0
docker push <YOUR-REGISTRY>/demo-edge-detection:v1.0
docker push <YOUR-REGISTRY>/demo-hough-transform:v1.0 
```

## 3. Configure and deploy the pipeline

#### 3.1 Configuring a pipeline
The file `deployment.json` in the root of this repository shows an example deployment file for a pipeline. This file looks something like this:
```
{
  "name": "demo-pipeline",
  "input_dataset": "cats-dataset",
  "input_dataset_commit_hash": "<YOUR-COMMIT-HASH>",
  "fragmenter": {
    "image": "<YOUR-REGISTRY>/demo-fragmenter:demo-v1",
    "output_channel": "fragmenter_output"
  },
  "steps": [
    {
      "name": "edge-detection",
      "image": "<YOUR-REGISTRY>/demo-edge-detection:demo-v1",
      "input_channel": "fragmenter_output",
      "output_channel": "edge_detection_output",
      "config": {
        "BLUR_KERNEL_SIZE": 3,
        "H_THRESHOLD1": 320,
        "H_THRESHOLD2": 220
      }
    },
    {
      "name": "hough-transform",
      "image": "<YOUR-REGISTRY>/demo-hough-transform:demo-v1",
      "input_channel": "edge_detection_output",
      "output_channel": "hough_transform_output",
      "config": {
        "HIGH_THRESHOLD": 20,
        "LOW_THRESHOLD": 20
      }
    }
  ],
  "combiner": {
    "input_channel": "hough_transform_output"
  }
}
```
Copy this json structure to a file called `my_deployment.json`, and change the following values: `<YOUR-REGISTRY>` to your container registry URL, and `<YOUR-COMMIT-HASH>` to the commit hash you retrieved in step 1.5 of this tutorial.


#### 3.3 Deploying a pipeline
You can now deploy this pipeline by running 
```
iterum pipelines deploy my_deployment.json
```

#### 3.4 Examine the status of the pipeline


#### 3.5 Examine the results of the pipeline