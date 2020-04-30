import traceback
import os
import sys
from datetime import datetime


state_db_ready = False


def init_state_db(conn)->bool:
    result = False
    try:
        c = conn.cursor()
        c.execute('DROP TABLE IF EXISTS cool_app_state')
        c.execute('CREATE TABLE cool_app_state ( thread_pid INTEGER, alive INTEGER, ready INTEGER, redis_flag INTEGER, redis_bad_counter INTEGER )')
        conn.commit()
    except:
        traceback.print_exc(file=sys.stdout)
    return result


def get_field_value(conn, thread_pid: int, field_name: str, default: int=-1)->int:
    result = default
    try:
        if state_db_ready:
            c = conn.cursor()
            c.execute('SELECT {} FROM cool_app_state WHERE thread_pid = ?'.format(field_name), (thread_pid,))
            row_result = tuple(conn.fetchone())
            if len(row_result) > 0:
                result = row_result[0]
            conn.commit()
        else:
            print('[pid={}] warning: get_field_value(): state db not ready.'.format(thread_pid))
    except:
        traceback.print_exc(file=sys.stdout)
    return result


def update_thread_field(conn, thread_pid: int, field_name: str, value: int)->int:
    result = -1
    try:
        if state_db_ready:
            c = conn.cursor()
            c.execute('UPDATE cool_app_state SET {} = ? WHERE thread_pid = ?'.format(field_name), (value, thread_pid,))
            conn.commit()
            result = get_field_value(conn=conn, thread_pid=thread_pid, field_name=field_name)
            if result != value:
                print('[pid={}] error: update_thread_field() expected {} but got {}. Resetting value to -2'.format(thread_pid, value, result))
                result = -2
        else:
            print('[pid={}] warning: update_thread_field(): state db not ready.'.format(thread_pid))
    except:
        traceback.print_exc(file=sys.stdout)
    return result


def test_state_db_ready(conn, thread_pid: int)->bool:
    global state_db_ready
    state_db_ready = True   # temporarily 
    result = False
    try:
        c = conn.cursor()
        c.execute('DELETE FROM cool_app_state WHERE thread_pid = ?', (thread_pid,))
        c.execute('INSERT INTO cool_app_state (thread_pid, alive, ready) VALUES (?, ?, ?)', (thread_pid, -99, -99))
        conn.commit()
        test1 = get_field_value(conn=conn, thread_pid=thread_pid, field_name='alive') * get_field_value(conn=conn, thread_pid=thread_pid, field_name='ready')
        if test1 == 9801:
            update_thread_field(conn=conn, thread_pid=thread_pid, field_name='alive', value=1)
            update_thread_field(conn=conn, thread_pid=thread_pid, field_name='ready', value=1)
            test2 = get_field_value(conn=conn, thread_pid=thread_pid, field_name='alive') * get_field_value(conn=conn, thread_pid=thread_pid, field_name='ready')
            if test2 == 1:
                result = True
            else:
                state_db_ready = False  # reset back to False
                print('[pid={}] error: state DB is NOT ready [002]'.format(thread_pid))
        else:
            state_db_ready = False
            print('[pid={}] error: state DB is NOT ready [001]'.format(thread_pid))
    except:
        traceback.print_exc(file=sys.stdout)
        state_db_ready = False
    return result