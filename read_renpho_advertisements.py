import asyncio
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

print("=== Renpho ES-CS20M - Escucha por Advertisements (Método Pasivo) ===\n")
print("Pisa la báscula ahora y mantén los pies firmes hasta que se apague sola (10-15 segundos).")

received = False

def detection_callback(device: BLEDevice, advertisement_data: AdvertisementData):
    global received
    if device.name == "QN-Scale":
        print(f"\n✅ QN-Scale detectada | RSSI: {device.rssi} dBm")
        
        if advertisement_data.manufacturer_data:
            for company_id, data in advertisement_data.manufacturer_data.items():
                hex_data = data.hex()
                print(f"   Manufacturer Data (ID 0x{company_id:04x}): {hex_data}")
                
                # Intento de decodificar peso (común en QN-Scale)
                if len(data) >= 8:
                    weight_raw = (data[2] << 8) | data[3]   # posición común
                    weight_kg = weight_raw / 100.0
                    print(f"   → Peso tentativo: {weight_kg:.2f} kg")
                
                received = True

        if advertisement_data.service_data:
            print(f"   Service Data: {advertisement_data.service_data}")

async def main():
    scanner = BleakScanner(detection_callback=detection_callback)
    await scanner.start()
    
    print("Escaneando... (mantén los pies en la báscula)\n")
    
    # Escaneamos durante 25 segundos (más que el tiempo normal de la báscula)
    await asyncio.sleep(25)
    
    await scanner.stop()
    
    if not received:
        print("\nNo se recibieron datos de la báscula. Prueba pisando más fuerte o más cerca del Mac.")

if __name__ == "__main__":
    asyncio.run(main())
