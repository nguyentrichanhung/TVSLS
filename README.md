# TVSLS
[GB_VT] TRAFFIC VIOLATION SYSTEM  LOCAL SERVER


# ```Usage```
### ```Init setup```
 - Change folder .env.example to .env
  
 - Run environment variables
```bash
source .env
```
- Run docker
```bash
docker-compose build
docker-compose up
```

### ```Clean process```
```bash
### stop docker-compose process
docker-compose down -v

### Remove images of dockers
docker rmi $(docker images -a -q)

### Remove database data
sudo rm -rf /postgres-data
```

# ```Server Infomation```

- backend port : 5000

- database port : 5432

------
# ```Install Model```

You can download the model with attach link here: [Yolov5 + Deep_sort Model](https://drive.google.com/drive/folders/1CMBAeir3w_nchYcvYa4HvJMK65smjslO?usp=sharing)