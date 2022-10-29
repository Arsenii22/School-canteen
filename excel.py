from openpyxl import Workbook, load_workbook

a = Workbook()
b = a.active
b.title("Столовка")

for i in massive:
    b.append(i)

a.save()