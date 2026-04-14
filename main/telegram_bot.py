import requests
from django.conf import settings
from users.models import CustomUser

TELEGRAM_TOKEN = settings.TELEGRAM_BOT_TOKEN
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"


def send_telegram_message(chat_id, text):
    """Отправка сообщения в Telegram"""
    url = TELEGRAM_API_URL + "sendMessage"
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, data=data)
        return response.ok
    except:
        return False


def notify_doctor_about_appointment(appointment):
    """Уведомить врача о новой записи"""
    doctor = appointment.doctor

    # Проверяем, есть ли у врача telegram_id
    if not doctor.telegram_id:
        return False

    message = f"""
<b>Новая запись на приём!</b>

Клиент: {appointment.client.username}
Питомец: {appointment.pet_name} ({appointment.pet_type})
Дата и время: {appointment.appointment_date.strftime('%d.%m.%Y %H:%M')}
Симптомы: {appointment.symptoms or 'Не указаны'}

Для просмотра всех записей зайдите в личный кабинет.
    """

    return send_telegram_message(doctor.telegram_id, message)


def notify_client_about_status_change(appointment):
    """Уведомить клиента об изменении статуса записи"""
    client = appointment.client

    if not client.telegram_id:
        return False

    status_text = {
        'CONFIRMED': 'Подтверждён',
        'COMPLETED': 'Проведён',
        'CANCELLED': 'Отменён',
        'RESCHEDULED': 'Перенесён',
    }.get(appointment.status, appointment.status)

    message = f"""
<b>Статус записи изменён</b>

Питомец: {appointment.pet_name}
Врач: {appointment.doctor.username}
Дата: {appointment.appointment_date.strftime('%d.%m.%Y %H:%M')}
Новый статус: {status_text}

Подробности в личном кабинете.
    """

    return send_telegram_message(client.telegram_id, message)