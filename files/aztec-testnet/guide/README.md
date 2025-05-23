## OTLP >> Prometheus >> Grafana + TG Alarm

*Commnets or issues please at* **Discord** name **AlexeyM**,  ID **amsolutions**  
* * *

### Install Docker (if not installed)  
Update packages and install dependencies  
```
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release
```
Add Docker GPG Key  
```
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```
Add Docker repository  
```
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```
Install Docker  
```
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
Check installation if installaton is succesfull  
```
sudo docker version
sudo docker run hello-world
```
Add user to Docker group, to run without "sudo"  
```
sudo usermod -aG docker $USER
newgrp docker  # or restart session
```

### Launch OTLP 
Create config file
```
mkdir $HOME otlp-metrics
sudo tee $HOME/otlp-metrics/config.yaml << EOF
receivers:
  otlp:
    protocols:
      http:
        endpoint: "0.0.0.0:4318" 

exporters:
  prometheus:
    endpoint: "0.0.0.0:8889" 

service:
  pipelines:
    metrics:
      receivers: [otlp]
      exporters: [prometheus]
EOF
```

Launch OTLP container

```bash
docker run --rm --name ams-hotel -p  4318:4318 -p 8889:8889  -v "$HOME/otlp-metrics/config.yaml":/etc/otelcol/config.yaml -d otel/opentelemetry-collector:latest
```
Check logs  
```
docker logs ams-hotel
```
Good logs example (last line)
> Everything is ready. Begin running and processing data.


### Setup metrics flow from Sequencer > OTLP

Add metrics flag to the Sequencer node  
Change <OTLP_SERVER_IP> to IP address where is OTLP service operating

> For Docker launch

```--tel.metricsCollectorUrl=http://<OTLP_SERVER_IP>:4318/v1/metrics```

> For Docker Compose enviromnent

```OTEL_EXPORTER_OTLP_METRICS_ENDPOINT: "http://<OTLP_SERVER_IP>:4318/v1/metrics"```

 - Restart you Sequencer node
 -  check metrics at http://<OTLP_SERVER_IP>:8889/metrics

If metrics appeared, follow next steps


### Install Prometheus
```bash
cd $HOME
url=$(curl -s https://api.github.com/repos/prometheus/prometheus/releases/latest \
  | grep browser_download_url \
  | grep linux-amd64.tar.gz \
  | cut -d '"' -f 4) && \
wget "$url" -O prometheus.tar.gz && \
tar -xzf prometheus.tar.gz && \
rm prometheus.tar.gz && \
mv prometheus-* prometheus && \
sudo cp prometheus/prometheus /usr/local/bin/
```
#### Create Service file

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

#### Launch Prometheus and check status

```bash
systemctl daemon-reload
sudo systemctl enable prometheusd.service
sudo systemctl restart  prometheusd.service
sudo systemctl status prometheusd.service
sudo journalctl -u prometheusd.service -fn 50 -o cat
```
![prom-status](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/files/grafana/prom-status.png)

### Import OTLP to the Prometheus config
Insert the IP address of the server where OTLP is installed into the variable below
```
export OTLP_IP="<OTLP IP HERE>"
```
<sub>example : export OTLP_IP="151.211.147.201"</sub >  


Overwrite the Prometheus config
```
sudo tee $HOME/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: "otel-collector"
    static_configs:
      - targets: ['${OTLP_IP}:8889']
EOF
```

#### Restart Prometheus service & check status
```bash
sudo systemctl restart  prometheusd.service
sudo systemctl status prometheusd.service
```
#### Check Prometheus importing OTLP metrics 
Go  > `http://<PROMETHEUS SEVER IP>:9090/targets`  

Example of successed installation
![](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/files/aztec-testnet/guide/docs/prom-targets.png)  

### Install Grafana
```
docker run -d -p 3000:3000 --name=grafana grafana/grafana
```
#### Grafana Login in

Open Grafana page via `http://<SERVER_IP>:3000`

First login credentials 
 - username : admin
 - password : admin

![graf-login](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/files/grafana/graf-login.png)  

### Add data source 

On the sidebar go > Connections > Add new connection 

Add name and IP of the server where Prometheus being operating + default port 9090 

![adding-prom](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/files/grafana/adding-source.png)

At the bottom of the page press Save & test

![save&test](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/files/grafana/save-test.png)

Success result as on picture below

![added-source](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/files/grafana/working-source.png)

All created Data sources can be found at  `Sidebar => Connections => Data sources`  

### Add Grafana dashboard

![dash-menu](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/files/grafana/add-dashboard.png)

There is two options to add dashboards :  
 - VIA JSON file  
 - VIA CODE/ID wich available at grafana.com website and requered to add specific exporters for each dashboard

   Our BETA dashboard(JSON) for AZTEC [HERE](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/files/aztec-testnet/guide/docs/AZTEC-beta.json) 

![add-dash](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/files/grafana/add-dash.png)  

> After Load button pressing, dashboard will appear automatically

### Create Telegram Node health notification/alarm service
 - Find TG bot by handle **@BotFather**
 - Execute /start, than /newbot
 - Enter bot name, make sure it ends with **bot**
 - **Copy and save HTTP API token**

![bot](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/Tenderduty/rebus/png/newbot.png) 

#### Create group and join bot
 - Create new group in Telegram
 - Find created bot by @USERNAME
 - Add bot to the group  

![bot-gr1](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/Tenderduty/rebus/png/add-group-bot.png)

#### Find group ID

 - Find bot named **@JsonViewBot** and add to your group
 - Bot should join group, show your group ID and leave the group
 - Save Grop ID

![gr-ad](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/Tenderduty/rebus/png/add-group-json.png)  


![id](https://github.com/AlexToTheMoon/AM-Solutions/blob/main/Tenderduty/rebus/png/group-id.png)








<p align="center">
    GOOD LUCK
</p>
