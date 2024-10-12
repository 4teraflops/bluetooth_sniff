import json


def decode_device_class(device_class):
    # Major Service Classes
    major_service_classes = {
        0x200000: "Network",
        0x100000: "Audio",
        0x080000: "Telephony",
        0x040000: "Object Transfer",
        0x020000: "Capturing",
        0x010000: "Rendering",
        0x008000: "Positioning",
        0x004000: "Networking",
        0x002000: "Broadcasting",
        0x001000: "Limited Discoverable Mode"
    }

    # Major Device Classes
    major_device_classes = {
        0x000100: "Computer",
        0x000200: "Phone",
        0x000300: "LAN/Network Access Point",
        0x000400: "Audio/Video",
        0x000500: "Peripheral",
        0x000600: "Imaging",
        0x000700: "Wearable",
        0x000800: "Toy",
        0x000900: "Health"
    }

    # Minor Device Classes (based on major device class)
    minor_device_classes_computer = {
        0x000000: "-",
        0x000004: "Desktop Workstation",
        0x000008: "Server",
        0x00000C: "Laptop",
        0x000010: "Handheld PC/PDA",
        0x000014: "Palm Sized PC/PDA",
        0x000018: "Wearable computer (watch)"
    }

    minor_device_classes_phone = {
        0x000000: "Uncategorized",
        0x000004: "Cellular",
        0x000008: "Cordless",
        0x00000C: "Smartphone",
        0x000010: "Wired Modem or Voice Gateway",
        0x000014: "Common ISDN Access"
    }

    # Расшифровываем Major Service Class
    major_service = []
    for service_class_code, service_class_name in major_service_classes.items():
        if device_class & service_class_code:
            major_service.append(service_class_name)

    # Расшифровываем Major Device Class
    major_device_class = "Unknown"
    for device_class_code, device_class_name in major_device_classes.items():
        if device_class & 0x1F00 == device_class_code:
            major_device_class = device_class_name
            break

    # Расшифровываем Minor Device Class, если это компьютер или телефон
    minor_device_class = "Uncategorized"
    if major_device_class == "Computer":
        minor_device_class = minor_device_classes_computer.get(device_class & 0xFC, "Uncategorized")
    elif major_device_class == "Phone":
        minor_device_class = minor_device_classes_phone.get(device_class & 0xFC, "Uncategorized")

    # Формируем результат
    return {
        "Major Service Class": ", ".join(major_service) if major_service else "None",
        "Major Device Class": major_device_class,
        "Minor Device Class": minor_device_class
    }

# Пример использования
#device_class_str = 0x240418  # Это пример кода класса устройства

def get_device_class_info(device_class_str):
    # Преобразуем строку в целое число (предполагаем, что это шестнадцатеричное значение)
    device_class_int = int(device_class_str, 16)
    decoded_class = decode_device_class(device_class_int)

    data =         {
            "Major Service Class": f"{decoded_class['Major Service Class']}",
            "Major Device Class": f"{decoded_class['Major Device Class']}",
            "Minor Device Class": f"{decoded_class['Minor Device Class']}"
        }
    json_data = json.dumps(data)

    return json_data
