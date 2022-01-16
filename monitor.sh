#!/bin/sh
# Twitter space Recorder
# This script is designd for docker-compose.

if [ -z "$TWITTER_ID" ]; then
  echo "This script is designd for docker-compose."
  exit 1
fi

INTERVAL=${INTERVAL:-10}
COOKIES_PATH="/output/cookies.txt"

# Monitor live streams of specific user
while true; do
  LOG_PREFIX=$(date +"[%m/%d/%y %H:%M:%S] [tw_space@${TWITTER_ID}] ")

  # Start recording
  if [ ! -f "$COOKIES_PATH" ]; then
    echo "$LOG_PREFIX [VRB] Start trying..."  
    /venv/bin/twspace_dl -U "https://twitter.com/${TWITTER_ID}" --write-url "master_urls.txt"
  else
    echo "$LOG_PREFIX [VRB] Start trying with cookies..."
    /venv/bin/twspace_dl -U "https://twitter.com/${TWITTER_ID}" --write-url "master_urls.txt" --input-cookie-file "$COOKIES_PATH" -o "$COOKIES_PATH"
  fi

  echo "$LOG_PREFIX [VRB] Sleep $INTERVAL sec."
  sleep "$INTERVAL"
done
