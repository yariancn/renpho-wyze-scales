import asyncio
from bleak import BleakScanner, BleakClient

async def main():
    print("=== Conexión con Renpho ES-CS20M ===")
    print("Pisa la báscula con los pies descalzos y secos ahora...")
    print("El script esperará 15 segundos mientras escanea.\n")

    # Escanear dispositivos
    devices = await BleakScanner.discover(timeout=15.0)

    renpho = None
    for d in devices:
        name = d.name or ""
        if any(word in name.lower() for word in ["renpho", "es-cs20", "cs20", "scale"]):
            renpho = d
            print(f"✅ Báscula Renpho encontrada:")
            print(f"   Nombre: {name}")
            print(f"   Dirección: {d.address}")
            break

    if not renpho:
        print("❌ No se encontró la Renpho. Asegúrate de pisarla y que esté cerca del Mac.")
        return

    # Intentar conectar
    print(f"\nIntentando conectar a {renpho.address} ...")
    try:
        async with BleakClient(renpho.address) as client:
            print("✅ ¡Conexión exitosa!")

            # Mostrar servicios y características (esto ayuda a entender el protocolo)
            print("\nServicios y características encontradas:")
            for service in client.services:
                print(f"  Servicio: {service.uuid}")
                for char in service.characteristics:
                    props = char.properties
                    print(f"    → Característica: {char.uuid}  |  Propiedades: {props}")

            print("\nSi ves una característica con 'notify' o 'read' (especialmente algo con FFE1), es buena señal.")

    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        print("Consejos:")
        print("- Prueba varias veces (a veces falla la primera)")
        print("- Reinicia la báscula quitando y poniendo las baterías")
        print("- Asegúrate de que el Bluetooth del Mac esté encendido")

if __name__ == "__main__":
    asyncio.run(main())
