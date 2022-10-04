from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

INGREDIENT = '{num}. {name} - {amount} {unit}'


def pfd_table(response, cart):
    """Метод формирования PDF таблицы."""
    pdfmetrics.registerFont(TTFont('times', 'timescyr.ttf'))
    page = canvas.Canvas(response)
    page.setFont('times', size=20)
    page.drawString(200, 800, 'Список ингредиентов')
    page.setFont('times', size=14)
    height = 750
    for num, (name, data) in enumerate(cart.items(), 1):
        page.drawString(75, height, INGREDIENT.format(
            num=num, name=name, amount=data['amount'], unit=data['unit']))
        height -= 25
    page.showPage()
    page.save()
    return response
