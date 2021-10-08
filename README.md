# Twspace-dl

Early development

## Usage

```bash
python twspace_dl/main.py -i space_id
ffmpeg -protocol_whitelist file,https,tls,tcp -i space_id.m3u8 -c copy space_id.aac
```
