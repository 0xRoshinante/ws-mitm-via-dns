import asyncio
import argparse
import websockets
import re
import ssl
from websocket import create_connection

#SADECE WEB SOCKET TE ÇALIŞIR
#address already in use hatası veriyorsa lsof -i:PORT ile bakıp PID leri kill -9 ile öldürmek gerekiyor.
#toolu CTRL + z ile kapamayın, CTRL C ve X tuşlarına art arda basın proccess sağlıklı ölecektir.
#portu uygulama hangi adrese çıkıyosa oraya ayarlamak lazım. Ya da uygulamayı hooklayıp portu keyfi bi değere set etmek.

def connection(hedef_url, proxy_host, proxy_port):
    global hedef_websocket
    hedef_websocket = create_connection(
    hedef_url,
    http_proxy_host=proxy_host,
    http_proxy_port=proxy_port,
    sslopt={"cert_reqs": ssl.CERT_NONE} #Kimseye güvenmeyen, kimseye güven vermez :)
)

async def echo(websocket, path, port, proxy_host, proxy_port):
    # hedefi ayıklıyoz

    global hedef_url
    protokol = "wss" if websocket.secure else "ws" # burda protokolü ayıklıyoz
    host = websocket.request_headers['Host'] # hostu çekiyoz
    if re.search(r":\d+$", host):  # Burda custom istemciler farklı davranabiliyo kimisinde host içinde port da geliyo kimisinde gelmeyo sonra sunucuya çıkarken sorun oluyo. sonunda port varsa bole yapıoz 
        hedef_url = f"{protokol}://{host}{path}"
    else:
        hedef_url = f"{protokol}://{host}:{port}{path}" # sonunda port yoksa portu ekliyoz
    # socket bağlantısını inite ediyoz.
    connection(hedef_url, proxy_host, proxy_port)

    # ana döngümüz bu asenkron yapıyla oynayınca bozuluyo. En temizi boyle.
    while True:
            # 1. İstemciden mesaj al burda döngü var çünkü istemci bazen 1 den çok mesaj çıkıyor. o durumda sunucuyu dinleyicinin treadi ölüyor, döngü bozuluyor. sunucudan birden çok mesaj gelirse sorun olmuyor ama orda döngüya gerek yok main döngüde dengeleniyo o.
        try:
            while True:
                mesaj = await asyncio.wait_for(websocket.recv(), timeout=2)
                print(f"istemciden kaptığımız mesaj: {mesaj}")
                await asyncio.get_event_loop().run_in_executor(None, hedef_websocket.send, mesaj)
                print("sunucuya çıktığımız mesaj: " + mesaj)
            
        except asyncio.TimeoutError:
            print("istemciden mesajı kapamadı")


                
        # 3. Sunucudan yanıt al
        try:
            yanıt = await asyncio.wait_for(asyncio.get_event_loop().run_in_executor(None, hedef_websocket.recv),timeout=2)
            await websocket.send(yanıt)
            print(f"istemciye geri döndüğümüz mesaj: {yanıt}")

        except asyncio.TimeoutError:
            print("Sunucudan yanıt alamıyoz")


# servü burda ayarlıyoz.
async def main(port, proxy_host, proxy_port, certfile, keyfile):
    print("Tikat: Lütfen hosts dosyanızda gerekli güncellemeleri yaptğınızdan emin olunuz ! Bi de gülümseyin :) Neşesiz bir toplumun parlak bir geleceği olmaz")
    ssl_context = None
    if certfile and keyfile:  # eğer cert verirsen secure serv etcek. cert vermezsen secure olmadan serv etcek. Yoksa hata veriyor.
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(certfile=certfile, keyfile=keyfile) # secure serv için ssl zımbırtılarını ayarlıyoz.

    async with websockets.serve(
        lambda ws, path: echo(ws, path, port, proxy_host, proxy_port), #argları iletiyoz echo fonksiyonuna
        "0.0.0.0", port, ssl=ssl_context #her yeri dinlicek şekilde serv veriyoz. Bunu istersen locale ayarlarsın ama böyle daha iyi mobil testlerde sorun çıkıyo sonra.
    ):
        await asyncio.Future()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Custom WebSocket istemcileri için DNS tabanlı MITM Aracı")
    parser.add_argument("--port", type=int, required=True, help="Dinlenecek port numarası")# bu localde trigger-serverı serve edeceğiniz port. Proxy portu değil.
    parser.add_argument("--proxy_host", type=str, required=True, help="Proxy sunucu IP adresi Örn. 127.0.0.1")#proxy olarak Burp kullanılabilir. WS mesajlarını görüntüleme derdim yok sadece belirli bir tünele route etcem diyosanız chisel, CCProxy filanda olur. Herhangi bir proxy olur ya :)
    parser.add_argument("--proxy_port", type=int, required=True, help="Proxy sunucu port numarası Örn. 8081")#buda proxynizde dinlediğiniz port. Diğer portla karıştırmayın lütfen. Unutmayın trigger-serverı serve ettiğiniz port ile bu aynı olamaz. proxynizde sonuçta serve ediyor aynı portta edemezler :)
    parser.add_argument("--certfile", type=str, help="SSL sertifika dosyası yolu (.pem türünde) Örn. mitm-cert.pem (openssl ile üretebilirsiniz) # sadece şifreli bağlantılarda")#bu
    parser.add_argument("--keyfile", type=str, help="SSL anahtar dosyası yolu (.pem türünde) Örn. mitm-key.pem # sadece şifreli bağlantılarda")#ve bunu hedefiniz sadece wss destekliyorsa girceniz. Yoksa girmiceniz.
    args = parser.parse_args() # argümanları alıyoz klasik

    asyncio.run(main(args.port, args.proxy_host, args.proxy_port, args.certfile, args.keyfile)) #marşa basıyoz.

