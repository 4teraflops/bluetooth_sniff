import asyncio
import json
from pydbus import SystemBus
from datetime import datetime
import device_class_decoder
from loguru import logger

logger.add(f'log/{__name__}.log', format='{time} {level} {message}', level='DEBUG', rotation='10 MB', compression='zip')

bus = SystemBus()
adapter = bus.get("org.bluez", "/org/bluez/hci0")
device_info_json = {}


# Функция для получения сервисов устройства через D-Bus
async def get_device_services(device_path):
    services = []
    try:
        device = bus.get("org.bluez", device_path)

        # Проверяем, что 'UUIDs' существует и это список
        if 'UUIDs' in device and isinstance(device.UUIDs, list):
            for uuid in device.UUIDs:
                service_info = {
                    'uuid': uuid,
                    'name': 'Unknown Service',  # BlueZ не всегда предоставляет название сервиса
                    'profile': 'Unknown Profile'
                }
                services.append(service_info)
        else:
            services.append({'name': 'No services found', 'uuid': '', 'profile': ''})
    except TypeError:
        services.append({'name': 'No services found', 'uuid': '', 'profile': ''})
    except Exception as e:
        logger.info(f"Какая-то другая ошибка получения сервисов: {e, Exception}")
    return services


# Обработчик для обнаружения устройств
async def device_found(path, properties):
    if 'Address' in properties and 'Name' in properties:
        addr = properties['Address']
        name = properties.get('Name', 'Неизвестное имя')
        device_class = properties.get('Class', 0)

        # Временная метка
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Преобразование класса устройства
        device_class_str = f"0x{device_class:06X}"

        device_class_info = json.loads(device_class_decoder.get_device_class_info(device_class_str))

        # Получаем сервисы устройства
        services = await get_device_services(path)

        # Выводим информацию
        logger.info(f"timestamp: {timestamp}")
        logger.info(f"MAC: {addr}")
        logger.info(f"Имя устройства: {name}")
        logger.info(f"Major Service Class: {device_class_info["Major Service Class"]}")
        logger.info(f"Major Device Class: {device_class_info["Major Device Class"]}")
        logger.info(f"Minor Device Class: {device_class_info["Minor Device Class"]}")
        #logger.info(f"Класс устройства: {device_class_info}")

        # RSSI (если доступен)
        rssi = properties.get('RSSI')
        if rssi:
            logger.info(f"Уровень сигнала: {rssi}")

        # Вывод сервисов
        # print(f"services: {services}")
        if services[0]['name'] != 'No services found':
            logger.log(f"Список сервисов:")
            for service in services:
                logger.info(f"  Имя сервиса: {service['name']}")
                logger.info(f"  UUID сервиса: {service['uuid']}")
                logger.info(f"  Профиль: {service['profile']}")
        else:
            logger.info("Список сервисов: -")
        logger.info("=" * 40)


# Асинхронная функция для запуска сканирования
async def bluetooth_inquiry():
    adapter.StartDiscovery()

    # Получение устройств через D-Bus
    obj_manager = bus.get("org.bluez", "/")
    objects = obj_manager.GetManagedObjects()

    tasks = []
    for path, interfaces in objects.items():
        if 'org.bluez.Device1' in interfaces:
            # Создаем задачу для асинхронного обнаружения устройств
            task = asyncio.create_task(device_found(path, interfaces['org.bluez.Device1']))
            tasks.append(task)

    # Ожидаем завершения всех задач
    await asyncio.gather(*tasks)

    adapter.StopDiscovery()


# Основной цикл работы с asyncio
async def main():
    logger.info("Поиск устройств Bluetooth...")  # Выводим только один раз при запуске программы
    try:
        while True:
            await bluetooth_inquiry()
            await asyncio.sleep(10)  # Асинхронная пауза перед повторным сканированием
    except KeyboardInterrupt:
        logger.info("Сканирование завершено.")


# Запуск основного цикла
try:
    if __name__ == "__main__":
        asyncio.run(main())
except KeyboardInterrupt:
    logger.info("Выход.")
