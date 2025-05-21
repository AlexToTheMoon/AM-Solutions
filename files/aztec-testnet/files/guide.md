## OTLP >> Prometheus >> Grafana + TG Alarm

*Commnets or issues please at* **Discord** name **AlexeyM** handle - **amsolutions**  

**Docker must be installed before using this guide**

* * *

### Launch OTLP
```bash
docker run --rm -p  4318:4318 -p 8889:8889  -v "$(pwd)/otel-config/otel-collector-config.yaml":/etc/otelcol/config.yaml -d otel/opentelemetry-collector:latest
```

### Install Prometheus
```bash
cd $HOME
curl -s https://api.github.com/repos/prometheus/prometheus/releases/latest | \
grep browser_download_url | grep linux-amd64 | cut -d '"' -f 4 | wget -qi -
tar xfz prometheus-2.*.*tar.gz
rm $HOME/prometheus-2.*.*tar.gz
mv prometheus-2.* prometheus
sudo cp ~/prometheus/prometheus /usr/local/bin/
```
> After step above home folder will be created for config. The path to config will be: $HOME/prometheus/prometheus.yml

### Create Service file

```bash
sudo tee /etc/systemd/system/prometheusd.service << EOF
[Unit]
Description=Prometheus 
After=network-online.target
#
[Service]
User=$USER
ExecStart=$(which prometheus) --config.file="$HOME/prometheus/prometheus.yml"
RestartSec=10
Restart=on-failure
LimitNOFILE=65535
#
[Install]
WantedBy=multi-user.target
EOF
```
> In default Prometheus listening on port 9090, in it conflict with any other ports at your server, U can easily change it by adding flag --web.listen-address="0.0.0.0:<YOUR_PORT>" to prometheus service faile

### Launch Prometheus and check status

```bash
systemctl daemon-reload
sudo systemctl enable prometheusd.service
sudo systemctl restart  prometheusd.service
sudo systemctl status prometheusd.service
sudo journalctl -u prometheusd.service -fn 50 -o cat
```
"active (running)" means all good so far
![prom-status](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/files/grafana/prom-status.png)

### Add Your metrics source to the Prometheus config file  

Here is 2 options:  
1) node located at the same machine as prometheus   
2) at any other server (in this case node has to broadcast metrics to public access)    
Please use only one of the optons.

Open config file and add our source/target. Remind that config file located at : $HOME/prometheus/prometheus.yml

```bash
  - job_name: '<YOUR METRICS/PROJECT NAME>'
    scheme: http
    metrics_path: /metrics
    static_configs:
#     - targets: ['localhost:<PORT>'] #IF VALIDATOR NODE LOCATED ON THE SAME SERVER
      - targets: ['<IP-ADDRESS>:<PORT>'] #IF VALIDATOR NODE LOCATED AT ANOTHER SERVER
```

#### Save changes and restart Prometheus service
```bash
sudo systemctl restart  prometheusd.service
sudo systemctl status prometheusd.service
```

### Install Grafana
```bash
sudo apt-get install -y apt-transport-https
sudo apt-get install -y software-properties-common wget
sudo wget -q -O /usr/share/keyrings/grafana.key https://apt.grafana.com/gpg.key
echo "deb [signed-by=/usr/share/keyrings/grafana.key] https://apt.grafana.com beta main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
sudo apt-get update
sudo apt-get install grafana-enterprise
```
> Grafana service file will be created at dir : /lib/systemd/system/grafana-server.service (DONT EDIT WITH NO REASON)

### Run Grafana service, check status

```bash
sudo systemctl daemon-reload
sudo systemctl enable grafana-servers
sudo systemctl start grafana-server
sudo systemctl status grafana-server
```  

#### Now we can connect to our Grafana web page. For that U have to spell in your browser Ur public IP address where U installed Grafana along with port 3000 > http://IP:3000  

First time Your's username and password will be : admin
After U spell, system will ask to set different password, so, just go for it and save/remeber it.

![graf-login](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/files/grafana/graf-login.png)  



### Add metrics provider to Grafana (in our case Prometheus)  

Press Grafana logo on the left top corner and It will bring U to the main page, where we need to find DATA SOURCE field  

![add-source](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/files/grafana/data-s.png ) 

Add name and IP of the machine where You have installed Prometheus and default port 9090 If U haven`t changed it..  

![adding-prom](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/files/grafana/adding-source.png)

At the bottom of the page press Save & test

![save&test](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/files/grafana/save-test.png)

Success result as on picture below

![added-source](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/files/grafana/working-source.png)

All created Data sources U can find at “Settings” button > Data sources

![all-sources](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/files/grafana/data-sources.png) 

### Add Grafana dashboard

![dash-menu](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/files/grafana/add-dashboard.png)

There is two options to add dashboards :  
1) VIA JSON file  
2) VIA CODE/ID wich available at grafana.com website and requered to add specific exporters for each dashboard..  

![add-dash](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/files/grafana/add-dash.png)  

> After You press Load button, dashboard automatically will appear.


<p align="center">
    GOOD LUCK
</p>
