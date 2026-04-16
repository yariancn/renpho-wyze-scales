import asyncio
from bleak import BleakScanner, BleakClient

SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
CHAR_NOTIFY = "0000ffe1-0000-1000-8000-00805f9b34fb"
CHAR_WRITE  = "0000ffe3-0000-1000-8000-00805f9b34fb"

def notification_handler(sender, data):
    hex_data = data.hex()
    print(f"\n📨 Datos: {hex_data}  ({len(data)} bytes)")
    
    if len(data) < 11:
        return
    
    # Decodificación mejorada para QN-Scale (Renpho ES-CS20M)
    packet_type = data[0]
    
    if packet_type == 0x10:   # Paquete de medición
        weight_raw = (data[3] << 8) | data[4]
        weight_kg = weight_raw / 100.0
        
        # Intentar detectar si es estable (byte 5 o 6 suele indicar estado)
        stable = data[5] == 0x01 or data[6] == 0x01
        
        if stable:
            print(f"✅ PESO ESTABLE: {weight_kg:.2f} kg")
        else:
            print(f"⚖️  Peso (inestable): {weight_kg:.2f} kg")
            
        # Otras pruebas rápidas
        print(f"   Prueba alternativa (bytes 5-6): {((data[5]<<8)|data[6])/100:.2f} kg")

async def main():
    print("=== Renpho ES-CS20M - Lectura v3 (Mejor decodificación) ===\n")
    print("Pisa la báscula con pies descalzos y secos...")

    devices = await BleakScanner.discover(timeout=10)
    renpho = next((d for d in devices if d.name == "QN-Scale"), None)

    if not renpho:
        print("❌ No se encontró la báscula.")
        return

    print(f"✅ Encontrada: {renpho.address}")

    try:
        async with BleakClient(renpho.address) as client:
            print("✅ Conectado")
            await client.start_notify(CHAR_NOTIFY, notification_handler)
            print("✅ Suscrito a notificaciones")

            # Comando para solicitar medición en kg
            cmd = bytes([0x13, 0x09, 0x15, 0x01, 0x10, 0x00, 0x00, 0x00, 0x42])
            await client.write_gatt_char(CHAR_WRITE, cmd, response=False)
            print("Comando enviado. Esperando medición...\n")

            print("Mantén los pies firmes en la báscula durante 25-30 segundos...\n")
            await asyncio.sleep(30)

            await client.stop_notify(CHAR_NOTIFY)
            print("\nPrueba terminada.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
