```
curl -sSfL -O https://github.com/penumbra-zone/penumbra/releases/download/v0.78.0/pd-x86_64-unknown-linux-gnu.tar.gz
tar -xf pd-x86_64-unknown-linux-gnu.tar.gz
sudo mv pd-x86_64-unknown-linux-gnu/pd /usr/local/bin/
```

```
git clone https://github.com/cometbft/cometbft.git
cd cometbft
git checkout  v0.37.5
make build
sudo mv build/cometbft /usr/local/bin/
```

```
curl --proto '=https' --tlsv1.2 -LsSf https://github.com/penumbra-zone/penumbra/releases/download/v0.78.0/pcli-installer.sh | sh
```

```
pd testnet join --moniker MY_MONIKER
```

```
sudo tee /etc/systemd/system/penumbra-pd.service << EOF
[Unit]
Description=Penumbra-PD
[Service]
User=$USER
#Group=ubuntu
ExecStart=/usr/local/bin/pd start --home $HOME/.penumbra/testnet_data/node0/pd
RestartSec=10
Restart=on-failure
LimitNOFILE=65535
[Install]
WantedBy=multi-user.target
EOF
```

```
sudo tee /etc/systemd/system/penumbra-cometbft.service << EOF
[Unit]
Description=Penumbra-CometBFT
[Service]
User=$USER
#Group=ubuntu
ExecStart=/usr/local/bin/cometbft start --home $HOME/.penumbra/testnet_data/node0/cometbft
RestartSec=10
Restart=on-failure
LimitNOFILE=65535
[Install]
WantedBy=multi-user.target
EOF
```

```
sudo systemctl daemon-reload
sudo systemctl enable penumbra-pd.service
sudo systemctl enable penumbra-cometbft.service
```

```
cd $HOME
snap=$(curl -s https://snap-penumbra.theamsolutions.info | egrep -o ">penumbra-snap*.*tar" | tr -d ">")
wget -P $HOME https://snap-penumbra.theamsolutions.info/${snap}
workd="$HOME/.penumbra/testnet_data/node0"
rm -rf ${workd}/cometbft/data/ ${workd}/pd/rocksdb/
tar xf ~/penumbra-snap*.*tar -C ${workd} && rm ~/penumbra-snap*.*tar
```

```
sudo systemctl restart penumbra-pd.service
sudo systemctl restart penumbra-cometbft.service
sudo journalctl -u penumbra-cometbft.service -fn 50 -o cat
```

```
curl -s http://localhost:26657/status | jq ."result"."sync_info"
```
