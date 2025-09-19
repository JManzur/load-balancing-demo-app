# Load Balancing Demo APP

Why do all demo apps have to be ugly? I don’t want another white page with off-center black text. Let’s use something prettier!

This is a simple Flask app that runs in a Docker container, designed to help test load balancing. The key feature for testing load balancing is that the app returns the hostname of the container it’s running on, so you can verify that your setup is distributing traffic correctly.

**Key features**:
- Home Page (`/`): Displays the hostname of the container and the application version.
- Status Page (`/status`): Provides a JSON response with the hostname, the http status code, and a message indicating the app is running.
- Graceful Shutdown: Handles SIGTERM signals to allow for clean shutdowns.
- Stress Endpoint (`/stress`): Simulates CPU load for testing autoscaling scenarios.
- Sticky Session Endpoint (`/sticky`): Helps test load balancer stickiness by returning the hostname and client source IP.


> #### :bulb: [Also available on Docker Hub!](https://hub.docker.com/r/jmanzur/demo-lb-app)

## Pulling and Running the app from my Docker Hub:

```bash
docker run --restart=always -d -p 8882:8882 --env APP_VERSION=v2.0 --name DEMO-LB-APP jmanzur/demo-lb-app:latest
```

## Running the app locally (No Docker):

Clone the project

```bash
git clone https://github.com/JManzur/load-balancing-demo-app.git
```

Go to the project directory:
```bash
cd load-balancing-demo-app
```

Proceed to create a virtual environment:
```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

```bash
venv/bin/pip3 install -r requirements.txt 
```

Start the server:
```bash
python3 app.py
```

Access the web app:

[http://127.0.0.1:8882/](http://127.0.0.1:8882/)

And you will see something like this:

![App Screenshot](./images/lb_demo_app.png)

## Test the healthcheck status page

In order to test the healthcheck status page, you can access [http://127.0.0.1:8882/status](http://127.0.0.1:8882/status) in a browser or perform a curl like this:

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

## Build and Run the Docker image Locally:

Form the project directory run:
```bash
docker build -t demo-lb-app .
```

After building the image if you wish to test it locally run the following command.

Copy the IMAGE_ID
```bash
docker image ls
```

Run the image
```bash
docker run --restart=always -d -p 8882:8882 --env APP_VERSION=v2.0 --name DEMO-LB-APP <IMAGE_ID>
```

:bulb: **TIP**: You can also use the `rebuild_image.sh` script located in the scripts directory to build and run the image.

## Run the Docker image in a EKS Kubernetes Cluster

Go to the [kubernetes directory](./kubernetes) and apply the manifests:

```bash
kubectl apply -f .
```

For more information and tips on how to deploy this app in a EKS Kubernetes Cluster, check the [README file](./kubernetes/README.md) in the [kubernetes directory](./kubernetes).

### Aditional tips:

### Use a `while` loop to test the load balancing:

```bash
while true; do echo -n; curl -s http://<alb-dns>/status | jq -r; sleep 1; done
```

### Test Load Balancers cookie based stickiness:

To test sticky sessions with an AWS ALB Ingress Controller, make sure you have the following annotation in your `ingress.yaml` file:

```yaml
alb.ingress.kubernetes.io/target-group-attributes: stickiness.enabled=true,stickiness.lb_cookie.duration_seconds=60
```

Then, capture the cookie using `curl -c` option and use it in subsequent requests with `curl -b` option.
```bash
# Get the cookies
curl -c cookies.txt http://<alb-dns>
# Use the cookies in subsequent requests:
for i in {1..100}; do curl -b cookies.txt http://<alb-dns>/sticky; done
```

Alternatively, you can use the provided `sticky_test.sh` script to automate this process. Make sure to replace `<alb-dns>` with your actual ALB DNS name.
```bash
chmod +x sticky_test.sh
./sticky_test.sh <alb-dns> [duration_in_seconds]
# Example: ./sticky_test.sh demo-lb-app-0000000000.us-east-1.elb.amazonaws.com 60
```

You should see the same hostname in the response if sticky sessions are working. If stickiness is disabled or the session breaks, you'll hit different backends (with different hostnames).

### Test Load Balancers Source IP based stickiness:

To test sticky sessions based on source IP with an AWS ALB Ingress Controller, we need to use a Network Load Balancer (NLB) instead of an Application Load Balancer (ALB). To do this, we need to comment or delete the `ingress.yaml` file and replace the contents of the `service.yaml` file with the following configuration:

```yaml
---
apiVersion: v1
kind: Service
metadata:
  name: demo-lb-app
  labels:
    app: demo-lb-app
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: external
    service.beta.kubernetes.io/aws-load-balancer-scheme: internet-facing
    service.beta.kubernetes.io/aws-load-balancer-nlb-target-type: ip
    service.beta.kubernetes.io/aws-load-balancer-name: demo-lb-app
    # Sticky sessions and Preserve Source IP
    service.beta.kubernetes.io/aws-load-balancer-target-group-attributes: stickiness.enabled=true,stickiness.type=source_ip,preserve_client_ip.enabled=true
spec:
  type: LoadBalancer
  selector:
    app.kubernetes.io/name: demo-lb-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8882
  loadBalancerClass: service.k8s.aws/nlb
```

To test this with `curl`, we need to use the `--keepalive` option to maintain the same TCP connection:

```bash
curl -s --keepalive $(for i in {1..100}; do echo -n "--url http://<alb-dns>/sticky "; done)
```

### Use the `/stress` endpoint to demostrate autoscaling (CPU Load Simulation)

In the `kustomization.yaml` set the `ENABLE_STRESS` value to `true`, apply the manifests, **open at least 4 terminal windows** and run the following command in each of them:

```bash
while true; do echo -n; curl -s http://<alb-dns>/stress | jq -r; sleep 1; done
```

Monitor the average CPU utilization of the pods by running:

```bash
kubectl get hpa demo-lb-app-hpa -w
```

## Author

- [@JManzur](https://jmanzur.com)

## Documentation

- [Python - Docker Official Images](https://hub.docker.com/_/python)
- [AWS Load Balancer Controller](https://kubernetes-sigs.github.io/aws-load-balancer-controller/v2.13/)
- [ALB Ingress Annotations](https://kubernetes-sigs.github.io/aws-load-balancer-controller/v2.13/guide/ingress/annotations/)
- [NLB Service Annotations](https://kubernetes-sigs.github.io/aws-load-balancer-controller/v2.13/guide/service/annotations/)
- [Target groups for your Network Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/load-balancer-target-groups.html)
- [Target groups for your Application Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-target-groups.html)