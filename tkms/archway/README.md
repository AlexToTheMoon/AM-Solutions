## Remote Signing setup via TMKMS for Archway.

#### Please notice:

This guide about "Soft-Sign" option, which is software signing structure. There is also HSM option available, for hardware signing methods like Ledger etc.. What requires physical access to the server. More information available at official docs [HERE](https://github.com/iqlusioninc/tmkms)

At remote signing host (where we setup tmkms) should be managed high level of security. Like non root access, firewalls etc.. 

Best option to use VPN tunel for connection between remote signer host and validator node.

How to setup VPN at Ubuntu U can find [HERE](https://www.digitalocean.com/community/tutorials/how-to-set-up-and-configure-an-openvpn-server-on-ubuntu-20-04)
or any another source like Google or YouTube.  

For any feedback or comments, please contact Discord - AlexeyM#5409

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
mkdir -p $HOME/tmkms/archway
tmkms init $HOME/tmkms/archway
```
#### Import Private key
Upload your validator (or create and move data) priv_validator_key.json 
to directory **$HOME/priv_validator_key.json***  
Then check availablity ```cat $HOME/priv_validator_key.json```  
If right output is appeared, follow next step below 
```
tmkms softsign import $HOME/priv_validator_key.json $HOME/tmkms/archway/secrets/archway-consensus.key
```
Now we can erase copy of original file  
```
shred -uvz $HOME/priv_validator_key.json
```

#### Swap tmkms.toml to the one below. The only "addr =" field edit need to be done, replace it with your validator node IP + port(26658 default)
```
rm -rf ~/tmkms/archway/tmkms.toml
```
```
tee ~/tmkms/archway/tmkms.toml << EOF
#Tendermint KMS configuration file
[[chain]]
id = "archway-1"
key_format = { type = "bech32", account_key_prefix = "archwaypub", consensus_key_prefix = "archwayvalconspub" }
state_file = "$HOME/tmkms/archway/state/archway-1-priv_validator_state.json"
#Software-based Signer Configuration
[[providers.softsign]]
chain_ids = ["archway-1"]
key_type = "consensus"
path = "$HOME/tmkms/archway/secrets/archway-consensus.key"
#Validator Configuration
[[validator]]
chain_id = "archway-1"
addr = "tcp://10.10.10.12:26658" #Set here validator IP and port
secret_key = "$HOME/tmkms/archway/secrets/kms-identity.key"
protocol_version = "v0.34"
reconnect = true
EOF
```

#### Create service file and run TMKMS
```
sudo tee /etc/systemd/system/tmkmsd-archway.service << EOF
[Unit]
Description=TMKMS-Archway
After=network.target
StartLimitIntervalSec=0
[Service]
Type=simple
Restart=always
RestartSec=10
User=$USER
ExecStart=$(which tmkms) start -c /home/tmkms/tmkms/archway/tmkms.toml
LimitNOFILE=1024
[Install]
WantedBy=multi-user.target
EOF
```
```
sudo systemctl daemon-reload
sudo systemctl enable tmkmsd-archway.service
sudo systemctl restart tmkmsd-archway.service
sudo systemctl status tmkmsd-archway.service
```
to check logs
```
sudo journalctl -u tmkmsd-archway.service -f -o cat
```
Sample of normal logs at present stage

`INFO tmkms::keyring: [keyring:softsign] added consensus Ed25519 key: archwayvalconspub1zcjduepqpg8kmjv...`  
`2022-12-07T09:04:15.959017Z  INFO tmkms::connection::tcp: KMS node ID: 8090d2661357dadb5e8888f234ecee41603f1873`  
`2022-12-07T09:04:15.962726Z ERROR tmkms::client: [archway-1@tcp://10.10.10.12:26658] I/O error: Connection refused (os error 111)`

#### LAST STEPS. Activate remote signing from Archway node side

Find field `priv_validator_laddr = ""` at dir `$HOME/.archway/config/config.toml` and edit to your Validator IP + port  
Basically it should be the same as in tmkms.toml file.

Example : `priv_validator_laddr = "tcp://10.10.10.12:26658"`

##### Restart Archway node and check TMKMS logs   

Good logs example :  

`INFO tmkms::session: [archway-1@tcp://173.212.215.104:26658] connected to validator successfully`  
`WARN tmkms::session: [archway-1@tcp://173.212.215.104:26658]: unverified validator peer ID! (458562cf0d3e17f0d7755ccafdcd977ca93e0304)`  
`INFO tmkms::session: [archway-1@tcp://173.212.215.104:26658] signed PreVote:266AB0AF95 at h/r/s 954948/0/1 (0 ms)`  
`INFO tmkms::session: [archway-1@tcp://173.212.215.104:26658] signed PreCommit:266AB0AF95 at h/r/s 954948/0/2 (0 ms)` 


### Backup in safe place priv_validator_key.json and remove it from Validator node.

##
<p align="center">
That pretty much all. Good luck!
</p>
