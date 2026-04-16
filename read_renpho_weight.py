import asyncio
from bleak import BleakScanner, BleakClient

# UUIDs de tu báscula
SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"

def notification_handler(sender, data):
    """Esta función se llama cada vez que la báscula envía datos"""
    print(f"\n📨 Datos recibidos (hex): {data.hex()}")
    print(f"   Longitud: {len(data)} bytes")
    
    # Decodificación básica conocida para QN-Scale (peso inestable y estable)
    if len(data) >= 6 and data[0] == 0x10:
        weight_raw = (data[3] << 8) | data[4]
        weight_kg = weight_raw / 100.0
        
        if data[5] == 0x01:
            print(f"✅ PESO ESTABLE: {weight_kg:.2f} kg")
        else:
            print(f"⚖️  Peso inestable: {weight_kg:.2f} kg")
    else:
        print("   (Formato desconocido por ahora)")

async def main():
    print("=== Leyendo peso de Renpho ES-CS20M (QN-Scale) ===")
    print("Pisa la báscula con los pies descalzos y secos...\n")

    # Escanear
    devices = await BleakScanner.discover(timeout=10.0)
    renpho = None
    for d in devices:
        if d.name == "QN-Scale":
            renpho = d
            print(f"✅ Encontrada: {d.name} - {d.address}")
            break

    if not renpho:
        print("❌ No se encontró la báscula. Pisa fuerte para activarla.")
        return

    # Conectar y suscribirse a notificaciones
    try:
        async with BleakClient(renpho.address) as client:
            print("✅ Conectado. Esperando mediciones...\n")
            print("Mantén los pies en la báscula hasta que veas el peso estable.\n")
            
            # Suscribirse a la característica FFE1
            await client.start_notify(CHAR_UUID, notification_handler)
            
            # Esperar 30 segundos para recibir datos
            await asyncio.sleep(30)
            
            await client.stop_notify(CHAR_UUID)
            print("\n✅ Prueba terminada.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
