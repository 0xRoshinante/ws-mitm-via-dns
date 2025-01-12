import asyncio
import argparse
import websockets
import re
import ssl
from websocket import create_connection
def connection(hedef_url, proxy_host, proxy_port):
    global hedef_websocket
    hedef_websocket = create_connection(
    hedef_url,
    http_proxy_host=proxy_host,
    http_proxy_port=proxy_port,
    sslopt={"cert_reqs": ssl.CERT_NONE}
)
async def echo(websocket, path, port, proxy_host, proxy_port):
    global hedef_url
    protokol = "wss" if websocket.secure else "ws"
    host = websocket.request_headers['Host'] 
    if re.search(r":\d+$", host):  
        hedef_url = f"{protokol}://{host}{path}"
    else:
        hedef_url = f"{protokol}://{host}:{port}{path}" 
    connection(hedef_url, proxy_host, proxy_port)
    while True:
        try:
            while True:
                mesaj = await asyncio.wait_for(websocket.recv(), timeout=2)
                await asyncio.get_event_loop().run_in_executor(None, hedef_websocket.send, mesaj)
        except asyncio.TimeoutError:
            print("istemciden mesajı alınmıyor")
        try:
            yanıt = await asyncio.wait_for(asyncio.get_event_loop().run_in_executor(None, hedef_websocket.recv),timeout=2)
            await websocket.send(yanıt)
        except asyncio.TimeoutError:
            print("Sunucudan yanıt alınmıyor")
async def main(port, proxy_host, proxy_port, certfile, keyfile):
    ssl_context = None
    if certfile and keyfile: 
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(certfile=certfile, keyfile=keyfile) 
    async with websockets.serve(
        lambda ws, path: echo(ws, path, port, proxy_host, proxy_port), 
        "0.0.0.0", port, ssl=ssl_context 
    ):
        await asyncio.Future()
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Custom WebSocket istemcileri için DNS tabanlı MITM Aracı")
    parser.add_argument("--port", type=int, required=True, help="Dinlenecek port numarası")
    parser.add_argument("--proxy-host", type=str, required=True, help="Proxy sunucu IP adresi Örn. 127.0.0.1")
    parser.add_argument("--proxy-port", type=int, required=True, help="Proxy sunucu port numarası Örn. 8080")
    parser.add_argument("--certfile", type=str, help="SSL sertifika dosyası yolu (.pem türünde)")
    parser.add_argument("--keyfile", type=str, help="SSL anahtar dosyası yolu (.pem türünde)")
    args = parser.parse_args()
    asyncio.run(main(args.port, args.proxy_host, args.proxy_port, args.certfile, args.keyfile))
