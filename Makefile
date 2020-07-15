.PHONY: FORCE

GKE_PATH=eu.gcr.io/iterum
K3D_PATH=registry.localhost:5000/iterum
MICROK8S_PATH=localhost:32000/iterum
TAG=latest



build: FORCE
	docker build -t demo-fragmenter:$(TAG) ./0_fragmenter
	docker build -t demo-edge-detection:$(TAG) ./1_edge_detection
	docker build -t demo-hough-transform:$(TAG) ./2_hough_transform

tag-gke: FORCE
	docker tag demo-fragmenter $(GKE_PATH)/demo-fragmenter:$(TAG)
	docker tag demo-edge-detection $(GKE_PATH)/demo-edge-detection:$(TAG)
	docker tag demo-hough-transform $(GKE_PATH)/demo-hough-transform:$(TAG)

push-gke: FORCE
	docker push $(GKE_PATH)/demo-fragmenter:$(TAG)
	docker push $(GKE_PATH)/demo-edge-detection:$(TAG)
	docker push $(GKE_PATH)/demo-hough-transform:$(TAG)


tag-k3d: FORCE
	docker tag demo-fragmenter $(K3D_PATH)/demo-fragmenter:$(TAG)
	docker tag demo-edge-detection $(K3D_PATH)/demo-edge-detection:$(TAG)
	docker tag demo-hough-transform $(K3D_PATH)/demo-hough-transform:$(TAG)

push-k3d: FORCE
	docker push $(K3D_PATH)/demo-fragmenter:$(TAG)
	docker push $(K3D_PATH)/demo-edge-detection:$(TAG)
	docker push $(K3D_PATH)/demo-hough-transform:$(TAG)


tag-microk8s: FORCE
	docker tag demo-fragmenter $(MICROK8S_PATH)/demo-fragmenter:$(TAG)
	docker tag demo-edge-detection $(MICROK8S_PATH)/demo-edge-detection:$(TAG)
	docker tag demo-hough-transform $(MICROK8S_PATH)/demo-hough-transform:$(TAG)

push-microk8s: FORCE
	docker push $(MICROK8S_PATH)/demo-fragmenter:$(TAG)
	docker push $(MICROK8S_PATH)/demo-edge-detection:$(TAG)
	docker push $(MICROK8S_PATH)/demo-hough-transform:$(TAG)

rebuild-push-microk8s: FORCE
	make build
	make tag-microk8s
	make push-microk8s