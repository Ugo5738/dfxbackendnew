import random
import re

from django.core.files import File
from django.utils.text import slugify

from inventory import utils
from inventory.models import (Brand, Category, Color, Media, Product,
                              ProductAttribute, ProductAttributeValue,
                              ProductAttributeValues, ProductInventory,
                              ProductType, ProductTypeAttribute, Stock,
                              Storage)

description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin \
            porta, eros vel sollicitudin lacinia, quam metus gravida elit, a elementum \
            nisl neque sit amet orci. Nulla id lorem ac nunc cursus consequat vitae ut orci."


brands = [
    "apple",
    "samsung",
    "google",
    "onePlus",
    "motorola",
    "microsoft",
    "amazon",
    "lenovo",
    "dell",
    "hP",
    "razer",
    "fitbit",
    "garmin",
    "amazfit",
    "sony",
    "bose",
    "sennheiser",
    "akg",
    "bowers & wilkins",
] 

mobile_memory_sizes = list(utils.MOBILE_STORAGE_CHOICES.keys())
desktop_memory_sizes = list(utils.DESKTOP_STORAGE_DEVICES.keys())

product_attributes = {
	"Form Factor": "The form factor refers to the physical size, shape, and layout of a hardware component or device. In the context of computer components, such as motherboards or expansion cards, form factor determines the specific dimensions and mounting configurations that are compatible with a particular system or standard. It ensures that components can be properly installed and fit within the designated spaces of the system case or chassis. Common form factors include ATX, microATX, Mini-ITX for motherboards, and PCIe for expansion cards. Choosing the appropriate form factor is essential for compatibility and efficient use of hardware within a computer system.",
	"Hard Disk": "The hard disk description provides information about the physical attributes and specifications of the device's storage component. It includes details such as the storage capacity, interface type (e.g., SATA or NVMe), rotational speed (e.g., 5400 RPM or 7200 RPM), and form factor (e.g., 2.5-inch or M.2). This information helps users understand the storage capabilities and performance of the device, allowing them to determine its suitability for their needs.",
	"CPU Speed": "The CPU speed refers to the clock frequency at which the device's central processing unit (CPU) operates. It is measured in hertz (Hz) and represents the number of instructions the CPU can execute per second. A higher CPU speed generally indicates faster processing performance, allowing for quicker execution of tasks and improved overall system responsiveness. The CPU speed is a crucial factor to consider when evaluating the device's performance capabilities, especially for demanding applications such as gaming, video editing, and computational tasks.",
	"Graphics Coprocessor": "The graphics coprocessor, also known as the GPU (Graphics Processing Unit), is a specialized component responsible for rendering and displaying visual content on the device's screen. It works in conjunction with the CPU to handle graphics-intensive tasks, including gaming, multimedia playback, and graphics editing. The graphics coprocessor enhances the device's visual capabilities, enabling smooth and realistic graphics rendering. Its specifications, such as the model, memory capacity, and processing power, provide insights into the device's graphics performance and determine its ability to handle graphically demanding applications.",
	"Graphics Card": "The graphics card description provides detailed information about the device's dedicated graphics card, if applicable. A dedicated graphics card, separate from the integrated graphics typically found in CPUs, offers enhanced graphical performance and is particularly important for gaming, 3D modeling, and other graphics-intensive tasks. The description may include the model, memory capacity, type of memory (e.g., GDDR6), clock speed, and other relevant specifications. This information allows users to assess the device's graphical capabilities and determine its suitability for their specific needs.",
	"CPU Model": "The CPU model refers to the specific type and model of the device's central processing unit (CPU). It provides information about the manufacturer, architecture, number of cores, and other relevant specifications. The CPU is the brain of the device, responsible for executing instructions and performing calculations. The CPU model influences the device's overall performance, power efficiency, and multitasking capabilities. Users can use the CPU model information to gauge the device's processing power and compatibility with software requirements, ensuring it meets their desired performance standards.",
	"Package Dimension": "The package dimension refers to the physical size and dimensions of the package in which the items are contained. It represents the measurements of the package, including length, width, and height, and is typically used to determine the size of the package for shipping, storage, and compatibility with accessories or carrying cases. The package dimension ensures that the item(s) are packaged securely and efficiently, while also considering convenience and portability for the end user.",
	"Display Size": "This refers to the physical dimensions of the gadget's screen, measured diagonally from one corner to the opposite corner. The display size determines the overall size of the gadget and influences the visual experience. A larger display size offers more screen real estate, making it ideal for activities like multimedia consumption, gaming, and productivity tasks. On the other hand, a smaller display size may result in a more compact and portable gadget, suitable for one-handed use and easy storage. The choice of display size depends on personal preferences and the intended usage of the gadget.",
	"Network Technology": "The gadget supports advanced network technologies such as 4G LTE and, in some models, 5G. With 4G LTE, you can enjoy fast data transfer speeds for quick web browsing and app downloads. 5G capabilities provide even faster speeds, lower latency, and improved responsiveness for a more immersive mobile experience. The gadget also supports Wi-Fi connectivity, Bluetooth for wireless device connections, and NFC for contactless communication with compatible devices and services.",
	"Screen Resolution": "The gadget features a high-resolution display that showcases vibrant colors and sharp details. The screen utilizes advanced technology to provide excellent contrast, deep blacks, and wide viewing angles, offering an immersive visual experience.",
	"Connectivity": "The gadget supports fast and reliable connectivity options, including 4G LTE and Wi-Fi, ensuring you stay connected wherever you are. It also seamlessly integrates with other devices, making it easy to share content, make calls, and send messages across different platforms.",
	"Battery Life": "The gadget is designed to provide long-lasting battery life, allowing you to stay connected throughout the day. Whether you're browsing the web, streaming media, or using power-intensive apps, the device optimizes power consumption to ensure you can rely on it for extended periods without needing to recharge.",
	"OS": "The gadget operates on a user-friendly and intuitive operating system. This operating system offers a seamless and consistent user experience across various devices and provides access to a wide range of apps, games, and services. Regular updates are released for the operating system, ensuring you have access to the latest features and security enhancements.",
}

# product_type_and_attributes = {
#     # "controller": [],
# 	# "console": [],
# 	# "headset": [],
# 	# "mouse": [],
# 	# "laptop": [],
# 	# "earpiece": [], 
# 	# "Accessories": [], 	
# 	# "iPad": [], 
#     # "Samsung": [],
# 	"Smartphone": ["Operating System", "Battery Life", "Connectivity", "Screen Resolution", "Network Technology", "Display Size"],
# 	"Tablets": ["Operating System", "Battery Life", "Connectivity", "Screen Resolution", "Network Technology", "Display Size"],
#     "Smartwatches": [],
#     "Laptops": [],
#     "Gaming Consoles": [],
# }

product_attribute_values_data = {
    'Lenovo IdeaPad Gaming 3': {
        'Graphics Card': 'Dedicated',
        'Operating System': 'Windows 11 Home',
        'CPU Model': 'Ryzen 5',
        'Display Size': '15.6 inches'
    },
    'Lenovo 2023 Legion 5i Pro 16\"': {
        'Hard Disk': 'SSD',
        'CPU Speed': '2.3 GHz',
        'Graphics Coprocessor': 'NVIDIA GeForce RTX 3050 Ti',
        'Graphics Card': 'Dedicated',
        'Operating System': 'Windows 11 Home',
        'CPU Model': 'Core i7 Family',
        'Display Size': '16 Inches'
    },
    'Apple 2023 MacBook Pro': {
        'Display Size': '14.2 inches',
        'Operating System': 'Mac OS',
    },
    'AirPods Pro (2nd Generation)': {
        'Battery Life': '1 Lithium Ion batteries',
        'Package Dimension': '3.82 x 3.35 x 1.65 inches',
    },
    'iPad Pro 12.9-inch': {
        'Display Size': '12.9 inches',
        'Network Technology': 'GSM / HSPA / LTE / 5G',
        'Screen Resolution': '2048 x 2732 pixels',
        "Connectivity": "Wi-Fi, Bluetooth, USB",
        'Battery Life': 'Li-Po 10758 mAh (40.88 Wh), non-removable',
        'Operating System': "iPadOS 16.1",
    },
    'iPhone 11': {
        "Display Size": "6.1 inches",
        "Network Technology": "GSM / CDMA / HSPA / EVDO / LTE",
        "Screen Resolution": "828 x 1792 pixels",
        "Connectivity": "Wi-Fi, Bluetooth, NFC, USB",
        "Battery Life": "Li-Ion 3110 mAh, non-removable (11.91 Wh)",
        "Operating System": "iOS 13",
    },
    'iPhone 11 Pro': {
        "Display Size": "5.8 inches",
        "Network Technology": "GSM / CDMA / HSPA / EVDO / LTE",	
        "Screen Resolution": "1125 x 2436 pixels",
        "Connectivity": "Wi-Fi, Bluetooth, NFC, USB",
        "Battery Life": "Li-Ion 3046 mAh, non-removable (11.67 Wh)",
        "Operating System": "iOS 13",
    },
    'iPhone 11 pro max': {
        "Display Size": "6.5 inches",
        "Network Technology": "GSM / CDMA / HSPA / EVDO / LTE",	
        "Screen Resolution": "1242 x 2688 pixels",
        "Connectivity": "Wi-Fi, Bluetooth, NFC, USB",
        "Battery Life": "Li-Ion 3969 mAh, non-removable (15.04 Wh)",
        "Operating System": "iOS 13",
    },
    'iPhone 12 Mini': {
        "Display Size": "5.4 inches",
        "Network Technology": "GSM / CDMA / HSPA / EVDO / LTE / 5G",	
        "Screen Resolution": "1170 x 2532 pixels",
        "Connectivity": "Wi-Fi, Bluetooth, NFC, USB",
        "Battery Life": "Li-Ion 2815 mAh, non-removable (10.78Wh)",
        "Operating System": "iOS 14.1",
    },
    'iPhone 13 mini': {
        "Display Size": "5.4 inches",
        "Network Technology": "GSM / CDMA / HSPA / EVDO / LTE / 5G",	
        "Screen Resolution": "1080 x 2340 pixels",
        "Connectivity": "Wi-Fi, Bluetooth, NFC, USB",
        "Battery Life": "Li-Ion 2438 mAh, non-removable (9.34 Wh)",
        "Operating System": "iOS 15",
    },
    'iPhone 12 Pro Max': {
        "Display Size": "6.7 inches",
        "Network Technology": "GSM / CDMA / HSPA / EVDO / LTE / 5G",	
        "Screen Resolution": "1284 x 2778 pixels",
        "Connectivity": "Wi-Fi, Bluetooth, NFC, USB",
        "Battery Life": "Li-Ion 2815 mAh, non-removable (10.78 Wh)",
        "Operating System": "iOS 14.1",
    },
    'iPhone 13': {
        "Display Size": "6.1 inches",
        "Network Technology": "GSM / CDMA / HSPA / EVDO / LTE / 5G",	
        "Screen Resolution": "	1170 x 2532 pixels",
        "Connectivity": "Wi-Fi, Bluetooth, NFC, USB",
        "Battery Life": "Li-Ion 3240 mAh, non-removable (12.41 Wh)",
        "Operating System": "iOS 15",
    },
    'iPhone 13 Pro': {
        "Display Size": "6.1 inches",
        "Network Technology": "GSM / CDMA / HSPA / EVDO / LTE / 5G",	
        "Screen Resolution": "1170 x 2532 pixels",
        "Connectivity": "Wi-Fi, Bluetooth, NFC, USB",
        "Battery Life": "Li-Ion 3095 mAh, non-removable (12.11 Wh)",
        "Operating System": "iOS 15",
    },
    'iPhone 12 Pro Max': {
        "Display Size": "6.7 inches",
        "Network Technology": "GSM / CDMA / HSPA / EVDO / LTE / 5G",
        "Screen Resolution": "1284 x 2778 pixels",
        "Connectivity": "Wi-Fi, Bluetooth, NFC, USB",
        "Battery Life": "Li-Ion 3687 mAh, non-removable (14.13Wh)",
        "Operating System": "iOS 14.1",
    },
    'iPhone 13 Pro Max': {
        "Display Size": "6.7 inches",
        "Network Technology": "GSM / CDMA / HSPA / EVDO / LTE / 5G",
        "Screen Resolution": "1284 x 2778 pixels",
        "Connectivity": "Wi-Fi, Bluetooth, NFC, USB",
        "Battery Life": "Li-Ion 4352 mAh, non-removable (16.75 Wh)",
        "Operating System": "iOS 15",
    },
    'iPhone 14': {
        "Display Size": "6.1 inches",
        "Network Technology": "GSM / CDMA / HSPA / EVDO / LTE / 5G",
        "Screen Resolution": "1170 x 2532 pixels",
        "Connectivity": "Wi-Fi, Bluetooth, NFC, USB",
        "Battery Life": "Li-Ion 3279 mAh, non-removable (12.68 Wh)",
        "Operating System": "iOS 16",
    },
    'iPhone 14 Plus': {
        "Display Size": "6.7 inches",
        "Network Technology": "GSM / CDMA / HSPA / EVDO / LTE / 5G",
        "Screen Resolution": "1284 x 2778 pixels",
        "Connectivity": "Wi-Fi, Bluetooth, NFC, USB",
        "Battery Life": "Li-Ion 4323 mAh, non-removable (16.68 Wh)",
        "Operating System": "iOS 16",
    },
    'Google Pixel Tablet': {
        "Display Size": "10.95 inches",
        "Screen Resolution": "1600 x 2560 pixels",
        "Connectivity": "Wi-Fi, Bluetooth, USB",
        "Battery Life": "Li-Po, non-removable (27 Wh)",
        "Operating System": "iOS 16",
    },
    'iPhone 14 Pro': {
        "Display Size": "6.1 inches",
        "Network Technology": "GSM / CDMA / HSPA / EVDO / LTE / 5G",
        "Screen Resolution": "1179 x 2556 pixels",
        "Connectivity": "Wi-Fi, Bluetooth, USB",
        "Battery Life": "Li-Ion 3200 mAh, non-removable (12.38 Wh)",
        "Operating System": "iOS 16",
    },
    'iPhone 14 Pro Max': {
        "Network Technology": "GSM / CDMA / HSPA / EVDO / LTE / 5G",
        "Screen Resolution": "1290 x 2796 pixels",
        "Connectivity": "Wi-Fi, Bluetooth, USB",
        "Battery Life": "Li-Ion 4323 mAh, non-removable (16.68 Wh)",
        "Operating System": "iOS 16",
    }
}

PRODUCT_TYPE_ATTRIBUTES_1 = [
    "model name",
    "wireless carrier",
    "connectivity technology",
    "screen size"
]

PRODUCT_TYPE_ATTRIBUTES_2 = [
    "operating system",
    "cellular technology",
    "memory storage capacity",
    "battery life",
]

DEFAULT_PRODUCT_TYPE_ATTRIBUTES = PRODUCT_TYPE_ATTRIBUTES_1 + PRODUCT_TYPE_ATTRIBUTES_2

product_type_attributes_data = {
    "Smartphones": DEFAULT_PRODUCT_TYPE_ATTRIBUTES,
    "Tablets": DEFAULT_PRODUCT_TYPE_ATTRIBUTES,
    "Laptops": DEFAULT_PRODUCT_TYPE_ATTRIBUTES + ["graphics card"],
    "Smartwatches": DEFAULT_PRODUCT_TYPE_ATTRIBUTES + ["health and fitness"],
    "Headphones": PRODUCT_TYPE_ATTRIBUTES_1 + ["noise cancelling"],
}


color_list = list(utils.COLOR_CHOICES.keys())

# phones
wireless_list = ["AT&T", "Verizon", "T-Mobile"]
IOS_OS_list = ["iOS 14", "iOS 15", "iOS 16"]
android_OS_list = ["Android 11", "Android 12", "Android 13"]
cellular_list = ["5G", "4G"]
memory = mobile_memory_sizes
connectivity_list = ["Bluetooth", "Wi-Fi", "USB", "NFC"]

# Tablets
mac_OS_list = ["macOS 1", "macOS 2", "macOS 3"]
tab_memory = desktop_memory_sizes
fire_OS_list = ["Fire1 OS", "Fire2 OS", "Fire3 OS"]
ox_OS_list = ["OxygenOS 11", "OxygenOS 12", "OxygenOS 13"]
win_OS_list = ["Windows 10", "Windows 11", "Windows 12"]

# Laptops
lap_memory = desktop_memory_sizes

# watch
tiz_OS_list = ["Tizen 1", "Tizen 2", "Tizen 3"]
fit_OS_list = ["FitbitOS 1", "FitbitOS 2", "FitbitOS 3"]
gar_OS_list = ["GarminOS 1", "GarminOS 2", "GarminOS 3"]
amaz_OS_list = ["AmazfitOS 1", "AmazfitOS 2", "AmazfitOS 3"]

gadgets = {
    "smartphone": {
        "iPhone 12": {
            "apple": {
                "model name": "iPhone 12",
                "wireless carrier": random.choice(wireless_list),
                "operating system": random.choice(IOS_OS_list),
                "cellular technology": random.choice(cellular_list),
                "memory storage capacity": random.choice(memory),
                "connectivity technology": random.choice(connectivity_list),
                "screen size": random.uniform(6.4, 8.0),
            },
        },
        "Samsung Galaxy S21": {
            "samsung": {
                "model name": "Samsung Galaxy S21",
                "wireless carrier": random.choice(wireless_list),
                "operating system": random.choice(android_OS_list),
                "cellular technology": random.choice(cellular_list),
                "memory storage capacity": random.choice(memory),
                "connectivity technology": random.choice(connectivity_list),
                "screen size": random.uniform(6.4, 8.0),
            },
        },
        "Google Pixel 5": {
            "google": {
                "model name": "Google Pixel 5",
                "wireless carrier": random.choice(wireless_list),
                "operating system": random.choice(android_OS_list),
                "cellular technology": random.choice(cellular_list),
                "memory storage capacity": random.choice(memory),
                "connectivity technology": random.choice(connectivity_list),
                "screen size": random.uniform(6.4, 8.0),
            },
        },
        "OnePlus 9 Pro": {
            "onePlus": {
                "model name": "OnePlus 9 Pro",
                "wireless carrier": random.choice(wireless_list),
                "operating system": random.choice(android_OS_list),
                "cellular technology": random.choice(cellular_list),
                "memory storage capacity": random.choice(memory),
                "connectivity technology": random.choice(connectivity_list),
                "screen size": random.uniform(6.4, 8.0),
            },
        },
        "Motorola Moto G Power": {
            "motorola": {
                "model name": "Motorola Moto G Power",
                "wireless carrier": random.choice(wireless_list),
                "operating system": random.choice(android_OS_list),
                "cellular technology": random.choice(cellular_list),
                "memory storage capacity": random.choice(memory),
                "connectivity technology": random.choice(connectivity_list),
                "screen size": random.uniform(6.4, 8.0),
            },
        },
    },
    "tablet": {
        "iPad Pro": {
            "apple": {
                "model name": "iPad Pro",
                "wireless carrier": random.choice(wireless_list),
                "operating system": random.choice(mac_OS_list),
                "cellular technology": random.choice(cellular_list),
                "memory storage capacity": random.choice(tab_memory),
                "connectivity technology": random.choice(connectivity_list),
                "screen size": random.uniform(10, 14),
            },
        },
        "Samsung Galaxy Tab S7": {
            "samsung": {
                "model name": "Samsung Galaxy Tab S7",
                "wireless carrier": random.choice(wireless_list),
                "operating system": random.choice(mac_OS_list),
                "cellular technology": random.choice(cellular_list),
                "memory storage capacity": random.choice(tab_memory),
                "connectivity technology": random.choice(connectivity_list),
                "screen size": random.uniform(10, 14),
            },
        },
        "Microsoft Surface Pro 7": {
            "microsoft": {
                "model name": "Microsoft Surface Pro 7",
                "wireless carrier": random.choice(wireless_list),
                "operating system": random.choice(win_OS_list),
                "cellular technology": random.choice(cellular_list),
                "memory storage capacity": random.choice(tab_memory),
                "connectivity technology": random.choice(connectivity_list),
                "screen size": random.uniform(10, 14),
            },
        },
        "Amazon Fire HD 10": {
            "amazon": {
                "model name": "Amazon Fire HD 10",
                "wireless carrier": random.choice(wireless_list),
                "operating system": random.choice(fire_OS_list),
                "cellular technology": random.choice(cellular_list),
                "memory storage capacity": random.choice(tab_memory),
                "connectivity technology": random.choice(connectivity_list),
                "screen size": random.uniform(10, 14),
            },
        },
        "Lenovo Tab M10 Plus": {
            "lenovo": {
                "model name": "Lenovo Tab M10 Plus",
                "wireless carrier": random.choice(wireless_list),
                "operating system": random.choice(android_OS_list),
                "cellular technology": random.choice(cellular_list),
                "memory storage capacity": random.choice(tab_memory),
                "connectivity technology": random.choice(connectivity_list),
                "screen size": random.uniform(10, 14),
            },
        },
    },
    "laptop": {
        "MacBook Pro": {
            "apple": {
                "model name": "MacBook Pro",
                "wireless carrier": random.choice(wireless_list),
                "operating system": random.choice(mac_OS_list),
                "cellular technology": random.choice(cellular_list),
                "memory storage capacity": random.choice(lap_memory),
                "connectivity technology": random.choice(connectivity_list),
                "screen size": random.uniform(10, 14),
            },
        },
        "Dell XPS 13": {
            "dell": {
                "model name": "Dell XPS 13",
                "wireless carrier": random.choice(wireless_list),
                "operating system": random.choice(win_OS_list),
                "cellular technology": random.choice(cellular_list),
                "memory storage capacity": random.choice(lap_memory),
                "connectivity technology": random.choice(connectivity_list),
                "screen size": random.uniform(10, 14),
            },
        },
        "HP Spectre x360": {
            "hP": {
                "model name": "HP Spectre x360",
                "wireless carrier": random.choice(wireless_list),
                "operating system": random.choice(win_OS_list),
                "cellular technology": random.choice(cellular_list),
                "memory storage capacity": random.choice(lap_memory),
                "connectivity technology": random.choice(connectivity_list),
                "screen size": random.uniform(10, 14),
            },
        },
        "Lenovo ThinkPad X1 Carbon": {
            "lenovo": {
                "model name": "Lenovo ThinkPad X1 Carbon",
                "wireless carrier": random.choice(wireless_list),
                "operating system": random.choice(win_OS_list),
                "cellular technology": random.choice(cellular_list),
                "memory storage capacity": random.choice(lap_memory),
                "connectivity technology": random.choice(connectivity_list),
                "screen size": random.uniform(10, 14),
            },
        },
        "Razer Blade Stealth": {
            "razer": {
                "model name": "Razer Blade Stealth",
                "wireless carrier": random.choice(wireless_list),
                "operating system": random.choice(win_OS_list),
                "cellular technology": random.choice(cellular_list),
                "memory storage capacity": random.choice(lap_memory),
                "connectivity technology": random.choice(connectivity_list),
                "screen size": random.uniform(10, 14),
            },
        },
    },
    "smartwatch": {
        "Apple Watch Series 6": {
            "apple": {
                "model name": "Apple Watch Series 6",
                "wireless carrier": random.choice(wireless_list),
                "operating system": random.choice(mac_OS_list),
                "cellular technology": random.choice(cellular_list),
                "connectivity technology": random.choice(connectivity_list),
                "screen size": random.uniform(1, 2),
            },
        },
        "Samsung Galaxy Watch 3": {
            "samsung": {
                "model name": "Samsung Galaxy Watch 3",
                "wireless carrier": random.choice(wireless_list),
                "operating system": random.choice(tiz_OS_list),
                "cellular technology": random.choice(cellular_list),
                "connectivity technology": random.choice(connectivity_list),
                "screen size": random.uniform(1, 2),
            },
        },
        "Fitbit Sense": {
            "fitbit": {
                "model name": "Fitbit Sense",
                "wireless carrier": random.choice(wireless_list),
                "operating system": random.choice(fit_OS_list),
                "cellular technology": random.choice(cellular_list),
                "connectivity technology": random.choice(connectivity_list),
                "screen size": random.uniform(1, 2),
            },
        },
        "Garmin Venu Sq": {
            "garmin": {
                "model name": "Garmin Venu Sq",
                "wireless carrier": random.choice(wireless_list),
                "operating system": random.choice(gar_OS_list),
                "cellular technology": random.choice(cellular_list),
                "connectivity technology": random.choice(connectivity_list),
                "screen size": random.uniform(1, 2),
            },
        },
        "Amazfit Bip S": {
            "amazfit": {
                "model name": "Amazfit Bip S",
                "wireless carrier": random.choice(wireless_list),
                "operating system": random.choice(amaz_OS_list),
                "cellular technology": random.choice(cellular_list),
                "connectivity technology": random.choice(connectivity_list),
                "screen size": random.uniform(1, 2),
            },
        },
    },
    "headphone": {
        "Sony WH-1000XM4": {
            "sony": {
                "model name": "Sony WH-1000XM4",
                "wireless carrier": random.choice(wireless_list),
                "connectivity technology": random.choice(connectivity_list),
            },
        },
        "Bose QuietComfort 35 II": {
            "bose": {
                "model name": "Bose QuietComfort 35 II",
                "wireless carrier": random.choice(wireless_list),
                "connectivity technology": random.choice(connectivity_list),
            },
        },
        "Sennheiser HD 660 S": {
            "sennheiser": {
                "model name": "Sennheiser HD 660 S",
                "wireless carrier": random.choice(wireless_list),
                "connectivity technology": random.choice(connectivity_list),
            },
        },
        "AKG N700NC": {
            "akg": {
                "model name": "AKG N700NC",
                "wireless carrier": random.choice(wireless_list),
                "connectivity technology": random.choice(connectivity_list),
            },
        },
        "Bowers & Wilkins PX7": {
            "bowers & wilkins": {
                "model name": "Bowers & Wilkins PX7",
                "wireless carrier": random.choice(wireless_list),
                "connectivity technology": random.choice(connectivity_list),
            },
        },
    },
}

def get_price():
    discount_percent = 10
    profit = 100
    give_away = 300

    store_price = round(random.uniform(100000, 1000000), 2)
    retail_price = store_price - profit
    sale_price = store_price - give_away
    discount_store_price = store_price - ((discount_percent / 100) * store_price)

    return retail_price, store_price, discount_store_price, sale_price

def populate_db():
    for brand in brands:
        new_brand = Brand(name=brand)
        new_brand.save()

    for i, size in enumerate(utils.MOBILE_STORAGE_CHOICES):
        new_size = Storage(size=size, order_field=i+1)
        new_size.save()

    for color, hex_code in utils.COLOR_CHOICES.items():
        new_color = Color(name=color, hex_code=hex_code)
        new_color.save()

    for product_type, product_type_attributes in product_types.items():
        product_type, created = ProductType.objects.get_or_create(name=product_type)
        if created:
            product_type.save()
            for product_attribute in product_type_attributes:
                new_product_attribute, created = ProductAttribute.objects.get_or_create(
                    name=product_attribute, product_type=product_type
                )
                if created:
                    new_product_attribute.save()
                product_type.product_type_attributes.add(new_product_attribute)

    _sku = random.randint(0, 99999)
    _upc = random.randint(0, 99999)
    for gadget, product_inventory_dict in gadgets.items():
        category = Category(
            name=gadget,
            slug=gadget,
            is_active=True,
        )
        category.save()

        _web_id = random.randint(1000000, 9999999)
        for product, branded_attributes in product_inventory_dict.items():
            reviewed_product = remove_special_characters(product)
            new_product = Product(
                web_id=str(_web_id),
                slug=reviewed_product.replace(" ", "-"),
                name=product,
                description=description,
            )
            new_product.save()
            new_product.category.set([category])
            _web_id += 1

            for i in range(3):
                for brand, product_attributes in branded_attributes.items():
                    brand_obj = Brand.objects.get(name=brand)
                    color_obj = Color.objects.get(name=random.choice(color_list))
                    storage_size = Storage.objects.get(size=random.choice(mobile_memory_sizes))

                    if i > 0:
                        default = False
                    else:
                        default = True

                    retail_price, store_price, discount_store_price, sale_price = get_price()
                    new_inventory = ProductInventory(
                        sku="SKU-{:05d}".format(_sku),
                        upc="UPC-{:05d}".format(_upc),
                        is_default=default,
                        retail_price=retail_price,
                        store_price=store_price,
                        discount_store_price=discount_store_price,
                        sale_price=sale_price,
                        weight=round(random.uniform(100, 500), 2),
                        product_type=product_type,
                        product=new_product,
                        brand=brand_obj,
                        color=color_obj,
                        storage_size=storage_size,
                    )

                    new_inventory.save()

                    product_stock = Stock(
                        product_inventory=new_inventory, units=random.randint(50, 500)
                    )
                    product_stock.save()

                    file_path = r"assets\phone.webp"

                    for j in range(4):
                        if j < 1:
                            img_default = True
                        else:
                            img_default = False
                        # Open the image file
                        with open(file_path, "rb") as f:
                            # Create a Django File object
                            django_file = File(f)

                            Media.objects.create(
                                product_inventory=new_inventory, image=django_file, is_feature=img_default
                            )

                    product_type = ProductType.objects.prefetch_related("product_type_attributes").get(
                        name=gadget
                    )
                    attribute_list = []
                    attributes = product_type.product_type_attributes.values_list("name", flat=True)
                    for attribute in attributes:
                        attribute_list.append(attribute)
                    for attribute_name, attribute_value in product_attributes.items():
                        if attribute_name in attribute_list:
                            productattribute_obj = ProductAttribute.objects.get(name=attribute_name)
                            attrib_value = ProductAttributeValue(attribute_value=attribute_value)
                            attrib_value.product_attribute = productattribute_obj
                            attrib_value.save()
                            new_inventory.attribute_values.add(attrib_value)
                        new_inventory.save()

                    _sku += 1
                    _upc += 1

def remove_special_characters(string):
    return re.sub(r"[^\w\s]", "", string)


categories_structure = {
    'Computers & Accessories': {
        'Laptops': {
            'Gaming Laptops': {
                'High-End Gaming Laptops': {
                    'VR Ready': {},
                    '4K Display': {}
                },
                'Budget Gaming Laptops': {}
            },
            'Ultrabooks': {
                'Touchscreen Ultrabooks': {},
                'Non-Touchscreen Ultrabooks': {}
            },
            '2-in-1 Laptops': {
                'Detachable 2-in-1s': {},
                'Convertible 2-in-1s': {}
            },
            'Mac Laptops': {
                'MacBook Air': {},
                'MacBook Pro': {
                    'MacBook Pro 13-inch': {},
                    'MacBook Pro 16-inch': {}
                }
            }
        },
        'Desktops': {
            'Gaming Desktops': {},
            'Workstations': {},
            'All-in-One PCs': {}
        },
        'Tablets': {
            'Android Tablets': {
                'High-Performance Tablets': {},
                'Budget Tablets': {}
            },
            'iPads': {
                'iPad Pro': {},
                'iPad Air': {},
                'iPad Mini': {},
                'Standard iPad': {}
            },
            'Windows Tablets': {
                'Surface Pro': {},
                'Other Windows Tablets': {}
            },
            'E-Readers': {
                'Kindle': {},
                'Other E-Readers': {}
            },
            'Tablet Accessories': {
                'Tablet Cases & Covers': {},
                'Styluses': {},
                'Screen Protectors for Tablets': {},
                'Tablet Keyboards': {},
                'Tablet Stands & Mounts': {}
            }
        },
        'Computer Accessories': {
            'Keyboards': {},
            'Mice': {},
            'Headsets': {}
        },
        'Other': {} 
    },
    'Mobile Phones & Accessories': {
        'Smartphones': {
            'Android Phones': {
                'Flagship Android Phones': {},
                'Mid-Range Android Phones': {},
                'Budget Android Phones': {}
            },
            'iPhones': {
                'Latest iPhone': {},
                'Older iPhone Models': {}
            },
            'Basic Phones': {
                'Feature Phones': {},
                'Rugged Phones': {}
            }
        },
        'Mobile Accessories': {
            'Cases & Covers': {
                'Silicone Cases': {},
                'Leather Cases': {},
                'Hard Plastic Cases': {},
                'Waterproof Cases': {}
            },
            'Screen Protectors': {
                'Tempered Glass': {},
                'Anti-Glare': {},
                'Privacy': {}
            },
            'Chargers & Cables': {
                'Wall Chargers': {},
                'Car Chargers': {},
                'Wireless Chargers': {},
                'USB-C Cables': {},
                'Micro-USB Cables': {},
                'Lightning Cables': {}
            },
            'Headphones & Earbuds': {
                'Wired Earbuds': {},
                'Bluetooth Earbuds': {},
                'Over-Ear Headphones': {}
            },
            'Other Accessories': {
                'Pop Sockets & Grips': {},
                'Camera Attachments': {},
                'Mobile Stands & Mounts': {}
            }
        },
        'Other': {} 
    },
    'Audio & Sound': {
        'Headphones': {
            'Over-Ear': {},
            'In-Ear': {},
            'Noise Cancelling': {}
        },
        'Speakers': {
            'Bluetooth Speakers': {},
            'Soundbars': {}
        },
        'Audio Accessories': {
            'Microphones': {},
            'Audio Cables': {}
        },
        'Other': {} 
    },
    'Gaming & Consoles': {
        'Gaming Consoles': {
            'PlayStation': {},
            'Xbox': {},
            'Nintendo': {}
        },
        'Video Games': {
            'PC Games': {},
            'Console Games': {}
        },
        'Gaming Accessories': {
            'Controllers': {},
            'VR Headsets': {}
        },
        'Other': {} 
    },
    'Wearables & Smartwatches': {
        'Fitness Trackers': {},
        'Smartwatches': {
            'Android Wear': {},
            'Apple Watch': {}
        },
        'Other': {} 
    },
    'Cameras & Photography': {
        'DSLR Cameras': {},
        'Mirrorless Cameras': {},
        'Point & Shoot Cameras': {},
        'Camera Accessories': {
            'Lenses': {},
            'Tripods': {}
        },
        'Other': {} 
    },
    'Home Appliances & Gadgets': {
        'Smart Home Devices': {
            'Smart Lights': {},
            'Smart Plugs': {}
        },
        'Kitchen Gadgets': {
            'Smart Coffee Makers': {},
            'Blenders': {}
        },
        'Cleaning Appliances': {
            'Robot Vacuums': {},
            'Air Purifiers': {}
        },
        'Other': {} 
    },
}


# ------------------ POPULATE CATEGORY MODEL ------------------
def create_category(name, parent=None):
    slug = slugify(name)
    category, created = Category.objects.get_or_create(
        name=name, 
        defaults={
            # 'slug': name.replace(" & ", "_").replace(" ", "_").lower(),
            'slug': slug,
            'parent': parent
        }
    )
    return category

def populate_categories(data, parent=None):
    for category_name, children in data.items():
        cat = create_category(category_name, parent)
        populate_categories(children, cat)


# 1. Categories
electronics = Category.objects.get(name="Electronics", slug="electronics")
computer_accessories = Category.objects.get(name='Computers & Accessories', slug="computers-accessories", parent=electronics)
mobiles = Category.objects.get(name='Mobile Phones & Accessories', slug="mobiles-accessories", parent=electronics)

android_tablets = Category.objects.get(name="Android Tablets")
iPad_tablets = Category.objects.get(name="iPads") 
            

# ------------------ POPULATE PRODUCT TYPE MODEL ------------------
def create_product_type(name, parent=None):
    product_type, created = ProductType.objects.get_or_create(
        name=name, 
        defaults={
            'parent': parent
        }
    )
    return product_type

def populate_product_types(categories, parent=None):
    for category, children in categories.items():
        product_type = create_product_type(category, parent)
        populate_product_types(children, product_type)


# ------------------ POPULATE BRAND MODEL ------------------
def create_brand(name):
    brand, created = Brand.objects.get_or_create(name=name)
    return brand

def populate_brands(brands_list):
    for brand_name in brands_list:
        create_brand(brand_name)


# ------------------ POPULATE COLOR MODEL ------------------
def create_color(name, hex_code):
    color, created = Color.objects.get_or_create(name=name, hex_code=hex_code)
    return color

def populate_colors():
    for color, hex_code in utils.COLOR_CHOICES.items():
        create_color(color, hex_code)


# ------------------ POPULATE STORAGE MODEL ------------------
def create_storage(size, order_value):
    storage, created = Storage.objects.get_or_create(size=size, order_field=order_value)
    return storage

def populate_storages():
    for order_value, memory in enumerate(mobile_memory_sizes):
        create_storage(memory, order_value)


# ------------------ POPULATE PRODUCT ATTRIBUTE MODEL ------------------
def create_product_attribute(name, description):
    attribute, created = ProductAttribute.objects.get_or_create(
        name=name,
        defaults={'description': description}
    )
    return attribute

def populate_product_attributes():
    for attribute_name, description in product_attributes.items():
        create_product_attribute(attribute_name, description)


# ------------------ POPULATE PRODUCT TYPE ATTRIBUTE MODEL ------------------
def create_product_type_attribute(product_type, attribute):
    product_type_attribute, created = ProductTypeAttribute.objects.get_or_create(
        product_type=product_type,
        attribute=attribute
    )
    return product_type_attribute

def populate_product_type_attributes(product_type_data):
    for product_type_name, attributes in product_type_data.items():
        product_type = ProductType.objects.get(name=product_type_name)
        for attribute_name in attributes:
            attribute = ProductAttribute.objects.get(name=attribute_name)
            create_product_type_attribute(product_type, attribute)


# ------------------ POPULATE PRODUCT ATTRIBUTE VALUE MODEL ------------------
def create_product_attribute_value(product, attribute, value):
    product_attribute_value, created = ProductAttributeValue.objects.get_or_create(
        product=product,
        attribute=attribute,
        defaults={'value': value}
    )
    return product_attribute_value

# def populate_product_attribute_values(data):
#     for product_name, attributes in data.items():
#         product = Product.objects.get(name=product_name)
#         for attribute_name, value in attributes.items():
#             attribute = ProductAttribute.objects.get(name=attribute_name)
#             create_product_attribute_value(product, attribute, value)


def populate_product_attribute_values(data):
    for product_name, attributes in data.items():
        try:
            product = Product.objects.get(name=product_name)
            product_type = product.product_type

            for attribute_name, value in attributes.items():
                attribute = ProductAttribute.objects.get(name=attribute_name)

                # Check if the product type supports this attribute
                if not ProductTypeAttribute.objects.filter(product_type=product_type, attribute=attribute).exists():
                    print(f"Error: {attribute_name} is not an allowed attribute for {product_type.name}. Skipping...")
                    continue

                create_product_attribute_value(product, attribute, value)

        except Product.DoesNotExist:
            print(f"Error: Product {product_name} does not exist. Skipping...")
        except ProductAttribute.DoesNotExist:
            print(f"Error: Attribute {attribute_name} does not exist. Skipping...")


def populate_data():
    populate_categories(categories_structure)
    populate_brands()
    populate_product_attributes()
    populate_product_types(categories_structure)
    populate_product_type_attributes(product_type_attributes_data)
    populate_product_attribute_values(product_attribute_values_data)