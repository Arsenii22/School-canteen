from openpyxl import Workbook, load_workbook
import bot

wb = load_workbook('a.xlsx')
ws = wb.active
ws.title = "School info"

for i in range(1, 178):
    pass

wb.save()
