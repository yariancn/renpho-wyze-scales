import asyncio
from bleak import BleakScanner, BleakClient

NOTIFY_CHAR = "0000ffe1-0000-1000-8000-00805f9b34fb"
WRITE_CHAR  = "0000ffe3-0000-1000-8000-00805f9b34fb"

received_packets = []

def notification_handler(sender, data):
    hex_str = data.hex()
    print(f"📨 Recibido: {hex_str} ({len(data)} bytes)")
    received_packets.append(bytes(data))

async def main():
    print("=== Renpho ES-CS20M - Versión SIMPLE y ESTABLE ===\n")
    print("Pisa la báscula fuerte con pies descalzos y secos ahora.\n")

    devices = await BleakScanner.discover(timeout=12.0)
    renpho = next((d for d in devices if d.name == "QN-Scale"), None)

    if not renpho:
        print("❌ No se encontró la báscula.")
        return

    print(f"✅ Báscula encontrada: {renpho.address}")

    try:
        async with BleakClient(renpho.address, timeout=30.0) as client:
            print("✅ Conectado")

            # Pausa larga para que macOS termine el Service Discovery
            await asyncio.sleep(4.5)

            await client.start_notify(NOTIFY_CHAR, notification_handler)
            print("✅ Suscrito a FFE1")

            # Comando para activar medición
            cmd = bytes([0x13, 0x09, 0x15, 0x01, 0x10, 0x00, 0x00, 0x00, 0x42])
            await client.write_gatt_char(WRITE_CHAR, cmd, response=False)
            print("✅ Comando enviado\n")

            print("Mantén los pies firmes hasta que la báscula termine y se apague (~15 segundos)\n")
            await asyncio.sleep(28)

            await client.stop_notify(NOTIFY_CHAR)

            # Procesar al final
            print("\n=== PROCESANDO DATOS ===")
            if not received_packets:
                print("No se recibieron paquetes.")
                return

            for i, data in enumerate(received_packets):
                if len(data) >= 6 and data[0] == 0x10:
                    weight_raw = (data[3] << 8) | data[4]
                    weight_kg = weight_raw / 100.0
                    stable = (len(data) > 5 and data[5] == 0x01)

                    if stable:
                        print(f"✅ PESO ESTABLE: **{weight_kg:.2f} kg**  ← Este debería ser tu peso correcto")
                    else:
                        print(f"   Paquete {i+1}: {weight_kg:.2f} kg")

            print(f"\nTotal de paquetes recibidos: {len(received_packets)}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
