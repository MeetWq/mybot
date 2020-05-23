#!/bin/bash

docker run --rm --name coolq \
	-v /sharedfolders/system/wangqian/coolq:/home/user/coolq \
	-p 9010:9000 \
	-p 5700:5700 \
	-e COOLQ_ACCOUNT=1846731675 \
	-e CQHTTP_POST_URL=http://0.0.0.0:8090 \
	-e CQHTTP_SERVE_DATA_FILES=true \
	-e VNC_PASSWD=12345678 \
	richardchien/cqhttp:latest | tee /var/log/coolq.log
