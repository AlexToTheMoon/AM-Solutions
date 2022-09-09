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
##