## Remote Signing setup via TMKMS for Umee "canon-2" chain testnet.

#### Please notice:

This guide about "Soft-Sign" option, which is software signing structure. There is also HSM option available, for hardware signing methods like Ledger etc.. What requires physical access to the server. More information available at official docs [HERE](https://github.com/iqlusioninc/tmkms)

In inducation proposes, for new users, we guide TMKMS at Umee testnet, but there is no difference between settings for mainnet. Just edit chain-id, "addr =" field and obviously use mainnet "priv_validator_key.json".

At remote signing host (where we setup tmkms) should be managed high level of security. Like non root access, firewalls etc.. 

Best option to use VPN tunel for connection between remote signer host and validator node.

How to setup VPN at Ubuntu U can find [HERE](https://www.digitalocean.com/community/tutorials/how-to-set-up-and-configure-an-openvpn-server-on-ubuntu-20-04)
or any another source like Google or YouTube.
##
<p align="center">
Instructions
</p>

##### Create new user (from root)
```
adduser tmkms
usermod -aG sudo tmkms
su tmkms
cd $HOME
```

##### Install RUST
```
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

##### Install GCC 
```
sudo apt update & sudo apt install build-essential curl jq  --yes
```

##### Compile and sort TMKMS binaries
```
cd $HOME
cargo install tmkms --features=softsign
sudo mv $HOME/.cargo/bin/tmkms /usr/local/bin/
```

##### Create and Init TKMS working directory
```
mkdir -p $HOME/tmkms/umee
tmkms init $HOME/tmkms/umee
```
#### Import Private key
Upload your validator (or create and move data) priv_validator_key.json 
to directory **$HOME/priv_validator_key.json***  
Then check availablity ```cat $HOME/priv_validator_key.json```  
If right output is appeared, follow next step below 
```
tmkms softsign import $HOME/priv_validator_key.json $HOME/tmkms/umee/secrets/umee-consensus.key
```
Now we can erase copy of original file  
```
shred -uvz $HOME/priv_validator_key.json
```

#### Swap tmkms.toml to the one below. The only "addr =" field edit need to be done, replace it with your validator node IP + port(26658 default)
```
rm -rf ~/tmkms/umee/tmkms.toml
```
```
tee ~/tmkms/umee/tmkms.toml << EOF
#Tendermint KMS configuration file
[[chain]]
id = "canon-2"
key_format = { type = "bech32", account_key_prefix = "umeepub", consensus_key_prefix = "umeevalconspub" }
state_file = "/home/kms/tmkms/umee/state/canon-2-priv_validator_state.json"
#Software-based Signer Configuration
[[providers.softsign]]
chain_ids = ["canon-2"]
key_type = "consensus"
path = "/home/kms/tmkms/umee/secrets/umee-consensus.key"
#Validator Configuration
[[validator]]
chain_id = "canon-2"
addr = "tcp://10.10.10.10:26658" #Set here validator IP and port
secret_key = "/home/kms/tmkms/umee/secrets/kms-identity.key"
protocol_version = "v0.34"
reconnect = true
EOF
```

#### Create service file and run TMKMS
```
sudo tee /etc/systemd/system/tmkmsd.service << EOF
[Unit]
Description=TMKMS
After=network.target
StartLimitIntervalSec=0
[Service]
Type=simple
Restart=always
RestartSec=10
User=$USER
ExecStart=$(which tmkms) start -c $HOME/tmkms/umee/tmkms.toml
LimitNOFILE=1024
[Install]
WantedBy=multi-user.target
EOF
```
```
sudo systemctl daemon-reload
sudo systemctl enable tmkmsd.service
sudo systemctl restart tmkmsd.service
sudo systemctl status tmkmsd.service
```
to check logs
```
sudo journalctl -u tmkmsd.service -f -o cat
```
Sample of normal logs at present stage
![tmkms-launch](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/tkms/umee/pict/logs-tmkms-first.png?raw=true)

##### Last step.  validator 



