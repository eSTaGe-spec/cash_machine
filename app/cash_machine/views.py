import os
import pdfkit
import qrcode
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.template.loader import render_to_string
from rest_framework import status
from django.http import HttpResponse, Http404
from django.conf import settings

from .models import Item


@api_view(['POST'])
def cash_machine(request):
    data = request.data
    item_ids = data.get('items', [])

    items = Item.objects.filter(id__in=item_ids)

    if not items:
        return Response({'error': 'Товар(ы) не были найдены'}, status=status.HTTP_400_BAD_REQUEST)

    total_price = sum(item.price for item in items)
    cur_time = timezone.now().strftime('%d.%m.%Y %H:%M')

    html_receipt = render_to_string('cash_machine/receipt.html', {
        'items': items,
        'total_price': total_price,
        'cur_time': cur_time,
    })

    current_date_for_filename = timezone.now().strftime('%Y-%m-%d')

    media_dir = os.path.join('media', current_date_for_filename)
    os.makedirs(media_dir, exist_ok=True)

    pdf_filename = f'receipt_{int(timezone.now().timestamp())}.pdf'
    pdf_path = os.path.join(media_dir, pdf_filename)

    config = pdfkit.configuration(wkhtmltopdf=os.getenv('CONFIG_PATH'))
    pdfkit.from_string(html_receipt, pdf_path, configuration=config)

    qr_data = f"http://{os.getenv('IP')}/media/{current_date_for_filename}/{pdf_filename}"
    qr = qrcode.make(qr_data)

    qr_file_path = os.path.join(media_dir, f'qr_{int(timezone.now().timestamp())}.png')
    qr.save(qr_file_path)

    with open(qr_file_path, 'rb') as qr_file:
        qr_image = qr_file.read()

    response = HttpResponse(qr_image, content_type='image/png')
    response['Content-Disposition'] = 'inline; filename="QR_code.png"'

    return response


def return_pdf(request, filepath):
    file_path = os.path.join(settings.MEDIA_ROOT, filepath)

    if not os.path.exists(file_path):
        raise Http404("Файл не найден")

    with open(file_path, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
        return response
