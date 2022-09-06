# How to move node from basic run to Cosmovisor service and prepare for an upgrade.
## Testnet "INNUENDO-1"  v0.6.4-rc.0 >> v0.6.6-hotfix

*If any commnets or issues U can contact me at* **Discord** - AlexeyM#5409

## Step by step instructions 

Install Cosmovisor 
```bash
git clone https://github.com/cosmos/cosmos-sdk
cd cosmos-sdk
git checkout v0.45.8
make cosmovisor
cp cosmovisor/cosmovisor $HOME/go/bin/cosmovisor
cd $HOME
```
Create cosmovisor subfolders
```bash
mkdir -p ~/.quicksilverd/cosmovisor/genesis/bin
mkdir -p ~/.quicksilverd/cosmovisor/upgrades/v0.6.6/bin/
```
Setting up some ENVIRONMENT VARIABLES
```bash
echo "export DAEMON_NAME=quicksilverd" >> ~/.bash_profile
echo "export DAEMON_HOME=$HOME/.quicksilverd" >> ~/.bash_profile
source ~/.bash_profile
```
Copy existing version `v0.6.4-rc.0` into cosmovisor launch folder
```bash
cp $(which quicksilverd) ~/.quicksilverd/cosmovisor/genesis/bin
cosmovisor version
```
Create a cosmovisor systemd service
```bash
sudo tee /etc/systemd/system/cosmovisor-qck.service > /dev/null <<EOF
[Unit]
Description=Cosmovisor Process Manager
After=network.target

[Service]
User=$USER
ExecStart=$(which cosmovisor) start
Restart=always
LimitNOFILE=4096

Environment="DAEMON_NAME=quicksilverd"
Environment="DAEMON_HOME=$HOME/.quicksilverd"
Environment="DAEMON_RESTART_AFTER_UPGRADE=true"
Environment="DAEMON_ALLOW_DOWNLOAD_BINARIES=false"
Environment="UNSAFE_SKIP_BACKUP=false"

[Install]
WantedBy=multi-user.target
EOF
```
Now stop basic quicksilverd.service and run it from cosmovisor
```bash
sudo systemctl stop quicksilverd.service
sudo systemctl disable quicksilverd.service
sudo systemctl daemon-reload
sudo systemctl enable cosmovisor-qck.service
sudo systemctl restart cosmovisor-qck.service
journalctl -u cosmovisor-qck.service -f -o cat
```
Prepare new binaries for upgrade
```bash
cd quicksilver
git pull
git checkout v0.6.6-hotfix.2
make install 
quicksilverd version
```
Move new binaries to upgrade folder
```bash
cp $(which quicksilverd) ~/.quicksilverd/cosmovisor/upgrades/v0.6.6/bin
```
Double check U got new binaries at upgrade folder. Output expected `v0.6.6-hotfix.2`
```bash
$HOME/.quicksilverd/cosmovisor/upgrades/v0.6.6/bin/quicksilverd version
```
Restart cosmovisor service and wait for upgrage height 
```bash
sudo systemctl restart cosmovisor-qck.service
```

<p align="center">
    GOOD LUCK
</p>


