
# Running the application in Kubernetes:

To deploy the application is strucutred to be deployed using Kustomize. Kustomize is a tool to customize Kubernetes configurations. It allows you to create a set of patches to apply to a base configuration. 

## Basic Deployment:

Without any changes, and without using Kustomize, you can deploy the application using the following command:

```bash
kubectl apply -k .
```
To get the LoadBalancer URL, you can use the following command:

```bash
kubectl get ingress/ingress-demo-lb-app -n demo-lb-app
```

Open the URL in a browser or use curl to check the status of the application:

```bash
curl -s http://<LOAD_BALANCER_URL>/status | jq -r
```

💡Use the following one-liner to get the LoadBalancer URL and check the status of the application in a loop:

```bash
INGRESS_URL=$(kubectl get ingress/ingress-demo-lb-app -n demo-lb-app -o jsonpath='{.status.loadBalancer.ingress[0].hostname}') && while true; do echo -n; curl -s http://$INGRESS_URL/status | jq -r; sleep 1; done
```

⚠️ **NOTE**: This deployment uses a LoadBalancer service type, so it will create a **PUBLIC AWS ALB** and you will be charged for it, also your eks cluster needs to have the correct permissions to create the ALB, and the ALB controller needs to be installed in your cluster.
- [Install the AWS Load Balancer Controller using Kubernetes Manifests](https://docs.aws.amazon.com/eks/latest/userguide/lbc-manifest.html).

## Using Kustomize:

Kustomize can be used to do more complex deployments, like changing the image tag, or the number of replicas, the environment variables, etc.

### Change image tag:

Edit the `kustomization.yaml` file and change the image `newTag` value from `latest` to `v2`, or use the following command:

```bash
kustomize edit set image jmanzur/demo-lb-app:latest=jmanzur/demo-lb-app:v2
```

Command explanation:

- `kustomize edit set image`: Command to change the image tag.
- `jmanzur/demo-lb-app:latest`: Current image tag.
- `jmanzur/demo-lb-app:v2`: New image tag.

![Command Explanation](../images/kustomize_set_image.png)

### Change number of replicas:

Edit the `kustomization.yaml` file and change the number of replicas `count` value to the desired number, or use the following command:

```bash
kustomize edit set replicas deployment-demo-lb-app=4 
```

### Testing, Applying and Deleting the changes:

Test the changes:
```bash
kustomize build .
```

Apply the changes:
```bash
kustomize build . | kubectl apply -f -
```

Delete the changes:
```bash
kustomize build . | kubectl delete -f -
```

## Troubleshooting Tips:

### Namespace stuck in "Terminating" state:

If after deleting the resources using `kubectl delete -k .` or `kustomize build. | kubectl delete -f -` commands, the namespace is in a "Terminating" state, you can force the namespace to be deleted using the following commands:

```bash
NAMESPACE=demo-lb-app
kubectl proxy & kubectl get namespace $NAMESPACE -o json |jq '.spec = {"finalizers":[]}' > temp.json
curl -k -H "Content-Type: application/json" -X PUT --data-binary @temp.json 127.0.0.1:8001/api/v1/namespaces/$NAMESPACE/finalize
sleep 5 && rm temp.json
```
### Accessing the pod:

```bash
kubectl exec -it <POD-NAME> -n demo-lb-app -- /bin/bash
```

### Watching the pods activity:

```bash
watch kubectl get pods -n demo-lb-app
```

### Documentation:

- [Kustomize](https://kustomize.io/)
- [Install Kustomize](https://kubectl.docs.kubernetes.io/installation/kustomize/)
- [Kustomize edit set image](https://github.com/kubernetes-sigs/kustomize/blob/master/examples/image.md)
- [Install the AWS Load Balancer Controller add-on using Kubernetes Manifests](https://docs.aws.amazon.com/eks/latest/userguide/lbc-manifest.html)
- [Application load balancing on Amazon EKS](https://docs.aws.amazon.com/eks/latest/userguide/alb-ingress.html)
- [Install jq](https://jqlang.github.io/jq/download/)