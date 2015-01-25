#!/bin/bash
# User: linhaobuaa
# Date: 2015-01-20 22:00:00
# Version: 0.1.0
# mongorestore

export DATETIME=2015-01-13_11-16-28
mongorestore --host 219.224.135.46 --port 27019 -d news_$DATETIME dump/news_$DATETIME/news
