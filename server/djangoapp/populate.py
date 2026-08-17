from .models import CarMake, CarModel


def initiate():
    # Seeding runs on demand from the get_cars view, so it must be
    # idempotent - a second call must not duplicate rows.
    if CarMake.objects.exists():
        return

    car_make_data = [
        {"name": "NISSAN", "description": "Great cars. Japanese technology.",
         "country": "Japan"},
        {"name": "Mercedes", "description": "Great cars. German technology.",
         "country": "Germany"},
        {"name": "Audi", "description": "Great cars. German technology.",
         "country": "Germany"},
        {"name": "Kia", "description": "Great cars. Korean technology.",
         "country": "South Korea"},
        {"name": "Toyota", "description": "Great cars. Japanese technology.",
         "country": "Japan"},
        {"name": "Ford", "description": "Great cars. American technology.",
         "country": "United States"},
    ]

    car_make_instances = {}
    for data in car_make_data:
        instance = CarMake.objects.create(
            name=data['name'],
            description=data['description'],
            country=data['country'])
        car_make_instances[data['name']] = instance

    car_model_data = [
        {"make": "NISSAN", "name": "Pathfinder", "type": "SUV", "year": 2023},
        {"make": "NISSAN", "name": "Qashqai", "type": "SUV", "year": 2023},
        {"make": "NISSAN", "name": "XTRAIL", "type": "SUV", "year": 2023},
        {"make": "Mercedes", "name": "A-Class", "type": "SUV", "year": 2023},
        {"make": "Mercedes", "name": "C-Class", "type": "SUV", "year": 2022},
        {"make": "Mercedes", "name": "E-Class", "type": "SUV", "year": 2023},
        {"make": "Audi", "name": "A4", "type": "Sedan", "year": 2023},
        {"make": "Audi", "name": "A5", "type": "Coupe", "year": 2022},
        {"make": "Audi", "name": "A6", "type": "Sedan", "year": 2023},
        {"make": "Kia", "name": "Sorento", "type": "SUV", "year": 2023},
        {"make": "Kia", "name": "Carnival", "type": "SUV", "year": 2022},
        {"make": "Kia", "name": "Cerato", "type": "Sedan", "year": 2023},
        {"make": "Toyota", "name": "Corolla", "type": "Sedan", "year": 2023},
        {"make": "Toyota", "name": "Camry", "type": "Sedan", "year": 2022},
        {"make": "Toyota", "name": "Kluger", "type": "SUV", "year": 2023},
        {"make": "Ford", "name": "Ranger", "type": "Wagon", "year": 2023},
        {"make": "Ford", "name": "Escape", "type": "SUV", "year": 2022},
        {"make": "Ford", "name": "Focus", "type": "Hatchback", "year": 2023},
    ]

    for data in car_model_data:
        CarModel.objects.create(
            car_make=car_make_instances[data['make']],
            name=data['name'],
            type=data['type'],
            year=data['year'])
