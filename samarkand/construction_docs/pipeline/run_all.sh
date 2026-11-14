cd /tmp/claude-0/-home-user-zerotwelve/1b150d8a-25e8-5370-b86d-453a7d8bda62/scratchpad
for v in $(python3 -c "import json;print(' '.join(json.load(open('cd/spec.json'))))"); do
  [ -f cd/out/${v}_c.png ] && continue
  timeout 1200 bvenv/bin/python cd/passes2.py -- cd/spec.json $v 2>&1 | grep -E "^ok|Error|Traceback" | head -3
done
echo ALLDONE
