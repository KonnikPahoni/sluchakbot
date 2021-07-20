# Бот СЛУЧАК

Бот СЛУЧАК патрэбен кожнаму, хто размаўляе па-беларуску:

- Дапаможа абараніць беларускую мову і вашыя моўныя правы
- Падзеліцца прыкладамі беларускамоўных бланкаў і дакументаў
- Распавядзе, дзе вы можаце пачуць беларускую мову ў адказ

Бот створаны ініцыятывай «Умовы для мовы». Тэхнічная падтрымка: @KonnikPahoni (Telegram)

### Рэдагаванне боту

Дадавай ці змяняй файлы ў тэчцы `files` каб мяняць кантэнт бота

### Разгортванне на серверы

```
docker stop sluchakbot || true && docker build -t sluchakbot_image . && docker container rm sluchakbot || true && docker run -d --restart always --network="host" --name sluchakbot -v "$(pwd)/var":/var sluchakbot_image
```

### Архіў доступу

Архіў доступу да бота захоўваецца ў файлах `var/access_log.txt` і `var/users.txt`
