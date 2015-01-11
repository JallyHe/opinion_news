#!/bin/bash
# User: linhaobuaa
# Date: 2015-01-09 12:00:00
# Version: 0.1.0
# mongodump

export DATETIME="$(date "+%Y-%m-%d_%H-%M-%S")"
echo $DATETIME
mongodump --host 219.224.135.46 --port 27019 -d news -o dump/news_$DATETIME
mongorestore --host 219.224.135.46 --port 27019 -d news_$DATETIME dump/news_$DATETIME/news
