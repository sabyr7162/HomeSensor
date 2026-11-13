from sqlalchemy import select, desc, delete

from models import users, devices, measurements


# create user 
def create_user(session, data):
    query = users.insert().values(data)
    result = session.execute(query)
    session.commit()
    return result


#delete user
def remove_user(session, id):
    query = delete(users).where(users.c.id == id)
    result = session.execute(query)
    session.commit()
    return result.rowcount


# find user by email/login
def find_user(session, email):
    query = select(users).where(users.c.email == email)
    result = session.execute(query).mappings().first()
    return result



def find_user_by_id(session, id):
    selected_columns = [col for col in users.c if col.name != 'hashed_password']
    query = select(*selected_columns).where(users.c.id == id)
    result = session.execute(query).mappings().first()
    return result 


def create_device(session, data):
    query = devices.insert().values(data)
    result = session.execute(query)
    session.commit()
    return result 


def remove_device(session, device_id, user_id):
    query = delete(devices).where((devices.c.id == device_id) & (devices.c.user_id == int(user_id)))
    result = session.execute(query)
    session.commit()
    return result.rowcount


def find_devices(session, user_id):
    query = select(devices).where(devices.c.user_id == user_id)
    result = session.execute(query).mappings().fetchall()
    return result


def find_device_by_id(session, device_id):
    query = select(devices).where(devices.c.id == device_id)
    result = session.execute(query).mappings().first()
    return result


def find_device_token(session, token):
    query = select(devices).where(devices.c.token == token)
    result = session.execute(query).mappings().first()
    return result


def add_measurements(session, data):
    query = measurements.insert().values(data)
    result = session.execute(query)
    session.commit()
    return result 


def find_measurements(session, device_id, period):
    query = (
        select(measurements).where(
        (measurements.c.device_id == device_id) & 
        (measurements.c.received_at >= period)
        ).order_by(desc(measurements.c.received_at))
    )
    result = session.execute(query).mappings().all()
    return result


def get_recent_measurement(session, device_id):
    query = select(measurements).where(measurements.c.device_id == device_id).order_by(desc(measurements.c.received_at)).limit(1)
    result =  session.execute(query).mappings().first()
    return result