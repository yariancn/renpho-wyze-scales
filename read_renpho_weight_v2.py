import asyncio
from bleak import BleakScanner, BleakClient

SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
CHAR_NOTIFY = "0000ffe1-0000-1000-8000-00805f9b34fb"
CHAR_WRITE  = "0000ffe3-0000-1000-8000-00805f9b34fb"   # Usada para enviar comandos

def notification_handler(sender, data):
    print(f"\n📨 Datos recibidos ({len(data)} bytes): {data.hex()}")
    
    # Intentamos varias formas comunes de extraer peso
    if len(data) >= 10:
        # Prueba 1: bytes 5 y 6 (común en muchas escalas)
        weight1 = ((data[5] << 8) | data[6]) / 100.0
        print(f"   Prueba 1 (bytes 5-6): {weight1:.2f} kg")
        
        # Prueba 2: bytes 3-4
        weight2 = ((data[3] << 8) | data[4]) / 100.0
        print(f"   Prueba 2 (bytes 3-4): {weight2:.2f} kg")
        
        # Prueba 3: bytes 7-8
        weight3 = ((data[7] << 8) | data[8]) / 100.0
        print(f"   Prueba 3 (bytes 7-8): {weight3:.2f} kg")

async def main():
    print("=== Renpho ES-CS20M - Lectura Mejorada v2 ===\n")
    print("Pisa la báscula con pies descalzos y secos...")

    devices = await BleakScanner.discover(timeout=10)
    renpho = next((d for d in devices if d.name == "QN-Scale"), None)

    if not renpho:
        print("❌ No se encontró la QN-Scale. Pisa más fuerte.")
        return

    print(f"✅ Encontrada: {renpho.address}")

    try:
        async with BleakClient(renpho.address) as client:
            print("✅ Conectado")

            # Suscribirse a notificaciones
            await client.start_notify(CHAR_NOTIFY, notification_handler)
            print("✅ Suscrito a notificaciones FFE1")

            # Enviar comando común para solicitar medición (magic bytes para QN-Scale)
            print("Enviando comando para activar medición...")
            cmd = bytes([0x13, 0x09, 0x15, 0x01, 0x10, 0x00, 0x00, 0x00, 0x42])
            await client.write_gatt_char(CHAR_WRITE, cmd, response=False)
            print("Comando enviado.")

            # Esperar más tiempo para recibir datos
            print("Mantén los pies en la báscula por 25-30 segundos...\n")
            await asyncio.sleep(30)

            await client.stop_notify(CHAR_NOTIFY)
            print("\nPrueba finalizada.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
