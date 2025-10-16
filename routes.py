from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse, StreamingResponse
import os
import glob
from pathlib import Path
import io


from models import Phone_data, Channel_Data


from parsing import phone_register_send, login_with_cookies, find_channel_by_name, parse_channel_data_optimized


import os


from auth_deps import security



router = APIRouter()


@router.post('/phone_auth', dependencies=[Depends(security.access_token_required)])
def phone_register(phone_num: Phone_data):
    phone_register_send(phone_num.phone)
    return {'message': f'Подтверждение отправлено в тг с номером {phone_num}'}


@router.post('/sign_in', dependencies=[Depends(security.access_token_required)])
def sign_in_with_cookie(phone_num: Phone_data):
    driver = login_with_cookies()
    if not driver:
        return {'message': 'Ошибка входа. Нужна авторизация.'}

    return {'message': f'Успешный вход через куки!{phone_num.phone}'}


@router.post('/univers_parsing', dependencies=[Depends(security.access_token_required)])
def choose_channel(channel_data: Channel_Data):
    driver = login_with_cookies()

    if not driver:
        return {'message': 'Ошибка входа.'}

    try:
        # Используем оптимизированную функцию для парсинга
        result = parse_channel_data_optimized(
            driver, channel_data.channel_name, save_excel=True)

        # Если есть Excel файл, отправляем его и удаляем
        if 'excel_file' in result and result['excel_file']:
            excel_file_path = result['excel_file']

            # Проверяем, что файл существует
            if os.path.exists(excel_file_path):
                # Читаем файл в память
                with open(excel_file_path, 'rb') as f:
                    file_content = f.read()

                # Удаляем файл с диска
                os.remove(excel_file_path)

                # Возвращаем файл как поток
                return StreamingResponse(
                    io.BytesIO(file_content),
                    media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    headers={
                        'Content-Disposition': f'attachment; filename="{excel_file_path}"'}
                )
            else:
                return {'error': 'Excel файл не найден'}
        else:
            return result

    except Exception as e:
        return {'error': f'Ошибка: {e}'}
    finally:
        driver.quit()


# @router.get('/download')
# def download_latest_file():
#     """
#     Скачивает последний созданный Excel файл
#     """
#     try:
#         # Ищем все Excel файлы в текущей директории
#         excel_files = glob.glob("*.xlsx")

#         if not excel_files:
#             raise HTTPException(
#                 status_code=404, detail="Excel файлы не найдены")

#         # Сортируем по времени создания (последний первый)
#         latest_file = max(excel_files, key=os.path.getctime)

#         # Проверяем, что файл существует
#         if not os.path.exists(latest_file):
#             raise HTTPException(status_code=404, detail="Файл не найден")

#         # Возвращаем файл для скачивания
#         return FileResponse(
#             path=latest_file,
#             filename=latest_file,
#             media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=500, detail=f"Ошибка при скачивании файла: {e}")

