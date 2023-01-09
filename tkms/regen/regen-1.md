## Remote Signing setup via TMKMS for Regen chain.

#### Please notice:

This guide about "Soft-Sign" option, which is software signing structure. There is also HSM option available, for hardware signing methods like Ledger etc.. What requires physical access to the server. More information available at official docs [HERE](https://github.com/iqlusioninc/tmkms)

In inducation proposes, for new users, we guide TMKMS at Umee testnet, but there is no difference between settings for mainnet. Just edit chain-id, "addr =" field and obviously use mainnet "priv_validator_key.json".

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
mkdir -p $HOME/tmkms/regen
tmkms init $HOME/tmkms/regen
```
#### Import Private key
Upload your validator (or create and move data) priv_validator_key.json 
to directory **$HOME/priv_validator_key.json***  
Then check availablity ```cat $HOME/priv_validator_key.json```  
If right output is appeared, follow next step below 
```
tmkms softsign import $HOME/priv_validator_key.json $HOME/tmkms/regen/secrets/regen-consensus.key
```
Now we can erase copy of original file  
```
sudo shred -uvz $HOME/priv_validator_key.json
```

#### Swap tmkms.toml to the one below. The only "addr =" field edit need to be done, replace it with your validator node IP + port(26658 default)
```
rm -rf ~/tmkms/regen/tmkms.toml
```
```
tee ~/tmkms/regen/tmkms.toml << EOF
#Tendermint KMS configuration file
[[chain]]
id = "regen-1"
key_format = { type = "bech32", account_key_prefix = "regenpub", consensus_key_prefix = "regenvalcons" }
state_file = "$HOME/tmkms/regen/state/cregen-1_priv_validator_state.json"
#Software-based Signer Configuration
[[providers.softsign]]
chain_ids = ["regen-1"]
key_type = "consensus"
path = "$HOME/tmkms/regen/secrets/regen-consensus.key"
#Validator Configuration
[[validator]]
chain_id = "regen-1"
addr = "tcp://10.10.10.12:26658" #Set here IP and port of the Regen node U will be using for signing blocks (port can be custom)   
secret_key = "$HOME/tmkms/regen/secrets/kms-identity.key"
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
ExecStart=$(which tmkms) start -c $HOME/tmkms/regen/tmkms.toml
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

`INFO tmkms::keyring: [keyring:softsign] added consensus Ed25519 key: umeevalconspub1zcjduepqpg8kmjv...`  
`2022-12-07T09:04:15.959017Z  INFO tmkms::connection::tcp: KMS node ID: 8090d2661357dadb5e8888f234ecee41603f1873`  
`2022-12-07T09:04:15.962726Z ERROR tmkms::client: [canon-2@tcp://10.10.10.12:26658] I/O error: Connection refused (os error 111)`

#### LAST STEPS. Activate siging from Validator side

Find field `priv_validator_laddr = ""` at dir `$HOME/.regen/config/config.toml` and edit to your Validator IP + port  
Make sure your firewall open only for KMS server IP to allow connect to port 26658 (or any custom port u set)

Example : `priv_validator_laddr = "tcp://0.0.0.0:26658"`

##### Restart UMEE node and check TMKMS logs   

Good logs example :  
 


### Backup in safe place priv_validator_key.json and remove it from Validator node.

##
<p align="center">
That pretty much all. Good luck!
</p>
