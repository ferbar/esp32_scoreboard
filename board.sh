
curl "http://esp_4bb5a3/initleds?0x43&0x40"
SLEEP=0.1
PIPE=/dev/null

while true; do
curl --silent "http://esp_4bb5a3/setleds?p=0&b=200&c=0x04&&c=0x04&c=0x04&c=0x04" > $PIPE
sleep $SLEEP
curl --silent "http://esp_4bb5a3/setleds?p=0&b=200&c=0x08&c=0x08&c=0x08&c=0x08" > $PIPE
sleep $SLEEP
curl --silent "http://esp_4bb5a3/setleds?p=0&b=200&c=0x10&c=0x10&c=0x10&c=0x10" > $PIPE
sleep $SLEEP
curl --silent "http://esp_4bb5a3/setleds?p=0&b=200&c=0x20&c=0x20&c=0x20&c=0x20" > $PIPE
sleep $SLEEP
curl --silent "http://esp_4bb5a3/setleds?p=0&b=200&c=0x40&c=0x40&c=0x40&c=0x40" > $PIPE
sleep $SLEEP
curl --silent "http://esp_4bb5a3/setleds?p=0&b=200&c=0x80&c=0x80&c=0x80&c=0x80" > $PIPE
sleep $SLEEP
done
