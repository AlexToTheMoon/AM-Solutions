## Remote Signing setup via TMKMS for Celestia "blockspacerace-0" testnet.

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
mkdir -p $HOME/tmkms/celestia
tmkms init $HOME/tmkms/celestia
```
#### Import Private key
Upload your validator (or create and move data) priv_validator_key.json 
to directory **$HOME/priv_validator_key.json**  
Then check availablity ```cat $HOME/priv_validator_key.json```  
If right output is appeared, follow next step below 
```
tmkms softsign import $HOME/priv_validator_key.json $HOME/tmkms/celestia/secrets/celestia-consensus.key
```
Now we can erase copy of original file  
```
sudo shred -uvz $HOME/priv_validator_key.json
```

#### Swap tmkms.toml to the one below. The only "addr =" field edit need to be done, replace it with your validator node IP + port(26658 default)
```
rm -rf ~/tmkms/celestia/tmkms.toml
```
```
tee ~/tmkms/celestia/tmkms.toml << EOF
#Tendermint KMS configuration file
[[chain]]
id = "blockspacerace-0"
key_format = { type = "bech32", account_key_prefix = "celestiapub", consensus_key_prefix = "celestiavalconspub" }
state_file = "$HOME/tmkms/celestia/state/blockspacerace-0_priv_validator_state.json"
#Software-based Signer Configuration
[[providers.softsign]]
chain_ids = ["blockspacerace-0"]
key_type = "consensus"
path = "$HOME/tmkms/celestia/secrets/celestia-consensus.key"
#Validator Configuration
[[validator]]
chain_id = "blockspacerace-0"
addr = "tcp://0.0.0.0:26658" #Set here IP and port of the Celestia node U will be using for signing blocks (port can be custom)   
secret_key = "$HOME/tmkms/celestia/secrets/kms-identity.key"
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
ExecStart=$(which tmkms) start -c $HOME/tmkms/celestia/tmkms.toml
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

`INFO tmkms::commands::start: tmkms 0.12.2 starting up...`    
`INFO tmkms::keyring: [keyring:softsign] added consensus Ed25519 key: celestiavalcons1....`    
`INFO tmkms::connection::tcp: KMS node ID: a1dbc4edb1dbb2bcd9316081bd810f57e0d`  
`ERROR tmkms::client: [blockspacerace-0@tcp://<NODE IP>:26658] I/O error: Connection`  

#### LAST STEPS. Activate signing from Celestia-App node side

Find field `priv_validator_laddr = ""` at dir `$HOME/.celestia-app/config/config.toml` and edit to your Validator IP + port  
**Make sure your firewall open only for KMS server IP to allow connect to port 26658 (or any custom port u set)**

Example : `priv_validator_laddr = "tcp://0.0.0.0:26658"`

If u have more than one IP u have to set right IP (the same as in tmkms config file)

##### Restart Celestia-App node and check TMKMS logs   

Good logs example :  
`INFO tmkms::session: [blockspacerace-0@tcp://<IP>:26658] connected to validator successfully`

`WARN tmkms::session: [blockspacerace-0@tcp://<IP>:26658]: unverified validator peer ID! (ad1fc4b45ee2340bb8148d7247bf82ea780y213q)`  
`INFO tmkms::session: [blockspacerace-0@tcp://<IP>:26658] signed PreCommit:<nil> at h/r/s 8825119/0/2 (0 ms)`  
`INFO tmkms::session: [blockspacerace-0@tcp://<IP>:26658] signed PreVote:144665D1CE at h/r/s 8825120/0/1 (0 ms)`  
`INFO tmkms::session: [blockspacerace-0@tcp://<IP>:26658] signed PreCommit:144665D1CE at h/r/s 8825120/0/2 (0 ms)`  
`INFO tmkms::session: [blockspacerace-0@tcp://<IP>:26658] signed PreVote:13BF759486 at h/r/s 8825121/0/1 (0 ms)`  


### Backup in safe place priv_validator_key.json and delete it from Validator node. Now U signing from KMS server!

##
<p align="center">
That pretty much all. Good luck!
</p>
