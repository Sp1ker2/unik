#!/usr/bin/env python3
"""
Загрузить session из локальной папки local-storage/sessions/
Использовать для локального тестирования без S3
"""

import json
import os
from pathlib import Path
from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio

def load_session_local(account_id: str):
    """Загрузить session из локального файла"""
    sessions_dir = Path('local-storage/sessions')
    session_file = sessions_dir / f"session_{account_id}.json"
    
    if not session_file.exists():
        return None
    
    with open(session_file, 'r', encoding='utf-8') as f:
        return json.load(f)


async def test_session_local(account_id: str):
    """Протестировать session локально"""
    session_data = load_session_local(account_id)
    
    if not session_data:
        print(f"❌ Session для account_id {account_id} не найден")
        return False
    
    try:
        client = TelegramClient(
            StringSession(session_data['session_string']),
            int(session_data['api_id']),
            session_data['api_hash']
        )
        
        await client.start()
        me = await client.get_me()
        
        print(f"✅ Session работает!")
        print(f"   Account ID: {me.id}")
        print(f"   Username: @{me.username}" if me.username else "   Username: (нет)")
        print(f"   Имя: {me.first_name} {me.last_name or ''}")
        
        await client.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании session: {e}")
        return False


def list_all_sessions():
    """Показать все локальные сессии"""
    sessions_dir = Path('local-storage/sessions')
    
    if not sessions_dir.exists():
        print("❌ Папка local-storage/sessions не найдена")
        return []
    
    sessions = list(sessions_dir.glob('session_*.json'))
    
    if not sessions:
        print("📭 Нет сохраненных сессий")
        return []
    
    print(f"📁 Найдено {len(sessions)} сессий:\n")
    
    for session_file in sessions:
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            account_id = data.get('account_id', 'unknown')
            phone = data.get('phone_number', 'unknown')
            username = data.get('username', 'нет')
            
            print(f"  • {session_file.name}")
            print(f"    Account ID: {account_id}")
            print(f"    Phone: {phone}")
            print(f"    Username: @{username}" if username != 'нет' else "    Username: (нет)")
            print()
        except Exception as e:
            print(f"  ⚠️  {session_file.name} - ошибка чтения: {e}")
    
    return sessions


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'list':
            list_all_sessions()
        elif sys.argv[1] == 'test' and len(sys.argv) > 2:
            account_id = sys.argv[2]
            asyncio.run(test_session_local(account_id))
        else:
            print("Использование:")
            print("  python load-sessions-local.py list          # Показать все сессии")
            print("  python load-sessions-local.py test <id>     # Протестировать session")
    else:
        print("Использование:")
        print("  python load-sessions-local.py list          # Показать все сессии")
        print("  python load-sessions-local.py test <id>     # Протестировать session")
        print("\nПример:")
        print("  python load-sessions-local.py list")
        print("  python load-sessions-local.py test 12345")

