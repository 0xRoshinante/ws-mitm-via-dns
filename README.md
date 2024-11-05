# ws-mitm-via-dns
Custom WebSocket istemcileri için DNS tabanlı Proxy Aracı

Bu proje spesifik amaçlar için geliştirilmiş, dahili olarak proxy özniteliği barındırmayan WebSocket istemcileri için DNS tabanlı bir proxy aracı sağlar. WebSocket üzerinden gelen istekleri alır ve bir trigger-server vasıtasıyla belirtilen proxy sunucusu üzerinden gerçek hedefe yönlendirir.

## Özellikler

- Proxy öz niteliği taşımayan websocket istemcileri için yönlendirme ve araya girme desteği sağlar.
- Hedef URL istemciden, trigger-servera gelen paketler üzerinden dinamik olarak belirlenir.

## Gereksinimler

- Python 3.7 veya üzeri
- `websockets` kütüphanesi
- `websocket-client` kütüphanesi

## Kurulum

1. Projeyi klonlayın:
   ```bash
   git clone https://github.com/0xRoshinante/ws-mitm-via-dns
   cd ws-mitm-via-dns

2. Gereklilikleri Kurun:
   ```bash
   pip install websockets websocket-client

3. Trigger-server için sertifikalarınızı oluşturun:
   ```bash
   openssl genrsa -out mitm-key.pem 2048
   openssl req -new -x509 -key mitm-key.pem -out mitm-cert.pem -days 365

4. Test uygulamanızın websocket bağlantısı kurmaya çalıştığı domaini hosts dosyanızda local IP değerinize eşleyin
   ```bash
   [Local IP Örn. 192.168.1.100] uygulamadan-bu-alana-ws-bağlantısı-gerceklesiyor.[hedef].com

## Kullanım

1. Secure bağlantılar için:
   ```bash
   python proxy_tool.py --port PORT_NUMARASI --proxy_host PROXY_IP --proxy_port PROXY_PORT --certfile mitm-cert.pem --keyfile mitm-key.pem

2. Secure olmayan bağlantılar için:
   ```bash
    python proxy_tool.py --port TRIGGER_SERVER_PORT_NUMARASI --proxy_host PROXY_IP --proxy_port PROXY_PORT
