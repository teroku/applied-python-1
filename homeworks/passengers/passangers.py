# -*- encoding: utf-8 -*-

def process(data, events, car):
	trains = list(data)
	for event in events:
   		if event['type'] == "walk":
   			passenger_exists = False
   			passenger = event['passenger']
   			for train in trains:
				for car_number in range(len(train['cars'])):
   					car_temp = train['cars'][car_number]
   					if passenger in car_temp['people']:
   						passenger_exists = True
   						car_temp['people'].remove(passenger)
   						if (car_number + event['distance'] < 0) or (car_number + event['distance'] >= len(train['cars'])):
   							return -1

   						train['cars'][car_number + event['distance']]['people'].append(passenger)
   						break

   			if not passenger_exists:
   				return -1

   		else:
   			train_from_exists = False
   			for train in trains:
   				if train['name'] == event['train_from']:
   					if (len(train['cars']) < event['cars']) or (event['cars'] < 0):
   						return -1

   					train_from_exists = True
   					cars = train['cars'][-event['cars']:]
   					train['cars'] = train['cars'][:-event['cars']]
   					break  # после нахождения нужного поезда далее итерировать не обязательно
   			if not train_from_exists:
   				return -1

   			train_to_exists = False
   			for train in trains:
   				if train['name'] == event['train_to']:
   					train_to_exists = True
   					train['cars'] += cars
   					break
   			if not train_to_exists:
   				return -1

   	for train in trains:
   		for car_temp in train['cars']:
   			if car_temp['name'] == car:
   				return len(car_temp['people'])

	return -1
