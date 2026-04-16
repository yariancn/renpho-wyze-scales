import asyncio
from bleak import BleakScanner, BleakClient

NOTIFY_CHAR = "0000ffe1-0000-1000-8000-00805f9b34fb"
WRITE_CHAR  = "0000ffe3-0000-1000-8000-00805f9b34fb"

received_data = []   # Aquí guardamos todos los paquetes primero

def notification_handler(sender, data):
    hex_str = data.hex()
    print(f"📨 Recibido: {hex_str}  ({len(data)} bytes)")
    received_data.append(data)   # Guardamos el paquete crudo

async def main():
    print("=== Renpho ES-CS20M - v6 (Recibir primero, procesar después) ===\n")

    devices = await BleakScanner.discover(timeout=12.0)
    renpho = next((d for d in devices if d.name == "QN-Scale"), None)

    if not renpho:
        print("❌ No se encontró la báscula.")
        return

    print(f"✅ Báscula encontrada: {renpho.address}")

    try:
        async with BleakClient(renpho.address) as client:
            print("✅ Conectado")

            await asyncio.sleep(2.0)   # Pausa importante para Service Discovery

            await client.start_notify(NOTIFY_CHAR, notification_handler)
            print("✅ Suscrito - Recibiendo datos...\n")

            # Enviar comando para activar medición
            cmd = bytes([0x13, 0x09, 0x15, 0x01, 0x10, 0x00, 0x00, 0x00, 0x42])
            await client.write_gatt_char(WRITE_CHAR, cmd, response=False)
            print("✅ Comando enviado\n")

            print("Mantén los pies firmes en la báscula durante **35 segundos**...\n")
            await asyncio.sleep(35)

            await client.stop_notify(NOTIFY_CHAR)

            # === PROCESAMOS TODOS LOS DATOS DESPUÉS ===
            print("\n=== Procesando datos recibidos ===")
            for i, data in enumerate(received_data):
                if len(data) >= 6 and data[0] == 0x10:
                    weight_raw = (data[3] << 8) | data[4]
                    weight_kg = weight_raw / 100.0
                    stable = (data[5] == 0x01)

                    if stable:
                        print(f"✅ PESO ESTABLE: {weight_kg:.2f} kg   ← ¡Este debería ser tu peso!")
                    else:
                        print(f"   Paquete {i}: Peso inestable {weight_kg:.2f} kg")

            if not received_data:
                print("No se recibieron datos.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
