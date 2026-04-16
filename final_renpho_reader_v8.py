import asyncio
from bleak import BleakScanner, BleakClient

NOTIFY_CHAR = "0000ffe1-0000-1000-8000-00805f9b34fb"
WRITE_CHAR  = "0000ffe3-0000-1000-8000-00805f9b34fb"

received_packets = []

def notification_handler(sender, data):
    hex_str = data.hex()
    print(f"📨 Recibido: {hex_str} ({len(data)} bytes)")
    received_packets.append(bytes(data))  # Copia segura

async def main():
    print("=== Renpho ES-CS20M - Lector Final v8 (Más estable) ===\n")
    print("Pisa la báscula fuerte con pies descalzos y secos.\n")

    devices = await BleakScanner.discover(timeout=12.0)
    renpho = next((d for d in devices if d.name == "QN-Scale"), None)

    if not renpho:
        print("❌ No se encontró la QN-Scale.")
        return

    print(f"✅ Báscula encontrada: {renpho.address}")

    try:
        # Conexión con timeout más alto
        async with BleakClient(renpho.address, timeout=25.0) as client:
            print("✅ Conectado correctamente")

            # Pausa larga para que macOS termine el Service Discovery
            await asyncio.sleep(3.0)

            await client.start_notify(NOTIFY_CHAR, notification_handler)
            print("✅ Suscrito a notificaciones FFE1")

            # Comando para solicitar medición
            cmd = bytes([0x13, 0x09, 0x15, 0x01, 0x10, 0x00, 0x00, 0x00, 0x42])
            await client.write_gatt_char(WRITE_CHAR, cmd, response=False)
            print("✅ Comando enviado\n")

            print("Mantén los pies firmes hasta que la báscula termine su proceso y se apague (~15 seg)\n")
            await asyncio.sleep(25)

            await client.stop_notify(NOTIFY_CHAR)

            # Procesar todo al final
            print("\n=== Procesando datos recibidos ===")
            if not received_packets:
                print("No se recibieron paquetes.")
                return

            for i, data in enumerate(received_packets):
                if len(data) >= 6 and data[0] == 0x10:
                    weight_raw = (data[3] << 8) | data[4]
                    weight_kg = weight_raw / 100.0
                    stable = (len(data) > 5 and data[5] == 0x01)

                    if stable:
                        print(f"✅ ¡PESO ESTABLE DETECTADO!: **{weight_kg:.2f} kg**")
                    else:
                        print(f"   Paquete {i+1}: {weight_kg:.2f} kg (inestable)")

            print(f"\nTotal paquetes recibidos: {len(received_packets)}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Consejo: Reinicia la báscula quitando una batería 5 segundos.")

if __name__ == "__main__":
    asyncio.run(main())
