# Tenderduty monitoring and alerting system guide for Umee validator + Telegram alert bot setup.
**Please notice!** This is just additional notification service which **can NOT be taken as a main source of the Validator control!**

In this guide Tenderduty run as a build from source binaries via systemd service.
Also docker container and docker compose available as an options.
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
git clone https://github.com/blockpane/tenderduty
cd tenderduty
go install
```
#### Download config sample
```bash
wget -q -O $HOME/config.yml https://github.com/AlexToTheMoon/AM-Solutions/raw/main/Tenderduty/config.yml
```
#### Set your valoper address
Open file `$HOME/config.yml` find `chains:` paragraph and set your valoper address and save. Right example below

![valoper](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/Tenderduty/png/set-valoper-adr.png)

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

![logs](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/Tenderduty/png/healthy-log.png)

#### Check dashboard 

By default Tenderduty dashboard run at port `8888`. Just open your browser and open dashboard by typing `http://<SERVER_IP_HERE>:8888`  <br />

Sample of right working dashboard  <br />
![dsh](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/Tenderduty/png/healthy-dsh.png)





