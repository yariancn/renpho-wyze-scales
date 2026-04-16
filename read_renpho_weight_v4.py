import asyncio
from bleak import BleakScanner, BleakClient

# UUIDs conocidos de tu Renpho ES-CS20M (QN-Scale)
NOTIFY_CHAR = "0000ffe1-0000-1000-8000-00805f9b34fb"
WRITE_CHAR  = "0000ffe3-0000-1000-8000-00805f9b34fb"

def notification_handler(sender, data):
    hex_str = data.hex()
    print(f"\n📨 Datos recibidos: {hex_str}  ({len(data)} bytes)")

    if len(data) < 6:
        return

    if data[0] == 0x10:                     # Paquete de medición (el importante)
        weight_raw = (data[3] << 8) | data[4]
        weight_kg = weight_raw / 100.0

        # Byte 5 suele indicar si el peso está estable
        stable = (data[5] == 0x01)

        if stable:
            print(f"✅ PESO ESTABLE: {weight_kg:.2f} kg   ← ¡Este es tu peso real!")
        else:
            print(f"⚖️  Peso inestable: {weight_kg:.2f} kg")

async def main():
    print("=== Renpho ES-CS20M (QN-Scale) - Lectura v4 ===\n")
    print("Pisa la báscula con los pies descalzos y secos ahora...\n")

    devices = await BleakScanner.discover(timeout=12.0)
    renpho = next((d for d in devices if d.name == "QN-Scale"), None)

    if not renpho:
        print("❌ No se encontró la báscula QN-Scale. Pisa más fuerte.")
        return

    print(f"✅ Báscula encontrada: {renpho.address}")

    try:
        async with BleakClient(renpho.address) as client:
            print("✅ Conectado correctamente")

            # Pequeña pausa para estabilizar la conexión
            await asyncio.sleep(1.0)

            await client.start_notify(NOTIFY_CHAR, notification_handler)
            print("✅ Suscrito a notificaciones FFE1")

            # Comando mágico para solicitar medición en kg (probado en QN-Scale)
            cmd = bytes([0x13, 0x09, 0x15, 0x01, 0x10, 0x00, 0x00, 0x00, 0x42])
            await client.write_gatt_char(WRITE_CHAR, cmd, response=False)
            print("✅ Comando enviado. Esperando medición...\n")

            print("Mantén los pies firmes en la báscula durante 25-35 segundos...\n")
            await asyncio.sleep(35)   # Más tiempo para recibir el peso estable

            await client.stop_notify(NOTIFY_CHAR)
            print("\nPrueba terminada.")

    except Exception as e:
        print(f"❌ Error durante la ejecución: {e}")

if __name__ == "__main__":
    asyncio.run(main())
