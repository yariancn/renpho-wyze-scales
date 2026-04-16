import asyncio
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

print("=== Renpho ES-CS20M - Escucha por Advertisements (Versión corregida) ===\n")
print("Pisa la báscula ahora y mantén los pies firmes hasta que se apague sola (10-15 segundos).")

def detection_callback(device: BLEDevice, advertisement_data: AdvertisementData):
    if device.name == "QN-Scale":
        print(f"\n✅ QN-Scale detectada | Dirección: {device.address}")
        
        # Manufacturer Data (aquí es donde suelen ir el peso en algunos modelos)
        if advertisement_data.manufacturer_data:
            for company_id, data in advertisement_data.manufacturer_data.items():
                hex_data = data.hex()
                print(f"   Manufacturer Data (ID 0x{company_id:04x}): {hex_data} ({len(data)} bytes)")
                
                # Intento de decodificar peso (posiciones comunes en QN-Scale)
                if len(data) >= 6:
                    # Prueba varias posiciones comunes
                    for offset in range(0, len(data)-1):
                        weight_raw = (data[offset] << 8) | data[offset+1]
                        if 2000 < weight_raw < 20000:   # rango razonable 20kg - 200kg
                            weight_kg = weight_raw / 100.0
                            print(f"   → Peso posible en offset {offset}: {weight_kg:.2f} kg")

        # Service Data (otro lugar donde pueden ir datos)
        if advertisement_data.service_data:
            for uuid, data in advertisement_data.service_data.items():
                print(f"   Service Data ({uuid}): {data.hex()}")

        print("-" * 60)

async def main():
    scanner = BleakScanner(detection_callback=detection_callback)
    
    await scanner.start()
    print("Escaneando... Mantén los pies en la báscula hasta que termine su medición normal y se apague.\n")
    
    await asyncio.sleep(25)   # 25 segundos debería ser suficiente
    
    await scanner.stop()
    print("\nEscaneo finalizado.")

if __name__ == "__main__":
    asyncio.run(main())
