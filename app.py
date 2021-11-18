try:
	import requests
	import json
	import os
	import time
	import sys
	import yadisk
	import humanize
except ImportError as e:
	module = str(e).split("'", 2)
	print("Установка следующих модулей: " + module[1] + ". Это может занять некоторое время (5 минут как максимум).")
	os.system("pip install " + module[1])
	os.system("pip3 install " + module[1])
except Exception as e:
	exit('Ошибка при импорте модулей: ' + str(e))
else:
	with open('settings.json', 'r', encoding="utf-8") as settings:
		settings = json.load(settings)
		y = yadisk.YaDisk(token=settings['token'])

def download():
	try:
		path_from = input("Укажите путь, где находится ресурс (со стороны Яндекс.Диска): ")
		path_to = input("Укажите путь, куда загружать ресурс: ")
		y.download(path_from, path_to)
		print("\nРесурс (\"" + str(path_from) + "\") скачан!")
	except yadisk.exceptions.PathNotFoundError:
		print("Не удалось найти запрошенный ресурс")
		return download()
	except yadisk.exceptions.ParentNotFoundError:
		print("Указанного пути \"" + str(path_from) + "\" не существует")
		return download()
	except yadisk.exceptions.PathExistsError:
		print("Ресурс \"" + str(path_from) + "\" уже существует")
		return download()
	except FileNotFoundError:
		print("Не удалось найти ресурс в каталоге \"" + str(path_to) + "\" ")
		return download()
def upload():
	try:
		path_from = input("Укажите путь, где находится ресурс: ")
		path_to = input("Укажите путь, куда загружать ресурс: ")
		y.upload(path_from, path_to)
		print("\nРесурс (\"" + str(path_from) + "\") загружен!")
	except yadisk.exceptions.PathNotFoundError:
		print("Не удалось найти запрошенный ресурс")
		return upload()
	except yadisk.exceptions.ParentNotFoundError:
		print("Указанного пути \"" + str(path_to) + "\" не существует")
		return upload()
	except yadisk.exceptions.PathExistsError:
		print("Ресурс \"" + str(path_to) + "\" уже существует")
		return upload()
	except FileNotFoundError:
		print("Не удалось найти ресурс в каталоге \"" + str(path_from) + "\" ")
		return upload()
def create_folder():
	try:
		path = input("Укажите путь, где будем создавать папку: ")
		y.mkdir(path)
		print("Папка \"" + str(path) + "\" создана!")
	except yadisk.exceptions.PathNotFoundError:
		print("Не удалось найти запрошенный ресурс")
		return create_folder()
	except yadisk.exceptions.ParentNotFoundError:
		print("Указанного пути \"" + str(path) + "\" не существует")
		return create_folder()
	except yadisk.exceptions.DirectoryExistsError:
		print("По указанному пути \"" + str(path) + "\" уже существует папка с таким именем")
		return create_folder()
def remove():
	try:
		path = input("Укажите путь вместе с ресурсом, который необходимо удалить: ")
		perman = input("Удалить безвозвратно [Y/n]: ")
		if perman == "Y" or perman == "y" or perman == "yes" or perman == "Yes":
			y.remove(path, permanently=True)
			print("Ресурс (" + str(path) + ") успешно удалён!")
		elif perman == "N" or perman == "n" or perman == "no" or perman == "No":
			y.remove(path, permanently=False)
			print("Ресурс (" + str(path) + ") успешно помещён в корзину!")
		else:
			remove()
	except yadisk.exceptions.PathNotFoundError:
		print("Не удалось найти запрошенный ресурс")
def remove_trash():
	answer = input("Вы уверены в очистке корзины? (y/[n]):  ")
	if answer.lower() in ("y", "yes"):
		print("Очистка корзины...")
		operation = y.remove_trash("/")
		print("Это может занять некоторое время...")
		if operation is None:
			print("Мне кажется, или корзина была пуста, но не важно. Дело сделано")
			sys.exit(0)
		while True:
			status = y.get_operation_status(operation.href)
			if status == "in-progress":
				time.sleep(5)
				print("Всё ещё жду...")
			elif status == "success":
				print("Корзина очищена!")
				break
			else:
				print("У меня такой статус: %r" % (status,))
				print("Это ненормально!!!")
				break
	else:
		print("Не собираюсь ничего делать")
def content():
	try:
		path = input("Введите путь: ")
		content = list(y.listdir(path))
		size_file = ""
		print("\nВыводим содержимое " + path + ":\n")
		#print(content) #выводит абсолютно всю информацию о контенте
		for x in range(len(content)):
			type_file = content[x]['type']
			if type_file == "dir":
				type_file = "Папка"
				size_file = ""
			elif type_file == "file":
				type_file = "Файл"
				size_file = round(content[x]['size'] / 1024)
				size_file = humanize.intcomma(size_file).replace(',', ' ')
				size_file = "\n	Размер ресурса (в МБ): " + str(size_file) + " КБ"
			else:
				type_file = "Неизвестный тип ресурса"
			media_type_file = content[x]['media_type']

			if media_type_file == "image":
				media_type_file = "Изображение"
			elif media_type_file == "document":
				media_type_file = "Документ"
			elif media_type_file == "compressed":
				media_type_file = "Архив"
			else:
				if type_file == "Папка":
					media_type_file = "Папка"
				else:
					media_type_file = "Неизвестный медиа-тип ресурса"
			data_modified = content[x]['modified'].strftime("%d.%m.%Y %H:%M")
			data_created = content[x]['created'].strftime("%d.%m.%Y %H:%M")
			print(
				"\n" +
				str(x+1) + ". " +
				"Информация о ресурсе " + str(content[x]['name']) +
				"\n	Имя ресурса: " + str(content[x]['name']) +
				"\n	Тип ресурса: " + str(type_file) +
				"\n	Медиа-тип ресурса: " + str(media_type_file) +
				str(size_file) +
				"\n	Создан: " + str(data_created) +
				"\n	Изменён: " + str(data_modified)
				)
	except yadisk.exceptions.PathNotFoundError:
		print("Не удалось найти запрошенный ресурс")
	except yadisk.exceptions.FieldValidationError:
		print("Запрос содержит поля с некорректными данными")
	except yadisk.exceptions.ResourceIsLockedError:
		print("Запрашиваемый ресурс заблокирован другой операцией")
	except yadisk.exceptions.MD5DifferError:
		print("MD5 хэш удаляемого ресурса не совпадает с указанным")
def get_info_disk():
	info_disk = y.get_disk_info()
	total_space = info_disk['total_space'] / 8 / 512 / 512 / 512
	used_space = info_disk['used_space'] / 8 / 512 / 512 / 512
	free_space = round(total_space - used_space, 2)
	trash_size = info_disk['trash_size'] / 8 / 512 / 512 / 512
	is_paid = info_disk['is_paid']
	if is_paid == True:
		is_paid = "Оплачивается"
	else:
		is_paid = "Не оплачивается"
	print(
		"\nИмя пользователя: " + info_disk['user']['display_name'] +
		"\nЛогин: " + info_disk['user']['login'] +
		"\nСвободно " + str(free_space) + " ГБ из " + str(total_space) + " ГБ" +
		"\nИспользуется " + str(round(used_space, 2)) + " ГБ"
		"\nЗанято " + str(round(trash_size, 2)) + " ГБ в корзине" +
		"\nДополнительное место: " + str(is_paid)
		)

def menu():
	try:
		main_menu = input(
			"\nЧто Вы желаете сделать?" +
			"\n\n[1] Скачать ресурс" +
			"\n[2] Загрузить ресурс" +
			"\n[3] Создать новую папку" +
			"\n[4] Удалить безвозвратно ресурс" +
			"\n[5] Очистить корзину" +
			"\n[6] Вывести содержимое ресурса" +
			"\n[7] Получить общую информацию о диске" +
			"\n[8] Выйти с программы" +
			"\n\nВыберите необходимый Вами пункт [1-8]: "
			)
		if main_menu == "1":
			download()
		elif main_menu == "2":
			upload()
		elif main_menu == "3":
			create_folder()
		elif main_menu == "4":
			remove()
		elif main_menu == "5":
			remove_trash()
		elif main_menu == "6":
			content()
		elif main_menu == "7":
			get_info_disk()
		elif main_menu == "8":
			exit("\nВы успешно вышли с программы!")
		else:
			print("\nЭтого пункта не существует. Повторите попытку!")
			menu()
	except ValueError:
		print("Произошла ошибка. Повторите попытку!")
		menu()

if y.check_token() == True:
	menu()
else:
	exit("При проверке токена произошла ошибка.\nВероятнее всего Вы указали неверный токен.\nУкажите верный токен, и перезапустите программу!")