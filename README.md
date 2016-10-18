# MacOpener
MacOpener for guet by nightwind

# Usage
guetsec@GuetSec:~/MacOpener$ python3.5 app.py  --help

usage: app.py [-h] [-l LISTEN] [-p PORT] [-s SERVER] [-sp SERVER_PORT] [-i IP]
              [-t INTERVAL] [-d DELAY] [-r ROOT] [--debug] [--timeout TIMEOUT]
              [--checker_interval CHECKER_INTERVAL] [--ip_forward] [-k KEY]

MAC opener for GUET by nightwind

optional arguments:
  -h, --help            show this help message and exit
  -l LISTEN, --listen LISTEN
  -p PORT, --port PORT
  -s SERVER, --server SERVER
  -sp SERVER_PORT, --server port SERVER_PORT
  -i IP, --ip IP
  -t INTERVAL, --interval INTERVAL
  -d DELAY, --delay DELAY
  -r ROOT, --root ROOT
  --debug
  --timeout TIMEOUT     status checker timeout seconds
  --checker_interval CHECKER_INTERVAL
                        status checker interval seconds
  --ip_forward
  -k KEY, --key KEY     the password for update server (default:I_am_the_key)


  
# Note
  1. 只能在宿舍使用,网段大概为（10.21.0.0/16),其他网段无效.
  2. 如果程序获取ip失败，可以使用参数指定本机ip：--ip xx.xx.xx.xx
  3. 可以自定义服务器，使用--server指定，还可以附加--ip_forward选项表示服务器用于转发报文（这样报文里面的本机IP是转发服务器的IP），这样就可以将客户端（可以使带端口转发的路由器）放在宿舍，然后web服务端，放在别的地方。
  4. 如果用转发服务器的话，而且放在宿舍的openwrt上，因为每天断电加上DHCP可能改变IP地址，这样可以在转发服务器上运行一下脚本来向服务器更新转发服务器地址：
 
``` bash
date
server='sec.guet.edu.cn/open'
ip=`ifconfig eth1.1 | awk '/inet addr/ {print $2}' | cut -f2 -d ":"`
echo $ip
curl -d "ip=$ip&key=I_am_the_key&blocking=true" $server/api/server
```
  作用就是获取指定网卡的ip然后通过/api/server的POST请求更新ip地址。参数key是服务端预设的密码，防止恶意干扰；
  blocking=true：阻塞模式，即等待服务端检查ip地址返回success或timeout。否则非阻塞模式：立刻返回，不立刻检查ip，服务端后台自行检查更新ip，一律返回accepted。
