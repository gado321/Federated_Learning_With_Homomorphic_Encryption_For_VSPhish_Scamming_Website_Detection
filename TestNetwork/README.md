## Step 1: Create docker image

```bash
docker build -t ubuntu_update
```

## Step 2: Create network

```bash
docker-compose -f docker-compose.yaml up
```

## Step 3: Test a node

Open a node:

```bash
docker exec -it node-1 /bin/bash
```

Change `node-1` by name of other node (this test network has 5 nodes).

## Step 4: Send and get data to other node

Access the `training` folder, there are two file: `send_data.py` to send (broadcast) data, and `get_data.py` to get data from network. Please read two files and modify for ussage.
