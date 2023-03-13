# Tenderduty monitoring and alerting system guide for Regen validator + Telegram alert bot setup.
**Please notice!** This is just additional notification service which **can NOT be taken as a main source of the Validator control!**

In this guide Tenderduty run as a "build from source" binaries via systemd service.
Also docker container and docker-compose available as an options.
U can find original docs [HERE](https://github.com/blockpane/tenderduty/blob/main/docs/install.md) for docker options.

*If any commnets or issues U can contact me at* **Discord** - AlexeyM#5409

## Create new user (from root)
```bash
adduser tenderduty
usermod -aG sudo tenderduty
ssh tenderduty@localhost
```

## Install dependencies

```bash
sudo apt update && sudo apt upgrade -y && sudo apt autoremove -y && sudo apt install make clang pkg-config libssl-dev build-essential git jq llvm libudev-dev -y
```

## Install GO

```bash
wget https://go.dev/dl/go1.19.linux-amd64.tar.gz \
&& sudo tar -xvf go1.19.linux-amd64.tar.gz \
&& sudo mv go /usr/local \
&& echo "export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin" >> ~/.bash_profile \
&& source ~/.bash_profile \
&& go version
rm go1.19.linux-amd64.tar.gz
```
## Install binaries and setup config file

```bash
git clone https://github.com/blockpane/tenderduty.git
cd tenderduty
go install
```
#### Download config sample
```bash
wget -qO $HOME/config.yml https://github.com/AlexToTheMoon/AM-Solutions/raw/main/Tenderduty/regen/config.yml
```
#### Set your valoper address
Open file `$HOME/config.yml` find `chains:` paragraph, set your valoper address here : `valoper_address:` and save file.

![valoper](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/Tenderduty/regen/png/val-conf.png)

## Create system file and run Tenderduty

```bash
sudo tee /etc/systemd/system/tenderduty.service << EOF
[Unit]
Description=Tenderduty
After=network.target
ConditionPathExists=$(which tenderduty)

[Service]
Type=simple
Restart=always
RestartSec=5
TimeoutSec=180

User=$USER
WorkingDirectory=$HOME
ExecStart=$(which tenderduty)

# there may be a large number of network connections if a lot of chains
LimitNOFILE=infinity

# extra process isolation
NoNewPrivileges=true
ProtectSystem=strict
RestrictSUIDSGID=true
LockPersonality=true
PrivateUsers=true
PrivateDevices=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF
```
#### Run service

```bash
sudo systemctl daemon-reload
sudo systemctl enable tenderduty
sudo systemctl start tenderduty
```

#### Check logs
```bash
sudo journalctl -u tenderduty -f -o cat
```
This is how the right logs supposed to look like

![logs](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/Tenderduty/regen/png/logs-ubuntu.png)

#### Check dashboard 

By default Tenderduty dashboard run at port `8888`. Just open your browser and open dashboard by typing `http://<SERVER_IP_HERE>:8888`  <br />

Sample of right working dashboard  <br />
![dsh](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/Tenderduty/regen/png/dashboard-logs.png)

<br />

# Telegram alert bot setup


Create your own group at Telegram where your bot will be sending alert notifications  <br />
Find **@BotFather** user at telegram and create your own Bot (use any available name) Use `/newbot` command <br />

**>>> PLEASE COPY HTTP API KEY AND SAVE <<<**

![bot](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/Tenderduty/rebus/png/newbot.png)

### Add bot to your group and find out group ID

Find your bot by TG @username and add to your group 

![bot-gr1](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/Tenderduty/rebus/png/add-group-bot.png)

#### Find out group ID

Find bot named **@JsonViewBot** and add to your group <br />
Bot should join group, show your group ID and leave the group. <br />

**>>> PLEASE COPY GROUP ID AND SAVE <<<**

![gr-ad](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/Tenderduty/rebus/png/add-group-json.png)

![id](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/Tenderduty/rebus/png/group-id.png)

### Activate Telegram bot

Open file `$HOME/config.yml` find `#telegram settings:` paragraph, set some params we saved above: <br />
enabled: yes <br />
api_key: <YOUR_BOT_API_KEY> <br />
channel: <YOUR_GROUP_ID> <br />
Save changes.

![tg-api-id](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/Tenderduty/rebus/png/tg-conf.png)

### Last steps...

Restart tenderduty service 
```bash
sudo systemctl restart tenderduty
```
**NOTE** : If after restart U will find logs like : <br />
`REGEN is configured for telegram alerts, but it is not enabled` never mind, it doesn`t mean Telegram notification is not working.

Set up Your Telegram notification settings to receive notifications from created group!

#### Test service

Now we can stop Regen validator to miss >=5 blocks, and this what we expect to see when missing blocks and then when node back to normal state:

#### AT DASHBOARD
![dash-miss](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/Tenderduty/regen/png/dash-alarm.png)

#### AT TELEGRAM
![tg-alarm](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/Tenderduty/regen/png/tg-alarm.png)

# Discord alert bot setup

Coming soon...

<p align="center">
    GOOD LUCK
</p>
