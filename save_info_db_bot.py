from db_models import User, Conversion, ConversionStatus
from db_sessions import sessionlocal
from logging import info, error

def save_info_db(user_id: int, username: str | None, original_file_id: str, pdf_file_id: str, timestamp):
    db = sessionlocal()
    try:
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if user:
            if user.username != username:
                user.username = username
            user_db_id = user.id
        else:
            user = User(telegram_id=user_id, username=username)
            db.add(user)
            db.flush()
            user_db_id = user.id

        status = db.query(ConversionStatus).filter_by(status_name="completed").first()
        if not status:
            raise RuntimeError("Статус 'completed' не найден в таблице conversion_status")

        conversion = Conversion(
            user_id=user_db_id,
            file_id=original_file_id,
            pdf_file_id=pdf_file_id,
            status_id=status.id,
            created_at=timestamp
        )
        db.add(conversion)
        db.commit()
        info("Запись сохранена в БД")
    except Exception as e:
        db.rollback()
        error("Ошибка сохранения в БД: %s", e)
    finally:
        db.close()