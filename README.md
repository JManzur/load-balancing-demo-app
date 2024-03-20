# Load Balancing Demo APP

Why do all demo apps have to be ugly? I don't want any white page with off-center black text. Let's use something prettier!

This is a simple Flask APP that runs in a Docker container and you can use it to test load balancing. The useful part for testing load balancing is that this app returns the hostname of the container it is running on, so you can confirm that your load balancing setup is working.

This app also includes a status page to test healthcheck, and a feature to show the "app version" in the footer, so you can test rolling updates.

> #### :bulb: [Also available on Docker Hub!](https://hub.docker.com/r/jmanzur/demo-lb-app)


## Tested with: 

| Environment | Application | Version  |
| ----------------- |-----------|---------|
| WSL2 Ubuntu 20.04 | Docker | 25.0.3  |
| WSL2 Ubuntu 20.04 | Python | 3.10.12 |

## Run App.py Locally

Clone the project

```bash
git clone https://github.com/JManzur/load-balancing-demo-app.git
```

Go to the project directory

```bash
cd load-balancing-demo-app
```

If you wish to test the python app locally, install the requirements:

```bash
  pip3 install -r requirements.txt
```

Start the server

```bash
  python3 app.py
```

Access the web app:

http://127.0.0.1:8882/

And you will see something like this:

![App Screenshot](./images/lb_demo_app.png)

## Test the healthcheck status page

In order to test the healthcheck status page, you can access http://127.0.0.1:8882/status in a browser or perform a curl like this:

```bash
curl -s http://127.0.0.1:8882/status
```

:bulb: **TIP**: Use "python3 -m json.tool" to prettify the json output

```bash
curl -s http://127.0.0.1:8882/status | python3 -m json.tool
```

:bulb: **TIP**: [jq](https://jqlang.github.io/jq/download/) also works great for this:

```bash
curl -s http://127.0.0.1:8882/status | jq -r
```
![App Screenshot](./images/lb_demo_app_status.png)

## Build the Docker image 

Form the project directory run:

```bash
docker build -t demo-lb-app .
```

## Run the Docker image Locally

After building the image if you wish to test it locally run the following command.

Copy the IMAGE_ID
```bash
docker image ls
```

Run the image
```bash
docker run -d -p 8882:8882 --name DEMO-LB-APP {IMAGE_ID}
```

:bulb: **TIP**: You can also use the `rebuild_image.sh` script located in the scripts directory to build and run the image.

```bash

## Run the Docker image in a EKS Kubernetes Cluster

Deploy the pod, service and ingress resources to your EKS cluster:
```bash
kubectl apply -f https://raw.githubusercontent.com/JManzur/load-balancing-demo-app/main/kubernetes/k8s_deployment.yaml
```

Wait a few minutes for the load balancer to be created and then get the ingress endpoint:
```bash
kubectl get ingress/ingress-demo-lb-app -n demo-lb-app
```

To delete the resources run:
```bash
kubectl delete -f https://raw.githubusercontent.com/JManzur/load-balancing-demo-app/main/kubernetes/k8s_deployment.yaml
```
> :warning: NOTE: This deployment uses a LoadBalancer service type, so it will create a **PUBLIC** AWS ELB and you will be charged for it, also your eks cluster needs to have the correct permissions to create the ELB, and the ELB controller needs to be installed in your cluster.


### Aditional tips:

Use a `while` loop to test the load balancing:

```bash
while true; do echo -n; curl -s http://<your-ingress-endpoint>/status | jq -r; sleep 1; done
```

## Author

- [@JManzur](https://jmanzur.com)

## Documentation

- [Python - Docker Official Images](https://hub.docker.com/_/python)
- [Install the AWS Load Balancer Controller add-on using Kubernetes Manifests](https://docs.aws.amazon.com/eks/latest/userguide/lbc-manifest.html)
- [Application load balancing on Amazon EKS](https://docs.aws.amazon.com/eks/latest/userguide/alb-ingress.html)