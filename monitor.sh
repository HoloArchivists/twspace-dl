#!/bin/sh
# Twitter space Recorder
# This script is designd for docker-compose.

if [ -z "$TWITTER_ID" ]; then
  echo "This script is designd for docker-compose."
  exit 1
fi

COOKIES_PATH="./cookies.txt"
if [ ! -f "$COOKIES_PATH" ]; then
  echo "The cookies file is now required due to the Twitter API change that prohibited guest user access to Twitter API endpoints on 2023-07-01."
  exit 1
fi

INTERVAL=${INTERVAL:-10}

# Monitor live streams of specific user
while true; do
  LOG_PREFIX=$(date +"[%m/%d/%y %H:%M:%S] [tw_space@${TWITTER_ID}]")

  # Start recording
  echo "$LOG_PREFIX Start trying..."
  /venv/bin/twspace_dl -U "https://twitter.com/${TWITTER_ID}" --write-url "master_urls.txt" --input-cookie-file "$COOKIES_PATH"

  echo "$LOG_PREFIX Sleep $INTERVAL sec."
  sleep "$INTERVAL"
done
